# PLAN — Sửa bốn lỗi đa nền tảng P1–P4
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: ĐÃ DUYỆT · Spec: ../spec/2026-09-03-1733-sua-loi-da-nen-tang.md · Lane: full

Mode thực thi: main — `tdq_bench.py mo-phong` ra `Winner: đội (gap 6.1 phút)`, nhưng con số đó
giả định các task chạy song song được, và ở plan này giả định đó SAI. `scripts/build_portable.py`
bị T2.1/T2.2/T2.3 cùng ghi, `tests/test_sua_da_nen_tang.py` bị sáu task đầu cùng ghi — đúng định
nghĩa file nóng, mà luật file nóng cấm hai worktree cùng lưu một file. Chuỗi phụ thuộc cũng gần
như thẳng: T2.2 và T2.3 phải có hàm của T2.1 mới viết được. Chia đội ở đây đổi 6 phút lý thuyết
lấy conflict thật, nên đề xuất `main`.

## Phase 1 — P2: cổng gác đọc đúng thứ cần đọc

- [x] **T1.1** (e12m) Viết ca test ĐỎ cho cổng gác bundle agy: dựng bundle giả trong thư mục
  tạm, `hooks.json` có dấu `~` nằm trong phần mô tả nhưng KHÔNG có trong `command` → đòi không
  còn NOTE "unexpanded"; bundle giả thứ hai có `command` trỏ vào một thư mục nhà lạ → đòi cảnh
  báo "dựng dưới thư mục nhà khác" phải NỔ. — Test: hai ca đều đỏ trước khi sửa mã
  Chạm: `tests/test_sua_da_nen_tang.py`

- [x] **T1.2** (e10m) Sửa `ghi_chu_antigravity`: parse `hooks.json` bằng JSON, gom mọi giá trị
  `command`, chỉ soi dấu `~` và thư mục nhà trong các giá trị đó; file hỏng JSON thì báo hỏng
  chứ không im. — Test: hai ca của T1.1 chuyển xanh
  Chạm: `scripts/tdq_checkportable.py`

## Phase 2 — P1: tên lệnh Python theo hệ điều hành

- [x] **T2.1** (e10m) Thêm hàm chọn tiền tố lệnh Python nhận hệ điều hành làm THAM SỐ (mặc định
  `sys.platform`): `win32` → `py -3`, còn lại → `python3`. Viết ca test cho cả ba giá trị
  `darwin`, `linux`, `win32` trước khi viết hàm. — Test: ba ca tham số giả lập xanh
  Chạm: `scripts/build_portable.py`, `tests/test_sua_da_nen_tang.py`

- [x] **T2.2** (e12m) Cho hai chỗ sinh `command` của bundle codex và agy gọi qua hàm T2.1,
  bỏ chuỗi `python3` viết cứng. Cả hai hàm sinh nhận thêm tham số hệ điều hành để test giả lập
  được. — Test: gọi hàm sinh với `win32` ra `command` mở đầu `py -3`, với `darwin` ra `python3`
  Chạm: `scripts/build_portable.py`, `tests/test_sua_da_nen_tang.py`

- [x] **T2.3** (e18m) Thêm lệnh con sinh lại `hooks/hooks.json` của Claude Code theo hệ điều
  hành máy đích, giữ nguyên thứ tự sự kiện và biến `${CLAUDE_PLUGIN_ROOT}`, chạy lại nhiều lần
  ra cùng một file. — Test: sinh với `darwin` không đổi file hiện có; sinh với `win32` ra
  `command` mở đầu `py -3`; chạy hai lần liên tiếp file y hệt
  Chạm: `scripts/build_portable.py`, `tests/test_sua_da_nen_tang.py`

## Phase 3 — P4: chuẩn hoá dòng `Test:` của plan

- [x] **T3.1** (e14m) Thêm hàm chuẩn hoá lệnh test trong `tdq_team.py`: token đầu tiên đúng là
  `python3` thì đổi sang chính Python đang chạy, mọi dạng khác giữ NGUYÊN; dòng chứa toán tử
  shell (`&&`, `||`, `|`, `>`) sinh cảnh báo nhưng vẫn chạy. `chay_test_task` gọi qua hàm này.
  — Test: chuỗi mở đầu `python3` bị đổi; chuỗi `mypython3 x` và `pytest -q` giữ nguyên; chuỗi có
  `&&` sinh cảnh báo và vẫn trả lệnh chạy được
  Chạm: `scripts/tdq_team.py`, `tests/test_sua_da_nen_tang.py`

## Phase 4 — P3: cảnh báo cho người ở máy khác

- [x] **T4.1** (e8m) Thêm vào README bundle agy một đoạn nói rõ: bundle gắn với thư mục nhà của
  máy dựng, phải chạy lại `build_portable.py` ở máy đích, và tên lệnh Python khác nhau giữa
  Windows và nơi khác. — Test: `doc_lint.py` exit 0 và ca test đòi README chứa đoạn đó xanh
  Chạm: `antigravity_portable/README.md`, `tests/test_sua_da_nen_tang.py`

## Khối hợp đồng skill

