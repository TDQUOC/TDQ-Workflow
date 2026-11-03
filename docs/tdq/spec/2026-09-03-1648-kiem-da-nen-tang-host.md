# SPEC — Kiểm bộ workflow chạy được ở máy khác và trên Linux/Windows
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Bản: 1 · Brief: ../brief/2026-09-03-1648-kiem-da-nen-tang-host.md · Lane: full

## 1. Mục tiêu & phạm vi

**Mục tiêu.** Trả lời bằng bằng chứng đọc từ mã nguồn, không phải bằng phỏng đoán: bộ workflow
TDQ — 3 bundle portable cho Claude Code, Codex CLI, Antigravity CLI (agy) — mang sang máy khác
thì vướng gì, và chạy trên Linux hay Windows thì hỏng ở đâu. Đầu ra là TÀI LIỆU, không sửa mã.

**Trong phạm vi:** `scripts/`, `hooks/`, 3 thư mục bundle, `build_portable.py`,
`tdq_checkportable.py`, README của từng bundle (đọc, không sửa).

**Ngoài phạm vi (user chọn 4b):** mọi thay đổi mã sản phẩm, kể cả bản vá một dòng cho P2. Cũng
ngoài phạm vi: đổi đường dẫn plugin của agy, sửa 18 chỗ `subprocess`, đổi `python3` thành
trình khởi chạy khác. Tất cả đi vào mục "đề xuất sửa" của báo cáo, để request sau thực thi.

## Lộ trình

`analyze` (xong) → `spec` → `diagram` → `plan` → `implement` → `qc` → `report`. Không bỏ phase
nào. `diagram` vẽ đúng một luồng: **một hook chạy từ lúc host gọi tới lúc trả quyết định** —
host tra `command` trong `hooks.json` → hệ điều hành phân giải tên `python3` → Python đọc JSON
từ stdin → script chạy → in quyết định ra stdout → host đọc lại. P1 cắt luồng ở bước phân giải
tên, câu hỏi console-encoding cắt ở bước in ra stdout; có sơ đồ mới chỉ được chính xác hai chỗ
đứt đó.

## 2. Đầu ra cụ thể

| # | File | Nội dung | Đo bằng gì |
|---|---|---|---|
| Đ1 | `docs/tdq/report/<slug>-tuong-thich.md` | Báo cáo tương thích: mỗi phát hiện một khối gồm triệu chứng, vị trí `file:dòng`, hệ điều hành bị dính, mức nguy, cách sửa đề xuất | ≥ 4 phát hiện P1–P4, mỗi khối đủ 5 trường, mọi vị trí trỏ đúng dòng thật |
| Đ2 | `docs/tdq/report/<slug>-lenh-kiem.md` | Danh sách lệnh để user tự chạy trên máy Linux và máy Windows; mỗi lệnh nêu "đạt là thấy gì / hỏng là thấy gì" | ≥ 6 lệnh, chia 2 nhóm Linux / Windows, không lệnh nào cần Git Bash hay WSL |
| Đ3 | Mục "điểm mạnh" trong Đ1 | Những chỗ ĐÃ an toàn, kèm số đo, để request sau không sửa nhầm | ≥ 3 mục, mỗi mục một con số đếm được |
| Đ4 | Mục "chưa chốt được" trong Đ1 | Chỗ chỉ máy thật mới trả lời, nêu rõ vì sao chưa chốt | ≥ 3 mục, mỗi mục nối tới một lệnh trong Đ2 |
| Đ5 | Bộ test tự động cho báo cáo | Ca test kiểm chính các con số của Đ1 để báo cáo không mục theo thời gian | bộ test riêng của request chạy xanh |

## 2b. Ranh giới module

| Module | Vùng file | Vai trò trong request này | Phụ thuộc |
|---|---|---|---|
| Sinh bundle | `scripts/build_portable.py` | Nơi mọi `command` của hook ra đời — gốc của P1 và P3 | đọc `hooks/`, `skills/`, `agents/` |
| Kiểm bundle | `scripts/tdq_checkportable.py` | Cổng gác bundle — nơi P2 nằm | đọc manifest do build sinh ra |
| Hook thời chạy | `hooks/hooks.json` + `hooks/scripts/*.py` | Thứ host thật sự chạy — nơi câu hỏi encoding nằm | stdin/stdout của host |
| Chạy lệnh ngoài | `tdq_team.py`, `tdq_finish.py`, `tdq_eval.py`, `tdq_bench.py`, `tdq_lsp.py` | 18 chỗ `subprocess(text=True)` và `shell=True` (P4) | `git`, `python3`, shell của hệ điều hành |
| Đầu ra request | `docs/tdq/report/` và bộ test riêng của request | Vùng DUY NHẤT được ghi ở request này | đọc 4 module trên |

Ràng buộc cứng: 4 module đầu **chỉ được đọc**. Task nào ghi ra ngoài vùng "Đầu ra request" là
vi phạm 4b, không phải sáng kiến.

## 3. Cách tiếp cận & lý do

Kiểm bằng ba lớp, xếp theo độ tin cậy giảm dần, và báo cáo phải NÓI RÕ mỗi phát hiện đứng ở
lớp nào:

1. **Đọc mã bằng `ast`, không bằng grep.** Đếm `subprocess` thiếu `encoding=`, `open()` thiếu
   `encoding=`, lời gọi stdlib chỉ có trên POSIX. Đây là số đếm chính xác, không phải ước lượng.
2. **Chạy giả lập trên macOS.** Ví dụ: tạm ẩn `python3` khỏi PATH rồi chạy hook để thấy đúng
   triệu chứng Windows sẽ gặp; ép `PYTHONIOENCODING=cp1252` rồi chạy hook có tiếng Việt.
   Giả lập tái hiện được cơ chế hỏng, nhưng không thay thế máy thật.
