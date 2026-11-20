package de.universelab.orbitalclock;

import android.animation.ObjectAnimator;
import android.animation.ValueAnimator;
import android.app.Activity;
import android.appwidget.AppWidgetManager;
import android.content.ComponentName;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Insets;
import android.graphics.Paint;
import android.graphics.SweepGradient;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.WindowInsets;
import android.view.animation.LinearInterpolator;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextClock;
import android.widget.TextView;
import android.widget.Toast;

/** Native, offline orbital-clock preview and a launcher widget picker. */
public final class MainActivity extends Activity {
    private static final int NAVY = Color.rgb(5, 10, 19);
    private static final float TALL_RATIO = 709f / 1210f;

    private LinearLayout root;
    private FrameLayout stage;
    private FrameLayout face;
    private Glint glint;
    private ObjectAnimator rotation;
    private TextView brand;
    private LinearLayout heading;
    private LinearLayout modeRow;
    private LinearLayout toolRow;
    private TextView footer;
    private Button tallButton, dialButton, motionButton, addWidgetButton;
    private boolean dial = false;
    private boolean lightEnabled = true;

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        if (saved != null) {
            dial = saved.getBoolean("dial", false);
            lightEnabled = saved.getBoolean("light", true);
        }
        getWindow().setStatusBarColor(NAVY);
        getWindow().setNavigationBarColor(Color.BLACK);
        if (Build.VERSION.SDK_INT >= 29) getWindow().setNavigationBarContrastEnforced(false);
        // Android 15+ enforces edge-to-edge. We deliberately handle system insets.
        if (Build.VERSION.SDK_INT >= 30) getWindow().setDecorFitsSystemWindows(false);