- Dùng: Gác bundle trước khi cài
- Để: sửa `scripts/tdq_checkportable.py` để cổng gác hết dương tính giả và cảnh báo "máy khác" nổ được thật.
- Ra: hai ca test đối xứng — một ca đòi KHÔNG nổ, một ca đòi PHẢI nổ.
- Kiểm: `python3 -m pytest tests/test_sua_da_nen_tang.py -k cong_gac` xanh.
- Không dùng cho: đổi nội dung manifest hay cách so khớp file — chỗ đó đang đúng.

- Dùng: Sinh lại `command` của hook
- Để: sửa `scripts/build_portable.py` để tên lệnh Python sinh theo hệ điều hành nhận qua tham số.
- Ra: ba bundle dựng lại đều CLEAN, `command` đúng tiền tố theo hệ đích.
- Kiểm: `python3 scripts/build_portable.py` rồi `tdq_checkportable.py check` CLEAN cả ba.
- Không dùng cho: sửa nội dung `hooks/scripts/*.py` — spec §2b cấm đụng.

- Dùng: Chạy dòng `Test:` của plan
- Để: sửa `scripts/tdq_team.py` để dòng `Test:` mở đầu `python3` chạy được ở máy không có tên lệnh đó.
- Ra: hàm chuẩn hoá thuần chuỗi, kiểm được không cần chạy test thật.
- Kiểm: `python3 -m pytest tests/test_sua_da_nen_tang.py -k chuan_hoa` xanh.
- Không dùng cho: bỏ `shell=True` — spec §3 đã chốt giữ, bỏ sẽ hỏng plan cũ.

- Dùng: Rà tài liệu sinh ra
- Để: rà mọi `.md` request này sinh hoặc sửa bằng `scripts/doc_lint.py`.
- Ra: exit 0, 0 violation.
- Kiểm: `python3 scripts/doc_lint.py <các file .md>` mã thoát 0.
- Không dùng cho: kiểm nội dung kỹ thuật — việc đó là của bộ test T5.1.

## Phase 5 — Đóng số

- [x] **T5.1** (e12m) Dựng lại cả ba bundle từ nguồn rồi chạy cổng gác trên từng bundle; dán
  output thật vào báo cáo. Chạy toàn bộ suite đúng một lần. — Test: `tdq_checkportable.py check`
  in CLEAN cho cả ba bundle, `pytest -q` không vượt mốc đỏ 100
  Chạm: `portable_claude/`, `portable_codex/`, `antigravity_portable/`

- [x] **T5.2** (e5m) Đóng sổ turn bằng dịch vụ log: `tdq_finish.py --files <các .md> --log
  "<đã làm gì, file nào, kết quả test>" --phase qc`. — Test: lệnh in `✓ tdq_finish` với
  `lint=ok · worklog=ok`
  Chạm: `docs/workinglog/2026-09-03.md`

## Cụm song song

Cụm A (T1.1, T1.2) → Cụm B (T2.1) → Cụm C (T2.2, T2.3) → Cụm D (T3.1) → Cụm E (T4.1) → Cụm F
(T5.1) → T5.2. Ba task T2.1/T2.2/T2.3 cùng ghi `scripts/build_portable.py`, và sáu task đầu cùng
ghi một file test — đó là file nóng, không tách worktree được.

## Definition of Done

Bám §6 của spec, 13 dòng, mỗi dòng một lệnh kiểm:

- [x] Hàm chọn tên lệnh trả `py -3` với `win32`, `python3` với `darwin` và `linux` — `pytest tests/test_sua_da_nen_tang.py -k tien_to`
- [x] Hai chỗ sinh `command` codex và agy không còn chuỗi `python3` viết cứng — `pytest ... -k sinh_command`
- [x] Lệnh sinh lại `hooks/hooks.json` chạy hai lần ra file y hệt — `pytest ... -k bat_bien`
- [x] Lệnh đó với hệ đích Windows ra `command` mở đầu `py -3` — `pytest ... -k hook_claude_win`
- [x] Cổng gác không còn NOTE sai khi `~` chỉ nằm trong mô tả — `pytest ... -k cong_gac_khong_no_sai`
- [x] Cổng gác nổ cảnh báo "thư mục nhà khác" trên bundle giả — `pytest ... -k cong_gac_no_dung`
- [x] Dòng `Test:` mở đầu `python3` được chuẩn hoá, dạng khác giữ nguyên — `pytest ... -k chuan_hoa`
- [x] Dòng `Test:` có toán tử shell sinh cảnh báo mà vẫn chạy — `pytest ... -k canh_bao_shell`
- [x] README bundle agy có đoạn cảnh báo gắn máy dựng — `pytest ... -k readme_agy`
- [x] Ba bundle dựng lại đều CLEAN — `python3 scripts/tdq_checkportable.py check --root <từng bundle>`
- [x] Bộ test riêng của request xanh toàn bộ — `python3 -m pytest tests/test_sua_da_nen_tang.py -q`
- [x] `doc_lint.py` exit 0 trên mọi `.md` của request — `python3 scripts/doc_lint.py <các file>`
- [x] Toàn bộ suite không vượt mốc đỏ 100 — `python3 -m pytest -q`
