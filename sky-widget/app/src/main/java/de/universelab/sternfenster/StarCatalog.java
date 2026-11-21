package de.universelab.sternfenster;

import android.content.Context;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

/** Public-domain Yale Bright Star Catalogue, 5th revised edition (via isene/starmap). */
final class StarCatalog {
    static final class Star {
        final double ra, dec, mag, bv;
        final String name;
        Star(double ra, double dec, double mag, double bv, String name) {
            this.ra=ra; this.dec=dec; this.mag=mag; this.bv=bv; this.name=name;
        }
    }
    private static List<Star> cached;
    static synchronized List<Star> load(Context context) {
        if (cached != null) return cached;
        ArrayList<Star> result = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(
                context.getAssets().open("stars.csv"), StandardCharsets.UTF_8))) {
            String line;
            while ((line=reader.readLine()) != null) {
                if (line.isEmpty() || line.charAt(0)=='#') continue;
                String[] parts = line.split(",", -1);
                if (parts.length < 9) continue;
                try {
                    double mag = Double.parseDouble(parts[2]);
                    if (mag > 6.3) continue;
                    double bv = parts[3].isEmpty()?0:Double.parseDouble(parts[3]);
                    result.add(new Star(Double.parseDouble(parts[0]), Double.parseDouble(parts[1]),
                            mag, bv, parts[8].trim()));
                } catch (NumberFormatException ignored) { }
            }
        } catch (Exception e) { android.util.Log.e("Sternfenster", "Sternkatalog konnte nicht geladen werden", e); }
        cached = result;
        return cached;
    }
}
