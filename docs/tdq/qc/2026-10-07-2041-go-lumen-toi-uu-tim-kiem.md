# QC — Gỡ Lumen và tối ưu luật tìm kiếm 3 tầng
Ngày: 2026-10-07 · Plan: ../plan/2026-10-07-2041-go-lumen-toi-uu-tim-kiem.md · Vòng: 1 · Mức QC: `full`
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Mã không còn lumen | `grep -rn -i lumen scripts hooks --include=*.py --include=*.json` | 18 dòng, tất cả là chú thích lịch sử ghi rõ "until/removed in 0.58.0" hoặc số đo cũ (liệt kê dưới); 0 tham chiếu chạy được | PASS |
| Q2 | Luật 3 tầng | `grep -rn -i lumen skills scripts/tdq_state.py`; đếm hàng `**lumen**` trong bảng | 6 dòng, đều là câu lịch sử/đường dẫn số đo; 0 hàng bảng dẫn tới lumen; `chung.md:81` từng còn "one round of lumen or grep" → sửa thành `graphify query` (QC1.1) | PASS |
| Q3 | Thang 7 bậc | `python3 scripts/tdq_lsp.py check` | 7 bậc đánh số liền, smoke 3 tầng, `Tổng: ĐẠT · 7/7 bậc ĐẠT · smoke 3/3`, `exit=0` (mốc: CHƯA ĐẠT, exit 4) | PASS |
| Q4 | Gate ≤ 1 lượt thừa | 4 phiên `claude -p` (bench `claude-code.md`) | bản lời nhắc đầu: 3 và 4 → sửa (đưa `start_lsp` + `language_id` lên trước) → bản hai: **1 và 1**; lời chặn không chứa "lumen" | PASS |
| Q5 | Hook TDQ chạy trong Codex | `grep -c phien:01a116d9 <bản sao>/docs/tdq/.tdq-search.jsonl` | **4** (mốc 0) — dưới hai điều kiện sandbox cho tạo tiến trình + hook đã duyệt | PASS (lệch #1, chờ duyệt) |
| Q6 | Test | `python3 scripts/tdq_test.py tron-bo` | `modules=127 failed=0 missed=0 ok=True` (mốc: 3 đỏ) | PASS (lệch #2, chờ duyệt) |
| Q7 | Hồi quy hub | `pytest tests/test_tdq_lsp.py tests/test_tdq_setup.py`; `grep -n "^## 0.5[78]" CHANGELOG.md` | `53 passed`; `5:## 0.58.0`, `31:## 0.57.0` — mục cũ còn nguyên dưới mục mới | PASS |
| Q8 | Máy sạch lumen | xem `docs/tdq/bench/2026-10-07-2041-sau-khi-go/may-user.md` | `grep -i lumen` settings/config: 0 · 3 thư mục lumen: không còn · `qwen3-embedding` trong `ollama list`: 0 · 3 file `.bak` có · khối CLAUDE.md là bản 3 tầng, diff ngoài khối rỗng | PASS |
| Q9 | Phát hành | `grep '"version"'` 2 plugin.json; `grep -c "^## 0.58.0" CHANGELOG.md` | `0.58.0` ×2; `1` | PASS |
| QC-F1 | Trọn suite | `tdq_test.py tron-bo` + `tdq_test.py so` | 127 module, 0 đỏ, 390 s; `full-suite runs: 3 of budget 3 · radius misses: 0` | PASS |
| QC-F2 | Hồi quy vùng chạm | các module trên dòng `Chạm:` của plan nằm trong trọn suite xanh; test riêng từng cụm chạy sau mỗi task (97 · 17 · 61 · 133 · 86 · 31 ca) | xanh | PASS |
| QC-F3 | Ràng buộc kiến trúc | `search_gate` vẫn trả `deny` (`test_search_gate.py::Chan`, `ChuaSanSang` xanh); hub `Changelog`, `main()` → Q7 | giữ nguyên | PASS |
| QC-F4 | Clean code | 5 câu tự kiểm (dưới) | 5 có | PASS |

## Bằng chứng
### Q1 — 18 dòng còn chữ lumen (tất cả là chú thích)
`search_rules.py:23,79,604` · `setup_status.py:12` · `tdq_codex_mcp.py:2,14,157` · `tdq_finish.py:10` · `tdq_lsp.py:29` · `tdq_no.py:6` · `tdq_setup.py:374,384` · `search_gate.py:6,36,39` · `search_observe.py:13` · `session_start.py:59,73` — mỗi dòng nói lumen đã gỡ ở 0.58.0, hoặc giữ lý do của một con số cũ (cửa sổ `CUA_SO`, trần 30 phút dựng nền), hoặc giải thích vì sao khoá `lumen` của mốc cũ bị bỏ qua.

### Q3
```
Bậc 1 · binary agent-lsp → ĐẠT (0.19.2)
… Bậc 7 · đồ thị graphify → ĐẠT (đồ thị mới hơn mọi file mã nguồn)
Smoke test ba tầng: grep ĐẠT · LSP ĐẠT · graphify ĐẠT
Tổng: ĐẠT · 7/7 bậc ĐẠT · smoke 3/3 tầng trả lời được
exit=0
```

### Q4
| Lần | Lời nhắc | Lượt thừa |
|---|---|---|
| mốc (request 1843) | có lumen | 4 |
| 1 · 2 | bản đầu | 3 · 4 |
| 3 · 4 | `start_lsp` + `language_id` lên trước | **1 · 1** |

### Q5 (trích sổ)
```
{"khoa": "phien:01a116d9-…", "loai": "tim", "cho_phep": false, …}
{"khoa": "phien:01a116d9-…", "loai": "khai_niem", "cong_cu": "lsp:find_symbol"}
{"khoa": "phien:01a116d9-…", "loai": "tim", "cho_phep": true, …}
{"khoa": "phien:01a116d9-…", "loai": "tim", "cho_phep": true, …}
```

### QC-F1
```
tdq_test: tron-bo modules=127 failed=0 missed=0 ok=True seconds=390.49
full-suite runs: 3 of budget 3
radius misses: 0
```

### QC-F4 — clean code (mã mới: `search_rules.loi_nhac` + `LOP_KHAI_NIEM`, `search_gate.tang_song`, `tdq_codex_mcp._la_repo_plugin` + `DIEU_KIEN_CHAY`)
- SRP — có: mỗi hàm một việc (dựng lời nhắc · đọc tầng sống từ mốc · nhận ra repo plugin).
- OCP — có: thêm một tầng khái niệm là thêm một dòng vào `LOP_KHAI_NIEM` (và `TANG_KHAI_NIEM`), không mở thân hàm.
- LSP — có: `loi_nhac` luôn trả `str`; `tang_song` trả `tuple`, hoặc `None` khi KHÔNG có mốc — có tài liệu, và `loi_nhac` dùng chính sự phân biệt đó ("không biết" → nêu mọi tầng); `_la_repo_plugin` luôn `bool`, nuốt `OSError` thành `False`.
- ISP — có: mọi tham số đều được dùng.
- DIP — có: đi qua lối chung sẵn có (`_doc_moc`, `search_rules.quyet_dinh`, `tdq_setup.ghim_huong_dan_tool`, `doc_index.py`, `token_budget.py`), không chép lại.

## QC vòng 1 — fix
- [x] **QC1.1** `skills/tdq-build/references/rules/chung.md:81` còn "one round of lumen or grep" → "one round of `graphify query` or grep"; `token_budget.py` ghi lại khoá; `doc_lint` 0 vi phạm; 261 ca test chạm luật xanh; trọn suite lần cuối xanh.

## Lệch spec chờ duyệt
- #1 · Q5 · ngưỡng: một phiên `codex exec` ghi ≥ 1 dòng sổ · đo được: mặc định trên máy này hook không chạy vì (1) sandbox Windows của Codex chặn mọi tiến trình, (2) hook dự án chưa duyệt bị bỏ qua lặng lẽ — nguyên nhân ngoài repo (`docs/tdq/research/2026-10-07-2041-hook-codex.md`) · phương án đã áp: TDQ in hai điều kiện mỗi lần ghi hook; Q5 đo dưới hai điều kiện đó → 4 dòng.
- #2 · Q6 · ngưỡng (spec §1): khối search gate trong `.codex/hooks.json` gốc repo thành bản chính thức · đo được: file đó là hàng rào VIẾT TAY của mode `codex implement`, khối search gate là do `tdq_setup` ghi đè nhầm · phương án đã áp: trả file về bản commit, `khai_hook_codex` bỏ qua chính repo plugin (có test).

## Kết luận
PASS toàn bộ 9 mục DoD + 4 mục cố định, sau 1 vòng fix (QC1.1). Hai lệch chờ user duyệt.
