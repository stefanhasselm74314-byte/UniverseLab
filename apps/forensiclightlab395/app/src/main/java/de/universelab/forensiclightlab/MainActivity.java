package de.universelab.forensiclightlab;

import android.Manifest;
import android.app.Activity;
import android.content.ContentValues;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.MediaStore;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import java.io.ByteArrayInputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

/** Offline WebView wrapper. The only permitted origin is appassets.androidplatform.net. */
public final class MainActivity extends Activity {
    private static final String HOST = "appassets.androidplatform.net";
    private static final int CAMERA_PERMISSION = 10;
    private static final int SELECT_IMAGE = 20;
    private WebView web;
    private PermissionRequest pendingCamera;
    private ValueCallback<Uri[]> pendingFiles;
    private final Handler main = new Handler(Looper.getMainLooper());

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(Color.rgb(17,17,23));
        getWindow().setNavigationBarColor(Color.rgb(17,17,23));
        web = new WebView(this);
        web.setBackgroundColor(Color.rgb(17,17,23));
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowContentAccess(true); // Only user-selected images; network resources remain denied.
        s.setAllowFileAccess(false);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        s.setMediaPlaybackRequiresUserGesture(false);
        web.setOverScrollMode(WebView.OVER_SCROLL_NEVER);
        web.addJavascriptInterface(new ExportBridge(), "Android");
        web.setWebViewClient(new WebViewClient() {
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                if ("https".equals(uri.getScheme()) && HOST.equals(uri.getHost())) {
                    String path=uri.getPath();
                    if ("/assets/index.html".equals(path)) {
                        try { return new WebResourceResponse("text/html", "utf-8", getAssets().open("index.html")); }
                        catch(Exception e){ return forbidden(); }
                    }
                }
                return forbidden(); // No network requests leave this local app
            }
            private WebResourceResponse forbidden() {
                WebResourceResponse response = new WebResourceResponse("text/plain", "utf-8", new ByteArrayInputStream("Blocked".getBytes(StandardCharsets.UTF_8)));
                response.setStatusCodeAndReasonPhrase(403, "Forbidden");
                return response;
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override public void onPermissionRequest(PermissionRequest request) {
                main.post(() -> {
                    boolean camera = false;
                    for(String resource : request.getResources()) {
                        if (PermissionRequest.RESOURCE_VIDEO_CAPTURE.equals(resource)) camera = true;
                        else { request.deny(); return; }
                    }
                    if (!camera) { request.deny(); return; }
                    if(checkSelfPermission(Manifest.permission.CAMERA)==PackageManager.PERMISSION_GRANTED)
                        request.grant(new String[]{PermissionRequest.RESOURCE_VIDEO_CAPTURE});
                    else {
                        pendingCamera=request;
                        requestPermissions(new String[]{Manifest.permission.CAMERA}, CAMERA_PERMISSION);
                    }
                });
            }
            @Override public void onPermissionRequestCanceled(PermissionRequest request) {
                if(pendingCamera==request) pendingCamera=null;
            }
            @Override public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if(pendingFiles!=null) pendingFiles.onReceiveValue(null);
                pendingFiles=callback;
                try {
                    Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
                    intent.addCategory(Intent.CATEGORY_OPENABLE);
                    intent.setType("image/*");
                    startActivityForResult(Intent.createChooser(intent, "Bild auswählen"), SELECT_IMAGE);
                    return true;
                } catch(Exception ex) {
                    pendingFiles.onReceiveValue(null);pendingFiles=null;return false;
                }
            }
        });
        setContentView(web);
        web.loadUrl("https://"+HOST+"/assets/index.html");
    }
    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(requestCode, permissions, results);
        if(requestCode==CAMERA_PERMISSION && pendingCamera!=null) {
            if(results.length>0 && results[0]==PackageManager.PERMISSION_GRANTED)
                pendingCamera.grant(new String[]{PermissionRequest.RESOURCE_VIDEO_CAPTURE});
            else pendingCamera.deny();
            pendingCamera=null;
        }
    }
    @Override protected void onActivityResult(int requestCode,int resultCode,Intent data) {
        super.onActivityResult(requestCode,resultCode,data);
        if(requestCode==SELECT_IMAGE && pendingFiles!=null) {
            Uri[] value = resultCode==RESULT_OK && data!=null && data.getData()!=null ? new Uri[]{data.getData()} : null;
            pendingFiles.onReceiveValue(value);pendingFiles=null;
        }
    }
    private final class ExportBridge {
        @JavascriptInterface public void savePng(String filename,String dataUrl) {
            try {
                if(!dataUrl.startsWith("data:image/png;base64,")) throw new SecurityException("Only PNG accepted");
                byte[] bytes = Base64.getDecoder().decode(dataUrl.substring("data:image/png;base64,".length()));
                if(bytes.length>32_000_000) throw new SecurityException("Image exceeds 32 MB");
                String safe=filename.replaceAll("[^a-zA-Z0-9_\-.]","_");
                if(!safe.toLowerCase(java.util.Locale.ROOT).endsWith(".png"))safe+=".png";
                ContentValues values=new ContentValues();
                values.put(MediaStore.Images.Media.DISPLAY_NAME,safe);
                values.put(MediaStore.Images.Media.MIME_TYPE,"image/png");
                values.put(MediaStore.Images.Media.RELATIVE_PATH,"Pictures/ForensicLightLab");
                values.put(MediaStore.Images.Media.IS_PENDING,1);
                Uri uri=getContentResolver().insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI,values);
                if(uri==null) throw new Exception("Could not create media image");
                try(OutputStream out=getContentResolver().openOutputStream(uri)) {
                    if(out==null) throw new Exception("No output stream");
                    out.write(bytes);
                }
                values.clear();values.put(MediaStore.Images.Media.IS_PENDING,0);
                getContentResolver().update(uri,values,null,null);
                main.post(()->Toast.makeText(MainActivity.this,"Gespeichert: Bilder / ForensicLightLab",Toast.LENGTH_LONG).show());
            } catch(Exception ex) {
                main.post(()->Toast.makeText(MainActivity.this,"Speichern fehlgeschlagen: "+ex.getMessage(),Toast.LENGTH_LONG).show());
            }
        }
    }
    @Override public void onBackPressed() {
        if(web.canGoBack()) web.goBack(); else super.onBackPressed();
    }
    @Override protected void onDestroy() {
        if(pendingCamera!=null)pendingCamera.deny();
        if(pendingFiles!=null)pendingFiles.onReceiveValue(null);
        web.destroy();super.onDestroy();
    }
}
