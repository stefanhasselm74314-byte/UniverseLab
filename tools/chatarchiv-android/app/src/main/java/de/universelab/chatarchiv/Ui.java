package de.universelab.chatarchiv;

import android.content.Context;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowInsets;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;

final class Ui {
    static final int BACKGROUND = Color.rgb(11, 17, 26);
    static final int SURFACE = Color.rgb(25, 35, 48);
    static final int TEXT = Color.rgb(237, 244, 252);
    static final int MUTED = Color.rgb(165, 185, 205);
    static final int ACCENT = Color.rgb(129, 197, 255);

    private Ui() { }

    static int dp(Context context, float value) {
        return (int) (value * context.getResources().getDisplayMetrics().density + 0.5f);
    }

    static LinearLayout column(Context context, int paddingDp) {
        LinearLayout root = new LinearLayout(context);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(context, paddingDp), dp(context, paddingDp),
                dp(context, paddingDp), dp(context, paddingDp));
        root.setBackgroundColor(BACKGROUND);
        return root;
    }

    /**
     * Prevent actionable content from sitting behind Android's status/navigation bars.
     * Capture the original padding once; new inset dispatches must not accumulate it.
     */
    static void applySystemBarInsets(LinearLayout root) {
        final int baseLeft = root.getPaddingLeft();
        final int baseTop = root.getPaddingTop();
        final int baseRight = root.getPaddingRight();
        final int baseBottom = root.getPaddingBottom();
        root.setOnApplyWindowInsetsListener((view, windowInsets) -> {
            int left;
            int top;
            int right;
            int bottom;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                android.graphics.Insets safe = windowInsets.getInsets(
                        WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
                left = safe.left;
                top = safe.top;
                right = safe.right;
                bottom = safe.bottom;
            } else {
                left = windowInsets.getSystemWindowInsetLeft();
                top = windowInsets.getSystemWindowInsetTop();
                right = windowInsets.getSystemWindowInsetRight();
                bottom = windowInsets.getSystemWindowInsetBottom();
            }
            view.setPadding(baseLeft + Math.max(0, left), baseTop + Math.max(0, top),
                    baseRight + Math.max(0, right), baseBottom + Math.max(0, bottom));
            return windowInsets;
        });
        root.post(root::requestApplyInsets);
    }

    /** Permanent, inset and larger native fast-scroller for message/list navigation. */
    static void configurePersistentFastScroll(ListView list) {
        list.setScrollBarStyle(View.SCROLLBARS_INSIDE_INSET);
        list.setFastScrollStyle(R.style.ChatArchivFastScroll);
        list.setFastScrollEnabled(true);
        list.setFastScrollAlwaysVisible(true);
        list.setVerticalScrollBarEnabled(true);
        list.setScrollbarFadingEnabled(false);
    }

    static LinearLayout row(Context context) {
        LinearLayout row = new LinearLayout(context);
        row.setOrientation(LinearLayout.HORIZONTAL);
        return row;
    }

    static TextView text(Context context, String value, int sp, boolean bold) {
        TextView text = new TextView(context);
        text.setText(value);
        text.setTextColor(TEXT);
        text.setTextSize(sp);
        if (bold) text.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        text.setPadding(0, dp(context, 5), 0, dp(context, 5));
        return text;
    }

    static Button button(Context context, String value) {
        Button button = new Button(context);
        button.setText(value);
        button.setAllCaps(false);
        button.setTextColor(TEXT);
        button.setTextSize(13);
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(SURFACE);
        bg.setCornerRadius(dp(context, 9));
        bg.setStroke(dp(context, 1), ACCENT);
        button.setBackground(bg);
        button.setMinHeight(dp(context, 45));
        button.setMinimumHeight(dp(context, 45));
        return button;
    }

    static LinearLayout.LayoutParams weight(float weight) {
        return new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, weight);
    }

    static LinearLayout.LayoutParams fillRemaining() {
        return new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1);
    }

    static void addGap(Context context, LinearLayout parent, int dp) {
        View gap = new View(context);
        parent.addView(gap, new LinearLayout.LayoutParams(1, Ui.dp(context, dp)));
    }
}