        root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(14), dp(12), dp(14), dp(12));
        root.setBackground(new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,
                new int[] {0xff080e1a, 0xff03050a, 0xff05070d}));
        setContentView(root);
        if (Build.VERSION.SDK_INT >= 30) {
            root.setOnApplyWindowInsetsListener((v, insets) -> {
                Insets bars = insets.getInsets(WindowInsets.Type.systemBars()
                        | WindowInsets.Type.displayCutout());
                // Don't double-count bars when the OS changes the content window.
                int left = dp(14) + bars.left;
                int top = dp(12) + bars.top;
                int right = dp(14) + bars.right;
                int bottom = dp(14) + bars.bottom;
                if (root.getPaddingLeft() != left || root.getPaddingTop() != top
                        || root.getPaddingRight() != right || root.getPaddingBottom() != bottom) {
                    root.setPadding(left, top, right, bottom);
                }
                return insets;
            });
            root.requestApplyInsets();
        }

        brand = text("UNIVERSELAB  ·  ORBITAL", 11, 0xff91bbf2);
        brand.setLetterSpacing(0.13f);
        root.addView(brand);

        heading = new LinearLayout(this);
        heading.setGravity(Gravity.CENTER_VERTICAL);
        root.addView(heading, new LinearLayout.LayoutParams(-1, dp(44)));
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
        root.addView(stage, new LinearLayout.LayoutParams(-1, dp(190)));
        stage.addOnLayoutChangeListener((v, l, t, r, b, ol, ot, or_, ob) -> fitFace());

        modeRow = new LinearLayout(this);
        modeRow.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams mp = new LinearLayout.LayoutParams(-1, dp(48));
        mp.topMargin = dp(10);
        root.addView(modeRow, mp);
        tallButton = button("Raumstation");
        dialButton = button("Zifferblatt");
        modeRow.addView(tallButton, new LinearLayout.LayoutParams(0, -1, 1f));
        LinearLayout.LayoutParams dialParams = new LinearLayout.LayoutParams(0, -1, 1f);
        dialParams.leftMargin = dp(8);
        modeRow.addView(dialButton, dialParams);
        tallButton.setOnClickListener(v -> showFace(false));
        dialButton.setOnClickListener(v -> showFace(true));
        tallButton.setContentDescription("Raumstations-Uhr anzeigen");
        dialButton.setContentDescription("Mechanisches Zifferblatt anzeigen");

        toolRow = new LinearLayout(this);
        toolRow.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams tp = new LinearLayout.LayoutParams(-1, dp(44));
        tp.topMargin = dp(8);
        root.addView(toolRow, tp);
        motionButton = button(lightEnabled ? "Licht: An" : "Licht: Aus");
        toolRow.addView(motionButton, new LinearLayout.LayoutParams(0, -1, 1f));
        motionButton.setOnClickListener(v -> {
            lightEnabled = !lightEnabled;
            motionButton.setText(lightEnabled ? "Licht: An" : "Licht: Aus");
            setLightMotion();
        });
        addWidgetButton = button("Widget hinzufügen");
        LinearLayout.LayoutParams ap = new LinearLayout.LayoutParams(0, -1, 1.35f);
        ap.leftMargin = dp(8);
        toolRow.addView(addWidgetButton, ap);
        addWidgetButton.setOnClickListener(v -> requestWidgetPin());

        footer = text("v0.5 · Systemzeit · Offline · Transparente Widgets", 11, 0xff879cb7);
        footer.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams fp = new LinearLayout.LayoutParams(-1, dp(27));
        fp.topMargin = dp(4);
        root.addView(footer, fp);
        // The flex spacer is deliberately last. Controls stay near the artwork,
        // instead of being stranded at the very bottom in square-dial mode.
        root.addView(new View(this), new LinearLayout.LayoutParams(-1, 0, 1f));
        root.addOnLayoutChangeListener((v, l, t, r, b, ol, ot, or_, ob) -> arrangeStage());
        showFace(dial);
    }

    private void requestWidgetPin() {
        AppWidgetManager wm = AppWidgetManager.getInstance(this);
        if (Build.VERSION.SDK_INT >= 26 && wm.isRequestPinAppWidgetSupported()) {
            ComponentName provider = new ComponentName(this,
                    dial ? DialClockWidget.class : TallClockWidget.class);
            boolean requested = wm.requestPinAppWidget(provider, null, null);
            if (requested) {
                Toast.makeText(this, "Widget im Startbildschirm bestätigen", Toast.LENGTH_LONG).show();
                return;
            }
        }
        Toast.makeText(this,
                "Startbildschirm lange drücken → Widgets → Hassi OrbitalClock",
                Toast.LENGTH_LONG).show();
    }

    private void showFace(boolean nextDial) {
        dial = nextDial;
        if (rotation != null) { rotation.cancel(); rotation = null; }
        stage.removeAllViews();
        face = (FrameLayout) getLayoutInflater().inflate(
                dial ? R.layout.widget_dial : R.layout.widget_tall, stage, false);
        stage.addView(face);
        glint = new Glint();
        glint.setContentDescription("Optionaler Reflex über dem Gyroskop");
        face.addView(glint);
        decorateButton(tallButton, !dial);
        decorateButton(dialButton, dial);
        arrangeStage();
        stage.post(() -> { arrangeStage(); fitFace(); });
        setLightMotion();
    }

    private void arrangeStage() {
        if (root == null || stage == null || root.getHeight() <= 0) return;
        int avail = root.getHeight() - root.getPaddingTop() - root.getPaddingBottom()
                - brand.getHeight() - heading.getHeight()
                - modeRow.getHeight() - toolRow.getHeight() - footer.getHeight()
                - dp(10 + 8 + 4);
        avail = Math.max(dp(130), avail);
        int width = stage.getWidth();
        if (width <= 0) width = root.getWidth() - root.getPaddingLeft() - root.getPaddingRight();
        if (width <= 0) return;
        float aspect = dial ? 1f : TALL_RATIO;
        int desired = Math.max(dp(130), Math.min(avail, Math.round(width / aspect)));
        LinearLayout.LayoutParams p = (LinearLayout.LayoutParams) stage.getLayoutParams();
        if (p.height != desired) {
            p.height = desired;
            stage.setLayoutParams(p);
        }
        fitFace();
    }

    private void fitFace() {
        if (stage == null || face == null || glint == null) return;
        int sw = stage.getWidth(), sh = stage.getHeight();
        if (sw <= 0 || sh <= 0) return;
        float aspect = dial ? 1f : TALL_RATIO;
        int w = Math.min(sw, Math.round(sh * aspect));
        int h = Math.min(sh, Math.round(w / aspect));
        FrameLayout.LayoutParams p = new FrameLayout.LayoutParams(w, h,
                Gravity.TOP | Gravity.CENTER_HORIZONTAL);
        face.setLayoutParams(p);
        // The app preview already fits the outer face's aspect ratio. Let the
        // nested artwork occupy that entire face; widget sizing is handled
        // independently by BaseClockWidget using RemoteViews.
        View artwork = face.findViewById(R.id.widget_art);
        if (artwork != null) {
            artwork.setLayoutParams(new FrameLayout.LayoutParams(
                    -1, -1, Gravity.CENTER));
        }
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

    @Override protected void onSaveInstanceState(Bundle outState) {
        outState.putBoolean("dial", dial);
        outState.putBoolean("light", lightEnabled);
        super.onSaveInstanceState(outState);
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
        b.setPadding(dp(6), 0, dp(6), 0);
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

    /** Subtle circular highlight; source artwork itself remains static. */
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
