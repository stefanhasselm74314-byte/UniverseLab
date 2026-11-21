package de.universelab.sternfenster;

/**
 * Horizontsystem auf Basis von J2000-Katalogpositionen.
 * Näherung: keine Präzession, Nutation, Refraktion und Eigenbewegung.
 * Stundenwinkel und Sternzeit nach gängigen astronomischen Näherungsformeln.
 */
public final class SkyMath {
    private SkyMath() { }
    public static double rad(double deg) { return Math.toRadians(deg); }
    public static double wrap360(double degrees) { return ((degrees % 360.0) + 360.0) % 360.0; }
    public static double julianDay(long millis) { return 2440587.5 + millis / 86400000.0; }
    public static double gmstDeg(long millis) {
        double jd = julianDay(millis), t = (jd - 2451545.0) / 36525.0;
        return wrap360(280.46061837 + 360.98564736629 * (jd - 2451545.0)
                + 0.000387933 * t * t - t * t * t / 38710000.0);
    }
    /** x=east, y=north, z=up: Einheitsvektor im lokalen Horizontsystem. */
    public static double[] horizonVector(double raDeg, double decDeg,
                                         double latitudeDeg, double longitudeDeg, long millis) {
        double phi = rad(latitudeDeg), delta = rad(decDeg);
        double hourAngle = rad(wrap360(gmstDeg(millis) + longitudeDeg - raDeg));
        double c = Math.cos(delta);
        double east = -c * Math.sin(hourAngle);
        double north = Math.sin(delta) * Math.cos(phi) - c * Math.sin(phi) * Math.cos(hourAngle);
        double up = Math.sin(delta) * Math.sin(phi) + c * Math.cos(phi) * Math.cos(hourAngle);
        return new double[] { east, north, up };
    }
    /** 0=N, 90=O, 180=S, 270=W; Altitude in Grad. */
    public static double[] altitudeAzimuth(double raDeg, double decDeg,
                                            double lat, double lon, long millis) {
        double[] v = horizonVector(raDeg, decDeg, lat, lon, millis);
        return new double[] { Math.toDegrees(Math.asin(Math.max(-1, Math.min(1, v[2])))),
                              wrap360(Math.toDegrees(Math.atan2(v[0], v[1]))) };
    }
}
