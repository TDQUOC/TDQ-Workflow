# REQUEST — Bump version + làm lại bản export đầy đủ hơn

## Nguyên văn yêu cầu (2026-08-05 03:21)

```text
hãy pump version và check claude export và folder export của claude trong document
check xem versioin mới này dirt thế nào với bản đã export và cập nhật chi tiết để
tạo bản export đầy đủ hơn
```

## Cách hiểu đầu tiên

Mục tiêu gồm 4 phần, làm theo thứ tự:

1. **Bump version** plugin `tdq-workflow`: `.claude-plugin/plugin.json` đang `0.6.2`
   (phát hành 2026-08-02), từ đó đã có 5 commit tính năng. `tests/test_docs_consistency.py`
   bắt buộc mục đầu `CHANGELOG.md` phải trùng version đang phát hành → bump kèm entry.
2. **Check bộ công cụ export** `claude-export/` trong repo: `INSTRUCTIONS.md` (7 bước
   thủ công), `README.template.md`, `MANIFEST.template.json`, `EXPORT_LOG.md`.
3. **Đo drift** giữa trạng thái hiện tại và bundle đã export ở
   `~/Documents/claude-code-export` (sinh 2026-08-04 14:16).
4. **Cập nhật chi tiết** bộ công cụ để bản export mới ĐẦY ĐỦ HƠN bản cũ, rồi sinh lại
   bundle.

## Số liệu drift đã đo sơ bộ (read-only, trước khi chốt lane)

Repo (`diff -rq` bỏ `.git`/`__pycache__`/`.DS_Store`): **122 mục lệch**, trong đó
7 file `agents/*.md`, `claude-export/INSTRUCTIONS.md` + `EXPORT_LOG.md`, toàn bộ
`docs/tdq/*` của 5 request mới, `docs/tdq/STATE.md`.

Config local:

| File | Bản export | Hiện tại | Trạng thái |
|---|---|---|---|
| `CLAUDE.md` | 10.745 byte | 3.233 byte | LỆCH NẶNG (đã tái cấu trúc lõi vòng 2) |
| `plugin-tiers.json` | 517 byte | 693 byte | LỆCH |
| `settings.json` | — | — | LỆCH |
| `installed_plugins.json` | — | — | LỆCH |
| `statusline.sh` | — | — | giống |

Commit sau mốc export: `f344377`, `1175980`, `b41225f`, `07e7e1c`, `e019703`.

## Chỗ chưa rõ (cần interview)

- "Đầy đủ hơn" theo nghĩa nào: copy thêm hạng mục của `~/.claude` (hiện chỉ copy 9
  hạng mục, bỏ `agents/`, `commands/`, `plans/`, `specs/`, `tasks/`, `.claude.json`),
  hay tự động hoá 7 bước thủ công thành script, hay cả hai?
- Bump lên `0.6.3` hay `0.7.0`?
- Có ghi đè bundle cũ tại `~/Documents/claude-code-export` không, hay sinh bundle mới
  cạnh nó? Zip cũ (`claude-code-export.zip`, 2,3 MB) xử lý thế nào?
- Có cần cơ chế đo drift lặp lại được (script so bundle ↔ nguồn) hay chỉ cần con số
  cho lần này?
