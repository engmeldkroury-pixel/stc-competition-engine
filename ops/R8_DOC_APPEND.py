"""One-time append-only documentation writer; never part of live STC runtime."""
import csv, hashlib, io, json
from pathlib import Path
import sys

ALLOWED = {'PROJECT_STATE.md','NEXT_TASK.md','DECISIONS.md','BATCH_REGISTER.csv','TEST_REGISTER.csv','RISK_REGISTER.csv','docs/STC_ADAPTIVE_RESEARCH_MASTER_LEDGER.md','docs/R8_OUTCOME_ATTRIBUTION_2026-09-27.md','docs/R8_EVIDENCE_CHECKPOINT_2026-09-27.md','CURRENT_CHECKPOINT.md'}
def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def apply(root, payload):
    changes={};manifest={}
    for name,entry in payload['files'].items():
        if name not in ALLOWED:raise ValueError('unapproved_path')
        path=root/name;old=path.read_bytes() if path.exists() else b''
        marker=payload['checkpoint_id']
        if marker in old.decode('utf-8'):raise ValueError('already_applied')
        if name.endswith('.csv'):
            width=len(next(csv.reader(io.StringIO(old.decode('utf-8')))))
            buf=io.StringIO();writer=csv.writer(buf,lineterminator='\n')
            for row in entry['rows']:
                if len(row)!=width:raise ValueError('csv_width_mismatch')
                writer.writerow(row)
            new=old+(b'' if not old or old.endswith(b'\n') else b'\n')+buf.getvalue().encode()
        else:
            prefix=entry.get('prepend','').encode();suffix=entry.get('append','').encode()
            new=prefix+old+suffix
        if old and old not in new:raise ValueError('history_would_be_lost')
        changes[path]=new;manifest[name]={'before_blob':blob(old) if old else None,'after_blob':blob(new),'before_bytes':len(old),'after_bytes':len(new)}
    for path,data in changes.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    return manifest
if __name__=='__main__':
    root=Path(sys.argv[1]);payload=json.loads(Path(sys.argv[2]).read_text())
    result={'checkpoint_id':payload['checkpoint_id'],'code_ci_run':payload['code_ci_run'],'merged_code_sha':payload['merged_code_sha'],'files':apply(root,payload)}
    result['files']['docs/R8_HISTORY_RESULTS_2026-09-27.md']={'after_blob':blob((root/'docs/R8_HISTORY_RESULTS_2026-09-27.md').read_bytes())}
    (root/'ops/R8_CHECKPOINT_BLOBS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))
