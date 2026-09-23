# QC — Học cách tổ chức của superpowers
Ngày: 2026-09-21 · Plan: ../plan/2026-09-21-0029-hoc-superpowers-da-host.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Mọi lệnh chạy trên Windows 11, Python 3.13.15, **không** đặt `PYTHONUTF8` hay `PYTHONIOENCODING`.
"Máy sạch" = venv không pytest, PATH không có graphify/node/codex/python3,
`TDQ_TOKENS_VENV=/khong/co`.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Adapter Codex | `codex plugin marketplace add .` rồi `codex plugin list`, `CODEX_HOME` tạm | `tdq-workflow@tdq-local` | PASS |
| Q2 | Adapter OpenCode chạy được | `-p test_adapter_host.py -k opencode` | 5 ca OK, nạp thật bằng `node` | PASS |
| Q3 | OpenCode không kéo phụ thuộc | `-k phu_thuoc` + grep `import` | chỉ `node:path`, `node:fs`, `node:url` | PASS |
| Q4 | Lệnh sinh layout agy | `-p test_sinh_agy.py` | 9 ca OK, kể cả chạy hai lần không đổi | PASS |
| Q5 | Ba bundle biến khỏi repo | `git ls-files` lọc ba thư mục | 0 | PASS |
| Q6 | `build_portable.py` không còn tên chết | `-k khong_con_ten_chet` | 0 hàm, 0 hằng không nơi dùng | PASS |
| Q7 | `tdq_checkportable.py check` | chạy ở gốc repo | NOTE, exit 0 | PASS |
| Q8 | CI đủ 6 tổ hợp | `-p test_ci_matrix.py` | 8 ca OK | PASS |
| Q9 | Suite trên máy sạch | trọn suite, máy sạch | 1937 ca, 0 fail, 0 error, 32 skip | PASS |
| Q10 | Không ca nào xanh → đỏ | đối chiếu id ca với `main` | 0 đỏ; 66 ca bỏ, xem bằng chứng | PASS |
| Q11 | Tài liệu khớp kiến trúc | `-p test_docs_consistency.py` | OK | PASS |
| Q12 | Phát hành | version + `doc_lint CHANGELOG.md` | 0.50.0 ở cả hai manifest, 362 dòng, exit 0 | PASS |
| Q13 | Lint tài liệu request | `doc_lint` bốn thư mục + `--pair` | 0 vi phạm | PASS |
| QC-F1 | Trọn suite | `python -m unittest discover tests` | 1961 ca, 0 fail, 0 error, 9 skip | PASS |
| QC-F2 | Hồi quy vùng chạm | test của từng module ở dòng `Chạm:` | xanh, xem bằng chứng | PASS |
| QC-F3 | Ràng buộc kiến trúc | soát 5 dòng spec §5 | giữ đủ | PASS |
| QC-F4 | Clean code | 5 câu tự kiểm | 5 CÓ | PASS |

## Bằng chứng

### Q1

```
Added marketplace `tdq-local` from \\?\C:\...\TDQ-Workflow.
tdq-workflow@tdq-local  not installed           C:\...\TDQ-Workflow
```

`CODEX_HOME` trỏ thư mục tạm nên cấu hình Codex thật của máy không bị thêm marketplace.

### Q2, Q3

```
test_opencode_doc_dung_so_skill ... ok
test_opencode_log_bat_mac_dinh_co_timestamp ... ok
test_opencode_log_tat_duoc ... ok
test_opencode_node_nap_duoc ... ok
test_opencode_phu_thuoc_chi_thu_vien_chuan ... ok
25:import path from 'node:path';
26:import fs from 'node:fs';
27:import { fileURLToPath } from 'node:url';
```

### Q4

```
test_mcp_config_chi_tro_bien_khong_ghi_gia_tri ... ok
test_chay_hai_lan_khong_doi_gi ... ok
test_sinh_du_bon_thanh_phan ... ok
test_tu_choi_thu_muc_khong_phai_cua_minh ... ok
Ran 9 tests — OK
```

### Q6 — FAIL ở vòng 1, PASS sau khi user đổi ngưỡng

```
git show main:scripts/build_portable.py | wc -l   → 1077
wc -l scripts/build_portable.py                   → 634
test_khong_con_ten_chet ... ok
test_bo_do_bat_duoc_hang_chet_theo_chuoi ... ok
```