3. **Đối chiếu tài liệu host.** Codex CLI và agy đều đổi nhanh; mọi khẳng định về hành vi host
   phải có link nguồn ngay tại chỗ.

Vì sao không tự sửa luôn: user chọn 4b. Và P1 có ít nhất 3 cách sửa khác nhau (dò
`python`/`py`/`sys.executable` lúc build; viết script bọc; yêu cầu người dùng tự đặt bí danh),
mỗi cách đánh đổi khác nhau — chọn cách nào là quyết định của user ở request sau, không phải
quyết định lén trong một request đang mang danh "đi kiểm".

## 3b. Năng lực & công cụ

| Việc cần | Công cụ sẵn có | Phán quyết | Lý do |
|---|---|---|---|
| Kiểm bundle khớp manifest | `scripts/tdq_checkportable.py` | DÙNG | cổng gác bundle, đồng thời là đối tượng bị kiểm (P2) |
| Dựng lại bundle | `scripts/build_portable.py` | DÙNG | chỉ chạy để quan sát đầu ra, không sửa |
| Rà tài liệu sinh ra | `scripts/doc_lint.py` | DÙNG | mọi `.md` của request phải exit 0 |
| Quét mã theo cú pháp | `ast` của Python | DÙNG | thay grep cho mọi con số trong báo cáo |
| Tra tài liệu host | WebSearch | DÙNG | Codex và agy đổi nhanh, mỗi khẳng định kèm link |
| Chạy thử trên Linux/Windows | máy thật | KHÔNG | thiếu quyền/công cụ — user đã chốt 3a là không có máy; thay bằng Đ2 |
| Sửa các chỗ hỏng tìm được | `tdq-build` | KHÔNG | user đã cấm — 4b chốt request này chỉ báo cáo |

## 4. Yêu cầu thường trực

- Dịch vụ log BẬT mặc định; mọi turn đóng sổ bằng `tdq_finish.py --log`.
- Không placeholder: thiếu thông tin nghĩa là phân tích còn hụt, phải nói ra chứ không viết bừa.
- Mỗi phần có test: Đ5 giữ các con số của báo cáo khỏi mục.
- Mọi con số trong báo cáo phải kèm lệnh tái lập được nó.

## 5. Ràng buộc & rủi ro

**Ràng buộc.**
- R1 — Không sửa mã sản phẩm (4b). Vùng ghi duy nhất: thư mục báo cáo và bộ test riêng của request.
- R2 — Windows nghĩa là PowerShell thuần / cmd.exe (2b). Lệnh nào trong Đ2 cần Git Bash hay WSL
  là lệnh sai, phải viết lại.
- R3 — Không có máy thật (3a). Cấm dùng chữ "đã chạy được trên Linux/Windows" ở bất kỳ đâu; mức
  cao nhất được phép là "đọc mã không thấy lỗi".

**Rủi ro.**
- Ru1 — **Kết luận quá tay.** Giả lập trên macOS dễ bị kể lại thành bằng chứng máy thật. Chặn:
  mỗi phát hiện trong Đ1 mang nhãn lớp bằng chứng (`đọc mã` / `giả lập` / `tài liệu`), Đ5 có ca
  kiểm mọi phát hiện đều có nhãn.
- Ru2 — **Trượt sang sửa.** P2 sửa mất 1 phút, rất dễ "tiện tay". Chặn: R1 + ranh giới §2b, và
  QC có hạng mục `git diff --stat` không được chạm file nào ngoài vùng cho phép.
- Ru3 — **Đường dẫn plugin agy còn tranh chấp.** Tài liệu công khai lệch với đường dẫn repo đang
  dùng. Chặn: ghi vào Đ4 là "chưa chốt", kèm lệnh trong Đ2 để user tự kiểm trên máy có agy; cấm
  sửa theo bài blog.
- Ru4 — **Báo cáo mục theo thời gian.** Số 18 sẽ đổi khi mã đổi. Chặn: Đ5 tự đếm lại bằng `ast`
  và so với số đã ghi.

## 6. QC & Definition of Done

- [ ] Đ1 tồn tại, có đủ 4 phát hiện P1–P4, mỗi phát hiện đủ 5 trường và có nhãn lớp bằng chứng.
- [ ] Mọi vị trí `file:dòng` trong Đ1 trỏ đúng nội dung thật — kiểm bằng script đọc lại từng dòng.
- [ ] Đ2 có ≥ 6 lệnh, chia đúng 2 nhóm Linux / Windows.
- [ ] Không lệnh nào trong Đ2 nhắc tới `bash`, `sh`, `wsl` ở nhóm Windows — kiểm bằng grep.
- [ ] Đ3 có ≥ 3 điểm mạnh, mỗi điểm kèm con số tái lập được.
- [ ] Đ4 có ≥ 3 mục chưa chốt, mỗi mục nối tới ít nhất một lệnh trong Đ2.
- [ ] Không chỗ nào trong Đ1/Đ2 khẳng định "đã chạy được trên Linux/Windows" — kiểm bằng grep.
- [ ] Bộ test riêng của request chạy xanh, không ca đỏ.
- [ ] `doc_lint.py` exit 0 trên Đ1 và Đ2.
- [ ] `git diff --name-only` chỉ liệt kê file trong vùng "Đầu ra request" của §2b.
- [ ] `pytest -q` toàn bộ không vượt mốc đỏ 100 có sẵn.

## 7. Câu hỏi còn treo

Không còn. Bốn câu hỏi của phase analyze đã được user chốt bằng "1a 2b 3a 4b".
