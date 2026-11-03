# Execution timing report

Original result: PASS; exit code: 0.
Duration quality: complete; cases: 3665.
Execution phase total: 1018.7496596999772 s; known phases: 1018.7496596999772 s.
Wall time (separate): 1030.256894399994 s (complete).

## Top20 cases
| Case ID | Phase seconds | Outcome |
|---|---|---|
| tests/test_tdq_runtime_bench.py::test_runtime_all_scenarios_use_real_processes_and_persist_proof | 23.826627500005998 | pass |
| tests/test_bench.py::ThucDoTest::test_thuc_do_ghi_du_6_hang_so_kem_so_mau_va_do_tan | 23.38865349999105 | pass |
| tests/test_tdq_runtime_bench.py::test_cache_fixture_triples_have_parity_and_real_warm_hits | 20.399885399987397 | pass |
| tests/test_tdq_runtime_bench.py::test_full_fixture_runs_six_real_jobs_and_binds_raw_evidence | 16.190553300002648 | pass |
| tests/test_tdq_runtime_bench.py::test_six_actual_serial_jobs_cannot_be_relabeled_as_parallel | 12.058456899998419 | pass |
| tests/test_tdq_runtime_bench.py::test_join_remains_joined_when_second_caller_arrives_late | 10.949377199998708 | pass |
| tests/test_archify_e2e.py::RealArchifyE2E::test_full_and_quick_native_binding_and_mutation | 10.492295600000944 | pass |
| tests/test_archify_e2e.py::RealArchifyE2E::test_master_html_freshness_and_refresh | 10.474948399991263 | pass |
| tests/test_runtime_contracts.py::test_fresh_off_rollback_revokes_warm_receipt_and_preserves_timing_accounting | 9.901905400001851 | pass |
| tests/test_bench.py::ThucDoTest::test_repo_that_khong_moc_nhanh_hay_worktree_nao | 8.20553839999775 | pass |
| tests/test_bench.py::ThucDoTest::test_thuc_do_khong_de_lai_worktree_hay_thu_muc_tam | 7.4698481000014 | pass |
| tests/test_tdq_eval.py::DungNhanhTest::test_hai_worktree_dung_ngon_ngu_khac_nhau_o_skill | 6.902041100001952 | pass |
| tests/test_tdq_eval.py::DungNhanhTest::test_dung_hai_worktree_co_du_plugin_json | 6.8105844000019715 | pass |
| tests/test_tdq_eval.py::DungNhanhTest::test_dich_nam_trong_repo_nay_thi_bi_tu_choi | 6.455670500006818 | pass |
| tests/test_tdq_runner_integration.py::RunnerIntegration::test_external_runner_implementation_change_invalidates_receipt | 6.124338499997975 | pass |
| tests/test_tdq_runner_integration.py::RunnerIntegration::test_real_reuse_fresh_and_ledger_execution_counts | 5.658210200002941 | pass |
| tests/test_tdq_eval.py::DungNhanhTest::test_fixture_git_khong_dung_registry_repo_goc | 5.638512599987735 | pass |
| tests/test_team_mode.py::GitTest::test_hop_ba_nhanh_roi_nhau_du_ba_commit | 5.576913000004424 | pass |
| tests/test_tdq_eval.py::DungNhanhTest::test_hai_nhanh_khai_dung_hai_commit_can_so | 5.45888310000737 | pass |
| tests/test_tdq_runner_integration.py::RunnerIntegration::test_post_execution_proof_errors_retain_observed_failures | 5.390954599992256 | pass |

## Top20 modules
| Module | Phase seconds | Cases |
|---|---|---|
| tests/test_tdq_test.py | 105.15902850002749 | 97 |
| tests/test_tdq_runtime_bench.py | 87.79250979996868 | 16 |
| tests/test_team_mode.py | 87.14330029998382 | 154 |
| tests/test_tdq_runner_integration.py | 70.87439039997844 | 33 |
| tests/test_tdq_test_receipt.py | 60.03445460003422 | 109 |
| tests/test_bench.py | 44.989774699963164 | 53 |
| tests/test_team_chong_conflict.py | 38.140072499962116 | 41 |
| tests/test_tdq_eval.py | 34.56125459994655 | 116 |
| tests/test_claude_export.py | 34.06951340001251 | 64 |
| tests/test_tu_khoi_tao.py | 23.927718599996297 | 38 |
| tests/test_archify_e2e.py | 20.967243999992206 | 2 |
| tests/test_stop_gate.py | 18.697124700025597 | 108 |
| tests/test_context_hooks.py | 16.5827229000206 | 45 |
| tests/test_codex_cli.py | 16.52976720000879 | 40 |
| tests/test_phase1_logging.py | 15.968292500001553 | 9 |
| tests/test_archify_finish.py | 14.727782500012836 | 17 |
| tests/test_uu_tien_song_song.py | 13.385361799999373 | 13 |
| tests/test_tdq_test_manifest.py | 12.425633699982427 | 17 |
| tests/test_runtime_contracts.py | 12.181202600011602 | 16 |
| tests/test_phase1_contract.py | 11.196663299990178 | 6 |

## Quality and limits
Only execution setup/call/teardown phases are summed; subtests are not added again.
Incomplete cases/modules are unranked. Known phase time is not suite wall time or CPU time.
Unranked cases: 0; modules: 0. Full quality details are in JSON.

## Provenance
Input SHA256: ec60b7816e0f7efc06f5b4784e3fd3f5c3ea0adf604ddbbeaac8cff700e7d7d2.
[Input result](final-result.json)
