# PLAN — Setup tự phát hiện và bật plugin tdq-workflow chưa bật ở scope user

Ngày: 2026-10-11 · Spec: ../spec/2026-10-11-1724-unknown-skill-plugin-chua-nap.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — chuỗi phụ thuộc thẳng P1 → P2 → P3, nhiều task cùng chạm `scripts/tdq_setup.py` (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- Cụm song song
- P1 — Ghi settings dùng chung
- P2 — Bậc kiểm plugin + khối ghim trong setup
- P3 — Tài liệu và áp lên máy
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. Test không bao giờ chạm `~/.claude` thật: mọi hàm mới nhận `home`/đường dẫn làm tham số, test dùng `tempfile`.
6. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
7. Không commit/push cho đến khi user yêu cầu.

## Cụm song song

Một cụm vì `scripts/tdq_setup.py` là file nóng (T2.1, T2.2, T2.3 cùng chạm) và P2 phụ thuộc hàm của P1; chạy song song không rút được thời gian (bench: main thắng 1,1 phút).

## P1 — Ghi settings dùng chung
- [x] **T1.1** (e6m) Thêm hàm public `bat_khoa(path, key)` vào `scripts/plugin_tiers.py`:
  - đọc settings bằng `_load_json`; file hỏng hoặc `enabledPlugins` không phải object → trả `(False, lý do)`, không ghi;
  - khóa đã `True` → trả `(False, "đã bật")`, không ghi;
  - còn lại → đặt `True` và ghi bằng `_write_settings` (nguyên tử + `.bak`), log `key: cũ→True`, trả `(True, mô tả)`.
  - `cmd_enable` giữ nguyên hành vi.
  - Test: `python -m pytest tests/test_plugin_tiers.py -q` (thêm 4 ca: bật mới, đã bật, file hỏng, giữ khóa khác + `.bak` chứa bản cũ)
  - Chạm: `scripts/plugin_tiers.py`, `tests/test_plugin_tiers.py`

**Xong P1 khi**: 4 ca mới và toàn bộ test cũ của `test_plugin_tiers.py` xanh.

## P2 — Bậc kiểm plugin + khối ghim trong setup
- [x] **T2.1** (e10m) Thêm `kiem_plugin_user(home=None, goc_plugin=None, cham_may=None)` vào `scripts/tdq_setup.py`, trả `(da_cai, canh_bao, no)`:
  - đọc `<home>/.claude/plugins/installed_plugins.json`, lấy bản cài `tdq-workflow@*` có `scope == "user"` (khóa + `version`);
  - không có bản cài → nợ `plugin tdq-workflow chưa cài ở scope user — chạy /plugin install tdq-workflow@tdq-local`;
  - có bản cài nhưng `<home>/.claude/settings.json` chưa bật khóa đó → `_khong_cham_may()` thì chỉ ghi nợ; ngược lại gọi `plugin_tiers.bat_khoa`, thành công thì `đã cài · bật plugin <khóa> ở scope user (mở phiên mới để nạp)`, lỗi thì ghi nợ;
  - `version` ≠ `doc_phien_ban_plugin(goc_plugin)` → cảnh báo `bản cài <khóa> <v_cài> lệch instruction <v_gốc> — chạy /plugin update <khóa>`;
  - mỗi nhánh log qua `_log()`.
  - Test: `python -m pytest tests/test_tdq_setup.py -q -k plugin_user` (5 ca với HOME tạm: chưa bật → bật + `.bak`; đã bật → không ghi; chưa cài → nợ; lệch phiên bản → cảnh báo; `TDQ_KHONG_CHAM_MAY=1` → không ghi)
  - Chạm: `scripts/tdq_setup.py`, `tests/test_tdq_setup.py`
  - Dùng: `tdq-setup`
  - Để: bám khung bậc kiểm/nợ/cảnh báo sẵn có của setup, nạp skill TRƯỚC bước đỏ
  - Ra: hàm `kiem_plugin_user` trong `scripts/tdq_setup.py`
  - Kiểm: `python -m pytest tests/test_tdq_setup.py -q -k plugin_user`
  - Không dùng cho: cài/cập nhật plugin qua harness (`/plugin install|update`)
- [x] **T2.2** (e5m) Gọi `kiem_plugin_user()` trong `main()` (ngay sau `va_hook_xung_dot`), gộp `da_cai`/`canh_bao`/`no`. Mock `kiem_plugin_user` ở mọi test đang chạy `main()`.
  - Test: `python -m pytest tests/test_tdq_setup.py tests/test_mot_lenh_kiem.py tests/test_tu_khoi_tao.py -q`
  - Chạm: `scripts/tdq_setup.py`, `tests/test_tdq_setup.py`, `tests/test_mot_lenh_kiem.py`, `tests/test_tu_khoi_tao.py`
- [x] **T2.3** (e5m) Thêm dòng dự phòng vào `KHOI_HUONG_DAN` (mục "Nguyên tắc TDQ Workflow bắt buộc", ≤ 300 ký tự): gọi skill báo `Unknown skill` → plugin chưa bật ở project này: đọc `{goc}/skills/tdq-intake/SKILL.md` trên đĩa, thay `${CLAUDE_PLUGIN_ROOT}` bằng `{goc}`, làm theo, nhắc người dùng chạy `python3 {goc}/scripts/tdq_setup.py`. Chép nguyên văn khối (với `GOC_MAU`) sang `docs/claude-md-mau.md`.
  - Test: `python -m pytest tests/test_claude_md_core.py tests/test_auto_update_setup.py -q`
  - Chạm: `scripts/tdq_setup.py`, `docs/claude-md-mau.md`

**Xong P2 khi**: các test của T2.1–T2.3 xanh, dòng dự phòng ≤ 300 ký tự.

## P3 — Tài liệu và áp lên máy
- [x] **T3.1** (e4m) Thêm vào `docs/notes/user-level-install.md` mục "Plugin phải bật ở scope user": triệu chứng `Unknown skill` ở project chưa bật, setup tự bật, việc còn lại phải tự làm (`/plugin update`, mở phiên mới).
  - Test: `python -m pytest tests/test_docs_consistency.py -q`
  - Chạm: `docs/notes/user-level-install.md`
- [x] **T3.2** (e4m) Chạy setup thật trên máy: `python3 scripts/tdq_setup.py`. Kiểm `enabledPlugins` có `tdq-workflow@tdq-local: true`, có `settings.json.bak`, output có dòng cảnh báo lệch `0.59.0`, và `~/.claude/CLAUDE.md` có dòng dự phòng.
  - Test: `python3 -c "import json,os;d=json.load(open(os.path.expanduser('~/.claude/settings.json'),encoding='utf-8'));assert d['enabledPlugins']['tdq-workflow@tdq-local'] is True"`
  - Chạm: `~/.claude/settings.json`, `~/.claude/CLAUDE.md`
- [x] **T3.3** (e3m) Cập nhật token budget nếu khối/tài liệu đổi trần: `python3 scripts/token_budget.py`.
  - Test: `python -m pytest tests/test_doc_lint.py tests/test_luat_skill.py tests/test_skill_shape.py -q`
  - Chạm: `docs/tdq/token-budget.json`

**Xong P3 khi**: tài liệu có mục mới, máy này đã bật plugin, token budget hợp lệ.

## Definition of Done
- [x] DoD 1 (Q1): `python -m pytest tests/test_plugin_tiers.py -q` xanh.
- [x] DoD 2 (Q2): `python -m pytest tests/test_tdq_setup.py -q -k plugin_user` xanh (5 ca, HOME tạm).
- [x] DoD 3 (Q3): `python -m pytest tests/test_claude_md_core.py -q` xanh và dòng dự phòng ≤ 300 ký tự.
- [x] DoD 4 (Q4): `python -m pytest tests/test_tdq_setup.py tests/test_tdq_setup_skill.py tests/test_setup_status.py tests/test_setup_status_render.py tests/test_plugin_tiers.py tests/test_claude_md_core.py tests/test_mot_lenh_kiem.py tests/test_tu_khoi_tao.py tests/test_auto_update_setup.py tests/test_docs_consistency.py -q` xanh.
- [x] DoD 5 (Q5): lệnh kiểm của T3.2 thoát 0.

## QC vòng 1 — fix
- [x] **QC1.1** Dòng dự phòng viết tên biến plugin dưới dạng `${{...}}` trong `KHOI_HUONG_DAN` → `build_portable` đếm còn 1 lần `CLAUDE_PLUGIN_ROOT` mà không thay được, bản Antigravity vỡ. Đưa biến vào qua tham số `format` (literal `${CLAUDE_PLUGIN_ROOT}`) để bộ build thay như mọi chỗ khác. — Test: `python -m pytest tests/test_tuong_thich_host.py tests/test_build_portable.py tests/test_claude_md_core.py -q`
