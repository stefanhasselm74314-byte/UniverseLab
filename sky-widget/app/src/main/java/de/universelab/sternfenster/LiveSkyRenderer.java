package de.universelab.sternfenster;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Shader;
import android.graphics.Typeface;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;

/**
 * Persistent renderer for a display-synchronised View.
 *
 * Positions use the real catalogue and the timestamp supplied for this frame.
 * No star/label/rectangle objects, lists, shaders or bitmaps are allocated by
 * the steady-state frame loop. Faint stars are batched by colour and eight
 * visual magnitude bands; their coordinates are never quantised. The brighter
 * stars retain their individual radius/alpha and are drawn above those batches.
 * Local-horizon grid geometry is reused until the viewport or camera changes.
 * This reduces work; the caller still has to measure achieved device FPS.
 *
 * One instance belongs to one View and must only be used from that View's UI
 * thread. It owns no Surface, thread, timer or retained Canvas.
 */
final class LiveSkyRenderer {
    private static final int BANDS = 8, COLOURS = 4, BATCHES = BANDS * COLOURS;
    private static final double FAINT_MIN = 1.7, BAND_STEP = .65;
    private static final int[] COLOUR_VALUES = {
            0xffffc4a7, 0xffffe6c0, 0xffc2ddff, 0xfff2f7ff
    };
    private static final String[] DIRECTIONS = {"N", "NO", "O", "SO", "S", "SW", "W", "NW"};
    private static final GridVectors GRID_VECTORS = new GridVectors(false);
    private static final GridVectors HORIZON_VECTORS = new GridVectors(true);
    private static volatile PreparedCatalog sharedCatalog;

    private final PreparedCatalog catalog;
    private final Paint backgroundPaint = new Paint();
    private final Paint gridPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint horizonPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint starPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint labelPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint directionPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint[] pointPaints = new Paint[BATCHES];
    private final float[][] pointBatches = new float[BATCHES][];
    private final int[] pointCounts = new int[BATCHES];
    private final float[] targetX, targetY, targetRadius, labelWidth;
    private final boolean[] targetVisible;
    private final float[] occupied;
    private final float[] gridLines = new float[GRID_VECTORS.count * 4];
    private final float[] horizonLines = new float[HORIZON_VECTORS.count * 4];
    private final float[] directionX = new float[8], directionY = new float[8];
    private final float[] directionWidth = new float[8];
    private final boolean[] directionVisible = new boolean[8];

    private final SkyProjection projection = new SkyProjection(1, 1, 180, 42, 90);
    private int width, height, gridCount, horizonCount, occupiedCount;
    private float unit, labelAscent, labelDescent, directionAscent, directionDescent;
    private double cameraAz = Double.NaN, cameraAlt = Double.NaN, cameraFov = Double.NaN;
    private double siteLatitude = Double.NaN, sinLatitude, cosLatitude;
    private double centerEast, centerNorth, centerUp, minForward;
    private final double[] lastBasis = new double[9];
    private boolean cameraHasBasis;

    LiveSkyRenderer(Context context) {
        catalog = preparedCatalog(context.getApplicationContext());
        int targetCount = catalog.targets.length;
        targetX = new float[targetCount];
        targetY = new float[targetCount];
        targetRadius = new float[targetCount];
        labelWidth = new float[targetCount];
        targetVisible = new boolean[targetCount];
        occupied = new float[(targetCount + 8) * 4];
        labelPaint.setTypeface(Typeface.create("sans-serif", Typeface.NORMAL));
        directionPaint.setTypeface(Typeface.create("sans-serif-medium", Typeface.NORMAL));
        for (int group = 0; group < BATCHES; group++) {
            pointBatches[group] = new float[catalog.batchSizes[group] * 2];
            Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
            paint.setStrokeCap(Paint.Cap.ROUND);
            paint.setStyle(Paint.Style.FILL);
            paint.setColor(COLOUR_VALUES[group / BANDS]);
            double visualMagnitude = FAINT_MIN + (group % BANDS + .5) * BAND_STEP;
            paint.setAlpha(alpha(visualMagnitude));
            pointPaints[group] = paint;
        }
    }

