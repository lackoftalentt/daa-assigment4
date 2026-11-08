package kz.aitu.daa;

import java.util.List;

public interface StringSearch {
    List<Integer> search(String text, String pattern);
    Metrics metrics();

    static void validate(String text, String pattern) {
        java.util.Objects.requireNonNull(text);
        java.util.Objects.requireNonNull(pattern);
        if (pattern.isEmpty()) throw new IllegalArgumentException("Pattern must not be empty");
    }
}
