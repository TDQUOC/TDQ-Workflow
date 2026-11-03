# PLAN NHANH — Sửa cảnh báo lumen sai ở bậc 5
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Phạm vi

- **Trong**: bậc 5 của `scripts/tdq_lsp.py` đọc đúng model lumen thật (config → env → mặc định)
  và dò manifest ollama đúng đường dẫn cho tên dạng `name:tag`.
- **Ngoài**: không đụng lumen/ollama/`config.yaml`; không đổi 6 bậc còn lại; không sửa 4 issue
  người dùng đã bỏ; bậc 5 vẫn chỉ CẢNH BÁO, không bao giờ chặn.

## Task

- [x] **T1 — `_model_lumen()` đọc model thật.** Thứ tự đúng như lumen: `~/.config/lumen/config.yaml`
      (parser tối giản, chỉ bắt `model:` đầu tiên dưới `servers:` — 2 server bắt buộc cùng model)
      → `$LUMEN_EMBED_MODEL` → hằng mặc định `ordis/jina-embeddings-v2-base-code`. Chỉ stdlib.
      Test: có config → trả model trong config · không config, có env → trả env · không cả hai → mặc định
      · config rác/không đọc được → rơi về env/mặc định, không ném exception.
      Chạm: `scripts/tdq_lsp.py`, `tests/test_tdq_lsp.py`
- [x] **T2 — `_duong_dan_manifest(model)` tách đúng namespace + tag.** `ns/name:tag` →
      `~/.ollama/models/manifests/registry.ollama.ai/<ns|library>/<name>/<tag|latest>`.
      Test: `qwen3-embedding:0.6b` → `library/qwen3-embedding/0.6b` · `ordis/jina-embeddings-v2-base-code`
      → `ordis/jina-embeddings-v2-base-code/latest`. `_model_da_pull()` gọi qua hàm này.
      Chạm: `scripts/tdq_lsp.py`, `tests/test_tdq_lsp.py`
- [x] **T3 — `bac5_lumen()` nói tên model động.** Thông điệp thiếu model và lệnh `ollama pull <model>`
      lấy từ `_model_lumen()`, không còn hằng số cứng. Test: giả lập config qwen3 + thiếu model →
      `b.lenh_cai` chứa `qwen3-embedding:0.6b`, `b.chi_canh_bao` vẫn True.
      Chạm: `scripts/tdq_lsp.py`, `tests/test_tdq_lsp.py`

## DoD

1. `python3 scripts/tdq_lsp.py check` trên máy này → **bậc 5 ĐẠT**, tổng `7/7 bậc ĐẠT · 0 cảnh báo`.
2. `python3 tests/test_tdq_lsp.py` xanh toàn bộ (hiện 41 test), không test nào bị bỏ.
3. `grep -n 'MODEL_LUMEN' scripts/tdq_lsp.py` chỉ còn xuất hiện như **giá trị mặc định**, không
   còn được dùng trực tiếp trong `bac5_lumen`/`_model_da_pull`.
4. Xoá `~/.config/lumen/config.yaml` khỏi tầm nhìn (giả lập bằng test, không xoá file thật) →
   hàm vẫn trả mặc định, bậc 5 không ném lỗi.

## QC

| DoD | Lệnh | Kết quả |
|---|---|---|
| 1 | `python3 scripts/tdq_lsp.py check` | `Bậc 5 → ĐẠT (ollama đang chạy, có qwen3-embedding:0.6b)` · `Tổng: 7/7 bậc ĐẠT` (trước: 6/7 + 1 cảnh báo) |
| 2 | `python3 tests/test_tdq_lsp.py` | `Ran 49 tests · OK` (41 cũ + 8 mới, đều đi red→green) |
| 3 | `grep -rn MODEL_LUMEN scripts tests` | chỉ còn `MODEL_LUMEN_MAC_DINH` ở dòng khai báo 42 và nhánh fallback 317 — không chỗ nào dùng hằng số làm model thật |
| 4 | `_model_lumen()` khi mất/hỏng config | test `test_khong_config_khong_env_thi_lay_mac_dinh` + `test_config_rac_khong_lam_sap_bac5` xanh: trả mặc định, không ném exception |

Đo trên máy thật: `_model_lumen()` → `qwen3-embedding:0.6b`; `_duong_dan_manifest()` →
`~/.ollama/models/manifests/registry.ollama.ai/library/qwen3-embedding/0.6b`, tồn tại trên đĩa.

**Ngoài phạm vi plan, phát hiện lúc implement**: lệnh `tdq_lsp.py nha` cũng gọi
`ollama stop <hằng số>` nên trước đây nhả trượt model thật (model vẫn giữ RAM). Đã vá cùng T3,
có test `test_nha_nha_dung_model_dang_dung` đóng đinh.

**Hồi quy**: toàn suite `Ran 1533 · failures=290 errors=4` — đúng bằng nền cũ (~294 đỏ có sẵn),
không thêm đỏ mới. `tests/test_team_chong_conflict.py` đỏ vì thiếu `pytest`, kiểm bằng
`git archive HEAD` thấy đỏ y hệt từ trước.
