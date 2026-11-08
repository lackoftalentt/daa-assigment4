package kz.aitu.daa;

import java.util.Objects;

public final class TableEditDistance implements EditDistance {
    private final Metrics metrics = new Metrics();
    @Override public Metrics metrics() { return metrics; }

    // State: dp[i][j] is the distance between prefixes of lengths i and j.
    // Transition: equal chars -> diagonal; else 1+min(above, left, diagonal).
    // Base: dp[0][j]=j, dp[i][0]=i; fill rows from shorter prefixes to longer ones.
    @Override public int distance(String a, String b) {
        Objects.requireNonNull(a); Objects.requireNonNull(b);
        metrics.reset();
        int[][] dp = new int[a.length() + 1][];
        long live = 0;
        for (int i = 0; i <= a.length(); i++) {
            dp[i] = new int[b.length() + 1];
            live += dp[i].length;
            metrics.allocated(live);
            dp[i][0] = i;
        }
        for (int j = 0; j <= b.length(); j++) dp[0][j] = j;
        for (int i = 1; i <= a.length(); i++) {
            for (int j = 1; j <= b.length(); j++) {
                metrics.states++;
                metrics.comparisons++;
                dp[i][j] = a.charAt(i - 1) == b.charAt(j - 1) ? dp[i - 1][j - 1]
                        : 1 + Math.min(dp[i - 1][j - 1], Math.min(dp[i - 1][j], dp[i][j - 1]));
            }
        }
        return dp[a.length()][b.length()];
    }
}
