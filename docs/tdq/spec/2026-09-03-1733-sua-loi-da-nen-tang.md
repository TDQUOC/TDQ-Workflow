# SPEC — Sửa bốn lỗi đa nền tảng P1–P4
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Bản: 1 · Brief: ../brief/2026-09-03-1733-sua-loi-da-nen-tang.md · Lane: full

## 1. Mục tiêu & phạm vi

**Mục tiêu.** Sửa thật bốn lỗi mà request 2026-09-03-1648 đã tìm ra và cố ý không sửa: P1 (hook
gọi thẳng tên lệnh `python3`), P2 (cảnh báo "bundle dựng ở máy khác" là mã chết), P3 (bundle agy
nướng cứng thư mục nhà mà README không cảnh báo), P4 (`check`/`merge` chạy dòng `Test:` qua
`shell=True`). Sửa xong phải chứng minh được bằng test chạy trên macOS, vì không có máy Windows.

**Trong phạm vi:** `scripts/build_portable.py`, `scripts/tdq_checkportable.py`,
`scripts/tdq_team.py`, `hooks/hooks.json`, `antigravity_portable/README.md`, và ba bundle được
dựng lại từ nguồn.

**Ngoài phạm vi:** 18 chỗ `subprocess` thiếu `encoding=` (đó là C1 — chưa chốt được là lỗi hay
không, phải có máy thật); đường dẫn plugin của agy (C2, hai nguồn còn lệch nhau); hành vi hook
Codex trên Windows native (C3). Ba điểm đó vẫn nằm ở mục "chưa chốt được" của báo cáo 1648.

## Lộ trình

`analyze` (xong) → `spec` → `plan` → `implement` → `qc` → `report`.

Repo này KHÔNG có phase `diagram`: nó không có trong `PHASE_TABLE` của `scripts/tdq_state.py` và
không có skill `tdq-diagram` (repo có 8 skill, không skill nào tên đó). Đây là chỗ luật lệch code
đã ghi nhận ở request 1648, không phải chỗ tôi tự bỏ bước. Luồng cần hình dung vẫn là luồng cũ —
host tra `command` → hệ điều hành phân giải tên lệnh → Python đọc stdin → in quyết định — và
request này sửa đúng mắt xích "phân giải tên lệnh".

## 2. Đầu ra cụ thể

| # | File | Nội dung | Đo bằng gì |
|---|---|---|---|
| Đ1 | `scripts/build_portable.py` | Một hàm chọn tên lệnh Python theo hệ điều hành nhận vào làm THAM SỐ; cả hai chỗ sinh `command` (codex, agy) gọi qua hàm đó | gọi hàm với tham số `win32` ra tiền tố `py -3`, với `linux`/`darwin` ra `python3` |
| Đ2 | `scripts/build_portable.py` | Một lệnh con mới sinh lại `hooks/hooks.json` của Claude Code theo hệ điều hành máy đích, chạy lại nhiều lần vẫn ra một kết quả | chạy hai lần liên tiếp, file không đổi ở lần thứ hai |
| Đ3 | `scripts/tdq_checkportable.py` | Cổng gác đọc `hooks.json` bằng parse JSON và chỉ soi dấu `~` trong các giá trị `command` | trên một bundle giả có `~` nằm trong mô tả nhưng không nằm trong `command` → không còn nổ NOTE sai |
| Đ4 | `scripts/tdq_checkportable.py` | Cảnh báo "bundle dựng dưới thư mục nhà của người khác" nổ được thật | dựng bundle giả với `command` trỏ vào một thư mục nhà lạ → cổng gác in cảnh báo đó |
| Đ5 | `scripts/tdq_team.py` | Dòng `Test:` mở đầu bằng `python3` được đổi sang chính Python đang chạy; dòng chứa toán tử shell bị cảnh báo | gọi hàm chuẩn hoá với chuỗi mẫu, so chuỗi ra |
| Đ6 | `antigravity_portable/README.md` | Một đoạn nói rõ bundle gắn với máy dựng, phải chạy lại `build_portable.py` ở máy đích, và tên lệnh Python khác nhau giữa Windows và nơi khác | `doc_lint.py` exit 0 và đoạn đó tồn tại |
| Đ7 | Bộ test riêng của request | Ca test cho từng đầu ra Đ1–Đ6, chạy được trên macOS | toàn bộ ca xanh |

## 2b. Ranh giới module

