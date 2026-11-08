package kz.aitu.daa;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.Random;

public final class InputGenerator {
    public static final long SEED = 20261108L;
    public record Pair(String first, String second) {
        public String fingerprint() {
            try {
                byte[] bytes = (first.length() + ":" + first + second.length() + ":" + second)
                        .getBytes(StandardCharsets.UTF_8);
                return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
            } catch (NoSuchAlgorithmException e) { throw new AssertionError(e); }
        }
    }

    private InputGenerator() { }

    private static Random random(String family, String type, int n, int m) {
        long seed = SEED;
        String key = family + ":" + type + ":" + n + ":" + m;
        for (int i = 0; i < key.length(); i++) seed = seed * 31 + key.charAt(i);
        return new Random(seed);
    }

    private static String word(Random random, int n, String alphabet) {
        StringBuilder word = new StringBuilder(n);
        for (int i = 0; i < n; i++) word.append(alphabet.charAt(random.nextInt(alphabet.length())));
        return word.toString();
    }

    public static Pair edit(String type, int n) {
        Random random = random("edit", type, n, n);
        return switch (type) {
            case "identical" -> { String a = word(random, n, "abcdefghijklmnopqrstuvwxyz"); yield new Pair(a, a); }
            case "disjoint" -> new Pair(word(random, n, "abcdefghijklm"), word(random, n, "NOPQRSTUVWXYZ"));
            default -> throw new IllegalArgumentException("Unknown edit input: " + type);
        };
    }

    public static Pair search(String type, int n, int m) {
        Random random = random("search", type, n, m);
        return switch (type) {
            case "random" -> new Pair(word(random, n, "ABCDEFGHIJKLMNOPQRSTUVWXYZ"), word(random, m, "ABCDEFGHIJKLMNOPQRSTUVWXYZ"));
            case "near_match" -> new Pair("A".repeat(n), "A".repeat(m - 1) + "B");
            default -> throw new IllegalArgumentException("Unknown search input: " + type);
        };
    }
}
