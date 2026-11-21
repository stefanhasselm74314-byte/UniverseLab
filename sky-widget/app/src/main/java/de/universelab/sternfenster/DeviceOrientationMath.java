package de.universelab.sternfenster;

/**
 * Pure geometry for a rear-camera sky view; independent of Android and its lifecycle.
 *
 * SensorManager's row-major rotation matrix maps natural device axes into
 * magnetic east/north/up. Device +Z points out of the display towards its user,
 * so the rear-camera sightline is -Z. No camera permission or image is involved.
 *
 * The returned basis contains FORWARD, SCREEN RIGHT, SCREEN UP, in that order,
 * each expressed in true east/north/up. It can be projected directly, including
 * roll and passage through the zenith, without reconstructing Euler angles.
 */
final class DeviceOrientationMath {
    // Readout azimuth is undefined at the vertical axis. This threshold affects
    // only the UI's held last heading, never the exact camera basis/rendering.
    private static final double AZIMUTH_HORIZONTAL_MIN = Math.sin(Math.toRadians(.1));

    private DeviceOrientationMath() { }

    /**
     * @param rotation SensorManager 3x3 (9 floats) or 4x4 (16 floats), row-major
     * @param displayRotation Surface.ROTATION_0/90/180/270 encoded as 0/1/2/3
     * @param declinationDeg magnetic declination, east-positive: trueAz = magAz + D
     * @param out nine entries: forward ENU, screen-right ENU, screen-up ENU
     * @return false for malformed/nonfinite/non-rotational input; out is unchanged
     *
     * Display.getRotation is the rotation of DRAWN GRAPHICS, opposite to the
     * physical device rotation. At ROTATION_90, screen right is -device Y and
     * screen up is +device X. This matches Android's remapCoordinateSystem with
     * AXIS_Y, AXIS_MINUS_X; those parameters are not direct column selectors.
     */
    static boolean cameraBasis(float[] rotation, int displayRotation,
                               double declinationDeg, double[] out) {
        if (!validRotationMatrix(rotation)
                || out == null || out.length < 9 || displayRotation < 0 || displayRotation > 3
                || !Double.isFinite(declinationDeg)) return false;
        int stride = rotation.length == 9 ? 3 : 4;
        double xe = rotation[0], xn = rotation[stride], xu = rotation[2 * stride];
        double ye = rotation[1], yn = rotation[stride + 1], yu = rotation[2 * stride + 1];
        double ze = rotation[2], zn = rotation[stride + 2], zu = rotation[2 * stride + 2];
        double zz = ze * ze + zn * zn + zu * zu;

        double inverseForward = 1 / Math.sqrt(zz);
        double fe = -ze * inverseForward, fn = -zn * inverseForward, fu = -zu * inverseForward;
        double re, rn, ru;
        switch (displayRotation) {
            case 1: re = -ye; rn = -yn; ru = -yu; break;
            case 2: re = -xe; rn = -xn; ru = -xu; break;
            case 3: re = ye; rn = yn; ru = yu; break;
            default: re = xe; rn = xn; ru = xu;
        }
        // Gram-Schmidt removes tiny input roundoff. For this camera convention,
        // right x forward = up, while right x up = -forward.
        double alongForward = re * fe + rn * fn + ru * fu;
        re -= alongForward * fe; rn -= alongForward * fn; ru -= alongForward * fu;
        double inverseRight = 1 / Math.sqrt(re * re + rn * rn + ru * ru);
        re *= inverseRight; rn *= inverseRight; ru *= inverseRight;
        double ue = rn * fu - ru * fn, un = ru * fe - re * fu, uu = re * fn - rn * fe;

        double angle = Math.toRadians(declinationDeg % 360);
        double c = Math.cos(angle), s = Math.sin(angle);
        // Magnetic north at an east-positive declination has positive true east.
        out[0] = c * fe + s * fn; out[1] = c * fn - s * fe; out[2] = fu;
        out[3] = c * re + s * rn; out[4] = c * rn - s * re; out[5] = ru;
        out[6] = c * ue + s * un; out[7] = c * un - s * ue; out[8] = uu;
        return true;
    }

    /**
     * Convert a proper row-major device-to-world matrix to normalized [w,x,y,z].
     * The largest-diagonal branches remain well-conditioned at 180 degrees.
     * A quaternion and its negation describe the same rotation; no sign is promised.
     */
    static boolean quaternionFromMatrix(float[] rotation, double[] out) {
        if (!validRotationMatrix(rotation) || out == null || out.length < 4) return false;
        int stride = rotation.length == 9 ? 3 : 4;
        double m00=rotation[0], m01=rotation[1], m02=rotation[2];
        double m10=rotation[stride], m11=rotation[stride+1], m12=rotation[stride+2];
        double m20=rotation[2*stride], m21=rotation[2*stride+1], m22=rotation[2*stride+2];
        double w,x,y,z,trace=m00+m11+m22;
        if (trace > 0) {
            double s=2*Math.sqrt(trace+1);
            w=.25*s; x=(m21-m12)/s; y=(m02-m20)/s; z=(m10-m01)/s;
        } else if (m00 >= m11 && m00 >= m22) {
            double s=2*Math.sqrt(1+m00-m11-m22);
            w=(m21-m12)/s; x=.25*s; y=(m01+m10)/s; z=(m02+m20)/s;
        } else if (m11 >= m22) {
            double s=2*Math.sqrt(1+m11-m00-m22);
            w=(m02-m20)/s; x=(m01+m10)/s; y=.25*s; z=(m12+m21)/s;
        } else {
            double s=2*Math.sqrt(1+m22-m00-m11);
            w=(m10-m01)/s; x=(m02+m20)/s; y=(m12+m21)/s; z=.25*s;
        }
        double norm=Math.hypot(Math.hypot(w,x),Math.hypot(y,z));
        if (!Double.isFinite(norm) || norm < 1e-12) return false;
        out[0]=w/norm; out[1]=x/norm; out[2]=y/norm; out[3]=z/norm;
        return true;
    }

