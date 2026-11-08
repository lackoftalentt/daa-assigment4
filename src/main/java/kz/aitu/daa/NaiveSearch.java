package kz.aitu.daa;

import java.util.ArrayList;
import java.util.List;

public final class NaiveSearch implements StringSearch {
    private final Metrics metrics = new Metrics();
    @Override public Metrics metrics() { return metrics; }

    @Override public List<Integer> search(String text, String pattern) {
        StringSearch.validate(text, pattern);
        metrics.reset();
        List<Integer> matches = new ArrayList<>();
        for (int start = 0; start <= text.length() - pattern.length(); start++) {
            int j = 0;
            while (j < pattern.length()) {
                metrics.comparisons++;
                if (text.charAt(start + j) != pattern.charAt(j)) break;
                j++;
            }
            if (j == pattern.length()) matches.add(start);
        }
        return matches;
    }
}