    void draw(Canvas canvas, int width, int height, double latitude, double longitude,
              double azimuth, double altitude, double verticalFovDeg, long epochMillis) {
        draw(canvas, width, height, latitude, longitude, azimuth, altitude,
                verticalFovDeg, epochMillis, true);
    }

    void draw(Canvas canvas, int requestedWidth, int requestedHeight,
              double latitude, double longitude, double azimuth, double altitude,
              double verticalFovDeg, long epochMillis, boolean labels) {
        draw(canvas,requestedWidth,requestedHeight,latitude,longitude,azimuth,altitude,
                verticalFovDeg,epochMillis,labels,null);
    }

    void draw(Canvas canvas, int requestedWidth, int requestedHeight,
              double latitude, double longitude, double azimuth, double altitude,
              double verticalFovDeg, long epochMillis, boolean labels, double[] cameraBasis) {
        if (requestedWidth <= 0 || requestedHeight <= 0) return;
        configure(requestedWidth, requestedHeight, azimuth, altitude, verticalFovDeg, cameraBasis);
        double safeLatitude = Double.isFinite(latitude) ? Math.max(-90, Math.min(90, latitude)) : 51.0504;
        double safeLongitude = Double.isFinite(longitude) ? longitude : 13.7373;
        if (siteLatitude != safeLatitude) {
            siteLatitude = safeLatitude;
            double phi = Math.toRadians(siteLatitude);
            sinLatitude = Math.sin(phi);
            cosLatitude = Math.cos(phi);
        }
        int save = canvas.save();
        try {
            canvas.clipRect(0, 0, width, height);
            canvas.drawRect(0, 0, width, height, backgroundPaint);
            if (gridCount > 0) canvas.drawLines(gridLines, 0, gridCount, gridPaint);
            if (horizonCount > 0) canvas.drawLines(horizonLines, 0, horizonCount, horizonPaint);
            occupiedCount = 0;
            if (labels) drawDirections(canvas);
            drawStars(canvas, safeLongitude, epochMillis, labels);
        } finally {
            canvas.restoreToCount(save);
        }
    }

    private void configure(int newWidth, int newHeight, double azimuth,
                           double altitude, double verticalFovDeg, double[] basis) {
        double az = Double.isFinite(azimuth) ? SkyMath.wrap360(azimuth) : 180;
        double alt = Double.isFinite(altitude) ? Math.max(-90, Math.min(90, altitude)) : 42;
        double fov = Double.isFinite(verticalFovDeg) ? Math.max(20, Math.min(160, verticalFovDeg)) : 90;
        boolean resized = width != newWidth || height != newHeight;
        boolean viewportChanged = resized || cameraFov != fov;
        boolean sameBasis=(basis!=null)==cameraHasBasis;
        if(basis!=null&&sameBasis)for(int i=0;i<9;i++)if(lastBasis[i]!=basis[i]){sameBasis=false;break;}
        if (!resized && cameraAz == az && cameraAlt == alt && cameraFov == fov && sameBasis) return;
        width = newWidth;
        height = newHeight;
        cameraAz = az;
        cameraAlt = alt;
        cameraFov = fov;
        // Sensor following changes the camera on most frames. Reuse the projection
        // rather than allocating one for every such update.
        cameraHasBasis=basis!=null;
        if(cameraHasBasis)System.arraycopy(basis,0,lastBasis,0,9);
        if(cameraHasBasis)projection.configure(width,height,fov,lastBasis);
        else projection.configure(width,height,az,alt,fov);
        if (resized) resizePaints();
        double azRad = Math.toRadians(az), altRad = Math.toRadians(alt);
        centerEast = cameraHasBasis ? lastBasis[0] : Math.cos(altRad) * Math.sin(azRad);
        centerNorth = cameraHasBasis ? lastBasis[1] : Math.cos(altRad) * Math.cos(azRad);
        centerUp = cameraHasBasis ? lastBasis[2] : Math.sin(altRad);
        // Circumscribed viewport cone rejects stars before the expensive acos.
        // The margin includes the largest retained halo, avoiding edge popping.
        if (viewportChanged) {
            double margin = 18 * unit;
            double diagonal = Math.hypot(width * .5 + margin, height * .5 + margin);
            double maximumAngle = Math.min(Math.toRadians(170), diagonal * Math.toRadians(fov) / height);
            minForward = Math.cos(maximumAngle);
        }
        gridCount = projectGrid(GRID_VECTORS, gridLines);
        horizonCount = projectGrid(HORIZON_VECTORS, horizonLines);
        for (int i = 0; i < 8; i++) {
            directionVisible[i] = projection.horizontal(3.5, i * 45);
            directionX[i] = projection.x;
            directionY[i] = projection.y;
        }
    }

