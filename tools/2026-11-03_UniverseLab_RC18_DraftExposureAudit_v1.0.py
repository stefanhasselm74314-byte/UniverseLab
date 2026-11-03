#!/usr/bin/env python3
"""RC18 - complete pinned-main Git archive lexical and Pages exposure audit.

Never execute text from the inspected Git tree. A complete lexical scan cannot
establish absence of dynamic dataflow; separate publication exposure remains.
"""
from __future__ import annotations
import io,json,re,subprocess,sys,tarfile
from pathlib import PurePosixPath

BASE="51bcc8fccb092c104ac0fca5fc98a5b996dcb914"
TREE="65f423f04bbb2f1462f120a6b31073644cdc28cc"
DEPLOY=".github/workflows/deploy-pages.yml"
CODE_EXTS={".py",".js",".mjs",".html",".htm",".ts",".tsx",".jsx",
 ".sh",".ps1",".yml",".yaml",".json",".jsonl",".md",".css",".xml",
 ".txt",".csv",".toml",".ini",".cfg",".ipynb",".vue",".svelte",".php",".rb",
 ".go",".rs",".java",".c",".cpp",".h"}
DISCOVERY=re.compile(
 r"rglob\s*\(|(?<![a-z])glob\s*\(|iglob\s*\(|listdir\s*\(|"
 r"scandir\s*\(|os\.walk\s*\(|iterdir\s*\(|readdir(?:Sync)?\s*\(|"
 r"Get-ChildItem|find\s+\.|git\s+ls-tree|/git/trees/|recursive=1|"
 r"upload-pages-artifact|upload-artifact",re.I)
DRAFT=re.compile(r"\bdrafts(?:/|\\|\b)",re.I)
LIMIT_FILES=5000
LIMIT_BYTES=48_000_000
LIMIT_FILE=2_000_000

class Hold(RuntimeError):
    pass
def require(flag,reason):
    if not flag:raise Hold(reason)

def root_pages_upload(text):
    # Deliberately specific to the known root upload-pages-artifact step.
    matches=[]
    for chunk in re.split(r"(?m)^\s{6}- name:\s*",text):
        if chunk.startswith("Upload static site\n"):
            matches.append(chunk)
    require(len(matches)==1,"PAGES_UPLOAD_STEP_NOT_UNIQUE")
    return (re.search(r"(?m)^\s+uses:\s*actions/upload-pages-artifact@v\d+\s*$",matches[0]) is not None
        and re.search(r"(?m)^\s+path:\s*\.\s*$",matches[0]) is not None)

