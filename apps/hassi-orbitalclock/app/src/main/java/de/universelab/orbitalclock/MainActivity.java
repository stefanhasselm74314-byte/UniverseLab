package de.universelab.orbitalclock;

import android.animation.ObjectAnimator;
import android.animation.ValueAnimator;
import android.app.Activity;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Shader;
import android.graphics.SweepGradient;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.animation.LinearInterpolator;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextClock;
import android.widget.TextView;

/** Completely native, offline preview. No HTML viewer or JavaScript needed. */
public final class MainActivity extends Activity {
    private static final int NAVY = Color.rgb(5, 10, 19);
    private FrameLayout stage;
    private FrameLayout face;
    private Glint glint;
    private ObjectAnimator rotation;
    private Button tallButton, dialButton, motionButton;
    private boolean dial = false;
    private boolean lightEnabled = true;

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        getWindow().setStatusBarColor(NAVY);
        getWindow().setNavigationBarColor(Color.BLACK);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(12), dp(14), dp(12), dp(12));
        root.setBackground(new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,
                new int[] {0xff080e1a, 0xff03050a, 0xff05070d}));
        setContentView(root);

        TextView brand = text("UNIVERSELAB  ·  ORBITAL", 11, 0xff84b8fa);
        brand.setLetterSpacing(0.16f);
        root.addView(brand);

        LinearLayout heading = new LinearLayout(this);
        heading.setGravity(Gravity.CENTER_VERTICAL);
        root.addView(heading, new LinearLayout.LayoutParams(-1, dp(45)));
        TextView title = text("Hassi OrbitalClock", 19, Color.WHITE);
        title.setTypeface(null, 1);
        heading.addView(title, new LinearLayout.LayoutParams(0, -2, 1f));
        TextClock date = new TextClock(this);
        date.setFormat24Hour("EEE, dd.MM.");
        date.setFormat12Hour("EEE, dd.MM.");
        date.setTextColor(0xffb2c5dd);
        date.setTextSize(12);
        heading.addView(date);

        stage = new FrameLayout(this);
        root.addView(stage, new LinearLayout.LayoutParams(-1, 0, 1f));
        stage.addOnLayoutChangeListener((v, l, t, r, b, ol, ot, or, ob) -> fitFace());

        LinearLayout modes = new LinearLayout(this);
        modes.setGravity(Gravity.CENTER);
        modes.setPadding(0, dp(10), 0, 0);
        root.addView(modes);
        tallButton = button("Raumstation");
        dialButton = button("Zifferblatt");
        modes.addView(tallButton, new LinearLayout.LayoutParams(0, dp(48), 1f));
        modes.addView(dialButton, new LinearLayout.LayoutParams(0, dp(48), 1f));
        tallButton.setOnClickListener(v -> showFace(false));
        dialButton.setOnClickListener(v -> showFace(true));
        tallButton.setContentDescription("Hochkant-Uhr anzeigen");
        dialButton.setContentDescription("Quadratische Mechanikuhr anzeigen");

        motionButton = button("Lichtrotation: An");
        LinearLayout.LayoutParams m = new LinearLayout.LayoutParams(-2, dp(46));
        m.gravity = Gravity.CENTER;
        m.topMargin = dp(7);
        root.addView(motionButton, m);
        motionButton.setOnClickListener(v -> {
            lightEnabled = !lightEnabled;
            motionButton.setText(lightEnabled ? "Lichtrotation: An" : "Lichtrotation: Aus");
            motionButton.setContentDescription(motionButton.getText());
            setLightMotion();
        });

        TextView foot = text("Lokale Gerätezeit  ·  Offline  ·  Startbildschirm-Widgets", 11,
                0xff7c91ae);
        foot.setGravity(Gravity.CENTER);
        foot.setPadding(0, dp(8), 0, 0);
        root.addView(foot);
        showFace(false);
    }

    private void showFace(boolean nextDial) {
        dial = nextDial;
        if (rotation != null) rotation.cancel();
        stage.removeAllViews();
        face = (FrameLayout) getLayoutInflater().inflate(
                dial ? R.layout.widget_dial : R.layout.widget_tall, stage, false);
        stage.addView(face);
        glint = new Glint();
        glint.setContentDescription("Animierter Reflex auf dem Gyroskop");
        face.addView(glint);
        tallButton.setSelected(!dial);
        dialButton.setSelected(dial);
        decorateButton(tallButton, !dial);
        decorateButton(dialButton, dial);
        fitFace();
        stage.post(this::fitFace);
        setLightMotion();
    }

    private void fitFace() {
        if (stage == null || face == null || glint == null) return;
        int sw = stage.getWidth(), sh = stage.getHeight();
        if (sw <= 0 || sh <= 0) return;
        float aspect = dial ? 1f : 709f / 1210f;
        int w = Math.min(sw, Math.round(sh * aspect));
        int h = Math.min(sh, Math.round(w / aspect));
        FrameLayout.LayoutParams p = new FrameLayout.LayoutParams(w, h, Gravity.CENTER);
        face.setLayoutParams(p);
        int diameter = Math.round(w * (dial ? .44f : .45f));
        FrameLayout.LayoutParams g = new FrameLayout.LayoutParams(diameter, diameter);
        g.gravity = Gravity.LEFT | Gravity.TOP;
        g.leftMargin = (w - diameter) / 2;
        g.topMargin = Math.round(h * (dial ? .65f : .78f) - diameter / 2f);
        glint.setLayoutParams(g);
    }

    private void setLightMotion() {
        if (rotation != null) { rotation.cancel(); rotation = null; }
        if (glint == null) return;
        glint.setVisibility(lightEnabled ? View.VISIBLE : View.GONE);
        if (lightEnabled && hasWindowFocus()) {
            rotation = ObjectAnimator.ofFloat(glint, View.ROTATION, 0f, 360f);
            rotation.setDuration(11000);
            rotation.setRepeatCount(ValueAnimator.INFINITE);
            rotation.setInterpolator(new LinearInterpolator());
            rotation.start();
        }
    }

    @Override public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        setLightMotion();
    }

    @Override protected void onPause() {
        if (rotation != null) rotation.cancel();
        super.onPause();
    }

    @Override protected void onResume() {
        super.onResume();
        if (lightEnabled && hasWindowFocus()) setLightMotion();
    }

    @Override protected void onDestroy() {
        if (rotation != null) rotation.cancel();
        rotation = null;
        super.onDestroy();
    }

    private TextView text(String value, int sizeSp, int color) {
        TextView v = new TextView(this);
        v.setText(value);
        v.setTextSize(sizeSp);
        v.setTextColor(color);
        return v;
    }
    private Button button(String label) {
        Button b = new Button(this);
        b.setText(label);
        b.setTextSize(13);
        b.setAllCaps(false);
        b.setTextColor(0xffd3e4ff);
        b.setPadding(dp(12), 0, dp(12), 0);
        decorateButton(b, false);
        return b;
    }
    private void decorateButton(Button b, boolean selected) {
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(selected ? 0xff213e65 : 0xff101a2c);
        bg.setCornerRadius(dp(14));
        bg.setStroke(dp(1), selected ? 0xff71a8ff : 0xff283e5d);
        b.setBackground(bg);
    }
    private int dp(float v) { return Math.round(v * getResources().getDisplayMetrics().density); }

    /** A translucent ring highlight only; the station image itself does not rotate. */
    private final class Glint extends View {
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        Glint() { super(MainActivity.this); setLayerType(View.LAYER_TYPE_SOFTWARE, null); }
        @Override protected void onDraw(Canvas canvas) {
            super.onDraw(canvas);
            float r = Math.min(getWidth(), getHeight()) * .43f;
            float cx = getWidth() / 2f, cy = getHeight() / 2f;
            int[] colors = {0x00d3eaff, 0x009bcfff, 0x88d7f5ff, 0x009bcfff,
                    0x006ba5ff, 0x55b5ddff, 0x00d3eaff};
            paint.setShader(new SweepGradient(cx, cy, colors, null));
            paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeWidth(Math.max(2f, r * .065f));
            canvas.drawCircle(cx, cy, r, paint);
            paint.setShader(null);
        }
    }
}
