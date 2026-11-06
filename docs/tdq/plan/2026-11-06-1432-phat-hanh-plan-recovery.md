# QUICK — Phát hành cải tiến khôi phục plan

**Ngày:** 2026-11-06 · Brief: ../brief/2026-11-06-1432-phat-hanh-plan-recovery.md · Lane: quick
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
**Trạng thái:** ĐÃ DUYỆT (làm luôn ko cần mở request)
**Ước tính sẽ dùng skill:** `tdq-intake` (nền)

## Phạm vi

- Trong: bump `0.93.0` → `0.94.0` (minor: hành vi Stop/resume), hai manifest plugin, `CHANGELOG.md`; commit release trên nhánh request, merge về `dev`, `build_portable.py --sinh-main --nguon dev --nhanh-dich main`, push `dev` + `main` đến `origin` theo yêu cầu.
- Ngoài: sửa mã Stop/resume đã được QC full và merge, chạy eval model (`eval: chưa kích hoạt (opt-in)`), sửa file dirty tự động của request cũ, xóa worktree, tag/GitHub release (không được yêu cầu rõ).
- Bỏ B0: release version theo README và report cũ, không có lĩnh vực/công cụ mới. Bỏ B2: dùng Git/build_portable sẵn, không cần nghiên cứu hành vi bên ngoài.
- B1: `README.md:213-218` hướng dẫn bump hai manifest + Changelog + `--sinh-main`; remote `origin` đã kiểm qua `git ls-remote` (`dev` c7233bf5, `main` e3f618f5). `dev` local eb5051d7, `main` local de56437d; remote đều cũ hơn local. Dry-run kept=175, dropped=5365. Chỉ tài liệu/graphify dirty; không mã nguồn dirty.

## Task

- [x] **T1** Bump 0.94.0 và ghi mục thay đổi khôi phục plan, giữ `CHANGELOG.md` dưới 500 dòng — Test: `python scripts/doc_lint.py CHANGELOG.md docs/CHANGELOG-archive-2.md` và JSON manifest cùng version.
  - Chạm: `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `CHANGELOG.md`, `docs/CHANGELOG-archive-2.md` (nếu cần để giữ trần 500).
- [~] **T2** Test đóng gói/version, commit request, merge `dev`, build/publish `main` và push hai nhánh (không tag) — Test: `python -m pytest tests/test_build_portable.py tests/test_adapter_host.py -q`; `git ls-remote --heads origin dev main` khớp local sau push.
  - Cần: T1

## Definition of Done

- [ ] Q1 Hai plugin manifest cùng `0.94.0`; Changelog có bản mới, lint đạt — `python scripts/doc_lint.py CHANGELOG.md docs/CHANGELOG-archive-2.md`.
- [ ] Q2 Test đóng gói/adapter đạt, `build_portable.py --sinh-main` thành công, local `main` nhận version 0.94.0 — `python -m pytest tests/test_build_portable.py tests/test_adapter_host.py -q`.
- [ ] Q3 Commit và merge về `dev`, push `dev` + `main` tới `origin`, hash remote khớp local; không tag — `git ls-remote --heads origin dev main`.

## QC

Chờ test và chứng cứ thực; không suy PASS từ dry-run hoặc lệnh push chưa xác minh.
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-06-1432-phat-hanh-plan-recovery-flow.manifest.json -->
<!-- manifest_digest: 19a2bcae0371492ab7390714c8642c9e0e734a69cecdfb05038529f43e2f4ef9 -->
<!-- tdq-archify-binding:end -->