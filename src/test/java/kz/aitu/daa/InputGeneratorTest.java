package kz.aitu.daa;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class InputGeneratorTest {
    @Test void reproducibleAndPurposefulInputs() {
        var identical = InputGenerator.edit("identical", 12);
        assertEquals(identical.first(), identical.second());
        var disjoint = InputGenerator.edit("disjoint", 12);
        assertEquals(disjoint, InputGenerator.edit("disjoint", 12));
        assertEquals(64, disjoint.fingerprint().length());
        assertEquals(12, new TableEditDistance().distance(disjoint.first(), disjoint.second()));
        for (char a : disjoint.first().toCharArray()) assertEquals(-1, disjoint.second().indexOf(a));
        var search = InputGenerator.search("near_match", 4096, 64);
        assertEquals("A".repeat(4096), search.first());
        assertEquals("A".repeat(63) + "B", search.second());
        assertEquals(InputGenerator.search("random", 4096, 64), InputGenerator.search("random", 4096, 64));
        assertNotEquals(InputGenerator.search("random", 4096, 64).fingerprint(), search.fingerprint());
    }
}
