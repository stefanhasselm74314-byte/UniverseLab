#!/usr/bin/env python3
"""Pinned PR #248/#257 compatibility DIAGNOSIS, never release authorization.

--self-test uses small synthetic inputs. --integration needs real complete Git
history and creates detached temporary worktrees only. An expected rejection is
not a repaired gate. The single-digest counterfactual is restored before exit;
no registry, manifest, branch, ref or remote is updated in the source checkout.
"""
from __future__ import annotations
import argparse
import copy
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

BASE = '312e767628f003494a51edf685cf679469e35f13'
UI = '6a98bc3b9e3f6601ad13ec00f5d70c735fabfb18'
BINDING = '133fbc59b98ae88fead859f36abcf944e9f01ded'
SELF = 'tests/2026-10-05_test_UniverseLab_StatusProvenanceCompatibility_v1.0.py'
WORKFLOW = '.github/workflows/2026-10-05_UniverseLab_StatusProvenanceCompatibility_QA_v1.0.yml'
REGISTRY = 'registry/2026-10-03_UniverseLab_ClaimProvenanceBinding_v1.0.json'
CANDIDATES = 'registry/2026-09-03_UniverseLab_PublicScientificClaimLexicalCandidates_v0.1.json'
VALIDATOR = 'tools/2026-10-03_validate_UniverseLab_ClaimProvenanceBinding_v1.0.py'
UI_TEST = 'tests/2026-09-26_test_UniverseLab_StatusShell_v1.0.py'
PAGES = {'research-status.html', 'research-status-en.html'}
BINDING_BLOBS = {REGISTRY:'737742cdac4a689425c1c44f47c1621280016085', VALIDATOR:'5b9a2b9cc67d39b3cd5151874cb7f3cd74f7fd71'}
PAGE_BLOBS = {
    'research-status.html': ('3fff2ef8b763e1bb26a79c2279c51592c009b39f','d51f570992ad8e1a2c25e91959a14ac5f02ce7a4'),
    'research-status-en.html': ('ff61b2091014ea9945e21a5948702c02d0b164a9','563ae09a8111602247d3505f14cd5069addfc4c0'),
}
CHECKS = [
    VALIDATOR,
    'tests/2026-10-03_test_UniverseLab_ClaimProvenanceBinding_v1.0.py',
    'tests/2026-09-03_test_UniverseLab_BandVB_HighClaimAdjudication_v1.0.py',
    'tests/2026-09-04_test_UniverseLab_BandVB_MediumCompletionAdjudication_v1.0.py',
    'tests/2026-09-04_test_UniverseLab_BandVC_StateFreshnessClosure_v1.0.py',
    'tools/2026-09-03_generate_UniverseLab_SitemapLastmod_v1.0.py --check',
    'tests/2026-09-03_test_UniverseLab_BandVB_SitemapLastmod_v1.0.py',
]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)+'\n', encoding='utf-8')


