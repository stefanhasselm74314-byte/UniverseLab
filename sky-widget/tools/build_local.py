#!/usr/bin/env python3
"""Offline build using an installed Android SDK. Never creates a disposable signing key."""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

parser=argparse.ArgumentParser()
parser.add_argument("--sdk",required=True,type=Path)
parser.add_argument("--signing-info",type=Path)
parser.add_argument("--output",type=Path)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
gradle=(root/"app/build.gradle").read_text(encoding="utf-8")
version_code=re.search(r"\bversionCode\s+(\d+)",gradle).group(1)
version_name=re.search(r"\bversionName\s+['\"]([^'\"]+)['\"]",gradle).group(1)
build=root/"build-manual"
if build.exists(): shutil.rmtree(build)
for name in ("gen","classes","dex"): (build/name).mkdir(parents=True,exist_ok=True)
tools=args.sdk/"build-tools"/"36.0.0"
android=args.sdk/"platforms"/"android-36"/"android.jar"
manifest=root/"app/src/main/AndroidManifest.xml"
ET.register_namespace("android","http://schemas.android.com/apk/res/android")
xml=ET.parse(manifest)
xml.getroot().set("package","de.universelab.sternfenster")
xml.write(build/"AndroidManifest.xml",encoding="utf-8",xml_declaration=True)

def run(command,env=None):
    result=subprocess.run([str(s) for s in command],text=True,capture_output=True,env=env)
    if result.returncode:
        print(result.stdout,file=sys.stderr);print(result.stderr,file=sys.stderr)
        raise SystemExit(result.returncode)
    if result.stderr: print(result.stderr,file=sys.stderr)
    return result.stdout

run([tools/"aapt2","compile","--dir",root/"app/src/main/res","-o",build/"resources.zip"])
run([tools/"aapt2","link","-o",build/"resources.apk","-I",android,
     "--manifest",build/"AndroidManifest.xml","--java",build/"gen",
     "--min-sdk-version","26","--target-sdk-version","36","--version-code",version_code,
     "--version-name",version_name,"-A",root/"app/src/main/assets",build/"resources.zip"])
sources=sorted((root/"app/src/main/java").rglob("*.java"))+sorted((build/"gen").rglob("*.java"))
javac=shutil.which("javac")
compiler=[javac] if javac else [shutil.which("java"),"-m","jdk.compiler/com.sun.tools.javac.Main"]
run(compiler+["-source","17","-target","17","-encoding","UTF-8","-classpath",android,"-d",build/"classes"]+sources)
with zipfile.ZipFile(build/"classes.jar","w",zipfile.ZIP_DEFLATED) as archive:
    for path in sorted((build/"classes").rglob("*.class")): archive.write(path,path.relative_to(build/"classes"))
run([tools/"d8","--release","--min-api","26","--lib",android,"--output",build/"dex",build/"classes.jar"])
shutil.copyfile(build/"resources.apk",build/"unsigned.apk")
with zipfile.ZipFile(build/"unsigned.apk","a",zipfile.ZIP_DEFLATED) as archive:
    for dex in sorted((build/"dex").glob("*.dex")): archive.write(dex,dex.name)
run([tools/"zipalign","-f","-p","4",build/"unsigned.apk",build/"aligned.apk"])
output=args.output or build/f"Sternfenster_Android_v{version_name}.apk"
output.parent.mkdir(parents=True,exist_ok=True)
if args.signing_info:
    signing=json.loads(args.signing_info.read_text())
    key=Path(signing["keystore"])
    if not key.is_absolute():key=args.signing_info.parent/key
    environment=os.environ.copy()
    environment["STERNFENSTER_SIGN_PASS"]=signing["password"]
    run([tools/"apksigner","sign","--ks",key,"--ks-key-alias",signing["alias"],
         "--ks-pass","env:STERNFENSTER_SIGN_PASS","--key-pass","env:STERNFENSTER_SIGN_PASS",
         "--v1-signing-enabled","true","--v2-signing-enabled","true",
         "--v3-signing-enabled","true","--out",output,build/"aligned.apk"],environment)
    verification=run([tools/"apksigner","verify","--verbose","--print-certs",output])
    print(verification)
else:
    output=output.with_name(output.stem+"-UNSIGNED.apk")
    shutil.copyfile(build/"aligned.apk",output)
    print("Unsigned build only; sign with the retained private release key before installation.")
with zipfile.ZipFile(output) as archive:
    assert archive.testzip() is None
    assert "classes.dex" in archive.namelist()
    assert "assets/stars.csv" in archive.namelist()
print(json.dumps({"output":str(output),"bytes":output.stat().st_size,
                  "sha256":hashlib.sha256(output.read_bytes()).hexdigest()},ensure_ascii=False))
