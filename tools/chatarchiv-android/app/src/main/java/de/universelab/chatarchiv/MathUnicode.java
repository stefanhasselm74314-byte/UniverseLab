package de.universelab.chatarchiv;

import java.util.HashMap;
import java.util.Map;

/** Best-effort *display-only* conversion of common linear LaTeX to Unicode. */
final class MathUnicode {
    private static final Map<String, String> SYMBOLS = new HashMap<>();
    private static final String SUPER_FROM = "0123456789+-=()ni";
    private static final String SUPER_TO   = "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ";
    private static final String SUB_FROM   = "0123456789+-=()ae hijklmnoprstux".replace(" ", "");
    private static final String SUB_TO     = "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤₓ";

    static {
        String[][] symbols = {
                {"alpha","α"},{"beta","β"},{"gamma","γ"},{"delta","δ"},
                {"epsilon","ε"},{"varepsilon","ϵ"},{"zeta","ζ"},{"eta","η"},
                {"theta","θ"},{"vartheta","ϑ"},{"iota","ι"},{"kappa","κ"},
                {"lambda","λ"},{"mu","μ"},{"nu","ν"},{"xi","ξ"},
                {"pi","π"},{"varpi","ϖ"},{"rho","ρ"},{"varrho","ϱ"},
                {"sigma","σ"},{"tau","τ"},{"upsilon","υ"},{"phi","φ"},
                {"varphi","ϕ"},{"chi","χ"},{"psi","ψ"},{"omega","ω"},
                {"Gamma","Γ"},{"Delta","Δ"},{"Theta","Θ"},{"Lambda","Λ"},
                {"Xi","Ξ"},{"Pi","Π"},{"Sigma","Σ"},{"Upsilon","Υ"},
                {"Phi","Φ"},{"Psi","Ψ"},{"Omega","Ω"},
                {"times","×"},{"cdot","·"},{"ast","∗"},{"star","⋆"},
                {"approx","≈"},{"simeq","≃"},{"sim","∼"},{"equiv","≡"},
                {"neq","≠"},{"ne","≠"},{"le","≤"},{"leq","≤"},
                {"ge","≥"},{"geq","≥"},{"ll","≪"},{"gg","≫"},
                {"pm","±"},{"mp","∓"},{"infty","∞"},{"partial","∂"},
                {"nabla","∇"},{"sum","∑"},{"prod","∏"},{"int","∫"},
                {"iint","∬"},{"oint","∮"},{"otimes","⊗"},{"oplus","⊕"},
                {"in","∈"},{"notin","∉"},{"subset","⊂"},{"subseteq","⊆"},
                {"supset","⊃"},{"forall","∀"},{"exists","∃"},
                {"rightarrow","→"},{"to","→"},{"leftarrow","←"},
                {"Rightarrow","⇒"},{"Leftarrow","⇐"},{"Leftrightarrow","⇔"},
                {"mapsto","↦"},{"propto","∝"},{"circ","∘"},
                {"parallel","∥"},{"perp","⟂"},{"cdots","⋯"},{"ldots","…"},
                {"hbar","ℏ"},{"ell","ℓ"},{"Re","ℜ"},{"Im","ℑ"},
                {"land","∧"},{"lor","∨"},{"neg","¬"},
                {"quad"," "},{"qquad","  "},{";"," "},{","," "},
                {"log","log"},{"ln","ln"},{"exp","exp"},{"sin","sin"},
                {"cos","cos"},{"tan","tan"},{"lim","lim"}
        };
        for (String[] row : symbols) SYMBOLS.put(row[0], row[1]);
    }

    private static final class Group {
        final String value;
        final int end;
        Group(String value, int end) { this.value = value; this.end = end; }
    }

    static String convert(String input) {
        if (input == null || input.isEmpty()) return "";
        String[] lines = input.split("\n", -1);
        StringBuilder output = new StringBuilder(input.length());
        boolean fencedCode = false;
        for (int i = 0; i < lines.length; i++) {
            String line = lines[i];
            if (line.trim().startsWith("```")) {
                fencedCode = !fencedCode;
                output.append(line);
            } else if (!fencedCode && looksLikeMath(line)) {
                output.append(convertFragment(line, 0));
            } else {
                output.append(line);
            }
            if (i + 1 < lines.length) output.append('\n');
        }
        return output.toString();
    }

    private static boolean looksLikeMath(String line) {
        return line.contains("\\") || line.contains("$") || line.contains("^")
                || line.indexOf('=') >= 0 || line.indexOf('≈') >= 0
                || line.indexOf('√') >= 0 || line.indexOf('∑') >= 0;
    }

    private static boolean mathExpression(String content) {
        return content.contains("\\") || content.contains("^") || content.contains("_")
                || content.contains("=") || content.contains("+") || content.contains("≈")
                || content.contains("√") || content.contains("∑");
    }

    private static Group group(String input, int start) {
        int i = start;
        while (i < input.length() && Character.isWhitespace(input.charAt(i))) i++;
        if (i >= input.length()) return null;
        char startChar = input.charAt(i);
        if (startChar == '{' || startChar == '[') {
            char closing = startChar == '{' ? '}' : ']';
            int depth = 1;
            int from = ++i;
            while (i < input.length()) {
                if (input.charAt(i) == startChar) depth++;
                else if (input.charAt(i) == closing && --depth == 0) {
                    return new Group(input.substring(from, i), i + 1);
                }
                i++;
            }
            return null;
        }
        if (startChar == '\\') {
            int end = i + 1;
            while (end < input.length() && Character.isLetter(input.charAt(end))) end++;
            if (end > i + 1) return new Group(input.substring(i, end), end);
        }
        return new Group(input.substring(i, i + 1), i + 1);
    }

