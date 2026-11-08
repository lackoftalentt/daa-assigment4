#!/usr/bin/env python3
"""Build the four-page PDF report using validated benchmark summaries and plots."""
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, PageBreak

ROOT = Path(__file__).resolve().parents[1]
WIDTH = A4[0] - 32 * mm
BLUE = colors.HexColor("#174a75")
STYLES = getSampleStyleSheet()
STYLES.add(ParagraphStyle(name="ReportTitle", fontName="Helvetica-Bold", fontSize=18, leading=21, textColor=BLUE, spaceAfter=8))
STYLES.add(ParagraphStyle(name="Section", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=BLUE, spaceBefore=9, spaceAfter=5))
STYLES.add(ParagraphStyle(name="Text", fontName="Helvetica", fontSize=9.2, leading=12.5, spaceAfter=6))
STYLES.add(ParagraphStyle(name="SmallText", fontName="Helvetica", fontSize=8.3, leading=10.7, spaceAfter=4))
STYLES.add(ParagraphStyle(name="CaptionText", fontName="Helvetica-Oblique", fontSize=8.5, leading=11, textColor=colors.HexColor("#365166"), spaceAfter=7))


def p(text, style="Text"):
    return Paragraph(text, STYLES[style])


def lookup(rows, algorithm, kind, n):
    return next(r for r in rows if r["algorithm"] == algorithm and r["input"] == kind and r["n"] == n)


def number(n):
    return f"{n:,}"


def chart(name, caption):
    return [Image(str(ROOT / "results/plots" / name), width=WIDTH, height=WIDTH * 2.65 / 9), p(caption, "CaptionText")]


