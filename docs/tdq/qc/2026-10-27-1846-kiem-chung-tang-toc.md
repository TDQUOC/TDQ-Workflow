# QC — Kiểm chứng và tăng tốc TDQ Workflow
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-31 · Request: `2026-10-27-1846-kiem-chung-tang-toc` · Source `81c1946345d8495ef32dbb3924de801020c957c5599918b9c3d4317c5f3278ad`.

<!-- results -->
## Kết quả và phạm vi chốt

**PASS correctness/runtime/architecture; D9/D10 SKIPPED_USER; browser/report kiểm riêng.** Đây không phải kết luận toàn DoD 12/12 hoặc PASS hiệu năng. [Quyết định người dùng](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/benchmark-user-waiver-20261031.md) giữ nguyên spec/verifier và evidence cũ.

| Check | Trạng thái | Bằng chứng |
|---|---|---|
| D1–D8 | Semantic PASS | [Kết quả từng check](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/dod-checks-final-QC3.json): assertion bắt buộc 76/27/14/121/61/37/18/20. |
| D9 — Full A/B | SKIPPED_USER | Không chạy tiếp bộ 3 cặp, không chứng nhận parity/median 20%. |
| D10 — cache/log | SKIPPED_USER | Không chạy tiếp off/cold/warm reuse/readiness/transcript; chưa có lợi ích log thật. |
| D11 — runtime/independent QC | PASS trong scope đã điều chỉnh | [QC độc lập](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/qc-final-user-waiver.md), [JSON bind reviewer/source](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/qc-final-user-waiver.json), [runtime](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/runtime-final.json). |
| D12 — report/browser | Phạm vi điều chỉnh | Gate gốc cần benchmark không áp dụng; component verify_report kiểm nội dung/link/browser theo waiver, xem [kết quả](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/summary-scope-validation.json). |

Full cuối: **3594 PASS, 8 skip, 3602 case**, đủ 3306 baseline + 296; không remap/missing/extra/duplicate. Wall `1117.6745853999746` giây. [Result](../cache/test-runs/c030d75ca44ab99e/e23f6ac6de544713b9cc3c68b5224dda/result.json) và [receipt](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/runs/QC-F1-final-after-QC3-20261031-6add68337dd44ca9b785b1603918f786/receipt.json) khớp source, exit 0, quyền thường, config/source/dependency guard sạch, cleanup complete.

[Runtime receipt](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/runs/runtime-final-after-QC3-ed06898fbca3436baf4a965c036e004a/receipt.json) PASS; 6 scenario simulation/process thật dưới 120 giây: timeout 3.422055699978955; cancel 0.6415148000232875; join 5.785335699969437; owner-crash 5.926353799994104; freshness 5.685249699978158; transcript 0.353201900026761 giây. Đây là smoke bounded, không là hiệu quả A/B toàn suite.

<!-- raw-samples -->
## Lịch sử QC và bằng chứng không đạt

- QC-F1 lịch sử có lỗi isolation/encoding/Archify; guard config từng FAIL được giữ nguyên, không chứng nhận theo child PASS.
- QC1 sửa project anchor của helper, cô lập Archify/browser, UTF-8/scanner binary và registry luật batch. QC2 sửa fixture sinh token lock để không dùng repo/HOME thật. QC3 giữ metadata subtest canonical trước xdist và reason sau hook; sắp thứ tự nhánh, dùng nhãn payload ổn định, giữ đủ scenario/assertion.
- RED/GREEN và parent checks lưu trong artifacts; [QC sơ bộ](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/qc-preliminary-20261031.md) giữ review nguồn chi tiết. [QC cuối](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/qc-final-user-waiver.md) thay verdict sơ bộ bằng phạm vi mới, không xóa lịch sử.
- [Benchmark ngắt](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/benchmark-full.interrupted-20261031-1905.json): 1 mẫu đã lưu, source/environment đổi, result INCOMPLETE.
- [Benchmark parity fail](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/benchmark-full.parity-failed-20261031.json): 2 mẫu child PASS, pair không đạt metadata parity; 293 case khác trước QC3.
- [Benchmark config drift](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/benchmark-full.config-drift-QC3-20261031.json): 1 mẫu child PASS trên 3602 case; harness FAIL config_guard, lượt sau bị dừng. Không bộ nào đủ 6 mẫu hợp lệ.

<!-- limitations -->
## Giới hạn

8 skip có reason/capability: 3 symlink, 4 giới hạn POSIX/permission, 1 CLI không có argparse help; không chứng nhận POSIX host thật. Ruff UNAVAILABLE. D9/D10 được user bỏ qua, không đổi nhãn thành PASS. Model compute unavailable; timing có khoảng chờ và unattributed, xem nguyên văn trong [báo cáo](../reports/2026-10-27-1846-kiem-chung-tang-toc.md).

Reviewer `gpt61sol_high_review_qc13` độc lập với implementers, findings còn mở bằng 0. QC-F3 architecture PASS; QC-F4 SOLID PASS qua review thủ công và regression evidence. Source snapshot có generated exclusions công khai; không thay fingerprint/hermetic của sản phẩm.

Chrome DevTools MCP kiểm viewport desktop 1440×900 và mobile 375×812; [bằng chứng browser](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/report-browser.json) giữ DOM/console và screenshot. Đây là kiểm viewport, không phải thiết bị vật lý. Gate D12 gốc không áp dụng vì benchmark được user bỏ qua.

<!-- before-after -->
## Ánh xạ đầu ra

O1 manifest/result → D1/D2; O2 process/helper → D2–D4; O3 receipt/join → D5/D6; O4 readiness/batch → D7; O5 transcript → D8; O6 CLI đo/rollback → D9/D10 SKIPPED_USER; O7 QC/report → D11 PASS scope, report/browser theo phạm vi điều chỉnh. Xem [báo cáo Markdown](../reports/2026-10-27-1846-kiem-chung-tang-toc.md) và [HTML](../reports/2026-10-27-1846-kiem-chung-tang-toc.html).

<!-- recommendations -->
## Khuyến nghị

Giữ workers 1, reuse/readiness/transcript off; không công bố median hoặc phần trăm tăng tốc. Chỉ đánh giá opt-in bằng evidence mới nếu người dùng yêu cầu phạm vi đó sau này.

<!-- rollback -->
## Rollback

```sh
python scripts/tdq_test.py tron-bo --repo . --workers 1 --fresh --reuse off --timeout-seconds 1800
```
Giữ `--readiness-cache off` cho setup/LSP và `--transcript-cache off` cho timing. Không cần xóa cache hoặc sửa cấu hình cá nhân. Git chưa commit/push/merge; nhánh giữ `bugfix/kiem-chung-tang-toc`.