| Module | Vùng file | Vai trò trong request này | Phụ thuộc |
|---|---|---|---|
| Sinh bundle | `scripts/build_portable.py` | Nơi sửa P1 cho codex + agy (Đ1) và thêm lệnh sinh hook Claude (Đ2) | đọc `hooks/`, `skills/`, `agents/` |
| Cổng gác bundle | `scripts/tdq_checkportable.py` | Nơi sửa P2 (Đ3, Đ4) | đọc `hooks.json` và manifest |
| Chạy lệnh test | `scripts/tdq_team.py` | Nơi sửa P4 (Đ5) | shell của hệ điều hành, `git` |
| Hook nguồn | `hooks/hooks.json` | File viết tay, bị Đ2 sinh lại | host Claude Code |
| Tài liệu bundle | `antigravity_portable/README.md` | Nơi sửa P3 (Đ6) | không |
| Đầu ra kiểm | bộ test riêng của request | Chứng minh cả sáu đầu ra trên | đọc năm module trên |

Ràng buộc cứng: **không đụng `hooks/scripts/*.py`**. Sửa hành vi bên trong hook là việc khác,
không nằm trong P1–P4.

## 3. Cách tiếp cận & lý do

**Nguyên tắc xuyên suốt: hệ điều hành là THAM SỐ, không phải thứ đọc lén.** Mọi chỗ quyết định
tên lệnh nhận hệ điều hành qua đối số, mặc định là `sys.platform`. Đây không phải cầu kỳ thừa —
đó là điều kiện duy nhất để kiểm được hành vi Windows từ máy macOS, đúng như user chốt ở 3A.

**P1 chia hai nhóm host, vì `hooks/hooks.json` là file nguồn viết tay.** Codex và agy có
`command` do `build_portable.py` sinh (`:673`, `:905`), mà lệnh build chạy TẠI máy đích — sửa ở
đó là đủ. Còn `hooks/hooks.json` được commit sẵn và dùng chung cho mọi máy, không qua bước sinh
nào; nên thêm một lệnh con để người ở máy Windows sinh lại file đó một lần. File vẫn giữ mặc
định `python3` trong repo, vì đó là giá trị đúng cho macOS và Linux — tuyệt đại đa số người dùng.

**Chọn `py -3` chứ không phải `python`.** `py` là trình khởi chạy chính thức đi kèm bản cài
Python trên Windows và luôn trỏ đúng Python 3; còn `python` trên nhiều bản Linux không tồn tại,
và trên Windows có thể là cái stub của Microsoft Store mở cửa hàng ứng dụng thay vì chạy Python.

**P2 sửa bằng cách đọc đúng thứ cần đọc.** Lỗi gốc là quét văn bản thô cả file, trong khi chỉ
các giá trị `command` mới đáng quan tâm. Parse JSON rồi duyệt — vừa hết dương tính giả, vừa làm
nhánh cảnh báo "máy khác" sống lại.

**P4 sửa ở tầng chuẩn hoá chuỗi, không đổi `shell=True`.** Bỏ `shell=True` sẽ làm hỏng mọi dòng
`Test:` đang dùng toán tử shell trong các plan cũ. Thay vào đó: đổi tên lệnh `python3` ở đầu dòng
sang chính Python đang chạy, và CẢNH BÁO (không từ chối) khi dòng `Test:` chứa toán tử shell —
vì cú pháp đó khác nhau giữa `cmd.exe` và `sh`.

## 3b. Năng lực & công cụ

| Việc cần | Công cụ sẵn có | Phán quyết | Lý do |
|---|---|---|---|
| Sinh lại `command` của hook | `scripts/build_portable.py` | DÙNG | nơi duy nhất sinh `command` cho bundle codex và agy |
| Gác bundle trước khi cài | `scripts/tdq_checkportable.py` | DÙNG | chỗ P2 nằm, và là nơi cảnh báo P3 phải nổ |
| Chạy dòng `Test:` của plan | `scripts/tdq_team.py` | DÙNG | chỗ P4 nằm |
| Rà tài liệu sinh ra | `scripts/doc_lint.py` | DÙNG | mọi `.md` của request phải exit 0 |
| Đo lại số liệu đa nền tảng | `tools_kiem/dem_da_nen_tang.py` | NỀN | đã có từ request 1648, nay thành thước nghiệm thu chứ không sửa |
| Chạy thử trên máy Windows | máy thật | KHÔNG | thiếu quyền/công cụ — vẫn không có máy, thay bằng test tham số giả lập |
| Viết lại hook bằng Node | `node` | KHÔNG | spec §3 đã chọn cách khác tốt hơn — user chốt 1A, và Codex/agy không bảo đảm có Node |

