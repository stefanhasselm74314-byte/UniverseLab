package de.universelab.chatarchiv;

import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.StateListDrawable;
import android.os.Build;
import android.view.Gravity;
import android.view.Window;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowInsets;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.RadioButton;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;

final class Ui {
    // Pure grayscale palette: every RGB component is equal (no blue tint).
    // High-contrast neutral grayscale throughout the app (R=G=B).
    static final int BACKGROUND = Color.rgb(18, 18, 18); // #121212
    static final int SURFACE = Color.rgb(48, 48, 48);    // #303030
    static final int TEXT = Color.rgb(250, 250, 250);       // #FAFAFA
    static final int MUTED = Color.rgb(210, 210, 210);      // #D2D2D2
    static final int ACCENT = Color.rgb(230, 230, 230);     // #E6E6E6
    static final int BORDER = Color.rgb(190, 190, 190);     // #BEBEBE

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
        // More visible, consistently grayscale borders on dark cards.
        bg.setStroke(dp(context, 1.6f), BORDER);
        button.setBackground(bg);
        button.setMinHeight(dp(context, 45));
        button.setMinimumHeight(dp(context, 45));
        return button;
    }

    /** A clearly outlined panel; callers keep their original content and click behavior. */
    static void outlineSurface(Context context, View panel) {
        GradientDrawable background = new GradientDrawable();
        background.setColor(SURFACE);
        background.setCornerRadius(dp(context, 7));
        background.setStroke(dp(context, 1.2f), BORDER);
        panel.setBackground(background);
    }

    /**
     * Native AlertDialog behavior with a consistent monochrome outer frame and
     * independently outlined, press-highlighted, scrollable menu rows.
     */
    static AlertDialog showFramedMenu(Context context, String title, String[] options,
                                     String cancelText, DialogInterface.OnClickListener action) {
        return showFramedOptions(context, title, options, -1, cancelText, action, null);
    }

    static AlertDialog showFramedMenu(Context context, String title, String[] options,
                                     String cancelText, DialogInterface.OnClickListener action,
                                     DialogInterface.OnClickListener cancelAction) {
        return showFramedOptions(context, title, options, -1, cancelText, action, cancelAction);
    }

    /** Same framed layout, but renders the currently selected radio choice. */
    static AlertDialog showFramedChoices(Context context, String title, String[] options,
                                        int currentChoice, String cancelText,
                                        DialogInterface.OnClickListener action) {
        return showFramedOptions(context, title, options, currentChoice, cancelText, action, null);
    }

    private static AlertDialog showFramedOptions(Context context, String title, String[] options,
            int currentChoice, String cancelText, DialogInterface.OnClickListener action,
            DialogInterface.OnClickListener cancelAction) {
        ArrayAdapter<String> adapter = new ArrayAdapter<String>(
                context, android.R.layout.simple_list_item_1, options) {
            @Override public View getView(int position, View recycled, ViewGroup parent) {
                boolean choice = currentChoice >= 0;
                TextView label = choice ? new RadioButton(context) : new TextView(context);
                label.setText(options[position]);
                label.setTextColor(TEXT);
                label.setTextSize(16);
                label.setGravity(Gravity.CENTER_VERTICAL);
                label.setMinHeight(dp(context, 52));
                label.setPadding(dp(context, 14), dp(context, 10),
                        dp(context, 14), dp(context, 10));
                label.setBackground(menuRowBackground(context));
                if (choice) {
                    RadioButton radio = (RadioButton) label;
                    radio.setChecked(position == currentChoice);
                    radio.setButtonTintList(ColorStateList.valueOf(ACCENT));
                    radio.setFocusable(false);
                    radio.setClickable(false);
                }
                return label;
            }
        };
        AlertDialog dialog = new AlertDialog.Builder(context)
                .setTitle(title)
                .setAdapter(adapter, action)
                .setNegativeButton(cancelText, cancelAction)
                .create();
        dialog.show();
        Window window = dialog.getWindow();
        if (window != null) {
            GradientDrawable frame = new GradientDrawable();
            frame.setColor(SURFACE);
            frame.setCornerRadius(dp(context, 12));
            frame.setStroke(dp(context, 2), ACCENT);
            window.setBackgroundDrawable(frame);
            int screenWidth = context.getResources().getDisplayMetrics().widthPixels;
            int screenHeight = context.getResources().getDisplayMetrics().heightPixels;
            int width = Math.min((int) (screenWidth * 0.92f), dp(context, 560));
            int height = options.length > 6
                    ? (int) (screenHeight * 0.78f)
                    : ViewGroup.LayoutParams.WRAP_CONTENT;
            window.setLayout(width, height);
        }
        ListView list = dialog.getListView();
        if (list != null) {
            list.setDivider(null);
            list.setDividerHeight(dp(context, 5));
            list.setPadding(dp(context, 12), dp(context, 6),
                    dp(context, 12), dp(context, 6));
            list.setClipToPadding(false);
        }
        return dialog;
    }

    private static StateListDrawable menuRowBackground(Context context) {
        GradientDrawable normal = new GradientDrawable();
        normal.setColor(Color.rgb(54, 54, 54));
        normal.setCornerRadius(dp(context, 7));
        normal.setStroke(dp(context, 1.2f), BORDER);

        GradientDrawable active = new GradientDrawable();
        active.setColor(Color.rgb(82, 82, 82));
        active.setCornerRadius(dp(context, 7));
        active.setStroke(dp(context, 1.8f), ACCENT);

        StateListDrawable states = new StateListDrawable();
        states.addState(new int[]{android.R.attr.state_pressed}, active);
        states.addState(new int[]{android.R.attr.state_focused}, active);
        states.addState(new int[]{}, normal);
        return states;
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