    private void resizePaints() {
        unit = Math.max(.55f, Math.min(4f, Math.min(width, height) / 330f));
        backgroundPaint.setShader(new LinearGradient(0, 0, 0, height,
                0xff030a16, 0xff14283c, Shader.TileMode.CLAMP));
        gridPaint.setColor(0x304f7790);
        gridPaint.setStrokeWidth(Math.max(.7f, unit * .55f));
        horizonPaint.setColor(0xa46bafbf);
        horizonPaint.setStrokeWidth(Math.max(1f, unit));
        labelPaint.setTextSize(11.5f * unit);
        labelAscent = labelPaint.ascent();
        labelDescent = labelPaint.descent();
        directionPaint.setTextSize(12 * unit);
        directionAscent = directionPaint.ascent();
        directionDescent = directionPaint.descent();
        for (int i = 0; i < 8; i++) directionWidth[i] = directionPaint.measureText(DIRECTIONS[i]);
        for (int i = 0; i < catalog.targets.length; i++) {
            PreparedStar star = catalog.targets[i];
            targetRadius[i] = star.radius * unit;
            labelWidth[i] = star.label ? labelPaint.measureText(star.name) : 0;
        }
        for (int group = 0; group < BATCHES; group++) {
            double visualMagnitude = FAINT_MIN + (group % BANDS + .5) * BAND_STEP;
            pointPaints[group].setStrokeWidth(2 * radius(visualMagnitude) * unit);
        }
    }

    private int projectGrid(GridVectors vectors, float[] lines) {
        int count = 0;
        boolean previous = false;
        float oldX = 0, oldY = 0;
        float maxStep = Math.max(24, Math.min(width, height) * .18f);
        float maxStepSquared = maxStep * maxStep;
        for (int i = 0; i < vectors.count; i++) {
            if (vectors.start[i]) previous = false;
            boolean visible = projection.project(vectors.east[i], vectors.north[i], vectors.up[i]);
            if (visible) {
                float x = projection.x, y = projection.y;
                float dx = x - oldX, dy = y - oldY;
                if (previous && dx * dx + dy * dy < maxStepSquared) {
                    lines[count++] = oldX;
                    lines[count++] = oldY;
                    lines[count++] = x;
                    lines[count++] = y;
                }
                oldX = x;
                oldY = y;
            }
            previous = visible;
        }
        return count;
    }

    private void drawDirections(Canvas canvas) {
        for (int i = 0; i < 8; i++) {
            if (!directionVisible[i]) continue;
            float x = directionX[i], y = directionY[i], half = directionWidth[i] * .5f;
            float left = x - half - 3 * unit, top = y + directionAscent - 2 * unit;
            float right = x + half + 3 * unit, bottom = y + directionDescent + 2 * unit;
            if (!fits(left, top, right, bottom)) continue;
            occupy(left, top, right, bottom);
            outlinedText(canvas, DIRECTIONS[i], x - half, y, directionPaint, 0xff9fd3dc);
        }
    }

