# Nghiệm thu Master Kiến trúc Archify (`2026-11-03-2055-master-archify-va-trinh-bay`) {#tong-quan}

@meta locale=vi

Kết quả thực tế cho request `2026-11-03-2055-master-archify-va-trinh-bay` (lane full, mode subagent, 8/8 task). Trang master `docs/architecture/index.html` đã được nâng cấp thành trang `explainer` đơn nhất có sơ đồ tổng quan 6 trụ cột kèm 5 thẻ luồng nghiệp vụ kế bên; click thẻ mở modal sơ đồ con ngay trong cùng HTML, nhấn `Escape` trả focus về đúng thẻ kích hoạt. Trạng thái master hiện tại: `status=current`, `reasons=[]`. Hồi quy trọn bộ: **4.161 passed, 10 skipped, 0 failures** (`details_complete=true`).

## Trước vs Sau — Master Kiến trúc & Đi sâu Luồng {#truoc-sau}

@workflow id=truoc-master title="Trước khi nâng cấp"
| index | Portal tĩnh 6 link rời | frontend |
| click | Click node chỉ mở Passport | frontend |
| stale | Master stale 44 lý do | database |
| finish | Chỉ mark_stale, thiếu cổng report | backend |
| index > click | không có modal luồng con |
| click > stale | candidate con ngoài fingerprint |
| stale > finish | không ép refresh trước nghiệm thu |

@workflow id=sau-master title="Sau khi nâng cấp (Working-tree)"
| overview | Master explainer + 6 node tổng | frontend |
| cards | 5 thẻ flow cạnh sơ đồ | frontend |
| modal | Modal diagram con + trả focus | frontend |
| sync | Fingerprint 5 tầng + atomic swap | security |
| overview > cards | không gắn onclick vào SVG native |
| cards > modal | mở đúng detail-* trong cùng HTML |
| modal > sync | status=current, giữ last-good khi lỗi |

Tách bạch bằng chứng: file `docs/tdq/spec/2026-11-03-2055-master-archify-va-trinh-bay-preview.html` là thiết kế **planned** (`binding.valid=true`); file `docs/architecture/index.html` và báo cáo này là kết quả **working-tree** đã chạy qua engine thật và kiểm chứng trên trình duyệt.

## Hợp đồng Model, Nguồn thật & Chống Bịa Luồng {#model-evidence}

@workflow id=luong-model title="Kiểm tra Model & Provenance"
| schema | validate_model fail-closed | security |
| source | Bước gắn file:line + test thật | backend |
| gap | Khoảng trống ghi chưa xác minh | security |
| docsonly | Dự án docs-only báo rõ trống | backend |
| schema > source | từ chối target/path/ID sai |
| source > gap | không suy diễn login/HTTP từ call graph |
| gap > docsonly | không sinh flow mẫu giả |

Năm luồng chi tiết của TDQ-Workflow trong `docs/tdq/models/master.model.json`:
- `flow-hooks-and-gates`: `hooks/tdq_stop_gate.py:922` → `scripts/tdq_state.py:2492` (`tests/test_stop_gate.py`).
- `flow-pipeline-lifecycle`: `scripts/tdq_state.py:2492` → `scripts/tdq_team.py:678` → `scripts/tdq_finish.py:552` (`tests/test_archify_finish.py`).
- `flow-runtime-verification`: `scripts/tdq_test.py:420` → `scripts/tdq_runtime_verify.py:42` → `scripts/tdq_browser_verify.py:62` (`tests/test_tdq_test_receipt.py`).
- `flow-search-and-archify`: `scripts/tdq_lsp.py:390` → `scripts/tdq_graphify.py:720` → `scripts/tdq_archify.py:725` (`tests/test_archify_pipeline.py`).
- `flow-optimization-report`: `scripts/tdq_skill_eval.py:71` → `scripts/tdq_timing.py:598` (nhánh runtime scorer chưa đăng ký ghi rõ `chưa xác minh`).

## Freshness 5 Tầng & Cổng Lifecycle {#freshness-lifecycle}

@workflow id=luong-freshness title="Kiểm tra Freshness & Publish"
| pre | Chụp source_fingerprint trước render | database |
| stage | Render vào .staging + finalize | backend |
| post | So lại source_fingerprint sau swap | security |
| gate | Cổng report/idle cảnh báo nếu stale | security |
| pre > stage | lỗi bất kỳ view giữ nguyên last-good |
| stage > post | đổi source lúc render -> stale |
| post > gate | tdq_finish giữ check rẻ ~60ms |

`check_master_status` đối chiếu: (1) `model_sha256`, (2) `candidate_sha256` của master, (3) `html_sha256` của `index.html`, (4) `html_sha256` + `candidate_sha256` của từng view con, và (5) `source_fingerprint` toàn repo.

## Bằng chứng Kiểm thử, Browser & Giới hạn Thật {#ket-qua}

@workflow id=luong-kiem-chung title="Chuỗi Bằng chứng Nghiệm thu"
| unit | 222 test Archify chuyên biệt PASS | backend |
| browser | Desktop 1280x900 + Mobile 390x844 PASS | frontend |
| full | 4.161 passed, 10 skipped, 0 fail | security |
| eval | Source-bound plan valid, INCONCLUSIVE | database |
| unit > browser | modal + Escape focus + 0 console error |
| browser > full | receipt 8f898b1e... details_complete=true |
| full > eval | T1.1 cấm gọi paid model -> WAIVED_USER |

Giới hạn thật:
- Eval hành vi (`skills/tdq-build/references/archify-lifecycle.md`): đã khóa `eval-plan.json` source-bound (`experiment_hash=628de8ae438ace4f2c7742c724e61ac609f24dcd2e844ed4d92b0e336631edbb`), nhưng theo đúng ràng buộc T1.1 (`Không dùng cho: chạy paid model`) và Spec §4/§6 (`thiếu outcome scorer → INCONCLUSIVE`), không chạy paid model sống nên verdict chất lượng là `INCONCLUSIVE` / `INCOMPLETE` (mở cổng `report` bằng `WAIVED_USER` theo lệnh user, chờ duyệt lệch `#1` trên `Q6`).
- Lưu ý mức LOW từ QC độc lập: `source_fingerprint(project_dir)` khi gọi không truyền `source_paths` (ví dụ manifest preview spec) có quét `.pytest_cache`/`.ruff_cache` nếu phát sinh sau khi tạo manifest; không ảnh hưởng `binding.valid` của tài liệu hay `docs/architecture/manifest.json` khi working tree sạch cache.