    /**
     * Shortest-path normalized linear quaternion interpolation (not constant-
     * angular-speed slerp). alpha is clamped to [0,1]. out may alias either input.
     * Null/short/nonfinite/zero inputs fail without changing out.
     */
    static boolean blendQuaternion(double[] from, double[] target, double alpha, double[] out) {
        if (from == null || from.length < 4 || target == null || target.length < 4
                || out == null || out.length < 4 || !Double.isFinite(alpha)) return false;
        double aw=from[0],ax=from[1],ay=from[2],az=from[3];
        double bw=target[0],bx=target[1],by=target[2],bz=target[3];
        if (!Double.isFinite(aw) || !Double.isFinite(ax) || !Double.isFinite(ay) || !Double.isFinite(az)
                || !Double.isFinite(bw) || !Double.isFinite(bx) || !Double.isFinite(by) || !Double.isFinite(bz)) return false;
        double an=Math.hypot(Math.hypot(aw,ax),Math.hypot(ay,az));
        double bn=Math.hypot(Math.hypot(bw,bx),Math.hypot(by,bz));
        if (!Double.isFinite(an) || !Double.isFinite(bn) || an < 1e-12 || bn < 1e-12) return false;
        aw/=an; ax/=an; ay/=an; az/=an; bw/=bn; bx/=bn; by/=bn; bz/=bn;
        if (aw*bw+ax*bx+ay*by+az*bz < 0) { bw=-bw; bx=-bx; by=-by; bz=-bz; }
        double t=Math.max(0,Math.min(1,alpha)), inverse=1-t;
        double w=inverse*aw+t*bw, x=inverse*ax+t*bx, y=inverse*ay+t*by, z=inverse*az+t*bz;
        double norm=Math.hypot(Math.hypot(w,x),Math.hypot(y,z));
        if (!Double.isFinite(norm) || norm < 1e-12) return false;
        out[0]=w/norm; out[1]=x/norm; out[2]=y/norm; out[3]=z/norm;
        return true;
    }

    /** UI heading only; previous finite heading is held within 0.1 degree of a pole. */
    static double azimuth(double[] basis, double lastAzimuthDeg) {
        double fallback = Double.isFinite(lastAzimuthDeg) ? wrap360(lastAzimuthDeg) : 0;
        if (!finiteForward(basis)
                || Math.hypot(basis[0], basis[1]) < AZIMUTH_HORIZONTAL_MIN) return fallback;
        return wrap360(Math.toDegrees(Math.atan2(basis[0], basis[1])));
    }

    /** Actual rear-camera altitude in degrees, including negative altitude. */
    static double altitude(double[] basis) {
        if (!finiteForward(basis)) return Double.NaN;
        return Math.toDegrees(Math.atan2(basis[2], Math.hypot(basis[0], basis[1])));
    }

    /** Useful for UI interpolation only; direct rendering should retain the basis. */
    static double shortestDeltaDegrees(double from, double to) {
        if (!Double.isFinite(from) || !Double.isFinite(to)) return Double.NaN;
        return wrap360((to % 360) - (from % 360) + 180) - 180;
    }

    private static boolean finiteForward(double[] basis) {
        return basis != null && basis.length >= 3 && Double.isFinite(basis[0])
                && Double.isFinite(basis[1]) && Double.isFinite(basis[2])
                && (basis[0] != 0 || basis[1] != 0 || basis[2] != 0);
    }

    private static boolean validRotationMatrix(float[] rotation) {
        if (rotation == null || (rotation.length != 9 && rotation.length != 16)) return false;
        int stride=rotation.length==9?3:4;
        double xe=rotation[0], xn=rotation[stride], xu=rotation[2*stride];
        double ye=rotation[1], yn=rotation[stride+1], yu=rotation[2*stride+1];
        double ze=rotation[2], zn=rotation[stride+2], zu=rotation[2*stride+2];
        if (!Double.isFinite(xe) || !Double.isFinite(xn) || !Double.isFinite(xu)
                || !Double.isFinite(ye) || !Double.isFinite(yn) || !Double.isFinite(yu)
                || !Double.isFinite(ze) || !Double.isFinite(zn) || !Double.isFinite(zu)) return false;
        double xx=xe*xe+xn*xn+xu*xu, yy=ye*ye+yn*yn+yu*yu, zz=ze*ze+zn*zn+zu*zu;
        double xy=xe*ye+xn*yn+xu*yu, xz=xe*ze+xn*zn+xu*zu, yz=ye*ze+yn*zn+yu*zu;
        double determinant=xe*(yn*zu-yu*zn)-ye*(xn*zu-xu*zn)+ze*(xn*yu-xu*yn);
        // Tolerate roundoff, not a reflected, degenerate or materially sheared pose.
        return Math.abs(xx-1)<=.02 && Math.abs(yy-1)<=.02 && Math.abs(zz-1)<=.02
                && Math.abs(xy)<=.02 && Math.abs(xz)<=.02 && Math.abs(yz)<=.02
                && determinant>=.97 && determinant<=1.03;
    }

    private static double wrap360(double degrees) {
        double value = degrees % 360;
        return value < 0 ? value + 360 : value;
    }
}