def table(data, widths, header=False):
    content = [[p(str(cell), "SmallText") for cell in row] for row in data]
    result = Table(content, colWidths=widths, hAlign="LEFT")
    commands = [("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 7),
                ("RIGHTPADDING", (0,0), (-1,-1), 7), ("TOPPADDING", (0,0), (-1,-1), 5),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                ("LINEBELOW", (0,0), (-1,-1), 0.35, colors.HexColor("#d3dee5")),
                ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.white, colors.HexColor("#f3f7fa")])]
    if header:
        commands += [("BACKGROUND", (0,0), (-1,0), colors.HexColor("#dfebf4"))]
    result.setStyle(TableStyle(commands))
    return result


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d3dee5"))
    canvas.line(16*mm, 15*mm, A4[0]-16*mm, 15*mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#526574"))
    canvas.drawString(16*mm, 10*mm, "Beibarys Balykbayev | SE-2516 | DAA Assignment 4")
    canvas.drawRightString(A4[0]-16*mm, 10*mm, str(doc.page))
    canvas.restoreState()


def build():
    data = json.loads((ROOT / "results/analysis.json").read_text())
    rows = data["summary"]
    rec = lookup(rows, "recursive", "disjoint", 12)
    rec9 = lookup(rows, "recursive", "disjoint", 9)
    identical = lookup(rows, "recursive", "identical", 12)
    full = lookup(rows, "table", "disjoint", 2048)
    two = lookup(rows, "two_rows", "disjoint", 2048)
    naive = lookup(rows, "naive", "near_match", 262144)
    kmp = lookup(rows, "kmp", "near_match", 262144)
    random_naive = lookup(rows, "naive", "random", 262144)
    random_kmp = lookup(rows, "kmp", "random", 262144)
    ratio = naive["total_comparisons"] / kmp["total_comparisons"]
    story = []

    # Page 1: plan at the start, recorded independently before all measurements.
    story += [p("Dynamic Programming &amp; String Algorithms", "ReportTitle"),
              p("<b>Assignment 4</b> · Beibarys Balykbayev · SE-2516 · 8 November 2026", "SmallText"),
              p("Experiment Design Card", "Section"),
              p("Written and committed before the first benchmark; the original is EXPERIMENT_DESIGN.md. Plan revisions: none.", "SmallText")]
    card = [
        ["<b>Questions</b>", "<b>Edit:</b> how do recursion, a full table, and two rows change work, time, and storage as input length grows? <b>Search:</b> how does repeated near-matching text change Naive and KMP comparison counts and time?"],
        ["<b>Sizes</b>", "All edit versions: n = 3, 6, 9, 12. DP extension: 128, 256, 512, 1024, 2048. Both strings have length n. Search: text n = 4096, 16384, 65536, 262144; pattern m = n/64. Every series has at least four sizes and spans at least 4x. Small edit cases bound recursion; large cases give useful times."],
        ["<b>Inputs</b>", "Edit: <b>identical</b> generated strings exercise matching shortcuts; <b>disjoint</b> alphabets force three recursive branches at every non-base call (hard case). Search: <b>random</b> text/pattern over 26 letters exposes quick mismatches; <b>near_match</b> uses A^n versus A^(m-1)B to repeat long failed checks (hard case). Search cases isolate comparisons with no matches; tests cover successful and overlapping matches."],
        ["<b>Metrics</b>", "Median of five timed runs after three untimed warmups per case. Edit: non-base state evaluations, calls, character comparisons, peak live int-array cells, and recursion depth. Search: character comparisons separately in search and LPS, plus their sum. Counters are incremented inside the algorithms; storage counts exclude object overhead and call frames."],
        ["<b>Prediction</b>", "Disjoint recursion grows exponentially; identical recursion needs n+1 calls. Both DP versions evaluate n^2 cells; table storage is quadratic and two-row storage linear. Naive is near-linear on random input but approaches n*m on near matches. Since m grows with n, that series should be quadratic; KMP including LPS remains linear."],
        ["<b>Plots</b>", "Edit work versus n (log y) tests repeated work. DP storage (log-log) tests quadratic versus linear space. Search comparisons (log-log) contrasts input types. Median runtime panels show practical costs. Each chart includes units and a one-sentence takeaway."],
        ["<b>Reproduction</b>", "Own Java generator: fixed seed 20261108, fresh case-specific seed derived from family/type/n/m. Save SHA-256 input fingerprints. Same commands reproduce inputs, answers, and counters; clock readings vary. Generate and validate outside timing. Stop recursion at n=12 by design, without claiming an absolute machine limit."],
    ]
    story += [table(card, [75, WIDTH-75]), p("Measurement protocol", "Section"),
              p("The CSV contains 300 individual measured runs across 60 algorithm/input/size cases. Timing uses System.nanoTime and includes counter updates, algorithm allocation, and KMP preprocessing. Cases run sequentially in a fixed order, without forced garbage collection. JIT compilation and cache effects can remain after three warmups.", "SmallText"),
              p("State, transition, base case", "Section"),
              p("D(i,j) is the edit distance between prefixes of lengths i and j. Equal last characters use D(i-1,j-1); otherwise use 1 + min(D(i-1,j), D(i,j-1), D(i-1,j-1)). The base cases are D(0,j)=j and D(i,0)=i. The same recurrence is documented above each implementation.", "SmallText"), PageBreak()]

    # Page 2: edit work and space, with comparisons tied to actual counters.
    story += [p("Edit Distance: work and storage", "ReportTitle")]
    story += chart("01_edit_work.png", f"Figure 1. At n=12, disjoint recursion evaluates {number(rec['states'])} non-base states; each DP version evaluates only 144.")
    story += chart("02_dp_storage.png", f"Figure 2. At n=2048, two rows retain {number(two['peak_array_cells'])} integer cells versus {number(full['peak_array_cells'])} for the table ({full['peak_array_cells']/two['peak_array_cells']:.1f}x fewer).")
    story += [p("Prediction versus result", "Section"),
              p(f"The work and storage predictions match the counters. Disjoint recursion rises from {number(rec9['calls'])} calls at n=9 to {number(rec['calls'])} at n=12. Identical recursion at n=12 takes {identical['calls']} calls because every comparison follows one diagonal branch. Both DP versions still evaluate all n^2 non-base cells for either input type; they do not skip the table on identical inputs."),
              table([["<b>Case</b>", "<b>Median (ms)</b>", "<b>Measured work / storage</b>"],
                     ["Recursive, disjoint n=12", f"{rec['time_ms']:.3f}", f"{number(rec['calls'])} calls; depth {rec['max_depth']}"],
                     ["Full table, disjoint n=2048", f"{full['time_ms']:.3f}", f"{number(full['states'])} states; {number(full['peak_array_cells'])} cells"],
                     ["Two rows, disjoint n=2048", f"{two['time_ms']:.3f}", f"{number(two['states'])} states; {number(two['peak_array_cells'])} cells"]], [WIDTH*.33, WIDTH*.16, WIDTH*.51], header=True),
              p("Storage is a count of retained int-array elements, observed at allocation sites. Multiplying by four estimates only the integer payload, not Java heap usage. The recursive version retains no integer arrays but does use a call stack; its recorded depth is separate.", "SmallText"), PageBreak()]

    # Page 3: search, including the preprocessing cost and deliberately visible clock noise.
    story += [p("String search: structure matters", "ReportTitle")]
    story += chart("03_search_work.png", f"Figure 3. On the largest near-match case, Naive uses {ratio:,.0f}x as many comparisons as KMP including LPS construction.")
    story += chart("04_median_time.png", "Figure 4. Median time separates the expensive near-match Naive scans, while the DP timing curves show overhead as well as increasing work.")
    story += [p("Prediction versus result", "Section"),
              p(f"The search prediction matches measured work. At n=262144 and m=4096, Naive performs {number(naive['comparisons'])} comparisons, exactly m(n-m+1); KMP performs {number(kmp['comparisons'])} search comparisons plus {number(kmp['lps_comparisons'])} LPS comparisons, totaling {number(kmp['total_comparisons'])}. Increasing n fourfold also increases m fourfold, so Naive's near-match count grows about sixteenfold, while KMP's count grows about fourfold."),
              p(f"For the largest random case, Naive and KMP use {number(random_naive['total_comparisons'])} and {number(random_kmp['total_comparisons'])} comparisons. Quick first-character mismatches keep both close to linear, and KMP preprocessing adds a small cost. All generated benchmark search cases have zero matches; separate reference and random tests verify the lists of actual matches, including overlaps."),
              p(f"At the largest near-match size, measured medians are {naive['time_ms']:.3f} ms (Naive) and {kmp['time_ms']:.3f} ms (KMP). These times describe this JVM run; the comparison counts provide the stronger evidence about growth. Naive's time on the smallest random case is higher than on the next size, consistent with residual JIT and other runtime overhead rather than fewer comparisons at larger n.", "SmallText"), PageBreak()]

    # Page 4: each required short answer is three or four sentences.
    story += [p("Interpretation and short answers", "ReportTitle"),
              p("Which input made string search slowest, and why?", "Section"),
              p(f"The slowest measured search was Naive on near_match at n=262144 and m=4096, with a {naive['time_ms']:.3f} ms median. Every candidate start agrees with the first m-1 pattern characters and fails on the final B. Naive repeats those checks at all n-m+1 starts, giving m(n-m+1) comparisons. KMP reuses the known border through LPS and keeps its text index moving forward."),
              p("How large an n could recursive Edit Distance handle?", "Section"),
              p(f"The largest tested equal length was n=12; disjoint input completed with a {rec['time_ms']:.3f} ms median. It made {number(rec['calls'])} recursive calls, compared with {number(rec9['calls'])} at n=9. The experiment stopped at the planned cap because repeated subproblems grow exponentially, not because a timeout or stack failure occurred. Matching inputs are much easier, so n=12 is a tested limit for this experiment rather than the largest possible input on this machine."),
              p("What do two rows gain and lose compared with the table?", "Section"),
              p(f"Two rows keep only the previous and current rows, reducing extra storage from O(n*m) to O(m) while retaining O(n*m) time and the exact distance. At n=m=2048, the measured retained integer cells drop from {number(full['peak_array_cells'])} to {number(two['peak_array_cells'])}. Discarded rows prevent straightforward backtracking through the full table to reconstruct the edit sequence. Recovering that sequence needs additional storage, recomputation, or a different reconstruction method."),
              p("Which string search would suit the city platform?", "Section"),
              p("I would choose KMP for finding literal patterns in long city-platform logs because it has O(n+m) time even on repetitive input. Its O(m) LPS array avoids the repeated prefix checks that make Naive slow in the adversarial experiment. Naive is still easy to implement and can be competitive for short, mostly mismatching inputs. Street-name spell checking needs Edit Distance or another approximate matching method, because KMP alone cannot correct typos."),
              p("What the measured times mean", "Section"),
              p("Times use five independent invocations of each deterministic case and report their median, after three warmups. Small cases remain sensitive to JIT compilation, timer overhead, CPU scheduling, caches, and allocation or garbage collection; fractional milliseconds are retained instead of rounding to zero. The JVM ran with a 256 MiB initial heap and a 1 GiB maximum heap; the exact runtime and measurement timestamp are recorded in results/environment.txt. Instrumentation is included in timing, so these are timings of the counted implementations. The state, comparison, and storage counters support growth conclusions when clock ratios are noisy."),
              p("Validation and reproducibility", "Section"),
              p("All 17 JUnit 5 test invocations pass: reference distances and LPS arrays, empty inputs, overlaps, 100 random short edit pairs, 100 random search texts against String.indexOf, 100 brute-force LPS checks, and counter/reset checks. The analysis script verifies all 300 CSV rows, five runs per case, consistent fingerprints/counters, and expected case coverage. Production code has no external libraries. Run scripts/reproduce.sh to rebuild the experiments, plots, and PDF.", "SmallText"),
              p('Repository: <link href="https://github.com/lackoftalentt/daa-assigment4">github.com/lackoftalentt/daa-assigment4</link> · branch main · release tag v1.0.<br/>AI acknowledgement: OpenAI Codex assisted with implementation, tests, experiments, analysis, and writing; the saved results were measured locally.', "SmallText")]
    doc = SimpleDocTemplate(str(ROOT / "REPORT.pdf"), pagesize=A4,
                            rightMargin=16*mm, leftMargin=16*mm, topMargin=15*mm, bottomMargin=20*mm,
                            title="DAA Assignment 4 - Dynamic Programming and String Algorithms",
                            author="Beibarys Balykbayev", subject="Measured Edit Distance and Naive/KMP experiments")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print("Wrote REPORT.pdf")


if __name__ == "__main__":
    build()
