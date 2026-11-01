"""Build approved working-tree architecture artifacts as a normal user, not a test receipt."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location('_master_policy', HERE / 'safe_run_telemetry.py')
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
sys.path.insert(0, str(ROOT / 'scripts'))
from tdq_test_process import OwnedProcessJob

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dispatch-reply', type=Path)
    args = parser.parse_args()
    if policy.legacy.elevated() and args.dispatch_reply is None:
        with patch.object(policy.legacy, '__file__', str(Path(__file__).resolve())):
            return policy.legacy.normal_dispatch([], HERE / 'master-build', 180)
    if policy.legacy.elevated():
        raise RuntimeError('Normal-user architecture build required')
    output = HERE / 'master-build'
    output.mkdir(exist_ok=True)
    audit = []
    before = policy._snapshot(Path.home(), audit)
    source = policy.legacy.source_snapshot(ROOT)
    environment = {'ARCHIFY_CHROME': 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
                   'TDQ_KHONG_CHAM_MAY': '1', 'TDQ_KHOI_TAO_NEN': '0'}
    with OwnedProcessJob(ROOT, timeout_seconds=180, env=environment) as job:
        result = job.run([sys.executable, '-X', 'utf8', str(ROOT / 'scripts/tdq_archify.py'),
            'sync-master', '--model', str(ROOT / 'docs/tdq/models/master.model.json'),
            '--project', str(ROOT), '--out', str(ROOT / 'docs/architecture')], phase='master-build')
    after = policy._snapshot(Path.home(), audit)
    final = policy.legacy.source_snapshot(ROOT)
    changed = sorted(name for name in source['files'].keys() | final['files'].keys()
                     if source['files'].get(name) != final['files'].get(name))
    unexpected = [name for name in changed if not name.startswith('docs/architecture/')]
    good = (result['exit_code'] == 0 and result['reason'] == 'exited'
            and result['cleanup_complete'] and before == after and not unexpected)
    (output / 'stdout.txt').write_text(result.pop('stdout'), encoding='utf-8')
    (output / 'stderr.txt').write_text(result.pop('stderr'), encoding='utf-8')
    record = {'kind': 'source-artifact-build; not test certification',
              'status': 'BUILT' if good else 'FAILED', 'elevated': False,
              'config_policy': policy.POLICY, 'config_before': before, 'config_after': after,
              'config_raw': audit, 'process': result, 'changed_output_paths': changed,
              'unexpected_source_changes': unexpected, 'builder_sha256': policy.legacy.file_hash(__file__)}
    policy.legacy.write_json(output / 'build.json', record)
    code = 0 if good else 1
    if args.dispatch_reply:
        policy.legacy.write_json(args.dispatch_reply, {'exit_code': code, 'elevated': False,
            'operation': 'architecture-build', 'record': str(output / 'build.json')})
    print(json.dumps({'status': record['status'], 'record': str(output / 'build.json')}))
    return code

if __name__ == '__main__':
    raise SystemExit(main())
