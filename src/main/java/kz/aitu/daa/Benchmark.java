package kz.aitu.daa;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.function.IntSupplier;

public final class Benchmark {
    public static final int RUNS = 5;
    public static final int WARMUPS = 3;
    private static volatile int sink;
    private final List<String> log = new ArrayList<>();

    public void run(Path directory) throws IOException {
        Files.createDirectories(directory);
        Path temporary = Files.createTempFile(directory, "results-", ".tmp");
        try (BufferedWriter csv = Files.newBufferedWriter(temporary)) {
            csv.write("algorithm,input,n,m,run,time_ms,result,calls,states,comparisons,lps_comparisons,peak_array_cells,max_depth,seed,input_sha256\n");
            for (int n : new int[]{3, 6, 9, 12}) {
                for (String type : List.of("identical", "disjoint")) {
                    editCase(csv, type, n, true);
                }
            }
            for (int n : new int[]{128, 256, 512, 1024, 2048}) {
                for (String type : List.of("identical", "disjoint")) editCase(csv, type, n, false);
            }
            for (int n : new int[]{4096, 16384, 65536, 262144}) {
                for (String type : List.of("random", "near_match")) searchCase(csv, type, n, n / 64);
            }
        } catch (Throwable failure) {
            Files.deleteIfExists(temporary);
            throw failure;
        }
        try {
            Files.move(temporary, directory.resolve("results.csv"), StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
        } catch (AtomicMoveNotSupportedException e) {
            Files.move(temporary, directory.resolve("results.csv"), StandardCopyOption.REPLACE_EXISTING);
        }
        Files.write(directory.resolve("benchmark.log"), log);
        Files.writeString(directory.resolve("environment.txt"),
                "Measured at (UTC): " + Instant.now() + "\nJava: " + System.getProperty("java.runtime.version")
                + "\nVM: " + System.getProperty("java.vm.name") + "\nOS: " + System.getProperty("os.name")
                + " " + System.getProperty("os.version") + " " + System.getProperty("os.arch")
                + "\nAvailable processors: " + Runtime.getRuntime().availableProcessors()
                + "\nMax heap bytes: " + Runtime.getRuntime().maxMemory()
                + "\nSeed: " + InputGenerator.SEED + "\nWarmups per case: " + WARMUPS + "\nMeasured runs per case: " + RUNS
                + "\nTiming: System.nanoTime; generation, fingerprinting and validation excluded.\n"
                + "Sequential, fixed case order; no forced GC. Instrumentation and allocations included.\n");
        System.out.println("Saved 300 measured rows to " + directory.resolve("results.csv"));
    }

    private void editCase(BufferedWriter csv, String type, int n, boolean recursive) throws IOException {
        InputGenerator.Pair input = InputGenerator.edit(type, n);
        int expected = new TableEditDistance().distance(input.first(), input.second());
        List<EditDistance> algorithms = new ArrayList<>();
        if (recursive) algorithms.add(new RecursiveEditDistance());
        algorithms.add(new TableEditDistance()); algorithms.add(new TwoRowEditDistance());
        for (EditDistance algorithm : algorithms) {
            String name = algorithm instanceof RecursiveEditDistance ? "recursive"
                    : algorithm instanceof TableEditDistance ? "table" : "two_rows";
            measure(csv, name, type, n, n, input.fingerprint(), algorithm.metrics(),
                    () -> algorithm.distance(input.first(), input.second()), expected);
        }
    }

    private void searchCase(BufferedWriter csv, String type, int n, int m) throws IOException {
        InputGenerator.Pair input = InputGenerator.search(type, n, m);
        List<Integer> expected = new ArrayList<>();
        for (int at = input.first().indexOf(input.second()); at >= 0; at = input.first().indexOf(input.second(), at + 1)) expected.add(at);
        for (StringSearch algorithm : List.of(new NaiveSearch(), new KmpSearch())) {
            if (!expected.equals(algorithm.search(input.first(), input.second()))) throw new IllegalStateException("Search validation failed");
            measure(csv, algorithm instanceof NaiveSearch ? "naive" : "kmp", type, n, m, input.fingerprint(),
                    algorithm.metrics(), () -> algorithm.search(input.first(), input.second()).size(), expected.size());
        }
    }

    private void measure(BufferedWriter csv, String algorithm, String type, int n, int m,
                         String fingerprint, Metrics metrics, IntSupplier action, int expected) throws IOException {
        for (int i = 0; i < WARMUPS; i++) {
            sink = action.getAsInt();
            if (sink != expected) throw new IllegalStateException("Warmup answer mismatch");
        }
        long[] times = new long[RUNS];
        String counters = null;
        for (int run = 1; run <= RUNS; run++) {
            long start = System.nanoTime();
            int answer = action.getAsInt();
            long elapsed = System.nanoTime() - start;
            sink = answer;
            if (answer != expected) throw new IllegalStateException("Answer mismatch");
            String current = metrics.csv();
            if (counters != null && !counters.equals(current)) throw new IllegalStateException("Non-deterministic counters");
            counters = current;
            times[run - 1] = elapsed;
            csv.write(String.format(Locale.ROOT, "%s,%s,%d,%d,%d,%.9f,%d,%s,%d,%s%n",
                    algorithm, type, n, m, run, elapsed / 1_000_000.0, answer, current, InputGenerator.SEED, fingerprint));
        }
        Arrays.sort(times);
        String line = String.format(Locale.ROOT, "%s %-10s n=%d m=%d median_ms=%.6f %s",
                algorithm, type, n, m, times[RUNS / 2] / 1_000_000.0, counters);
        log.add(line);
        System.out.println(line);
    }
}
