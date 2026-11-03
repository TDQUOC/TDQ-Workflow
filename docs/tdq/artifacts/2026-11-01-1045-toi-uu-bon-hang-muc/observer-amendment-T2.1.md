# T2.1 observer correction

The old observer forced PYTEST_DISABLE_PLUGIN_AUTOLOAD=1. Captured real nested Full stderr rejects -n (pytest exit 4), producing ERROR with zero executed cases and incomplete radius coverage. Failing baseline and diagnostic receipts remain unchanged.

Remove only the forced override; preserve caller environment and normal installed-plugin discovery, all audit/profile hooks, and all harness integrity checks. No production/test/config changes. This is an instrumentation correction, not certification.

Old measure_work SHA256: 3a9f446b6afd5b4d428a2b5aeb264664eb60ef41606488fa7a9fd999e8b3d4ed
New measure_work SHA256: 971850c4f9c15e87006f9c201211716e1e6d64e5115f539dad51ec2dc0615e88
Preimages: observer-preimages/T2.1/.
Diagnostic: T2.1-author/runs/T2.1-observer-diagnostic-30bd22cad021492e8b136386ac054eb8/receipt.json.
Failed invocation ca10b04d86aa4159968b68bdf0c16b27 used two invalid selectors; retained, not baseline proof.
