package de.universelab.chatarchiv;

import org.junit.Test;
import static org.junit.Assert.assertEquals;

public final class ScrollPositionTest {
    @Test public void mapsZeroAndEndOfLongMessage() {
        assertEquals(0, ScrollPosition.progressFor(0, 10000, 1000));
        assertEquals(1000, ScrollPosition.progressFor(9000, 10000, 1000));
        assertEquals(0, ScrollPosition.offsetFor(0, 10000, 1000));
        assertEquals(9000, ScrollPosition.offsetFor(1000, 10000, 1000));
    }

    @Test public void mapsMiddleWithSmallRoundingError() {
        assertEquals(500, ScrollPosition.progressFor(4500, 10000, 1000));
        assertEquals(4500, ScrollPosition.offsetFor(500, 10000, 1000));
    }

    @Test public void clampsInvalidAndOverflowInputs() {
        assertEquals(0, ScrollPosition.progressFor(-80, 200, 1000));
        assertEquals(0, ScrollPosition.offsetFor(1000, 200, 1000));
        assertEquals(0, ScrollPosition.offsetFor(-2, 10000, 1000));
        assertEquals(9000, ScrollPosition.offsetFor(2000, 10000, 1000));
        assertEquals(1000, ScrollPosition.progressFor(Integer.MAX_VALUE,
                Integer.MAX_VALUE, 1000));
    }

    @Test public void exactVisibilityHasNoScrollRange() {
        assertEquals(0, ScrollPosition.progressFor(60, 800, 800));
        assertEquals(0, ScrollPosition.offsetFor(300, 800, 800));
    }
}
