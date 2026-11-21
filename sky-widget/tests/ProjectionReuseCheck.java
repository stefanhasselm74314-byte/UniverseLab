package de.universelab.sternfenster;

import java.util.Random;

/** Differential regression for mutable camera state against the released 0.4.0 formula. */
public final class ProjectionReuseCheck {
    private static final Random RANDOM = new Random(731041L);
    private static int comparisons, configurations;

    private static void same(SkyProjection actual, FrozenProjection expected,
                             double east, double north, double up) {
        boolean shown = actual.project(east, north, up);
        boolean referenceShown = expected.project(east, north, up);
        if (shown != referenceShown || (shown &&
                (Float.floatToIntBits(actual.x) != Float.floatToIntBits(expected.x)
                || Float.floatToIntBits(actual.y) != Float.floatToIntBits(expected.y)))) {
            throw new AssertionError("reconfiguration " + configurations + ", ray " + comparisons
                    + ": visible=" + shown + "/" + referenceShown + " x=" + actual.x + "/" + expected.x
                    + " y=" + actual.y + "/" + expected.y);
        }
        comparisons++;
    }

    private static void compareRays(SkyProjection actual, FrozenProjection reference) {
        configurations++;
        // Axis, horizon and pole rays exercise state left by the preceding camera.
        for (int axis = 0; axis < 3; axis++) for (int sign = -1; sign <= 1; sign += 2) {
            same(actual, reference, axis == 0 ? sign : 0, axis == 1 ? sign : 0, axis == 2 ? sign : 0);
        }
        for (int i = 0; i < 96; i++) {
            double up = 2 * RANDOM.nextDouble() - 1;
            double az = 2 * Math.PI * RANDOM.nextDouble();
            double radius = Math.sqrt(Math.max(0, 1 - up * up));
            same(actual, reference, radius * Math.sin(az), radius * Math.cos(az), up);
        }
    }

    private static double[] basis(double azimuth, double altitude, double roll) {
        double sa = Math.sin(azimuth), ca = Math.cos(azimuth);
        double sh = Math.sin(altitude), ch = Math.cos(altitude);
        double sr = Math.sin(roll), cr = Math.cos(roll);
        return new double[] {ch * sa, ch * ca, sh,
                cr * ca - sr * sh * sa, -cr * sa - sr * sh * ca, sr * ch,
                -sr * ca - cr * sh * sa, sr * sa - cr * sh * ca, cr * ch};
    }

    public static void main(String[] args) {
        SkyProjection reused = new SkyProjection(1, 1, 0, 0, 90);
        int[][] sizes = {{720, 1200}, {1200, 720}, {280, 360}, {1, 1}, {0, -5},
                {1, 8000}, {8000, 1}, {1080, 1296}};
        double[] angles = {0, 90, 180, 270, -360, 725, Double.NaN,
                Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY};
        double[] heights = {-120, -90, -42, 0, 42, 89, 90, 120, Double.NaN};
        double[] fields = {-1, 20, 35, 100, 135, 160, 190, Double.NaN, Double.POSITIVE_INFINITY};
        for (int i = 0; i < 432; i++) {
            int[] size = sizes[i % sizes.length];
            double az = angles[i % angles.length], alt = heights[(i / 3) % heights.length];
            double fov = fields[(i / 7) % fields.length];
            reused.configure(size[0], size[1], az, alt, fov);
            FrozenProjection angleReference = new FrozenProjection(size[0], size[1], az, alt, fov);
            compareRays(reused, angleReference);

            // Alternate the two configuration forms on the same instance; include roll
            // and both poles so an old right/up basis or viewport cannot survive unnoticed.
            double cameraAlt = i % 3 == 0 ? Math.PI / 2 : i % 3 == 1 ? -Math.PI / 2
                    : (RANDOM.nextDouble() - .5) * Math.PI;
            double[] input = basis(RANDOM.nextDouble() * 2 * Math.PI, cameraAlt,
                    RANDOM.nextDouble() * 2 * Math.PI);
            int[] nextSize = sizes[(i + 3) % sizes.length];
            reused.configure(nextSize[0], nextSize[1], fov, input);
            FrozenProjection basisReference = new FrozenProjection(nextSize[0], nextSize[1], fov, input);
            // Reusing/changing the caller's sensor buffer must not change the configured camera.
            for (int j = 0; j < input.length; j++) input[j] = 1234 + j;
            compareRays(reused, basisReference);

            // Construction still uses the same public-to-package API and old formula.
            compareRays(new SkyProjection(size[0], size[1], az, alt, fov), angleReference);
        }
        System.out.println("PASS: " + comparisons + " bit-exact projection comparisons across "
                + configurations + " configurations; angle/basis switches, input-buffer reuse,"
                + " resize, roll, poles, clamping and non-finite defaults.");
    }

    /**
     * Frozen reference copied from SkyProjection in release source commit
     * fdb4f7e7d45fca20a0b8289556699ddb984066f0. Intentionally has no configure()
     * method and does not call production projection helpers. This protects the
     * old numerical contract while testing new repeated state replacement.
     */
    private static final class FrozenProjection {
        private final double centerX, centerY, scale;
        private final double ce, cn, cu, re, rn, ru, ue, un, uu;
        float x, y;

        FrozenProjection(int width, int height, double azimuth, double altitude, double verticalFovDeg) {
            centerX = Math.max(1, width) * .5;
            centerY = Math.max(1, height) * .5;
            double az = Math.toRadians(Double.isFinite(azimuth) ? azimuth : 180);
            double alt = Math.toRadians(Double.isFinite(altitude) ? Math.max(-90, Math.min(90, altitude)) : 42);
            double fov = Double.isFinite(verticalFovDeg) ? Math.max(20, Math.min(160, verticalFovDeg)) : 90;
            scale = Math.max(1, height) / Math.toRadians(fov);
            double sa = Math.sin(az), ca = Math.cos(az), sh = Math.sin(alt), ch = Math.cos(alt);
            ce = ch * sa; cn = ch * ca; cu = sh;
            re = ca; rn = -sa; ru = 0;
            ue = -sh * sa; un = -sh * ca; uu = ch;
        }

        FrozenProjection(int width, int height, double verticalFovDeg, double[] cameraBasis) {
            centerX = Math.max(1, width) * .5;
            centerY = Math.max(1, height) * .5;
            double fov = Double.isFinite(verticalFovDeg) ? Math.max(20, Math.min(160, verticalFovDeg)) : 90;
            scale = Math.max(1, height) / Math.toRadians(fov);
            ce=cameraBasis[0]; cn=cameraBasis[1]; cu=cameraBasis[2];
            re=cameraBasis[3]; rn=cameraBasis[4]; ru=cameraBasis[5];
            ue=cameraBasis[6]; un=cameraBasis[7]; uu=cameraBasis[8];
        }

        boolean project(double east, double north, double up) {
            double forward = Math.max(-1, Math.min(1, east * ce + north * cn + up * cu));
            double angle = Math.acos(forward);
            if (!Double.isFinite(angle) || angle > Math.toRadians(170)) return false;
            double right = east * re + north * rn + up * ru;
            double top = east * ue + north * un + up * uu;
            double transverse = Math.hypot(right, top);
            if (transverse < 1e-12) {
                x = (float) centerX; y = (float) centerY;
            } else {
                double factor = scale * angle / transverse;
                x = (float) (centerX + right * factor);
                y = (float) (centerY - top * factor);
            }
            return Float.isFinite(x) && Float.isFinite(y);
        }
    }
}
