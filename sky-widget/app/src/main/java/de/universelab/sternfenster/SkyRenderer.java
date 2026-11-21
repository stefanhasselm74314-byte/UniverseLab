package de.universelab.sternfenster;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.Shader;
import android.graphics.Typeface;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;

/** Shared Canvas sky renderer. It owns no native surface or GPU resources. */
final class SkyRenderer {
    private static volatile PreparedStar[] preparedStars;
    private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Canvas canvas;
    private final SkyProjection projection;
    private final int width, height;
    private final float unit;
    private final List<RectF> occupied = new ArrayList<>();

    private SkyRenderer(Canvas canvas, int width, int height,
                        double azimuth, double altitude, double verticalFovDeg) {
        this.canvas = canvas;
        this.width = Math.max(1, width);
        this.height = Math.max(1, height);
        this.unit = Math.max(.55f, Math.min(4f, Math.min(width, height) / 330f));
        this.projection = new SkyProjection(this.width, this.height,
                azimuth, altitude, verticalFovDeg);
    }

    /** Widget map only; native text and controls are supplied by the host layout. */
    static Bitmap draw(Context context, int width, int height,
                       double latitude, double longitude, int direction, boolean gps) {
        int[] size = SkyProjection.bitmapSize(width, height);
        Bitmap bitmap = Bitmap.createBitmap(size[0], size[1], Bitmap.Config.RGB_565);
        paint(new Canvas(bitmap), context, size[0], size[1], latitude, longitude,
                Math.floorMod(direction, 4) * 90.0, 42.0, 105.0,
                System.currentTimeMillis(), true);
        return bitmap;
    }

    /** Direct live rendering without allocating a full-frame bitmap. */
    static void paint(Canvas canvas, Context context, int width, int height,
                      double latitude, double longitude, double azimuth,
                      double altitude, double verticalFovDeg, long now, boolean labels) {
        if (width <= 0 || height <= 0) return;
        SkyRenderer renderer = new SkyRenderer(canvas, width, height,
                azimuth, altitude, verticalFovDeg);
        int save = canvas.save();
        try {
            canvas.clipRect(0, 0, width, height);
            renderer.background();
            renderer.grid();
            renderer.stars(context, latitude, longitude, now, labels);
        } finally {
            canvas.restoreToCount(save);
        }
    }

    private void background() {
        p.setShader(new LinearGradient(0, 0, 0, height,
                0xff030a16, 0xff14283c, Shader.TileMode.CLAMP));
        canvas.drawRect(0, 0, width, height, p);
        p.setShader(null);
    }

    private void grid() {
        p.setStyle(Paint.Style.STROKE);
        p.setStrokeWidth(Math.max(.7f, unit * .55f));
        p.setColor(0x304f7790);
        for (int altitude = 30; altitude <= 60; altitude += 30) {
            gridLine(true, altitude, 0, 360);
        }
        for (int azimuth = 0; azimuth < 360; azimuth += 30) {
            gridLine(false, azimuth, 0, 90);
        }
        p.setColor(0xa46bafbf);
        p.setStrokeWidth(Math.max(1f, unit));
        gridLine(true, 0, 0, 360);
        p.setStyle(Paint.Style.FILL);
        p.setTextSize(12 * unit);
        p.setTypeface(Typeface.create("sans-serif-medium", Typeface.NORMAL));
        String[] names = {"N", "NO", "O", "SO", "S", "SW", "W", "NW"};
        for (int i = 0; i < names.length; i++) {
            if (!projection.horizontal(3.5, i * 45)) continue;
            float x = projection.x, y = projection.y;
            float textWidth = p.measureText(names[i]);
            RectF box = new RectF(x - textWidth / 2 - 3 * unit, y + p.ascent() - 2 * unit,
                    x + textWidth / 2 + 3 * unit, y + p.descent() + 2 * unit);
            if (!fits(box)) continue;
            occupied.add(box);
            drawText(names[i], x - textWidth / 2, y, 0xff9fd3dc);
        }
    }

    private void gridLine(boolean constantAltitude, int fixed, int from, int to) {
        boolean previous = false;
        float oldX = 0, oldY = 0;
        float maxStep = Math.max(24, Math.min(width, height) * .18f);
        for (int varying = from; varying <= to; varying += 2) {
            boolean visible = constantAltitude
                    ? projection.horizontal(fixed, varying)
                    : projection.horizontal(varying, fixed);
            if (visible) {
                float x = projection.x, y = projection.y;
                if (previous && Math.hypot(x - oldX, y - oldY) < maxStep) {
                    canvas.drawLine(oldX, oldY, x, y, p);
                }
                oldX = x;
                oldY = y;
            }
            previous = visible;
        }
    }