    private void drawStars(Canvas canvas, double longitude, long now, boolean labels) {
        if (catalog.stars.length == 0) {
            outlinedText(canvas, "Sternkatalog nicht verfügbar", 14 * unit, 28 * unit,
                    labelPaint, 0xffd4dde7);
            return;
        }
        Arrays.fill(pointCounts, 0);
        Arrays.fill(targetVisible, false);
        double lst = Math.toRadians(SkyMath.wrap360(SkyMath.gmstDeg(now) + longitude));
        double sinLst = Math.sin(lst), cosLst = Math.cos(lst);
        float margin = 18 * unit;
        for (PreparedStar star : catalog.stars) {
            double cosHour = cosLst * star.cosRa + sinLst * star.sinRa;
            double sinHour = sinLst * star.cosRa - cosLst * star.sinRa;
            double up = star.sinDec * sinLatitude + star.cosDec * cosLatitude * cosHour;
            if (up <= 0) continue;
            double east = -star.cosDec * sinHour;
            double north = star.sinDec * cosLatitude - star.cosDec * sinLatitude * cosHour;
            if (east * centerEast + north * centerNorth + up * centerUp < minForward) continue;
            if (!projection.project(east, north, up)) continue;
            float x = projection.x, y = projection.y;
            if (x < -margin || x > width + margin || y < -margin || y > height + margin) continue;
            if (star.target >= 0) {
                targetX[star.target] = x;
                targetY[star.target] = y;
                targetVisible[star.target] = true;
            }
            if (star.group >= 0) {
                int n = pointCounts[star.group];
                pointBatches[star.group][n] = x;
                pointBatches[star.group][n + 1] = y;
                pointCounts[star.group] = n + 2;
            }
        }
        // Faint-to-bright layers: at most 32 draw calls for the bulk catalogue.
        for (int band = BANDS - 1; band >= 0; band--) {
            for (int colour = 0; colour < COLOURS; colour++) {
                int group = colour * BANDS + band;
                if (pointCounts[group] > 0) {
                    canvas.drawPoints(pointBatches[group], 0, pointCounts[group], pointPaints[group]);
                }
            }
        }
        for (int i = 0; i < catalog.targets.length; i++) {
            PreparedStar star = catalog.targets[i];
            if (!targetVisible[i] || !star.bright) continue;
            float x = targetX[i], y = targetY[i], radius = targetRadius[i];
            starPaint.setColor(star.colour);
            starPaint.setAlpha(24);
            canvas.drawCircle(x, y, radius * 3.5f, starPaint);
            starPaint.setAlpha(60);
            canvas.drawCircle(x, y, radius * 1.9f, starPaint);
            starPaint.setAlpha(star.alpha);
            canvas.drawCircle(x, y, radius, starPaint);
        }
        if (labels) {
            // Prepared targets are faint-to-bright; the brightest labels get priority.
            for (int i = catalog.targets.length - 1; i >= 0; i--) {
                if (targetVisible[i] && catalog.targets[i].label) placeLabel(canvas, i);
            }
        }
    }

    private void placeLabel(Canvas canvas, int target) {
        float gap = targetRadius[target] + 4 * unit, textWidth = labelWidth[target];
        for (int option = 0; option < 4; option++) {
            float x = (option & 1) == 0 ? targetX[target] + gap : targetX[target] - gap - textWidth;
            float y = targetY[target] + (option < 2 ? -3 : 13) * unit;
            float left = x - 2 * unit, top = y + labelAscent - 2 * unit;
            float right = x + textWidth + 2 * unit, bottom = y + labelDescent + 2 * unit;
            if (!fits(left, top, right, bottom) || collides(left, top, right, bottom)) continue;
            occupy(left, top, right, bottom);
            outlinedText(canvas, catalog.targets[target].name, x, y, labelPaint, 0xffc8d8e5);
            return;
        }
    }

    private boolean fits(float left, float top, float right, float bottom) {
        return left >= 5 * unit && top >= 4 * unit
                && right <= width - 5 * unit && bottom <= height - 4 * unit;
    }

    private boolean collides(float left, float top, float right, float bottom) {
        for (int i = 0; i < occupiedCount; i += 4) {
            if (left < occupied[i + 2] && occupied[i] < right
                    && top < occupied[i + 3] && occupied[i + 1] < bottom) return true;
        }
        return false;
    }

    private void occupy(float left, float top, float right, float bottom) {
        occupied[occupiedCount++] = left;
        occupied[occupiedCount++] = top;
        occupied[occupiedCount++] = right;
        occupied[occupiedCount++] = bottom;
    }

