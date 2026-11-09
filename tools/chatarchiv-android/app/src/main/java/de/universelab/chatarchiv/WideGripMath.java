package de.universelab.chatarchiv;

/** Calculations shared by the touch-friendly fast-scroll grip and JVM tests. */
final class WideGripMath {
    private WideGripMath() { }

    /**
     * The native 24-dp thumb stays visible; only the strip immediately to its left
     * responds to the expanded drag gesture. The native region remains untouched.
     */
    static boolean isExpandedGrip(float x, int width, int fullGripPx, int nativeGripPx) {
        if (!Float.isFinite(x) || width <= 0 || fullGripPx <= nativeGripPx) return false;
        return x >= Math.max(0, width - fullGripPx)
                && x < width - nativeGripPx;
    }

    /** Translate a relative vertical drag into an adapter position, with clamping. */
    static int targetIndex(int start, float deltaY, int viewportHeight, int totalItems) {
        if (totalItems <= 0) return 0;
        final int last = totalItems - 1;
        final int initial = Math.max(0, Math.min(last, start));
        if (viewportHeight <= 0 || !Float.isFinite(deltaY)) return initial;
        final double raw = initial + (double) deltaY * last / viewportHeight;
        return (int) Math.round(Math.max(0, Math.min(last, raw)));
    }
}
