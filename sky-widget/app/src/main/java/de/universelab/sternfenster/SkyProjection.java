package de.universelab.sternfenster;

/** Pure Java azimuthal-equidistant projection in local east/north/up coordinates. */
final class SkyProjection {
    private final double centerX, centerY, scale;
    private final double ce, cn, cu, re, rn, ue, un, uu;
    float x, y;

    SkyProjection(int width, int height, double azimuth, double altitude, double verticalFovDeg) {
        centerX = Math.max(1, width) * .5;
        centerY = Math.max(1, height) * .5;
        double az = Math.toRadians(Double.isFinite(azimuth) ? azimuth : 180);
        double alt = Math.toRadians(Double.isFinite(altitude) ? Math.max(-90, Math.min(90, altitude)) : 42);
        double fov = Double.isFinite(verticalFovDeg) ? Math.max(20, Math.min(160, verticalFovDeg)) : 90;
        scale = Math.max(1, height) / Math.toRadians(fov);
        double sa = Math.sin(az), ca = Math.cos(az), sh = Math.sin(alt), ch = Math.cos(alt);
        ce = ch * sa; cn = ch * ca; cu = sh;
        re = ca; rn = -sa;
        ue = -sh * sa; un = -sh * ca; uu = ch;
    }

    boolean horizontal(double altitude, double azimuth) {
        double alt = Math.toRadians(altitude), az = Math.toRadians(azimuth), c = Math.cos(alt);
        return project(c * Math.sin(az), c * Math.cos(az), Math.sin(alt));
    }

    /** Accepts a unit vector; points near the projection antipode are deliberately omitted. */
    boolean project(double east, double north, double up) {
        double forward = Math.max(-1, Math.min(1, east * ce + north * cn + up * cu));
        double angle = Math.acos(forward);
        if (!Double.isFinite(angle) || angle > Math.toRadians(170)) return false;
        double right = east * re + north * rn;
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

    /** Isotropic downscaling, preserving aspect ratio within integer-pixel rounding. */
    static int[] bitmapSize(int width, int height) {
        int w = Math.max(1, width), h = Math.max(1, height);
        double factor = Math.min(1, Math.min(1350.0 / Math.max(w, h),
                Math.sqrt(850000.0 / ((double) w * h))));
        return new int[] {Math.max(1, (int) Math.floor(w * factor)),
                Math.max(1, (int) Math.floor(h * factor))};
    }
}