    private void outlinedText(Canvas canvas, String text, float x, float y, Paint paint, int colour) {
        paint.setAlpha(255);
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(3 * unit);
        paint.setColor(0xff08101c);
        canvas.drawText(text, x, y, paint);
        paint.setStyle(Paint.Style.FILL);
        paint.setColor(colour);
        canvas.drawText(text, x, y, paint);
    }

    private static float radius(double magnitude) {
        return (float) Math.max(.5, Math.min(4.6, 3.15 - .46 * magnitude));
    }

    private static int alpha(double magnitude) {
        return Math.max(90, Math.min(255, (int) (255 - Math.max(0, magnitude) * 23)));
    }

    private static PreparedCatalog preparedCatalog(Context context) {
        PreparedCatalog ready = sharedCatalog;
        if (ready != null) return ready;
        synchronized (LiveSkyRenderer.class) {
            if (sharedCatalog == null) sharedCatalog = new PreparedCatalog(StarCatalog.load(context));
            return sharedCatalog;
        }
    }

    private static final class PreparedCatalog {
        final PreparedStar[] stars, targets;
        final int[] batchSizes = new int[BATCHES];
        PreparedCatalog(List<StarCatalog.Star> source) {
            stars = new PreparedStar[source.size()];
            for (int i = 0; i < stars.length; i++) stars[i] = new PreparedStar(source.get(i));
            Arrays.sort(stars, Comparator.comparingDouble((PreparedStar star) -> star.magnitude).reversed());
            int targetCount = 0;
            for (PreparedStar star : stars) {
                if (star.bright || star.label) targetCount++;
                if (star.group >= 0) batchSizes[star.group]++;
            }
            targets = new PreparedStar[targetCount];
            int next = 0;
            for (PreparedStar star : stars) {
                if (star.bright || star.label) {
                    star.target = next;
                    targets[next++] = star;
                }
            }
        }
    }

    private static final class PreparedStar {
        final double cosRa, sinRa, cosDec, sinDec, magnitude;
        final String name;
        final boolean bright, label;
        final int colour, alpha, group;
        final float radius;
        int target = -1; // Assigned once, before the prepared catalogue is published.
        PreparedStar(StarCatalog.Star star) {
            double ra = Math.toRadians(star.ra), dec = Math.toRadians(star.dec);
            cosRa = Math.cos(ra);
            sinRa = Math.sin(ra);
            cosDec = Math.cos(dec);
            sinDec = Math.sin(dec);
            magnitude = star.mag;
            name = star.name;
            bright = magnitude < FAINT_MIN;
            label = magnitude <= 2.15 && !name.isEmpty();
            int colourGroup = star.bv > 1.35 ? 0 : star.bv > .65 ? 1 : star.bv < -.05 ? 2 : 3;
            colour = COLOUR_VALUES[colourGroup];
            radius = radius(magnitude);
            alpha = alpha(magnitude);
            int band = Math.max(0, Math.min(BANDS - 1, (int) ((magnitude - FAINT_MIN) / BAND_STEP)));
            group = bright ? -1 : colourGroup * BANDS + band;
        }
    }

    private static final class GridVectors {
        final int count;
        final double[] east, north, up;
        final boolean[] start;
        GridVectors(boolean horizonOnly) {
            count = horizonOnly ? 181 : 2 * 181 + 12 * 46;
            east = new double[count];
            north = new double[count];
            up = new double[count];
            start = new boolean[count];
            int n = 0;
            if (horizonOnly) {
                for (int az = 0; az <= 360; az += 2) set(n++, 0, az, az == 0);
            } else {
                for (int alt = 30; alt <= 60; alt += 30) {
                    for (int az = 0; az <= 360; az += 2) set(n++, alt, az, az == 0);
                }
                for (int az = 0; az < 360; az += 30) {
                    for (int alt = 0; alt <= 90; alt += 2) set(n++, alt, az, alt == 0);
                }
            }
        }
        private void set(int i, double altitude, double azimuth, boolean first) {
            double alt = Math.toRadians(altitude), az = Math.toRadians(azimuth), c = Math.cos(alt);
            east[i] = c * Math.sin(az);
            north[i] = c * Math.cos(az);
            up[i] = Math.sin(alt);
            start[i] = first;
        }
    }
}