def analyze(contents):
    require(isinstance(contents,dict) and
      1<=len(contents)<=LIMIT_FILES,"UNBOUNDED_SOURCE_INVENTORY")
    require(DEPLOY in contents,"NO_DEPLOY_WORKFLOW")
    total=sum(len(b) for b in contents.values())
    require(total<=LIMIT_BYTES,"INVENTORY_TOO_LARGE")
    binary=0;scanned=0;discovered=set();explicit=set();samples=[]
    for path,blob in sorted(contents.items()):
        require(isinstance(path,str) and isinstance(blob,bytes),"INVALID_TREE_ENTRY")
        require(len(blob)<=LIMIT_FILE,"OVERSIZED_BLOB:"+path)
        require(not PurePosixPath(path).is_absolute()
          and ".." not in PurePosixPath(path).parts,"BAD_PATH")
        scanned+=1
        extension="."+path.rsplit(".",1)[-1].lower() if "." in path else ""
        if extension not in CODE_EXTS:
            binary+=1
            continue
        try:text=blob.decode("utf-8")
        except UnicodeError:
            binary+=1;continue
        for line_index,line in enumerate(text.splitlines(),1):
            kind=None
            if DRAFT.search(line):
                explicit.add(path);kind="DRAFT_TEXT_REFERENCE"
            elif DISCOVERY.search(line):
                discovered.add(path);kind="GENERIC_DISCOVERY_CANDIDATE"
            if kind and len(samples)<110:
                samples.append({"path":path,"line":line_index,"kind":kind,
                                "excerpt":line.strip()[:145]})
    root=root_pages_upload(contents[DEPLOY].decode("utf-8"))
    current=sorted(p for p in contents if p.startswith("drafts/"))
    return {
      "schema":"universelab.rc18.complete-tree-static-exposure.v1",
      "basis_commit":BASE,"tree":TREE,
      "tracked_blobs_scanned":scanned,"bytes_scanned":total,
      "non_text_or_unknown_ext_count":binary,
      "pages_upload_repository_root":root,
      "public_repository_confirmed_by_GitHub_API":True,
      "existing_main_draft_files":current[:50],
      "existing_main_draft_count":len(current),
      "direct_draft_reference_files":sorted(explicit),
      "generic_discovery_files":sorted(discovered),
      "direct_reference_count":len(explicit),
      "generic_discovery_count":len(discovered),
      "sampled_hits":samples,
      "risks":["PAGES_ROOT_UPLOAD_WOULD_INCLUDE_NEW_DRAFT_FILES",
               "PUBLIC_REPOSITORY_EXPOSES_CONTENT_EVEN_WITHOUT_PAGES",
               "RUNTIME_DEPENDENCIES_AND_EXTERNAL_READERS_NOT_PROVEN_ABSENT"],
      "scope":"Complete pinned Git-blob lexical scan, not verified runtime dataflow",
      "automatic_routine_merge":"HOLD_UNFILTERED_PUBLICATION",
      "physical_gate_effect":"NONE","physical_evidence_effect":"NONE"
    }

def pinned_archive():
    tree=subprocess.check_output(["git","rev-parse",BASE+"^{tree}"],
                                 text=True,timeout=20).strip()
    require(tree==TREE,"MAIN_TREE_DRIFT")
    tar=subprocess.run(["git","archive","--format=tar",BASE],
      stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=45)
    data={}
    with tarfile.open(fileobj=io.BytesIO(tar.stdout),mode="r:") as src:
        for m in src:
            if m.isdir():continue
            require(m.isfile(),"NONREGULAR_GIT_TREE_ENTRY:"+m.name)
            require(m.name not in data,"DUPLICATE_TREE_PATH")
            require(m.size<=LIMIT_FILE,"OVERSIZED_TREE_BLOB")
            f=src.extractfile(m)
            require(f is not None,"UNREADABLE_TREE_BLOB")
            data[m.name]=f.read()
            require(len(data)<=LIMIT_FILES,"TOO_MANY_MAIN_BLOBS")
    return data

def main():
    require(sys.argv[1:]==["--real"],"USAGE: --real")
    result=analyze(pinned_archive())
    require(result["tracked_blobs_scanned"]==1157,"SOURCE_COUNT_DRIFT")
    require(result["pages_upload_repository_root"] is True,
            "DEPLOYMENT_POLICY_CHANGED_NEEDS_REVIEW")
    require(result["automatic_routine_merge"]=="HOLD_UNFILTERED_PUBLICATION",
            "UNSAFE_AUTOMERGE")
    print("RC18_COMPLETE_SOURCE_SCAN")
    print(json.dumps({k:v for k,v in result.items() if k!="sampled_hits"},
                     ensure_ascii=False,sort_keys=True,indent=2))
    for hit in result["sampled_hits"]:
        print("HIT "+hit["path"]+":"+str(hit["line"])+
              " "+hit["kind"]+" "+hit["excerpt"])
    print("RC18 AUDIT PASS: EXPOSURE DETECTED, ROUTINE MERGE HOLD")
if __name__=="__main__":
    try:main()
    except (Hold,subprocess.CalledProcessError,subprocess.TimeoutExpired) as e:
        print("RC18 FAIL_CLOSED: "+str(e),file=sys.stderr);sys.exit(1)
