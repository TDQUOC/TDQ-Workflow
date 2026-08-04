# REPORT — Bộ công cụ export cấu hình Claude Code sang máy khác

Ngày: 2026-08-04 · Spec: ../spec/2026-08-04-export-claude-setup.md · Plan: ../plan/2026-08-04-export-claude-setup.md · QC: ../qc/2026-08-04-export-claude-setup.md

## Đã làm gì
- Viết bộ công cụ tái dùng `claude-export/` trong repo: `INSTRUCTIONS.md` (7 bước),
  `MANIFEST.template.json`, `README.template.md` (6 mục, cross-platform), `EXPORT_LOG.md`.
- Chạy chính bộ công cụ đó, sinh bundle thật tại `~/Documents/claude-code-export/`
  (`config/` đã lọc secret, `tdqworkflow-repo/` copy toàn repo, `manifest.json`,
  `README.md` điền dữ liệu thật).
- Rewrite path marketplace `tdq-local` trong bundle trỏ đúng vị trí đích.
- Phát hiện + fix lỗi rsync lọt data loại trừ (bak/pycache/logs/cache) vào bundle,
  cập nhật `INSTRUCTIONS.md` để lần export sau không lặp lại.
- Chạy đủ 10 mục QC (Q1–Q10), toàn bộ PASS.

## Đầu ra
| Đầu ra | Đường dẫn |
|---|---|
| Bộ công cụ tái dùng | `claude-export/{INSTRUCTIONS.md,MANIFEST.template.json,README.template.md,EXPORT_LOG.md}` |
| Bundle thật | `~/Documents/claude-code-export/{manifest.json,README.md,config/,tdqworkflow-repo/}` |
| QC | `docs/tdq/qc/2026-08-04-export-claude-setup.md` |

## Cách chạy / cách kiểm
```
python3 -m json.tool claude-export/MANIFEST.template.json
grep -rEi "sk-|api[_-]?key|token" claude-export/ --include="*.json" --include="*.md"
python3 -m unittest discover -s tests   # 440 passed
```

## Kết quả QC
10/10 hạng mục PASS (vòng 1, có 1 fix giữa chừng ở Q10 — xem file QC).

## Quyết định đáng chú ý
- Xoá 6 mục lọt exclusion (1 `.bak`, 4 `__pycache__`, `.remember/logs/`,
  `graphify-out/cache/`) khỏi bundle + thêm 4 `--exclude` vào rsync của
  `INSTRUCTIONS.md` — tự quyết vì là chặn kỹ thuật rủi ro thấp, đã ghi working log.
- Không copy `oauthAccount`/`machineID`/`userID`/giá trị API key thật — máy đích tự
  đăng nhập và điền lại key theo README.

## Giới hạn còn lại
- Lệnh cài Linux/Windows trong README chỉ đối chiếu tài liệu chính thức, chưa test
  trực tiếp trên 2 OS đó (chỉ test được nhánh macOS trên máy nguồn).
- Bundle hiện tại là 1 bản chụp lúc 2026-08-04 14:20 — cấu hình đổi sau đó cần chạy
  lại `INSTRUCTIONS.md` để cập nhật.

## Đề xuất tiếp theo
- Không có, trừ khi user muốn test thử luồng cài trên máy Linux/Windows thật.
