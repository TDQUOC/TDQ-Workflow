# Checkpoint phục hồi ngày 2026-10-31
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Request `2026-10-27-1846-kiem-chung-tang-toc`, nhánh `bugfix/kiem-chung-tang-toc`, lane full, phase implement, mode subagent, QC ultra. Người dùng yêu cầu “tiếp tục”. Tiến độ cuối lượt: **18/25 task**, T5.1 còn `[~]`. Không commit, Git merge, push, đổi nhánh hoặc cập nhật plugin đã cài.

## Đã hoàn tất

- Setup theo AGENTS; LSP Python đã kiểm 3 references và ghi DAT. DevTools preflight thành công. Refresh Master từ model working-tree hiện có bằng Edge native; Master current. Binding spec đã duyệt current; snapshot source của preview là thiết kế lịch sử, không sửa lại snapshot đó.
- Hai reviewer đọc độc lập QC1.1/QC1.3, kiểm SHA root/worktree khớp, không có finding mới: [review](codex-resume-2026-10-31-review.md).
- QC1.3 parent root: **57 passed, 34 subtests passed, 98.30s**, harness/child exit 0, config/source/dependency guard và cleanup PASS. [Receipt](runs/QC1.3-codex-20261031-0292e87250e442b68d6663afcc521a04/receipt.json).
- QC1.1 parent root: **513 passed, 2 skipped, 215 subtests passed, 240.27s**, harness/child exit 0, các guard và cleanup PASS. [Receipt](runs/QC1.1-codex-20261031-fafa0d7dfe6c4124b329fb4b46b86000/receipt.json).

## Full fresh sau QC vòng 1

Lệnh: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label QC-F1-codex-20261031 --archify-chrome "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" -- python scripts/tdq_test.py tron-bo --repo . --workers 1 --fresh --reuse off --timeout-seconds 1800`.

- **3599 case: 3590 pass, 1 fail, 8 skip**, 2466 subtests pass. Pytest 1294.90s, runner 1304.34s. Coverage complete, không missing/extra/duplicate. Cả 3306 case gốc còn trong manifest, thêm 293 case; không remap. Mọi skip có reason và capability.
- Case lỗi duy nhất: `tests/test_tdq_finish.py::KhoaTokenTest::test_khoa_chay_khi_cham_file_luat`, assertion `fail` không thuộc `ok/skip`.
- Harness/child exit 1, verdict FAIL. Harness ghi thêm `config_guard: config changed during command`; chỉ `.claude.json` đổi digest. Source/dependency không bị guard từ chối; cleanup complete.
- [Receipt FAIL](runs/QC-F1-codex-20261031-0e56356e147e430b84172ce2feaf5f0e/receipt.json), [stdout](runs/QC-F1-codex-20261031-0e56356e147e430b84172ce2feaf5f0e/stdout.txt), [đối chiếu baseline và skips](codex-full-observation-20261031.json).
- Đây là quan sát trên source trước QC2.1, **không phải chứng nhận source cuối**. Không dùng lượt này làm benchmark hoặc Full PASS. Không quy kết tiến trình nào ghi cấu hình ở lượt này; chứng cứ ETW ngày 27 không chứng minh tác giả của thay đổi ngày 31.

## QC2.1 đã sửa và kiểm vùng chạm

- Chỉ sửa `tests/test_tdq_finish.py`. Test cũ gọi sinh khóa trên repo thật và phụ thuộc tokenizer/cấu hình máy. Chuyển sang project tạm một file luật, mock riêng factory counter; vẫn chạy `token_budget.sinh_khoa` thật và kiểm JSON token/hash. Bổ sung missing counter -> skip, counter lỗi -> fail và không sinh lock. Không sửa production, không nới guard/assertion. Không suy ra kết quả token thật từ counter fixture.
- Author ở worktree qc1.1: **20 passed, 7.03s**, guard/cleanup PASS. [Receipt GREEN](QC2.1-author/runs/QC2.1-green-1a80f83fe0984792a04e30e96201ad3f/receipt.json).
- Lượt author mang nhãn `QC2.1-red` thực tế 18 PASS do worktree không có venv và test cũ nhận skip. Giữ nguyên lượt đó, **không gọi đó là RED**. RED thật là case lỗi trong Full root. Exception tokenizer gốc chưa xác định vì assertion cũ không ghi detail.
- Reviewer độc lập `gpt61sol_high_review_qc13` không có finding. Đối chiếu candidate SHA và root trước copy, chỉ copy đúng file; SHA sau copy `dea25348cbcbaff173d8b1c418c15bd06d0bc96862f3a5b067088ac972419d07`. LSP 0 diagnostic, git diff --check sạch. Ruff chưa kiểm vì không có executable.
- Parent root chạy `tests/test_tdq_finish.py tests/test_skill_tokens.py`: **41 passed, 59 subtests passed, 11.63s**, harness/child exit 0, tất cả guard và cleanup PASS. [Receipt](runs/QC2.1-parent-20261031-60866b17fb6340b6884c73093a54c447/receipt.json).

## Điều kiện chặn và bước tiếp tục

Hai parent check ngắn đã PASS không chứng minh nguồn ghi cấu hình dừng trong toàn lượt Full/benchmark dài. Lượt Full mới lại thấy `.claude.json` đổi. Không chạy lại Full nhiều lần để tìm khoảng yên tĩnh; không khóa/hoàn nguyên cấu hình, nới guard hoặc tự dừng phiên người dùng.

Cần người dùng tạm dừng các phiên Claude/CloudCLI/VS Code đang ghi chung cấu hình và xác nhận nguồn ghi đã dừng. Sau đó resume qua CLI, chạy Full fresh trên source cuối (QC2.1 đã sửa), xác minh 3306 case gốc và skip; tiếp runtime smoke với cap 120s từng scenario, ba cặp Full A/B, ba cặp cache, QC độc lập, D1–D12 và report MD/HTML desktop/mobile. Giữ nguyên mọi lượt FAIL lịch sử.

Các worktree/candidate hiện hữu được giữ để bảo toàn công việc dirty và chứng cứ; không xóa chúng trong lượt này.