    private void stars(Context context, double latitude, double longitude,
                       long now, boolean labels) {
        PreparedStar[] catalog = catalog(context);
        if (catalog.length == 0) {
            p.setTextSize(13 * unit);
            p.setTypeface(Typeface.DEFAULT);
            drawText("Sternkatalog nicht verfügbar", 14 * unit, 28 * unit, 0xffd4dde7);
            return;
        }
        // LST and latitude are constant for this frame. Catalog trigonometry is cached.
        double phi = Math.toRadians(Math.max(-90, Math.min(90, latitude)));
        double lst = Math.toRadians(SkyMath.wrap360(SkyMath.gmstDeg(now) + longitude));
        double sinPhi = Math.sin(phi), cosPhi = Math.cos(phi);
        double sinLst = Math.sin(lst), cosLst = Math.cos(lst);
        ArrayList<Label> named = labels ? new ArrayList<>() : null;
        for (PreparedStar star : catalog) {
            double cosHour = cosLst * star.cosRa + sinLst * star.sinRa;
            double sinHour = sinLst * star.cosRa - cosLst * star.sinRa;
            double up = star.sinDec * sinPhi + star.cosDec * cosPhi * cosHour;
            if (up <= 0) continue;
            double east = -star.cosDec * sinHour;
            double north = star.sinDec * cosPhi - star.cosDec * sinPhi * cosHour;
            if (!projection.project(east, north, up)) continue;
            float x = projection.x, y = projection.y;
            if (x < -10 * unit || x > width + 10 * unit || y < -10 * unit || y > height + 10 * unit) continue;
            float radius = Math.max(.5f, Math.min(4.6f, 3.15f - .46f * star.mag)) * unit;
            p.setStyle(Paint.Style.FILL);
            p.setColor(star.color);
            if (star.mag < 1.7f) {
                p.setAlpha(24);
                canvas.drawCircle(x, y, radius * 3.5f, p);
                p.setAlpha(60);
                canvas.drawCircle(x, y, radius * 1.9f, p);
            }
            p.setAlpha(Math.max(90, Math.min(255, (int) (255 - Math.max(0, star.mag) * 23))));
            canvas.drawCircle(x, y, radius, p);
            if (labels && star.mag <= 2.15f && !star.name.isEmpty()) {
                named.add(new Label(star.name, x, y, radius));
            }
        }
        p.setAlpha(255);
        if (labels) {
            p.setTypeface(Typeface.create("sans-serif", Typeface.NORMAL));
            p.setTextSize(11.5f * unit);
            // Catalog is rendered faint-to-bright; label the brightest first.
            for (int i = named.size() - 1; i >= 0; i--) placeLabel(named.get(i));
        }
    }

    private void placeLabel(Label label) {
        float textWidth = p.measureText(label.name);
        float gap = label.radius + 4 * unit;
        float[] xs = {label.x + gap, label.x - gap - textWidth,
                label.x + gap, label.x - gap - textWidth};
        float[] ys = {label.y - 3 * unit, label.y - 3 * unit,
                label.y + 13 * unit, label.y + 13 * unit};
        for (int i = 0; i < xs.length; i++) {
            RectF box = new RectF(xs[i] - 2 * unit, ys[i] + p.ascent() - 2 * unit,
                    xs[i] + textWidth + 2 * unit, ys[i] + p.descent() + 2 * unit);
            if (!fits(box)) continue;
            boolean collision = false;
            for (RectF previous : occupied) {
                if (RectF.intersects(previous, box)) { collision = true; break; }
            }
            if (collision) continue;
            occupied.add(box);
            drawText(label.name, xs[i], ys[i], 0xffc8d8e5);
            return;
        }
    }

    private boolean fits(RectF box) {
        return box.left >= 5 * unit && box.top >= 4 * unit
                && box.right <= width - 5 * unit && box.bottom <= height - 4 * unit;
    }

    private void drawText(String text, float x, float y, int color) {
        p.setAlpha(255);
        p.setStyle(Paint.Style.STROKE);
        p.setStrokeWidth(3 * unit);
        p.setColor(0xff08101c);
        canvas.drawText(text, x, y, p);
        p.setStyle(Paint.Style.FILL);
        p.setColor(color);
        canvas.drawText(text, x, y, p);
    }

    private static PreparedStar[] catalog(Context context) {
        PreparedStar[] ready = preparedStars;
        if (ready != null) return ready;
        synchronized (SkyRenderer.class) {
            if (preparedStars != null) return preparedStars;
            List<StarCatalog.Star> source = StarCatalog.load(context);
            PreparedStar[] result = new PreparedStar[source.size()];
            for (int i = 0; i < result.length; i++) result[i] = new PreparedStar(source.get(i));
            Arrays.sort(result, Comparator.comparingDouble((PreparedStar s) -> s.mag).reversed());
            preparedStars = result;
            return result;
        }
    }

    private static final class PreparedStar {
        final double cosRa, sinRa, cosDec, sinDec;
        final float mag;
        final int color;
        final String name;
        PreparedStar(StarCatalog.Star star) {
            double ra = Math.toRadians(star.ra), dec = Math.toRadians(star.dec);
            cosRa = Math.cos(ra); sinRa = Math.sin(ra);
            cosDec = Math.cos(dec); sinDec = Math.sin(dec);
            mag = (float) star.mag;
            name = star.name;
            color = star.bv > 1.35 ? 0xffffc4a7 : star.bv > .65 ? 0xffffe6c0
                    : star.bv < -.05 ? 0xffc2ddff : 0xfff2f7ff;
        }
    }

    private static final class Label {
        final String name;
        final float x, y, radius;
        Label(String name, float x, float y, float radius) {
            this.name = name; this.x = x; this.y = y; this.radius = radius;
        }
    }
}
