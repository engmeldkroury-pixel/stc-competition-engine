#!/usr/bin/env python3
"""Normalize authenticated source locally, audit gaps and compare paired exits.

The input stays private/temporary. Outputs contain only validated research
fields. This script does not access any network or write the production ledger.
"""
from __future__ import annotations
import argparse
import hashlib
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from app.outcome_attribution import iso, utc
from app.outcome_dataset import prepare_dataset, coverage_audit, digest
from app.exit_policy_audit import audit_exit_policies


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--horizon-bars',type=int,default=32)
    p.add_argument('--cost-r',type=float,default=.02)
    args = p.parse_args()
    try:
        source=json.loads(args.input.read_text())
        meta=source.get('source_snapshot',{})
        cutoff=utc(meta['captured_at']) if 'captured_at' in meta else datetime.now(timezone.utc)
        dataset=prepare_dataset(source,as_of=cutoff)
        coverage=coverage_audit(dataset['bars'])
        report=audit_exit_policies(dataset,horizon_bars=args.horizon_bars,cost_r=args.cost_r)
        paths={
            'normalized-dataset.json':dataset,
            'coverage-audit.json':coverage,
            'paired-exit-audit.json':report,
        }
        # Export only known harmless metadata rather than an arbitrary source dict.
        allowed=('source','matching_rows','max_id','min_selected_id','row_limit','selected_rows',
                 'projection_failures','truncated','captured_at','database_writes','scope','all_event_status_counts')
        manifest=dict(schema='stc-r9-manifest-v1',code_sha=os.environ.get('GITHUB_SHA'),
                      dataset_sha256=dataset['dataset_sha256'], as_of=iso(cutoff),
                      source_snapshot={k:meta[k] for k in allowed if k in meta},
                      raw_source_exported=False, account_data_exported=False, execution='none',
                      normalized_fields_exported=True, research_only=True,
                      file_sha256={name:hashlib.sha256((json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()).hexdigest() for name,value in paths.items()})
        paths['manifest.json']=manifest
        args.output_dir.mkdir(parents=True,exist_ok=True)
        for name,value in paths.items():
            (args.output_dir/name).write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
        brief=dict(as_of=dataset['as_of'],source_rows=dataset['source_rows'],
                   normalized_bars=len(dataset['bars']),hypotheses=report['hypotheses'],
                   provenance=report['provenance_counts'],quarantine=dataset['quarantine_counts'],
                   status_counts=report['status_counts'],
                   selected_n=report['nonoverlapping_cohort']['selected_n'],
                   common_valued_n=report['nonoverlapping_cohort']['common_valued_n'],
                   unknown_path_n=report['nonoverlapping_cohort']['unknown_path_n'],
                   dataset_sha256=dataset['dataset_sha256'],live_promotion_allowed=False)
        print('STC_R9_AUDIT='+json.dumps(brief,sort_keys=True))
        return 0
    except Exception as exc:
        print('R9 audit failed; raw source/error details withheld: '+type(exc).__name__,file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
