package de.universelab.chatarchiv;

import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

public final class MathUnicodeTest {
    @Test public void convertsGreekRootsScriptsAndFractions() {
        assertEquals("α + β = √(a₀)", MathUnicode.convert("\\alpha + \\beta = \\sqrt{a_0}"));
        assertEquals("(a₀)/(H₀) ≈ 1", MathUnicode.convert("\\frac{a_0}{H_0} \\approx 1"));
        assertEquals("x² + y⁻¹", MathUnicode.convert("x^2 + y^{-1}"));
        assertEquals("ℝ", MathUnicode.convert("\\mathbb{R}"));
    }

    @Test public void keepsCodeAndUnsupportedScriptInformation() {
        String code = "```latex\n\\frac{1}{2}\n```";
        assertEquals(code, MathUnicode.convert(code));
        assertTrue(MathUnicode.convert("a_N = 5").contains("_(N)"));
        assertEquals("Unveränderter normaler Text", MathUnicode.convert("Unveränderter normaler Text"));
        assertEquals("Preis $5 und $10", MathUnicode.convert("Preis $5 und $10"));
        assertEquals("α² = 1", MathUnicode.convert("$\\alpha^2 = 1$"));
        assertEquals("α² = 1", MathUnicode.convert("$$\\alpha^2 = 1$$"));
    }
}
