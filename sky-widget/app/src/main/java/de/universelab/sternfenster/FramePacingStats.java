package de.universelab.sternfenster;

import java.util.Arrays;

/**
 * Bounded, single-threaded diagnostics for actual onDraw calls.
 *
 * All timestamps must use the same monotonic clock (for example System.nanoTime).
 * record() allocates nothing. Sorting and the immutable summary happen only at
 * finish(), outside the drawing measurement. These are app-side observations,
 * not GPU timings, presentation timestamps, or proof that a window was visible.
 */
final class FramePacingStats {
    static final int SAMPLE_CAPACITY = 32768;
    static final long LONG_INTERVAL_NS = 20_000_000L;

    private final long[] intervals = new long[SAMPLE_CAPACITY];
    private final long[] draws = new long[SAMPLE_CAPACITY];
    private boolean started, running, cancelled, overflowed;
    private long startNs, firstDrawStart, lastDrawStart, lastDrawEnd;
    private long frames, intervalCount, intervalMin, intervalMax, above20Ms;
    private long invalidEvents, unknownHzSamples;
    private int storedIntervals, storedDraws;
    private double hzMin = Double.NaN, hzMax = Double.NaN;
    private Summary finished;

    /** Starts a fresh session. A negative clock origin is valid. */
    void start(long nowNs) {
        reset();
        startNs = nowNs;
        started = running = true;
    }

    boolean isRunning() { return running; }

    /** Elapsed active session time; zero when idle or given a backwards clock. */
    long elapsedNs(long nowNs) {
        return running && validDifference(nowNs, startNs) ? nowNs - startNs : 0;
    }

    /**
     * Records a completed draw. Duplicate, backwards, overlapping or overflowing
     * timestamps are rejected and counted; an unavailable Hz value does not
     * discard an otherwise valid draw. Calls outside a running session are no-ops.
     */
    void record(long drawStartNs, long drawEndNs, double displayHz) {
        if (!running) return;
        if (!validDifference(drawStartNs, startNs)
                || !validDifference(drawEndNs, drawStartNs)
                || !validDifference(drawEndNs, startNs)
                || (frames > 0 && (drawStartNs <= lastDrawStart || drawStartNs < lastDrawEnd))) {
            invalidEvents++;
            return;
        }

        if (frames == 0) {
            firstDrawStart = drawStartNs;
        } else {
            long interval = drawStartNs - lastDrawStart;
            intervalCount++;
            if (intervalCount == 1 || interval < intervalMin) intervalMin = interval;
            if (interval > intervalMax) intervalMax = interval;
            if (interval > LONG_INTERVAL_NS) above20Ms++;
            if (storedIntervals < SAMPLE_CAPACITY) intervals[storedIntervals++] = interval;
            else overflowed = true;
        }
        if (storedDraws < SAMPLE_CAPACITY) draws[storedDraws++] = drawEndNs - drawStartNs;
        else overflowed = true;
        frames++;
        lastDrawStart = drawStartNs;
        lastDrawEnd = drawEndNs;
        if (Double.isFinite(displayHz) && displayHz > 0) {
            if (Double.isNaN(hzMin) || displayHz < hzMin) hzMin = displayHz;
            if (Double.isNaN(hzMax) || displayHz > hzMax) hzMax = displayHz;
        } else {
            unknownHzSamples++;
        }
    }

