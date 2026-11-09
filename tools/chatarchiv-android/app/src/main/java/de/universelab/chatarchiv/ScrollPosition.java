package de.universelab.chatarchiv;

/** Pure mapping for the optional pixel-position slider in the single-message reader. */
final class ScrollPosition {
    static final int MAX_PROGRESS = 1000;

    private ScrollPosition() { }

    static int progressFor(int offset, int contentHeight, int viewportHeight) {
        long max = Math.max(0L, (long) contentHeight - Math.max(0, viewportHeight));
        if (max == 0) return 0;
        long safe = Math.min(max, Math.max(0L, offset));
        return (int) Math.min(MAX_PROGRESS,
                (safe * MAX_PROGRESS + max / 2) / max);
    }

    static int offsetFor(int progress, int contentHeight, int viewportHeight) {
        long max = Math.max(0L, (long) contentHeight - Math.max(0, viewportHeight));
        long safe = Math.min(MAX_PROGRESS, Math.max(0, progress));
        return (int) Math.min(Integer.MAX_VALUE,
                (safe * max + MAX_PROGRESS / 2) / MAX_PROGRESS);
    }
}
