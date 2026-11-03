# Execution timing report

Original result: PASS; exit code: 0.
Duration quality: complete; cases: 3602.
Execution phase total: 1107.6038851980702 s; known phases: 1107.6038851980702 s.
Wall time (separate): 1117.6745853999746 s (complete).

## Top20 cases
| Case ID | Phase seconds | Outcome |
|---|---|---|
| tests/test_codex_cli.py::KiemSongThatTest::test_treo_thi_qua_han_va_van_don_home | 30.156144100008532 | pass |
| tests/test_bench.py::LogCodexTest::test_hai_mau_thi_tu_choi_va_noi_con_thieu_may_mau | 24.07871640002122 | pass |
| tests/test_bench.py::LogCodexTest::test_ba_mau_thi_ghi_duoc_hang_so_codex | 23.565378400031477 | pass |
| tests/test_bench.py::LogCodexTest::test_khong_dua_log_thi_file_do_khong_co_khoa_codex | 23.130245900014415 | pass |
| tests/test_bench.py::ThucDoTest::test_thuc_do_ghi_du_6_hang_so_kem_so_mau_va_do_tan | 22.731163699994795 | pass |
| tests/test_tdq_runtime_bench.py::test_runtime_all_scenarios_use_real_processes_and_persist_proof | 22.36315900000045 | pass |
| tests/test_tdq_runtime_bench.py::test_cache_fixture_triples_have_parity_and_real_warm_hits | 18.42351440008497 | pass |
| tests/test_bench.py::ThucDoTest::test_mau_that_sai_khuon_thi_loi_ro_rang | 17.39125929994043 | pass |
| tests/test_tdq_runtime_bench.py::test_full_fixture_runs_six_real_jobs_and_binds_raw_evidence | 14.884139500034507 | pass |
| tests/test_tdq_runtime_bench.py::test_six_actual_serial_jobs_cannot_be_relabeled_as_parallel | 11.115653899963945 | pass |
| tests/test_tdq_runtime_bench.py::test_join_remains_joined_when_second_caller_arrives_late | 10.37897730001714 | pass |
| tests/test_archify_e2e.py::RealArchifyE2E::test_full_and_quick_native_binding_and_mutation | 9.549783999973442 | pass |
| tests/test_archify_e2e.py::RealArchifyE2E::test_master_html_freshness_and_refresh | 9.269022699911147 | pass |
| tests/test_runtime_contracts.py::test_fresh_off_rollback_revokes_warm_receipt_and_preserves_timing_accounting | 9.052660300105345 | pass |
| tests/test_bench.py::ThucDoTest::test_repo_that_khong_moc_nhanh_hay_worktree_nao | 7.832329700002447 | pass |
| tests/test_bench.py::ThucDoTest::test_thuc_do_khong_de_lai_worktree_hay_thu_muc_tam | 7.783118900086265 | pass |
| tests/test_bench.py::VongFix1Test::test_mau_that_ghi_ro_la_nhap_tay | 7.748062499973457 | pass |
| tests/test_bench.py::ThucDoTest::test_mau_that_thay_han_so_stub_va_danh_dau_nguon | 7.718768000020646 | pass |
| tests/test_tdq_runner_integration.py::RunnerIntegration::test_external_runner_implementation_change_invalidates_receipt | 5.643687099975068 | pass |
| tests/test_tdq_test.py::So::test_so_json_dem_va_ngan_sach | 5.545218000013847 | pass |

## Top20 modules
| Module | Phase seconds | Cases |
|---|---|---|
| tests/test_bench.py | 150.46970170043642 | 46 |
| tests/test_tdq_test.py | 114.77809130004607 | 97 |
| tests/test_team_mode.py | 88.02106289978838 | 154 |
| tests/test_tdq_runtime_bench.py | 81.40720520011382 | 16 |
| tests/test_tdq_runner_integration.py | 57.36867999995593 | 24 |
| tests/test_tdq_test_receipt.py | 52.59690609987592 | 109 |
| tests/test_team_chong_conflict.py | 39.96919089992298 | 41 |
| tests/test_codex_cli.py | 35.96368020022055 | 32 |
| tests/test_claude_export.py | 35.146316299331374 | 64 |
| tests/test_tdq_eval.py | 25.216823900060263 | 116 |
| tests/test_tu_khoi_tao.py | 23.874169400252867 | 38 |
| tests/test_archify_e2e.py | 18.81880669988459 | 2 |
| tests/test_stop_gate.py | 18.795554799842648 | 108 |
| tests/test_context_hooks.py | 16.42507720005233 | 45 |
| tests/test_phase1_logging.py | 15.432002000045031 | 9 |
| tests/test_archify_finish.py | 13.848242199746892 | 17 |
| tests/test_tdq_test_manifest.py | 12.66896489955252 | 17 |
| tests/test_uu_tien_song_song.py | 12.573601800075267 | 13 |
| tests/test_phase1_contract.py | 11.226954899961129 | 6 |
| tests/test_runtime_contracts.py | 11.205569600104354 | 16 |

## Quality and limits
Only execution setup/call/teardown phases are summed; subtests are not added again.
Incomplete cases/modules are unranked. Known phase time is not suite wall time or CPU time.
Unranked cases: 0; modules: 0. Full quality details are in JSON.

## Provenance
Input SHA256: 2cdfe6b492528e488ad459f764647c37ac45cba485351ae091b34e95a09481dc.
[Input result](../../cache/test-runs/c030d75ca44ab99e/e23f6ac6de544713b9cc3c68b5224dda/result.json)