    /**
     * Ends the session and returns the same immutable result on repeated calls.
     * finish after cancel is allowed, but its result is explicitly incomplete.
     * complete describes measurement integrity, never a performance target.
     */
    Summary finish(long nowNs) {
        if (finished != null) return finished;
        boolean validEnd = started && validDifference(nowNs, startNs)
                && (frames == 0 || nowNs >= lastDrawEnd);
        if (started && !validEnd) invalidEvents++;
        long duration = started && validDifference(nowNs, startNs) ? nowNs - startNs : 0;
        long intervalSpan = intervalCount > 0 ? lastDrawStart - firstDrawStart : 0;
        boolean complete = started && duration > 0 && !cancelled && validEnd && !overflowed && invalidEvents == 0;
        // Quantiles of a truncated prefix would be misleading. Leave them absent
        // if that particular sample stream overflowed; retain exact counts/extrema.
        double intervalP95 = intervalCount == storedIntervals ? percentile95(intervals, storedIntervals) : Double.NaN;
        double drawP95 = frames == storedDraws ? percentile95(draws, storedDraws) : Double.NaN;
        finished = new Summary(frames, duration,
                duration > 0 ? frames * 1_000_000_000.0 / duration : Double.NaN,
                intervalCount, intervalMin, intervalMax,
                intervalCount > 0 ? (double) intervalSpan / intervalCount : Double.NaN,
                intervalP95,
                intervalSpan > 0 ? intervalCount * 1_000_000_000.0 / intervalSpan : Double.NaN,
                drawP95, above20Ms, hzMin, hzMax, storedIntervals, storedDraws,
                overflowed, invalidEvents, unknownHzSamples, complete, cancelled);
        running = false;
        return finished;
    }

    /** Stops recording, retaining partial observations with a cancellation flag. */
    void cancel() {
        if (running) {
            running = false;
            cancelled = true;
        }
    }

    /** Discards this session and any finished result without reallocating buffers. */
    void reset() {
        started = running = cancelled = overflowed = false;
        startNs = firstDrawStart = lastDrawStart = lastDrawEnd = 0;
        frames = intervalCount = intervalMin = intervalMax = above20Ms = 0;
        invalidEvents = unknownHzSamples = 0;
        storedIntervals = storedDraws = 0;
        hzMin = hzMax = Double.NaN;
        finished = null;
    }

    private static boolean validDifference(long later, long earlier) {
        return later >= earlier && later - earlier >= 0;
    }

    private static double percentile95(long[] samples, int count) {
        if (count == 0) return Double.NaN;
        Arrays.sort(samples, 0, count);
        return samples[(int) Math.ceil(count * .95) - 1];
    }

    static final class Summary {
        final long frames, durationNs, intervalCount, intervalMinNs, intervalMaxNs;
        final long intervalsAbove20Ms, invalidEvents, unknownHzSamples;
        final double renderFps, intervalMeanNs, intervalP95Ns, intervalFps, drawP95Ns;
        final double displayHzMin, displayHzMax;
        final int storedIntervalSamples, storedDrawSamples;
        final boolean samplesOverflowed, complete, cancelled;

        private Summary(long frames, long durationNs, double renderFps,
                long intervalCount, long intervalMinNs, long intervalMaxNs,
                double intervalMeanNs, double intervalP95Ns, double intervalFps,
                double drawP95Ns, long intervalsAbove20Ms,
                double displayHzMin, double displayHzMax,
                int storedIntervalSamples, int storedDrawSamples,
                boolean samplesOverflowed, long invalidEvents, long unknownHzSamples,
                boolean complete, boolean cancelled) {
            this.frames = frames;
            this.durationNs = durationNs;
            this.renderFps = renderFps;
            this.intervalCount = intervalCount;
            this.intervalMinNs = intervalMinNs;
            this.intervalMaxNs = intervalMaxNs;
            this.intervalMeanNs = intervalMeanNs;
            this.intervalP95Ns = intervalP95Ns;
            this.intervalFps = intervalFps;
            this.drawP95Ns = drawP95Ns;
            this.intervalsAbove20Ms = intervalsAbove20Ms;
            this.displayHzMin = displayHzMin;
            this.displayHzMax = displayHzMax;
            this.storedIntervalSamples = storedIntervalSamples;
            this.storedDrawSamples = storedDrawSamples;
            this.samplesOverflowed = samplesOverflowed;
            this.invalidEvents = invalidEvents;
            this.unknownHzSamples = unknownHzSamples;
            this.complete = complete;
            this.cancelled = cancelled;
        }
    }
}
