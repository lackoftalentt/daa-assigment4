package kz.aitu.daa;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import java.util.List;
import java.util.Random;
import static org.junit.jupiter.api.Assertions.*;

class EditDistanceTest {
    private List<EditDistance> algorithms() {
        return List.of(new RecursiveEditDistance(), new TableEditDistance(), new TwoRowEditDistance());
    }

    @ParameterizedTest
    @CsvSource({"kitten,sitting,3", "flaw,lawn,2", "intention,execution,5", "abc,abc,0",
            "a,b,1", "Abylai Han,Abylai Khan,2"})
    void referenceValues(String a, String b, int expected) {
        for (EditDistance edit : algorithms()) assertEquals(expected, edit.distance(a, b));
    }

    @Test void emptyStrings() {
        for (EditDistance edit : algorithms()) {
            assertEquals(0, edit.distance("", ""));
            assertEquals(3, edit.distance("", "abc"));
            assertEquals(3, edit.distance("abc", ""));
        }
    }

    @Test void oneHundredRandomShortPairsAgree() {
        Random random = new Random(42);
        for (int k = 0; k < 100; k++) {
            String a = word(random, random.nextInt(7));
            String b = word(random, random.nextInt(7));
            int expected = new TableEditDistance().distance(a, b);
            for (EditDistance edit : algorithms()) {
                assertEquals(expected, edit.distance(a, b), a + " / " + b);
                assertEquals(expected, edit.distance(b, a));
            }
        }
    }

    @Test void tableAndTwoRowsHandleUnequalDimensions() {
        assertEquals(999, new TwoRowEditDistance().distance("a", "a".repeat(1000)));
        assertEquals(999, new TwoRowEditDistance().distance("a".repeat(1000), "a"));
    }

    @Test void countersMeasureWorkAndReset() {
        RecursiveEditDistance recursive = new RecursiveEditDistance();
        assertEquals(1, recursive.distance("a", "b"));
        assertEquals(4, recursive.metrics().calls);
        assertEquals(1, recursive.metrics().states);
        assertEquals(2, recursive.metrics().maxDepth);
        recursive.distance("abc", "abc");
        assertEquals(4, recursive.metrics().calls);
        assertEquals(3, recursive.metrics().comparisons);
        TableEditDistance table = new TableEditDistance();
        TwoRowEditDistance rows = new TwoRowEditDistance();
        table.distance("abc", "xy"); rows.distance("abc", "xy");
        assertEquals(6, table.metrics().states);
        assertEquals(6, rows.metrics().states);
        assertEquals(12, table.metrics().peakArrayCells);
        assertEquals(6, rows.metrics().peakArrayCells);
        table.distance("", ""); rows.distance("", "");
        assertEquals(0, table.metrics().states);
        assertEquals(1, table.metrics().peakArrayCells);
        assertEquals(2, rows.metrics().peakArrayCells);
    }

    static String word(Random random, int length) {
        StringBuilder s = new StringBuilder(length);
        for (int i = 0; i < length; i++) s.append((char) ('a' + random.nextInt(3)));
        return s.toString();
    }
}
