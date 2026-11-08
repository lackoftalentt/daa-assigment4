# DAA Assignment 4 - Dynamic Programming and String Algorithms

**Beibarys Balykbayev - SE-2516**  
Design and Analysis of Algorithms, Taubakabyl Nurlybek.

Repository: https://github.com/lackoftalentt/daa-assigment4  
Branch: `main`. Final local release tag: `v1.0`.

## Build and test

Requires **JDK 17+** and **Maven 3.8+**. The first build downloads Maven plugins and JUnit 5; production code has no third-party dependencies.

```bash
mvn clean verify
java -jar target/daa-assignment4-1.0.jar demo
```

`mvn test` runs **17 JUnit 5 test invocations**. They check all assignment reference values, empty strings/patterns, patterns longer than text, overlapping occurrences, 100 random short edit-distance pairs, 100 random search cases against Java's `String.indexOf`, 100 brute-force LPS checks, unequal string lengths, and counters/reset behavior. Test reports are in `target/surefire-reports/`.

The demo prints distance 3 for `kitten`/`sitting` in all three implementations, `[0, 1, 2, 0, 1, 2, 3, 3]` for `lps("AAACAAAA")`, and matches `[0, 1, 2, 3]` for `AAAAA`/`AA` in both search implementations. Matching is case-sensitive and uses Java UTF-16 `char` indices. `Abylai Han`/`Abylai Khan` has distance **2**, because changing uppercase `H` to `K` and inserting lowercase `h` are separate edits.

## Experiment and PDF report

The delivered [REPORT.pdf](REPORT.pdf) is **four pages**. It starts with the Experiment Design Card, includes all four PNG plots and their takeaways, compares predictions with results, and answers the four required questions. The full original prediction-first plan is in [EXPERIMENT_DESIGN.md](EXPERIMENT_DESIGN.md), committed before the benchmark.

```bash
java -Xms256m -Xmx1g -jar target/daa-assignment4-1.0.jar benchmark results
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r scripts/requirements.txt
python3 scripts/analyze.py
python3 scripts/render_report.py
```

With the prerequisites installed, run `bash scripts/reproduce.sh` to rebuild, test, benchmark, draw plots, and regenerate the PDF. To redraw only the supplied results, run the last two Python commands. Python dependencies are used only for analysis and PDF creation; the submitted report and PNGs can be viewed without them.

Each case has **three warmups and five measured runs**. `results/results.csv` contains **300 individual rows**, covering 60 algorithm/input/size cases; `summary.csv` contains the 60 medians. Inputs, answers, and counters repeat for seed **20261108**. Wall-clock times vary across executions and hardware. Strings and SHA-256 fingerprints are generated outside timing, and the harness checks results outside timing; allocations, counters, and KMP preprocessing are included. Search results are consumed as list sizes within timing; full match lists are validated separately before each search case and in tests.

| Family | Sizes | Input purpose |
| --- | --- | --- |
| All Edit Distance versions | n=m=3, 6, 9, 12 | Identical strings show matching shortcuts; disjoint alphabets force recursive branching. |
| Full table and two rows extension | n=m=128, 256, 512, 1024, 2048 | Show quadratic state counts and different storage growth on both types. |
| Both string searches | n=4096, 16384, 65536, 262144; m=n/64 | Random 26-letter strings show quick mismatches; `A^n` versus `A^(m-1)B` forces repeated failed prefixes. |

The recursive cap is intentional: the largest difficult case already made 377,393,953 calls. The benchmark does not claim that n=12 is the hardware's absolute recursion limit. The search experiments deliberately use no-match cases to isolate comparison cost; tests cover successful matches and overlaps. Small timings can reflect remaining JIT effects even after warmup; counters support the growth conclusions.

## Code and counters

`src/main/java/kz/aitu/daa/` contains:

- `EditDistance`: one common `distance(String, String)` interface for `RecursiveEditDistance`, `TableEditDistance`, and `TwoRowEditDistance`.
- `StringSearch`: one common `search(String, String)` interface for `NaiveSearch` and `KmpSearch`; KMP also exposes public `int[] lps(String)`.
- `Metrics`: invocation counters, reset by each valid call; algorithm objects are reusable and intended for single-threaded use.
- `InputGenerator`, `Benchmark`, `Main`: case-specific seeded generators, the measurement harness, and the command-line entry point.

| CSV counter | Precise meaning |
| --- | --- |
| `calls` | Recursive calls including base cases; zero for other algorithms. |
| `states` | Non-base edit-state evaluations, including repeated recursive states. |
| `comparisons` | Character equality tests in edit distance or the search phase. |
| `lps_comparisons` | Character equality tests while constructing KMP's prefix array. |
| `peak_array_cells` | Peak simultaneously retained elements of algorithm-owned `int` arrays, recorded at allocation sites. Excludes array headers/references, input strings, output lists, and stack frames; it is not measured JVM heap usage. |
| `max_depth` | Largest active recursive call depth, counting the root as 1. |

KMP comparison totals in plots are `comparisons + lps_comparisons`. Unused counters are zero. `time_ms` stores fractional milliseconds without rounding small cases to zero. The CSV additionally records `algorithm,input,n,m,run,result,seed,input_sha256`; `result` is distance for Edit Distance and match count for search. The two-row implementation uses two arrays of `m+1` cells, with `m=b.length()`.

## Delivered artifacts

- `REPORT.pdf`: four-page report.
- `results/results.csv`: every measured run; `summary.csv` and `analysis.json`: derived summaries.
- `results/plots/`: four labeled PNG charts, including logarithmic axes.
- `results/benchmark.log`, `build.log`, `environment.txt`: actual run, test/build, and runtime evidence.
- `scripts/`: reproducible plot/PDF generation, benchmark workflow, and submission packaging.

After building and committing the final files, create the submission archive:

```bash
python3 scripts/package_release.py
```

It writes `../DAA_Assignment4_Beibarys_Balykbayev_SE-2516.zip`, containing committed deliverables plus `bin/daa-assignment4-1.0.jar`. The JAR can be run immediately after extraction with `java -jar bin/daa-assignment4-1.0.jar demo` from the project folder.

The requested handoff is a local commit. The remote URL is configured, but this workspace's shell cannot resolve GitHub and the remote history has not been inspected. Before publishing from a network-enabled checkout, run `git fetch origin` and inspect any existing remote history; integrate it if needed, then push `main` and `v1.0` without force-pushing. Upload the ZIP to Moodle separately.

## AI-use acknowledgement

OpenAI Codex assisted with the algorithm implementations, test design, benchmark generator and harness, plot generation, PDF report, and documentation. The recorded tests and benchmarks were executed locally; the report uses the saved measurements rather than invented results. The student should review the implementation and conclusions before submission.
