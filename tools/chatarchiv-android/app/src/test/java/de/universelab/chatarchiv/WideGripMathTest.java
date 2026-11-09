package de.universelab.chatarchiv;

import org.junit.Test;
import static org.junit.Assert.*;

public final class WideGripMathTest {
    @Test public void expansionAddsWidthButKeepsNativeThumbRegion() {
        assertFalse(WideGripMath.isExpandedGrip(423f, 480, 56, 24));
        assertTrue(WideGripMath.isExpandedGrip(424f, 480, 56, 24));
        assertTrue(WideGripMath.isExpandedGrip(455f, 480, 56, 24));
        assertFalse(WideGripMath.isExpandedGrip(456f, 480, 56, 24));
        assertFalse(WideGripMath.isExpandedGrip(Float.NaN, 480, 56, 24));
    }

    @Test public void noVerticalMotionDoesNotJumpAtFirstTouch() {
        assertEquals(100, WideGripMath.targetIndex(100, 0f, 1000, 641));
        assertEquals(100, WideGripMath.targetIndex(100, 0f, 1000, 24));
    }

    @Test public void draggingHalfViewportMovesHalfConversation() {
        assertEquals(320, WideGripMath.targetIndex(0, 500f, 1000, 641));
        assertEquals(332, WideGripMath.targetIndex(12, 500f, 1000, 641));
    }

    @Test public void clampsAtEndsAndHandlesInvalidGeometry() {
        assertEquals(0, WideGripMath.targetIndex(25, -5000f, 1000, 641));
        assertEquals(640, WideGripMath.targetIndex(25, 5000f, 1000, 641));
        assertEquals(10, WideGripMath.targetIndex(10, Float.NaN, 1000, 641));
        assertEquals(10, WideGripMath.targetIndex(10, 100f, 0, 641));
        assertEquals(0, WideGripMath.targetIndex(10, 100f, 1000, 1));
        assertEquals(0, WideGripMath.targetIndex(10, 100f, 1000, 0));
    }
}
