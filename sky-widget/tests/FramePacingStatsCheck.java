package de.universelab.sternfenster;

/** Deterministic timing traces; run with javac/java without Android. */
public final class FramePacingStatsCheck {
    private static int checks;

    private static void truth(boolean condition, String message) {
        checks++;
        if (!condition) throw new AssertionError(message);
    }

    private static void close(double got, double expected, double tolerance, String message) {
        checks++;
        if (!Double.isFinite(got) || Math.abs(got - expected) > tolerance)
            throw new AssertionError(message + ": " + got + " versus " + expected);
    }

    private static void cadence(int hz) {
        FramePacingStats s = new FramePacingStats();
        long origin = -5_000_000_000L; // nanoTime has no guaranteed nonnegative origin.
        s.start(origin);
        for (int i = 0; i < 20 * hz; i++) {
            long begin = origin + Math.round(i * 1_000_000_000.0 / hz);
            s.record(begin, begin + 1_000_000L, hz);
        }
        FramePacingStats.Summary r = s.finish(origin + 20_000_000_000L);
        truth(r.complete && !r.cancelled && !r.samplesOverflowed, hz + " valid session");
        truth(r.frames == 20 * hz && r.intervalCount == r.frames - 1, hz + " N frames / N-1 intervals");
        close(r.renderFps, hz, 1e-9, hz + " count/duration FPS");
        close(r.intervalFps, hz, 1e-6, hz + " interval FPS");
        close(r.intervalMeanNs, 1_000_000_000.0 / hz, 1, hz + " mean interval");
        close(r.intervalP95Ns, Math.ceil(1_000_000_000.0 / hz), 1, hz + " p95 interval");
        close(r.drawP95Ns, 1_000_000, 0, hz + " CPU p95");
        truth(r.intervalsAbove20Ms == 0, hz + " no diagnostic long intervals");
        close(r.displayHzMin, hz, 0, hz + " minimum display Hz");
        close(r.displayHzMax, hz, 0, hz + " maximum display Hz");
        truth(!s.isRunning() && s.finish(origin + 30_000_000_000L) == r, hz + " finish idempotent");
    }

    private static void spacingAndStalls() {
        FramePacingStats s = new FramePacingStats();
        s.start(0);
        long[] starts = {0, 10_000_000, 40_000_000, 50_000_000, 80_000_000, 280_000_000};
        for (int i = 0; i < starts.length; i++)
            s.record(starts[i], starts[i] + (i + 1) * 100_000L, i < 3 ? 120 : 60);
        FramePacingStats.Summary r = s.finish(1_000_000_000L);
        truth(r.frames == 6 && r.intervalCount == 5, "six calls have five intervals");
        close(r.renderFps, 6, 0, "idle tail remains in observation duration");
        close(r.intervalFps, 5e9 / 280_000_000, 1e-12, "spacing rate does not count first frame twice");
        close(r.intervalMeanNs, 56_000_000, 0, "nonuniform mean");
        close(r.intervalP95Ns, 200_000_000, 0, "stall survives p95 for short trace");
        truth(r.intervalMinNs == 10_000_000 && r.intervalMaxNs == 200_000_000, "spacing extrema");
        truth(r.intervalsAbove20Ms == 3, "count long intervals rather than guessed dropped frames");
        close(r.drawP95Ns, 600_000, 0, "CPU duration separate from frame spacing");
        close(r.displayHzMin, 60, 0, "variable display minimum");
        close(r.displayHzMax, 120, 0, "variable display maximum");

        s.start(0);
        s.record(0, 0, 60);
        s.record(20_000_000, 20_000_000, 60);
        s.record(40_000_001, 40_000_001, 60);
        r = s.finish(50_000_000);
        truth(r.intervalsAbove20Ms == 1, "strict threshold is >20ms, not >=20ms");
        close(r.drawP95Ns, 0, 0, "zero-duration callbacks remain valid");
    }

