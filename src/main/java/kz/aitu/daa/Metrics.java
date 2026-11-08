package kz.aitu.daa;

/** Per-invocation counters. Instances of algorithms are reusable, but not thread-safe. */
public final class Metrics {
    public long calls;
    public long states;
    public long comparisons;
    public long lpsComparisons;
    public long peakArrayCells;
    public int maxDepth;

    public void reset() {
        calls = states = comparisons = lpsComparisons = peakArrayCells = 0;
        maxDepth = 0;
    }

    public void allocated(long liveCells) {
        peakArrayCells = Math.max(peakArrayCells, liveCells);
    }

    public long totalComparisons() { return comparisons + lpsComparisons; }

    public String csv() {
        return calls + "," + states + "," + comparisons + "," + lpsComparisons
                + "," + peakArrayCells + "," + maxDepth;
    }
}
