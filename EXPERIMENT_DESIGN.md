# Experiment Design Card (written before the first benchmark)

Author: Beibarys Balykbayev, SE-2516. Fixed seed: 20261108.
No experimental measurements were available when this card was written.

| Field | Plan |
| --- | --- |
| Questions | Edit Distance: how do recursion, a full table, and two rows change work, time, and storage as equal input lengths grow? Search: how does repeated near-matching text change Naive versus KMP comparisons and time? |
| Sizes | All three Edit Distance versions: n = 3, 6, 9, 12. DP-only extension: n = 128, 256, 512, 1024, 2048. Search: text n = 4096, 16384, 65536, 262144; pattern m = n/64 (64 to 4096). Each series has at least four sizes and a largest/smallest ratio >= 4. Small sizes bound exponential recursion; large DP and search cases give measurable timings. |
| Inputs | Edit: `identical`, a generated word used twice, shows the recursion's matching shortcut; `disjoint`, words from non-overlapping alphabets, makes every recursive comparison branch three ways and is the intended hard case. Search: `random`, independent text/pattern over 26 letters, shows quick mismatches; `near_match`, text A^n and pattern A^(m-1)B, makes Naive repeat m comparisons at each possible start. These no-match inputs isolate comparison cost from result-list allocation. Tests separately cover successful and overlapping matches. |
| Generator | Java Random with a fresh seed derived from the fixed seed, family, type, n and m; no runtime hash or clock. Generate outside timing. Store a SHA-256 fingerprint with every run. Repeated commands reproduce inputs, answers and counters; elapsed times naturally vary. |
| Metrics | Five measured runs after three untimed warmups per case; report the median in milliseconds using System.nanoTime. Edit counters: recursive calls (including base cases), evaluated non-base states, character comparisons, and peak live integer-array cells (table/two rows). Search: character comparisons during search and separately during LPS construction; their sum includes preprocessing. Increment counters inside the algorithms; zero denotes an unused counter. Recursive max depth is measured separately from array cells. |
| Predictions | Disjoint recursion grows exponentially; identical recursion visits n+1 calls. Both DP versions evaluate n^2 cells for both types, but full-table storage grows quadratically while two-row storage grows linearly. For search, Naive is near-linear on random text, but approaches n*m on near matches; KMP remains linear including LPS. Since m grows with n, near-match Naive should show quadratic work here. |
| Plots | (1) Edit states versus n, logarithmic y-axis: exponential versus quadratic work; (2) DP storage versus n, log-log axes: quadratic versus linear retained cells; (3) search comparisons versus text n, log-log axes: typical versus adversarial growth, including KMP preprocessing; (4) median runtime panels: observed time and practical overhead. Each PNG will have units, a legend, and a takeaway below it in the PDF. |
| Limits | Stop at recursive n=12 by design; do not claim it is the machine's absolute maximum. No extrapolated timing is a measurement. Peak integer-array cells exclude object headers, Strings, result lists, and recursion frames; depth is not bytes. |

Plan revisions: none. If a revision is needed, record the reason here before rerunning.
