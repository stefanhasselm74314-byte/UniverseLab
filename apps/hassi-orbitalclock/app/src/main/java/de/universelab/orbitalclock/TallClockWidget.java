package de.universelab.orbitalclock;

public final class TallClockWidget extends BaseClockWidget {
    @Override protected int layoutId() { return R.layout.widget_tall; }
    @Override protected float artworkAspectRatio() { return 709f / 1210f; }
}
