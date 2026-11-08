package kz.aitu.daa;

import org.junit.jupiter.api.Test;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import static org.junit.jupiter.api.Assertions.*;

class StringSearchTest {
    private List<StringSearch> algorithms() { return List.of(new NaiveSearch(), new KmpSearch()); }

    @Test void lpsReferenceArrays() {
        KmpSearch kmp = new KmpSearch();
        assertArrayEquals(new int[]{0,1,2,0,1,2,3,3}, kmp.lps("AAACAAAA"));
        assertArrayEquals(new int[]{0,0,1,2,0,1,2,3,4}, kmp.lps("ABABCABAB"));
        assertArrayEquals(new int[]{0}, kmp.lps("A"));
        assertArrayEquals(new int[]{0,1,2,3}, kmp.lps("AAAA"));
        assertThrows(IllegalArgumentException.class, () -> kmp.lps(""));
    }

    @Test void referenceMatchesIncludingOverlaps() {
        for (StringSearch search : algorithms()) {
            assertEquals(List.of(10), search.search("ABABDABACDABABCABAB", "ABABCABAB"));
            assertEquals(List.of(0,1,2,3), search.search("AAAAA", "AA"));
            assertEquals(List.of(0,2,4), search.search("ABABABA", "ABA"));
            assertEquals(List.of(0,1,2), search.search("AAA", "A"));
            assertEquals(List.of(0), search.search("ABC", "ABC"));
            assertEquals(List.of(3), search.search("XYZABC", "ABC"));
            assertEquals(List.of(), search.search("ABC", "Z"));
        }
    }

    @Test void edgeCases() {
        for (StringSearch search : algorithms()) {
            assertThrows(IllegalArgumentException.class, () -> search.search("abc", ""));
            assertThrows(IllegalArgumentException.class, () -> search.search("", ""));
            assertEquals(List.of(), search.search("ab", "abc"));
            assertEquals(List.of(), search.search("", "a"));
        }
    }

    @Test void oneHundredRandomTextsAgreeWithIndependentIndexOf() {
        Random random = new Random(1234);
        for (int k = 0; k < 100; k++) {
            String text = EditDistanceTest.word(random, random.nextInt(101));
            String pattern = EditDistanceTest.word(random, 1 + random.nextInt(12));
            if (k % 2 == 0 && !text.isEmpty()) {
                int start = random.nextInt(text.length());
                pattern = text.substring(start, Math.min(text.length(), start + 1 + random.nextInt(8)));
            }
            List<Integer> expected = new ArrayList<>();
            int at = text.indexOf(pattern);
            while (at >= 0) { expected.add(at); at = text.indexOf(pattern, at + 1); }
            for (StringSearch search : algorithms()) assertEquals(expected, search.search(text, pattern));
        }
    }

    @Test void randomLpsMatchesBruteForceBorders() {
        Random random = new Random(71);
        for (int k = 0; k < 100; k++) {
            String p = EditDistanceTest.word(random, 1 + random.nextInt(30));
            int[] expected = new int[p.length()];
            for (int i = 0; i < p.length(); i++) {
                for (int length = 1; length <= i; length++) {
                    if (p.substring(0, length).equals(p.substring(i + 1 - length, i + 1))) expected[i] = length;
                }
            }
            assertArrayEquals(expected, new KmpSearch().lps(p));
        }
    }

    @Test void adversarialCountsAndReset() {
        NaiveSearch naive = new NaiveSearch(); KmpSearch kmp = new KmpSearch();
        String text = "A".repeat(1000), pattern = "A".repeat(99) + "B";
        assertEquals(naive.search(text, pattern), kmp.search(text, pattern));
        assertEquals(90100, naive.metrics().comparisons);
        assertTrue(kmp.metrics().totalComparisons() < 3 * (text.length() + pattern.length()));
        kmp.search("A", "A");
        assertEquals(1, kmp.metrics().comparisons);
        assertEquals(0, kmp.metrics().lpsComparisons);
        kmp.search("", "A");
        assertEquals(0, kmp.metrics().totalComparisons());
    }
}
