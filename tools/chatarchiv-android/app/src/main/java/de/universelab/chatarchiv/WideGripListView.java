package de.universelab.chatarchiv;

import android.content.Context;
import android.view.MotionEvent;
import android.view.ViewConfiguration;
import android.view.ViewParent;
import android.widget.ListView;

/**
 * A wider, invisible horizontal hit area alongside Android's existing fast-scroll thumb.
 *
 * Short taps are passed through to list items and their buttons. A vertical drag starting
 * in the extra strip navigates by adapter position; the original 24-dp native thumb and
 * its visual style remain unchanged.
 */
final class WideGripListView extends ListView {
    private static final int FULL_GRIP_DP = 56;
    private static final int NATIVE_THUMB_DP = 24;

    private final int fullGripPx;
    private final int nativeGripPx;
    private final int touchSlop;
    private boolean candidate;
    private boolean dragging;
    private float downY;
    private int startIndex;

    WideGripListView(Context context) {
        super(context);
        fullGripPx = Ui.dp(context, FULL_GRIP_DP);
        nativeGripPx = Ui.dp(context, NATIVE_THUMB_DP);
        touchSlop = ViewConfiguration.get(context).getScaledTouchSlop();
    }

    @Override public boolean onInterceptTouchEvent(MotionEvent event) {
        switch (event.getActionMasked()) {
            case MotionEvent.ACTION_DOWN:
                dragging = false;
                candidate = getCount() > 1
                        && WideGripMath.isExpandedGrip(
                                event.getX(), getWidth(), fullGripPx, nativeGripPx);
                if (candidate) {
                    downY = event.getY();
                    startIndex = getFirstVisiblePosition();
                    return false; // Keep ordinary item/button taps working.
                }
                return super.onInterceptTouchEvent(event);

            case MotionEvent.ACTION_MOVE:
                if (candidate && !dragging) {
                    if (Math.abs(event.getY() - downY) > touchSlop) {
                        dragging = true;
                        ViewParent parent = getParent();
                        if (parent != null) parent.requestDisallowInterceptTouchEvent(true);
                        scrollToDragPosition(event.getY());
                        return true; // Cancel the child tap and take over the drag.
                    }
                    return false;
                }
                if (dragging) return true;
                return super.onInterceptTouchEvent(event);

            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_CANCEL:
                if (dragging) return true;
                if (candidate) {
                    candidate = false;
                    return false;
                }
                return super.onInterceptTouchEvent(event);

            default:
                return candidate || dragging
                        ? dragging : super.onInterceptTouchEvent(event);
        }
    }

    @Override public boolean onTouchEvent(MotionEvent event) {
        if (dragging) {
            switch (event.getActionMasked()) {
                case MotionEvent.ACTION_MOVE:
                    scrollToDragPosition(event.getY());
                    return true;
                case MotionEvent.ACTION_UP:
                    scrollToDragPosition(event.getY());
                    // fall through
                case MotionEvent.ACTION_CANCEL:
                    candidate = false;
                    dragging = false;
                    return true;
                default:
                    return true;
            }
        }
        return super.onTouchEvent(event);
    }

    private void scrollToDragPosition(float y) {
        int index = WideGripMath.targetIndex(
                startIndex, y - downY, getHeight(), getCount());
        if (index != getFirstVisiblePosition()) {
            setSelectionFromTop(index, 0);
        }
    }
}
