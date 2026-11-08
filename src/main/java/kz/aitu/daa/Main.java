package kz.aitu.daa;

import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;

public final class Main {
    private Main() { }
    public static void main(String[] args) throws Exception {
        if (args.length == 0 || args[0].equals("demo")) {
            for (EditDistance edit : List.of(new RecursiveEditDistance(), new TableEditDistance(), new TwoRowEditDistance())) {
                System.out.println(edit.getClass().getSimpleName() + ": kitten -> sitting = " + edit.distance("kitten", "sitting"));
            }
            System.out.println("KMP lps(AAACAAAA): " + Arrays.toString(new KmpSearch().lps("AAACAAAA")));
            for (StringSearch search : List.of(new NaiveSearch(), new KmpSearch())) {
                System.out.println(search.getClass().getSimpleName() + ": AAAAA / AA = " + search.search("AAAAA", "AA"));
            }
        } else if (args[0].equals("benchmark") && args.length <= 2) {
            new Benchmark().run(Path.of(args.length == 2 ? args[1] : "results"));
        } else {
            System.err.println("Usage: java -jar target/daa-assignment4-1.0.jar [demo|benchmark [results-directory]]");
            System.exit(2);
        }
    }
}