def medium_digest(rows):
    medium = sorted((r for r in rows if r['preliminary_risk_class']=='MEDIUM'), key=lambda r:r['claim_id'])
    return sha(json.dumps(medium, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode())


def source_only_delta(before, after, sources):
    """One-to-one, all-field equality except truthfully rebound whole-file digest."""
    def index(rows):
        result = {r['claim_id']:r for r in rows}
        require(len(result)==len(rows), 'DUPLICATE_ID')
        return result
    old, new = index(before), index(after)
    require(old.keys()==new.keys(), 'ID_SET_CHANGED')
    require([r['claim_id'] for r in before]==[r['claim_id'] for r in after], 'ROW_ORDER_CHANGED')
    changed = []
    for key, row in old.items():
        current = new[key]
        require(row.keys()==current.keys(), 'FIELD_SET_CHANGED')
        fields = {k for k in row if row[k]!=current[k]}
        if not fields:
            continue
        require(fields=={'source_sha256'}, 'NON_DIGEST_FIELD_CHANGED')
        path=row['path']
        require(path in sources, 'UNDECLARED_SOURCE')
        left, right=sources[path]
        require(row['source_sha256']==sha(left) and current['source_sha256']==sha(right), 'SOURCE_BYTES_MISMATCH')
        changed.append({'claim_id':key,'path':path,'risk':row['preliminary_risk_class'],
                        'before_sha256':row['source_sha256'],'after_sha256':current['source_sha256']})
    require(changed, 'NO_SOURCE_DELTA')
    return changed


def proposed_record(record, before, after, sources):
    changed=source_only_delta(before,after,sources)
    require(record['live_medium_sha256']==medium_digest(before), 'WRONG_REVIEWED_BASE')
    proposed=copy.deepcopy(record)
    proposed['live_medium_sha256']=medium_digest(after)
    require({k for k in record if record[k]!=proposed[k]}=={'live_medium_sha256'}, 'COUNTERFACTUAL_SCOPE_CHANGED')
    return proposed, changed


class Controls(unittest.TestCase):
    def setUp(self):
        self.sources={'s.html':(b'old source', b'new source')}
        self.before=[{'claim_id':'one','path':'s.html','source_sha256':sha(b'old source'),
                      'preliminary_risk_class':'MEDIUM','text':'unchanged','source_line':4,'tag':'p','region':'main','explicit_status':'OPEN'}]
        self.after=copy.deepcopy(self.before);self.after[0]['source_sha256']=sha(b'new source')
        self.record={'live_medium_sha256':medium_digest(self.before),'scope':'frozen','physical_gate_effect':'NONE','bindings':[{'id':'frozen'}]}
    def test_exact_delta(self):
        result, changed=proposed_record(self.record,self.before,self.after,self.sources)
        self.assertEqual(len(changed),1);self.assertEqual(result['scope'],'frozen');self.assertEqual(result['bindings'],self.record['bindings'])
    def test_input_not_modified(self):
        original=copy.deepcopy(self.record);proposed_record(self.record,self.before,self.after,self.sources);self.assertEqual(self.record,original)
    def test_each_semantic_field(self):
        for key in ('text','path','source_line','tag','region','explicit_status','preliminary_risk_class'):
            changed=copy.deepcopy(self.after);changed[0][key]='MUTATED'
            with self.subTest(field=key),self.assertRaises(ValueError):source_only_delta(self.before,changed,self.sources)
    def test_extra_field(self):
        self.after[0]['approved']=True
        with self.assertRaisesRegex(ValueError,'FIELD_SET'):source_only_delta(self.before,self.after,self.sources)
    def test_missing_field(self):
        del self.after[0]['tag']
        with self.assertRaises(ValueError):source_only_delta(self.before,self.after,self.sources)
    def test_new_id(self):
        self.after[0]['claim_id']='other'
        with self.assertRaisesRegex(ValueError,'ID_SET'):source_only_delta(self.before,self.after,self.sources)
    def test_duplicate_before(self):
        with self.assertRaisesRegex(ValueError,'DUPLICATE'):source_only_delta(self.before*2,self.after,self.sources)
    def test_duplicate_after(self):
        with self.assertRaisesRegex(ValueError,'DUPLICATE'):source_only_delta(self.before,self.after*2,self.sources)
    def test_missing_row(self):
        with self.assertRaisesRegex(ValueError,'ID_SET'):source_only_delta(self.before,[],self.sources)
    def test_wrong_old_bytes(self):
        with self.assertRaisesRegex(ValueError,'SOURCE_BYTES'):source_only_delta(self.before,self.after,{'s.html':(b'wrong',b'new source')})
    def test_wrong_new_bytes(self):
        with self.assertRaisesRegex(ValueError,'SOURCE_BYTES'):source_only_delta(self.before,self.after,{'s.html':(b'old source',b'wrong')})
    def test_unknown_source(self):
        with self.assertRaisesRegex(ValueError,'UNDECLARED'):source_only_delta(self.before,self.after,{})
    def test_wrong_digest_base(self):
        self.record['live_medium_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'WRONG_REVIEWED'):proposed_record(self.record,self.before,self.after,self.sources)
    def test_no_change(self):
        with self.assertRaisesRegex(ValueError,'NO_SOURCE'):source_only_delta(self.before,self.before,self.sources)
    def test_row_order(self):
        row=copy.deepcopy(self.before[0]);row['claim_id']='two';before=self.before+[row]
        after=[copy.deepcopy(row),self.after[0]]
        with self.assertRaisesRegex(ValueError,'ROW_ORDER'):source_only_delta(before,after,self.sources)


def command(root, args, *, env=None, input_bytes=None):
    return subprocess.run(args, cwd=root, input=input_bytes, capture_output=True, timeout=180,
                          env={**os.environ, **(env or {})})


def git(root,*args,input_bytes=None,env=None):
    result=command(root,['git',*args],env=env,input_bytes=input_bytes)
    require(result.returncode==0, 'GIT_FAILURE: '+' '.join(args)+'\n'+result.stderr.decode(errors='replace'))
    return result.stdout


def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
    return mod


def integration(repo,out):
    repo=repo.resolve();out=out.resolve();out.mkdir(parents=True,exist_ok=True)
    report={'physical_gate_effect':'NONE','physical_evidence_effect':'NONE','release_approval':False,
            'proposal_status':'PROPOSED_NOT_APPROVED','main':BASE,'ui_input':UI,'binding_input':BINDING,
            'scope':'PINNED_COMPATIBILITY_DIAGNOSIS_NOT_SOURCE_ADOPTION','checks':[]}
    tracked_before=git(repo,'diff','HEAD','--').decode()
    def run(root, label, argline, expected=None):
        proc=command(root,[sys.executable,*argline.split()])
        text=proc.stdout.decode(errors='replace')+proc.stderr.decode(errors='replace')
        (out/(label+'.log')).write_text(text,encoding='utf-8')
        entry={'name':label,'command':argline,'returncode':proc.returncode,'expected_failure':expected}
        report['checks'].append(entry);write_json(out/'report.json',report)
        if expected:
            require(proc.returncode!=0 and expected in text,'EXPECTED_REJECTION_NOT_OBSERVED: '+label)
        else:require(proc.returncode==0,'CHECK_FAILED: '+label)
    try:
        report['diagnostic_source_sha']=git(repo,'rev-parse','HEAD').decode().strip()
        require(git(repo,'rev-parse','--is-shallow-repository').strip()==b'false','FULL_HISTORY_REQUIRED')
        require(git(repo,'rev-parse','refs/remotes/origin/main').decode().strip()==BASE,'MAIN_ADVANCED_REFRESH_PINS')
        for value in (BASE,UI,BINDING):git(repo,'cat-file','-e',value+'^{commit}')
        require(git(repo,'merge-base',UI,BINDING).decode().strip()==BASE,'MERGE_BASE_CHANGED')
        audit_paths=set(git(repo,'diff','--name-only',UI,'HEAD').decode().splitlines())
        require(audit_paths=={SELF,WORKFLOW},'DIAGNOSTIC_HEAD_HAS_UNREVIEWED_SOURCE_DELTA')
        left=set(git(repo,'diff','--name-only',BASE,UI).decode().splitlines())
        right=set(git(repo,'diff','--name-only',BASE,BINDING).decode().splitlines())
        require(len(left)==9 and len(right)==13 and left&right=={'sitemap.xml'},'SOURCE_SCOPE_CHANGED')
        report['overlap']=sorted(left&right);report['union_path_count']=len(left|right)
        merged=command(repo,['git','merge-tree','--write-tree',BINDING,UI])
        (out/'merge-tree.log').write_bytes(merged.stdout+merged.stderr)
        require(merged.returncode==0,'MERGE_CONFLICT_NO_AUTOMATIC_RESOLUTION')
        tree=merged.stdout.decode().splitlines()[0].strip();require(re.fullmatch('[0-9a-f]{40}',tree),'BAD_MERGE_TREE')
        # A local object provides real parent history to git-log based validators;
        # no named ref is moved and this diagnostic commit is never pushed.
        env={'GIT_AUTHOR_NAME':'WEB50 local diagnostic','GIT_AUTHOR_EMAIL':'web50@invalid.example',
             'GIT_COMMITTER_NAME':'WEB50 local diagnostic','GIT_COMMITTER_EMAIL':'web50@invalid.example',
             'GIT_AUTHOR_DATE':'2026-10-05T00:00:00+00:00','GIT_COMMITTER_DATE':'2026-10-05T00:00:00+00:00'}
        local_commit=git(repo,'commit-tree',tree,'-p',BINDING,'-p',UI,
                         input_bytes=b'LOCAL DIAGNOSTIC ONLY - NOT APPROVED OR PUSHED\n',env=env).decode().strip()
        report.update(combined_tree=tree,local_diagnostic_commit=local_commit)
        with tempfile.TemporaryDirectory(prefix='web50-compat-') as temp:
            basework=Path(temp)/'binding';combined=Path(temp)/'combined'
            paths=[]
            try:
                for path,commit in ((basework,BINDING),(combined,local_commit)):
                    git(repo,'worktree','add','--detach',str(path),commit);paths.append(path)
                for path,expected in BINDING_BLOBS.items():
                    require(blob((basework/path).read_bytes())==expected,'PINNED_BINDING_BLOB_CHANGED')
                    require((basework/path).read_bytes()==(combined/path).read_bytes(),'UNEXPECTED_BINDING_CODE_CHANGE')
                sources={}
                for path,(oldblob,newblob) in PAGE_BLOBS.items():
                    old=(basework/path).read_bytes();new=(combined/path).read_bytes()
                    require(blob(old)==oldblob and blob(new)==newblob,'PINNED_PAGE_BYTES_CHANGED')
                    sources[path]=(old,new)
                guard=load_module(combined/UI_TEST,'web50_pinned_ui_guard')
                for path in PAGES:guard.check_source(path,(combined/path).read_text(encoding='utf-8'))
                for i,check in enumerate(CHECKS):run(basework,f'base-{i:02}',check)
                run(combined,'unamended-combination',VALIDATOR,'REVIEWED_MEDIUM_CORPUS_CHANGED')
                before=json.loads((basework/CANDIDATES).read_text())['candidates']
                after=json.loads((combined/CANDIDATES).read_text())['candidates']
                registry_bytes=(combined/REGISTRY).read_bytes();record=json.loads(registry_bytes)
                counterfactual,changed=proposed_record(record,before,after,sources)
                require(len(before)==len(after)==993 and len(changed)==65,'CORPUS_DELTA_CHANGED')
                require(Counter(r['path'] for r in changed)==Counter({'research-status.html':31,'research-status-en.html':34}),'PAGE_CANDIDATE_DELTA_CHANGED')
                mediums=[r for r in changed if r['risk']=='MEDIUM'];require(len(mediums)==7,'MEDIUM_DELTA_CHANGED')
                report['source_delta']={'total':65,'medium':7,'ids_or_classifications_changed':0,
                    'before_medium_digest':record['live_medium_sha256'],
                    'after_medium_digest':counterfactual['live_medium_sha256'],'records':changed}
                report['unamended_result']='REJECTED_AS_EXPECTED'
                # Keep the entire frozen record intact, including scope/date/bindings.
                proposal={k:report[k] for k in ('physical_gate_effect','physical_evidence_effect','release_approval','proposal_status','main','ui_input','binding_input')}
                proposal.update(source_delta=report['source_delta'],registry_source_blob=blob(registry_bytes),
                    required_disposition='REVIEWED_APPEND_ONLY_SOURCE_BINDING_SUCCESSOR; DO_NOT_EDIT_OR_AUTOREBASE_V1_IN_PLACE',
                    counterfactual_only_field='live_medium_sha256')
                write_json(out/'source-binding-proposal.json',proposal)
                protected={p:(combined/p).read_bytes() for p in record['protected_sources']}
                manifest=(combined/'project-manifest.json').read_bytes()
                try:
                    write_json(combined/REGISTRY,counterfactual)
                    for i,check in enumerate(CHECKS):run(combined,f'COUNTERFACTUAL-{i:02}',check)
                    run(combined,'COUNTERFACTUAL-ui-source-guards',UI_TEST)
                    require((combined/'project-manifest.json').read_bytes()==manifest,'MANIFEST_CHANGED')
                    require(all((combined/p).read_bytes()==data for p,data in protected.items()),'PROTECTED_HISTORY_CHANGED')
                    report['counterfactual_result']='VALIDATORS_PASS_IN_SCRATCH_ONLY_NOT_ADOPTED'
                finally:
                    (combined/REGISTRY).write_bytes(registry_bytes)
                run(combined,'restored-unamended-combination',VALIDATOR,'REVIEWED_MEDIUM_CORPUS_CHANGED')
                require((combined/REGISTRY).read_bytes()==registry_bytes,'RESTORATION_FAILED')
                report['registry_restored']=True
            finally:
                for path in reversed(paths):git(repo,'worktree','remove','--force',str(path))
        report['diagnostic_result']='DIAGNOSIS_CONFIRMED_NOT_RELEASED'
    except Exception as exc:
        report['diagnostic_result']='INCONCLUSIVE_FAIL_CLOSED';report['error']=str(exc)
        raise
    finally:
        report['source_checkout_unchanged']=git(repo,'diff','HEAD','--').decode()==tracked_before
        write_json(out/'report.json',report)
    require(report['source_checkout_unchanged'],'SOURCE_CHECKOUT_CHANGED')
    print(json.dumps({k:v for k,v in report.items() if k not in ('checks','source_delta')},indent=2))


def main():
    parser=argparse.ArgumentParser();mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--self-test',action='store_true');mode.add_argument('--integration',action='store_true')
    parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path,default=Path('web50-provenance-compatibility-report'))
    args=parser.parse_args()
    if args.self_test:
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls))
        return 0 if result.wasSuccessful() else 1
    integration(args.repo,args.output);return 0

if __name__=='__main__':sys.exit(main())