## 4. Yêu cầu thường trực

- Dịch vụ log BẬT mặc định; mọi turn đóng sổ bằng `tdq_finish.py --log`.
- Không placeholder: thiếu thông tin nghĩa là phân tích còn hụt, phải nói ra chứ không viết bừa.
- Mỗi đầu ra Đ1–Đ6 có ít nhất một ca test riêng (Đ7).
- Đỏ trước, xanh sau: mỗi task viết ca kiểm cho thất bại trước khi sửa mã.

## 5. Ràng buộc & rủi ro

**Ràng buộc.**
- R1 — Windows nghĩa là PowerShell thuần / cmd.exe. Không được viện tới Git Bash hay WSL.
- R2 — Không có máy Linux/Windows thật. Cấm dùng chữ "đã chạy được trên Windows"; mức cao nhất
  được phép là "test tham số giả lập cho ra đúng tên lệnh mong đợi".
- R3 — Không đụng `hooks/scripts/*.py`, không đụng 18 chỗ `subprocess` của C1.
- R4 — Ba bundle dựng lại xong, `tdq_checkportable.py check` phải in CLEAN cho cả ba.

**Rủi ro.**
- Ru1 — **Sửa P1 làm hỏng macOS/Linux đang chạy tốt.** Chặn: hàm chọn tên lệnh có ca test cho cả
  ba giá trị `darwin`, `linux`, `win32`; và mốc đỏ `pytest -q` không được vượt 100.
- Ru2 — **Sửa P2 làm cổng gác câm hẳn thay vì hết dương tính giả.** Chặn: Đ4 bắt buộc có ca test
  dựng bundle giả với thư mục nhà lạ và đòi cảnh báo NỔ, chứ không chỉ ca "không nổ sai".
- Ru3 — **Lệnh sinh lại `hooks/hooks.json` làm bẩn git ở máy người dùng.** Chặn: lệnh phải bất
  biến (chạy lại không đổi file) và Đ6 nói rõ đây là bước tự chọn, chỉ máy Windows mới cần.
- Ru4 — **Đổi tên lệnh trong dòng `Test:` làm hỏng plan cũ.** Chặn: chỉ đổi khi token ĐẦU TIÊN
  đúng là `python3`, mọi dạng khác giữ nguyên; có ca test cho chuỗi không được đụng tới.

## 6. QC & Definition of Done

- [ ] Hàm chọn tên lệnh trả `py -3` với tham số `win32`, `python3` với `darwin` và `linux`.
- [ ] Cả hai chỗ sinh `command` cho codex và agy đều đi qua hàm đó, không còn chuỗi `python3` viết cứng.
- [ ] Lệnh sinh lại `hooks/hooks.json` chạy hai lần cho ra file y hệt nhau.
- [ ] Lệnh đó với hệ đích Windows cho ra `command` mở đầu bằng `py -3`.
- [ ] Cổng gác không còn in NOTE "unexpanded `~`" khi dấu `~` chỉ nằm trong phần mô tả.
- [ ] Cổng gác IN được cảnh báo "dựng dưới thư mục nhà khác" trên bundle giả có thư mục nhà lạ.
- [ ] Dòng `Test:` mở đầu `python3` được chuẩn hoá sang Python đang chạy; dạng khác giữ nguyên.
- [ ] Dòng `Test:` chứa toán tử shell sinh ra cảnh báo, và vẫn chạy chứ không bị từ chối.
- [ ] README bundle agy có đoạn cảnh báo gắn máy dựng và khác biệt tên lệnh Python.
- [ ] Dựng lại cả ba bundle, `tdq_checkportable.py check` in CLEAN cho từng bundle.
- [ ] Bộ test riêng của request chạy xanh, mỗi đầu ra Đ1–Đ6 có ít nhất một ca.
- [ ] `doc_lint.py` exit 0 trên mọi `.md` của request.
- [ ] `pytest -q` toàn bộ không vượt mốc đỏ 100 có sẵn.

## 7. Câu hỏi còn treo

Không còn. Bốn câu hỏi của phase analyze đã được user chốt bằng "1A 2A 3A".