    private static void emptySingleCancelReset() {
        FramePacingStats s = new FramePacingStats();
        s.record(1, 2, 60);
        FramePacingStats.Summary r = s.finish(10);
        truth(!r.complete && r.frames == 0 && Double.isNaN(r.renderFps), "never-started session is not complete");
        s.start(100);
        truth(s.isRunning() && s.elapsedNs(150) == 50 && s.elapsedNs(50) == 0, "elapsed bounded by monotonic start");
        r = s.finish(1_000_000_100L);
        truth(r.complete && r.frames == 0 && r.intervalCount == 0, "complete zero-draw session");
        close(r.renderFps, 0, 0, "zero draws over positive duration means zero FPS");
        truth(Double.isNaN(r.intervalFps) && Double.isNaN(r.intervalP95Ns)
                && Double.isNaN(r.drawP95Ns) && Double.isNaN(r.displayHzMin), "missing samples stay unavailable");

        s.start(0);
        s.record(10, 11, 60);
        r = s.finish(1_000_000_000L);
        truth(r.frames == 1 && r.intervalCount == 0 && Double.isNaN(r.intervalFps), "one frame has no interval-derived rate");
        close(r.renderFps, 1, 0, "single-frame count rate");
        s.start(0);
        s.record(1, 2, 60);
        s.cancel();
        s.record(3, 4, 60);
        r = s.finish(10);
        truth(!s.isRunning() && r.cancelled && !r.complete && r.frames == 1, "cancelled session stops and stays incomplete");
        s.reset();
        r = s.finish(10);
        truth(r.frames == 0 && !r.complete && !r.cancelled, "reset discards observations and cancellation");
        s.start(0);
        s.record(0, 0, 60);
        r = s.finish(0);
        truth(!r.complete && Double.isNaN(r.renderFps), "zero duration cannot yield a complete measurement or rate");
    }

    private static void invalidAndOverflow() {
        FramePacingStats s = new FramePacingStats();
        s.start(100);
        s.record(99, 100, 60); // before measurement
        s.record(100, 99, 60); // negative draw duration
        s.record(100, 110, Double.NaN); // valid timing, unavailable Hz
        s.record(100, 110, 60); // duplicate
        s.record(105, 115, 60); // overlapping main-thread draw
        s.record(120, 125, 0); // valid timing, unavailable Hz
        s.record(130, 135, 59.94);
        FramePacingStats.Summary r = s.finish(200);
        truth(r.frames == 3 && r.invalidEvents == 4 && !r.complete, "invalid callbacks rejected and disclosed");
        truth(r.unknownHzSamples == 2, "unavailable display Hz does not lose valid draw");
        close(r.displayHzMin, 59.94, 0, "only valid Hz samples affect range");
        close(r.displayHzMax, 59.94, 0, "valid fractional refresh rate");

        s.start(10);
        s.record(20, 30, 60);
        r = s.finish(25);
        truth(!r.complete && r.invalidEvents == 1, "finish cannot precede last draw completion");
        s.start(10);
        r = s.finish(5);
        truth(!r.complete && r.durationNs == 0 && Double.isNaN(r.renderFps), "backwards finish is not divided");
        s.start(Long.MIN_VALUE);
        s.record(Long.MAX_VALUE - 1, Long.MAX_VALUE, 60);
        r = s.finish(Long.MAX_VALUE);
        truth(r.frames == 0 && r.invalidEvents == 2 && !r.complete, "overflowing clock differences rejected");

        s.start(0);
        int count = FramePacingStats.SAMPLE_CAPACITY + 2;
        for (int i = 0; i < count; i++) s.record(i * 1_000_000L, i * 1_000_000L + 1, 120);
        r = s.finish(count * 1_000_000L);
        truth(r.frames == count && r.intervalCount == count - 1, "overflow retains exact counters");
        truth(r.samplesOverflowed && !r.complete, "bounded buffers disclose incomplete sample storage");
        truth(r.storedDrawSamples == FramePacingStats.SAMPLE_CAPACITY
                && r.storedIntervalSamples == FramePacingStats.SAMPLE_CAPACITY, "bounded storage");
        truth(Double.isNaN(r.intervalP95Ns) && Double.isNaN(r.drawP95Ns), "do not present prefix p95 as full-session p95");
        close(r.intervalMeanNs, 1_000_000, 0, "overflow retains exact interval mean");
        close(r.renderFps, 1000, 0, "overflow retains correct count/duration rate");
    }

    public static void main(String[] args) {
        cadence(60);
        cadence(120);
        spacingAndStalls();
        emptySingleCancelReset();
        invalidAndOverflow();
        System.out.println("FramePacingStats: " + checks + " checks passed");
    }
}