Vòng 1 cắt thêm 11 hằng chết và một tham số chết (QC1.1), nhưng 634 dòng vẫn là 41%, chưa tới
ngưỡng "một nửa". Phần còn lại đều sống: bộ sinh agy, mẫu README của agy, bộ viết lại
`hooks.json`, CLI — xuống dưới 538 dòng nghĩa là xoá chức năng đang chạy. Con số "một nửa" là
số ƯỚC viết trước khi đo, nên đổi nó là đổi nội dung spec.

2026-09-23: user chọn phương án A và duyệt lại spec (nguyên văn: "duyet spec"). Ngưỡng mới —
"không tên cấp module nào, hàm LẪN hằng, còn lại mà không có nơi dùng" — chặt hơn ngưỡng cũ ở
đúng chỗ đã để lọt lỗi: bản cũ chỉ đòi không hàm thừa, nên 11 hằng chết đi qua T2.3 mà không
phép kiểm nào thấy. Ngưỡng mới đo bằng máy, và `test_bo_do_bat_duoc_hang_chet_theo_chuoi` tự
kiểm bộ dò để nó không âm thầm trả về rỗng.

Số 1135 ghi trong mục hợp đồng skill bên dưới là mốc sai: đó là bản làm việc giữa request 1,
không phải `main`. Mốc đúng là 1077.

### Q7

```
NOTE     không thấy bundle ở đây — repo này tự là plugin, mỗi host đọc một manifest mỏng trỏ vào `skills/` dùng chung
exit=0
```

### Q9 — máy sạch

```
không có pytest · không có graphify · không có node · không có codex · không có python3
Ran 1937 tests in 262.407s
OK (skipped=32)
```

Mỗi skip mang lý do: 20 ca thiếu anthropic-tokenizer, 3 ca thiếu graphify, 4 ca thiếu node,
2 file thiếu pytest, 3 ca bit quyền POSIX không có trên Windows. Hai ca `tomllib` chỉ skip trên
Python < 3.11, máy này không có bản đó nên chưa thấy chúng skip thật — CI sẽ là lần đầu.

### Q10

Liệt kê id ca bằng `unittest.TestLoader` trên `main` (worktree tạm) và trên nhánh: 1983 → 1961.
Không ca nào đỏ. 66 ca biến mất, tất cả kiểm thứ đã gỡ: bundle claude/codex/agy dựng sẵn, lớp
trust/codex của `tdq_checkportable`, bản sao đánh số của skill trong bundle codex.

Soát lại từng ca bị bỏ thì ba ca đang **kiểm cả nguồn lẫn bản sao** — đã bỏ nhầm nửa nguồn. Đã
trả lại:

- `test_soul_rules.SoulPointers.test_dong_tro_soul` — nửa `skills/tdq-conventions/SKILL.md`.
- `test_user_facing_block.test_every_user_facing_skill_points_here` — nửa `skills/`.
- `test_checkportable.TestKhongLoSecret.test_mcp_json_cua_ban_sinh_khong_lot_gia_tri` — chuyển
  sang `test_sinh_agy.KhongLoSecretTest`, vì agy vẫn SINH `mcp_config.json`.

### QC-F1

```
Ran 1961 tests in 286.213s
OK (skipped=9)
```

Chạy hai suite song song một lần thì `test_bench` đỏ: nó quét `tdq-bench-*` trong `%TEMP%`
chung và thấy thư mục của suite kia. Chạy tuần tự thì xanh — đó là hiện vật của cách tôi chạy,
không phải lỗi sản phẩm.

### QC-F2

| Vùng chạm | Test | Kết quả |
|---|---|---|
| `.agents/plugins/`, `.codex-plugin/`, `.opencode/` | `test_adapter_host` | OK |
| `scripts/build_portable.py` | `test_build_portable`, `test_sinh_agy`, `test_sua_da_nen_tang`, `test_tuong_thich_host` | OK |
| `scripts/tdq_checkportable.py` | `test_checkportable`, `test_shim_python3` | OK |
| `scripts/utf8_io.py` | `test_utf8_io` | OK |
| `hooks/scripts/session_start.py` | `test_context_hooks`, `test_token_budget`, `test_compliance_protocol` | OK |
| `hooks/scripts/codex_edit_gate.py` | `test_codex_edit_gate` | OK |
| 20 lời gọi `subprocess` trong `scripts/` | `test_ma_hoa_subprocess` + trọn suite | OK |
| `.github/workflows/test.yml` | `test_ci_matrix` | OK |
| `README.md`, `docs/kien-truc.md`, `docs/notes/` | `test_docs_consistency` | OK |

### QC-F3