    private static String script(String input, boolean upper) {
        String from = upper ? SUPER_FROM : SUB_FROM;
        String to = upper ? SUPER_TO : SUB_TO;
        StringBuilder converted = new StringBuilder();
        for (int i = 0; i < input.length(); i++) {
            int position = from.indexOf(input.charAt(i));
            if (position < 0) return null;
            converted.append(to.charAt(position));
        }
        return converted.toString();
    }

    private static String convertFragment(String input, int level) {
        if (level > 30) return input;
        StringBuilder output = new StringBuilder(input.length());
        for (int i = 0; i < input.length();) {
            char current = input.charAt(i);
            if (current == '$') {
                // Never remove literal currency symbols. Only consume paired
                // TeX delimiters when the enclosed text resembles mathematics.
                boolean doubleDelimiter = input.startsWith("$$", i);
                String delimiter = doubleDelimiter ? "$$" : "$";
                int contentStart = i + delimiter.length();
                int close = input.indexOf(delimiter, contentStart);
                if (close > contentStart && mathExpression(input.substring(contentStart, close))) {
                    output.append(convertFragment(input.substring(contentStart, close), level + 1));
                    i = close + delimiter.length();
                } else {
                    output.append(current);
                    i++;
                }
                continue;
            }
            if (current == '^' || current == '_') {
                Group atom = group(input, i + 1);
                if (atom != null) {
                    String converted = convertFragment(atom.value, level + 1);
                    String unicode = script(converted, current == '^');
                    output.append(unicode != null ? unicode : current + "(" + converted + ")");
                    i = atom.end;
                    continue;
                }
            }
            if (current != '\\') { output.append(current); i++; continue; }
            if (i + 1 < input.length()) {
                char next = input.charAt(i + 1);
                if (next == '(' || next == ')' || next == '[' || next == ']') { i += 2; continue; }
                if (next == '\\') { output.append(' '); i += 2; continue; }
            }
            int end = i + 1;
            while (end < input.length() && Character.isLetter(input.charAt(end))) end++;
            if (end == i + 1) { output.append(current); i++; continue; }
            String command = input.substring(i + 1, end);
            if ("left".equals(command) || "right".equals(command)) { i = end; continue; }
            if ("frac".equals(command) || "dfrac".equals(command) || "tfrac".equals(command)) {
                Group numerator = group(input, end);
                Group denominator = numerator == null ? null : group(input, numerator.end);
                if (denominator != null) {
                    output.append('(').append(convertFragment(numerator.value, level + 1))
                            .append(")/(").append(convertFragment(denominator.value, level + 1)).append(')');
                    i = denominator.end;
                    continue;
                }
            }
            if ("sqrt".equals(command)) {
                Group atom = group(input, end);
                if (atom != null) {
                    if (input.substring(end, atom.end).trim().startsWith("[")) {
                        Group radicand = group(input, atom.end);
                        if (radicand != null) {
                            output.append(convertFragment(atom.value, level + 1))
                                    .append("√(").append(convertFragment(radicand.value, level + 1)).append(')');
                            i = radicand.end;
                            continue;
                        }
                    }
                    output.append("√(").append(convertFragment(atom.value, level + 1)).append(')');
                    i = atom.end;
                    continue;
                }
            }
            if ("mathbb".equals(command) || "mathcal".equals(command)
                    || "mathrm".equals(command) || "mathbf".equals(command)
                    || "mathsf".equals(command) || "text".equals(command)
                    || "operatorname".equals(command) || "boxed".equals(command)) {
                Group atom = group(input, end);
                if (atom != null) {
                    String converted = convertFragment(atom.value, level + 1);
                    if ("mathbb".equals(command) && "R".equals(converted)) converted = "ℝ";
                    if ("mathbb".equals(command) && "N".equals(converted)) converted = "ℕ";
                    if ("mathbb".equals(command) && "C".equals(converted)) converted = "ℂ";
                    output.append("boxed".equals(command) ? "[" + converted + "]" : converted);
                    i = atom.end;
                    continue;
                }
            }
            if ("dot".equals(command) || "ddot".equals(command)
                    || "bar".equals(command) || "hat".equals(command)
                    || "vec".equals(command) || "tilde".equals(command)) {
                Group atom = group(input, end);
                if (atom != null) {
                    String combined = "dot".equals(command) ? "\u0307" : "ddot".equals(command) ? "\u0308"
                            : "bar".equals(command) ? "\u0304" : "hat".equals(command) ? "\u0302"
                            : "vec".equals(command) ? "\u20d7" : "\u0303";
                    output.append(convertFragment(atom.value, level + 1)).append(combined);
                    i = atom.end;
                    continue;
                }
            }
            if ("begin".equals(command) || "end".equals(command)) {
                Group atom = group(input, end);
                if (atom != null && atom.value.matches("(aligned?|equation|gather)\\*?")) {
                    i = atom.end;
                    continue;
                }
            }
            String symbol = SYMBOLS.get(command);
            if (symbol != null) { output.append(symbol); i = end; continue; }
            output.append(input, i, end);
            i = end;
        }
        return output.toString();
    }

    private MathUnicode() { }
}
