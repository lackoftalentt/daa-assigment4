package kz.aitu.daa;

import java.util.Objects;

public final class TwoRowEditDistance implements EditDistance {
    private final Metrics metrics = new Metrics();
    @Override public Metrics metrics() { return metrics; }

    // State: previous[j]=D(i-1,j), current[j]=D(i,j) for prefixes of a and b.
    // Transition: equal chars -> previous[j-1]; else 1+min(previous[j], current[j-1], previous[j-1]).
    // Base: previous[j]=j, current[0]=i; swap rows after each completed row.
    @Override public int distance(String a, String b) {
        Objects.requireNonNull(a); Objects.requireNonNull(b);
        metrics.reset();
        int[] previous = new int[b.length() + 1];
        metrics.allocated(previous.length);
        int[] current = new int[b.length() + 1];
        metrics.allocated((long) previous.length + current.length);
        for (int j = 0; j <= b.length(); j++) previous[j] = j;
        for (int i = 1; i <= a.length(); i++) {
            current[0] = i;
            for (int j = 1; j <= b.length(); j++) {
                metrics.states++;
                metrics.comparisons++;
                current[j] = a.charAt(i - 1) == b.charAt(j - 1) ? previous[j - 1]
                        : 1 + Math.min(previous[j - 1], Math.min(previous[j], current[j - 1]));
            }
            int[] swap = previous; previous = current; current = swap;
        }
        return previous[b.length()];
    }
}