| Ràng buộc (spec §5) | Kiểm | Kết quả |
|---|---|---|
| Tầng "luật bản ngoài" phải viết lại | `test_kien_truc_bo_tang_ban_ngoai_them_adapter` | thay bằng tầng Adapter |
| Code mới chỉ trong `scripts/`/`hooks/` | `## Đã chốt` 2026-09-21 | ngoại lệ adapter đã ghi |
| `skills/` không chép nội dung script | `git status -- skills` | không đổi file nào |
| Chỉ `tdq_state.py` ghi `state.json` | dòng thêm có `state.json` trong `scripts/`, `hooks/` | 0 |
| `CHANGELOG.md` dưới 500 dòng | `wc -l` | 362 |

### QC-F4

- SRP: CÓ. Mỗi hàm mới làm một việc (`co_lenh`, `co_bo_dem_token`, `_is_console`, `_ten_chet`).
- OCP: CÓ. Thêm một lời nhắc sau đầu `SessionStart` là thêm một phần tử vào danh sách `nhac`.
- LSP: CÓ. `_is_console` và `co_bo_dem_token` luôn trả `bool`, kể cả nhánh lỗi.
- ISP: CÓ, sau khi sửa. Tham số `bo_qua_them` của `copy_loc` không còn ai truyền, đã bỏ.
- DIP: CÓ. Phép dò tokenizer đi qua `skill_tokens.nap_bo_dem`/`dem_qua_venv` thay vì tự đoán
  đường venv. Ngoại lệ có chủ đích: `codex_edit_gate.py` chép tại chỗ năm dòng ép UTF-8, vì hook
  đó chạy trong sandbox của Codex và không được import `scripts/` (docstring dòng 26-27).

## Kết luận

PASS toàn bộ, sau một vòng fix. Q6 đỏ ở vòng 1; QC1.1 cắt 11 hằng chết cộng một tham số chết,
phần còn lại không giảm thêm được mà không xoá chức năng, nên dừng vòng fix và hỏi user — user
chốt phương án A và duyệt lại spec ngày 2026-09-23. Không hạng mục nào còn FAIL.

## Hợp đồng skill — `tdq-lean` (dòng `Dùng:` của T2.3)

Chế độ `audit`, chạy trên `scripts/build_portable.py` sau khi ba bundle biến mất.

Không soi bằng mắt: dựng đồ thị gọi bằng `ast`, lấy `main` làm gốc, cắt hai nhánh sinh bundle
claude và codex, rồi xem hàm nào không còn đường tới.

| Tag | Cắt gì | Số dòng |
|---|---|---|
| `delete` | `sinh_ban_codex` | 79 |
| `delete` | `sinh_ban_claude` | 33 |
| `delete` | `_sinh_config_toml` — chỉ sinh `.codex/config.toml` của bundle | 25 |
| `delete` | `_sinh_hooks_codex` | 20 |
| `delete` | `doc_frontmatter` — viết cho adapter của bundle codex | 17 |
| `delete` | `_sinh_settings` | 12 |
| `delete` | `doc_adapter` | 4 |
| `delete` | `_sinh_mcp` | 2 |
| `delete` | hằng `README_CLAUDE`, `README_CODEX`, `TEN_BAN_CLAUDE`, `TEN_BAN_CODEX`, `THU_TU_FILE_WORKFLOW`, `WORKFLOW_DIR` | ~190 |

Kết quả: **1135 → 748 dòng**, cắt 387 dòng, và kiểm bằng `ast` thì không hàm nào còn lại mà
không có nơi gọi.

Ở tầng test, chín lớp kiểm chính hai hàm đã xoá cũng đi theo: `tests/test_build_portable.py`
809 → 346 dòng.

**Một chỗ tôi cắt sai và phải khôi phục:** hằng `PORTABLE_SRC`. Tôi tự liệt kê danh sách hằng
cần cắt thay vì đo nó như đã đo các hàm, và bản agy vẫn đọc `portable_src/skills/` để lấy skill
`tdq-checkportable` — thứ cố ý không nằm trong `skills/` để mọi phiên khỏi phải trả thêm một
dòng mô tả vào ngân sách context. Bài học đúng nghĩa `audit`: đo cả hằng, đừng chỉ đo hàm.

**Một chỗ KHÔNG cắt dù trông thừa:** `doc_frontmatter` bị xoá kéo theo một ca test đang gọi nó.
Cách rẻ là giữ hàm lại cho test chạy. Đã không làm vậy — một helper chỉ còn test gọi là code
chết đội lốt code sống; ca test nay tự đọc khối frontmatter, còn hàm thì đi hẳn.

`Lean already. Ship.` cho phần còn lại: 22 hàm còn sống đều có nơi gọi thật.
