package kz.aitu.daa;

import java.util.Objects;

public final class RecursiveEditDistance implements EditDistance {
    private final Metrics metrics = new Metrics();
    @Override public Metrics metrics() { return metrics; }

    // State: D(i,j) is the distance between prefixes a[0,i) and b[0,j).
    // Transition: equal last chars -> D(i-1,j-1); else 1+min(delete, insert, replace).
    // Base: D(0,j)=j and D(i,0)=i; direct recursion deliberately stores no answers.
    @Override public int distance(String a, String b) {
        Objects.requireNonNull(a); Objects.requireNonNull(b);
        metrics.reset();
        return solve(a, b, a.length(), b.length(), 1);
    }

    private int solve(String a, String b, int i, int j, int depth) {
        metrics.calls++;
        metrics.maxDepth = Math.max(metrics.maxDepth, depth);
        if (i == 0) return j;
        if (j == 0) return i;
        metrics.states++;
        metrics.comparisons++;
        if (a.charAt(i - 1) == b.charAt(j - 1)) {
            return solve(a, b, i - 1, j - 1, depth + 1);
        }
        int delete = solve(a, b, i - 1, j, depth + 1);
        int insert = solve(a, b, i, j - 1, depth + 1);
        int replace = solve(a, b, i - 1, j - 1, depth + 1);
        return 1 + Math.min(delete, Math.min(insert, replace));
    }
}
