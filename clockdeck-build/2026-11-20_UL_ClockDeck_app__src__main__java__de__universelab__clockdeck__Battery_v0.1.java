package de.universelab.clockdeck;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.BatteryManager;
final class Battery {
    private Battery() {}
    static int percent(Context context) {
        Intent status=context.registerReceiver(null,new IntentFilter(Intent.ACTION_BATTERY_CHANGED));
        if(status==null)return -1;
        int level=status.getIntExtra(BatteryManager.EXTRA_LEVEL,-1);
        int scale=status.getIntExtra(BatteryManager.EXTRA_SCALE,-1);
        return level<0||scale<=0?-1:Math.round(100f*level/scale);
    }
}
