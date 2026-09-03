# BRIEF — Sửa 4 lỗi đa nền tảng P1–P4
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> vậy hãy mở request sửa p1-p4

**Cách tôi đọc yêu cầu này**

- **Mục tiêu:** sửa thật 4 phát hiện mà request `2026-09-03-1648-kiem-da-nen-tang-host` đã tìm
  ra và cố ý để nguyên, để bộ workflow chạy được ở máy khác và trên Windows PowerShell thuần.
- **Bốn thứ phải sửa:** P1 hook gọi thẳng `python3` (3 host) · P2 cổng gác "bundle dựng ở máy
  khác" là mã chết ở `tdq_checkportable.py:367` · P3 bundle agy nướng cứng `$HOME` máy dựng,
  README không cảnh báo · P4 `tdq_team.py:896` chạy `Test:` qua `shell=True`.
- **Phạm vi đoán:** `scripts/build_portable.py`, `scripts/tdq_checkportable.py`,
  `scripts/tdq_team.py`, `hooks/hooks.json`, README của 3 bundle, và 3 bundle phải dựng lại.
- **Ràng buộc kế thừa:** Windows nghĩa là PowerShell thuần / cmd.exe, KHÔNG phải Git Bash hay
  WSL. Vẫn không có máy Linux/Windows thật để chạy thử.
- **Chỗ chưa rõ, phải hỏi:**
  1. P1 có 3 cách sửa đánh đổi khác nhau (nướng `sys.executable` lúc build / sinh `command`
     theo hệ đích / bắt người dùng tự tạo bí danh) — chọn cách nào là quyết định của user.
  2. Sửa cả 4 hay chỉ P2+P3 (rẻ, chắc, không cần máy thật) rồi để P1+P4 lại?
  3. Không có máy Windows để nghiệm thu thì nhận bằng chứng ở mức nào là đủ?

## Hiểu & kiến thức

### B0 — Kiểm kê năng lực

| Việc cần | Công cụ sẵn có | Phán quyết | Lý do |
|---|---|---|---|
| Sinh lại `command` của hook | `scripts/build_portable.py` | DÙNG | nơi duy nhất sinh `command` cho bundle codex + agy |
| Cổng gác bundle | `scripts/tdq_checkportable.py` | DÙNG | chỗ P2 nằm, và là nơi thêm cảnh báo mới |
| Rà tài liệu | `scripts/doc_lint.py` | DÙNG | README bundle sửa xong phải exit 0 |
| Đo lại số liệu | `tools_kiem/dem_da_nen_tang.py` | DÙNG | đã có từ request 1648, nay thành thước nghiệm thu |
| Chạy thử trên Windows | máy thật | KHÔNG | thiếu quyền/công cụ — vẫn không có máy, nghiệm thu bằng giả lập |

### Điều quan trọng nhất tìm được ở phase này

**`hooks/hooks.json` là file NGUỒN viết tay, không phải file sinh ra.** Đây là khác biệt quyết
định cách sửa P1, và nó chia 3 host làm hai nhóm:

- **Codex và agy:** `command` do `build_portable.py` sinh (`:673` và `:905`). Sửa ở đó là sửa
  được, vì lệnh build chạy TẠI máy đích.
- **Claude Code:** `hooks/hooks.json` là file trong repo, commit sẵn, mọi máy dùng chung một
  nội dung. Không có bước sinh nào để chèn tên lệnh theo hệ điều hành. Vì vậy P1 ở nhóm này
  KHÔNG sửa được bằng cách "sinh theo hệ đích" — phải chọn một tên lệnh chạy được ở cả ba hệ,
  hoặc thêm một bước cài đặt mới.

**P1 là lỗi đã biết của cả hệ sinh thái, không riêng TDQ.** Chính plugin chính chủ của Anthropic
cũng dính đúng bệnh này: [security-guidance dùng `python3` trong hook](https://github.com/anthropics/claude-code/issues/46449),
[Hookify hỏng trên Windows](https://github.com/anthropics/claude-plugins-official/issues/85).
Điều đó có nghĩa: cách sửa nào được cộng đồng dùng thì đã có tiền lệ, không phải tự nghĩ ra.

### Bốn cách sửa P1, đánh đổi khác nhau

1. **Đổi `python3` → `python`.** Rẻ nhất, một dòng. Nhưng trên nhiều bản Linux `python` không
   tồn tại (Debian/Ubuntu bỏ hẳn), hoặc từng trỏ vào Python 2. Đổi một lỗi Windows lấy một lỗi
   Linux.
2. **Sinh `command` theo hệ đích lúc build.** `py -3` trên Windows, `python3` nơi khác. Sửa
   được codex + agy triệt để; nhưng KHÔNG áp dụng được cho `hooks/hooks.json` của Claude Code
   vì file đó không qua bước sinh nào.
3. **Nướng `sys.executable` tuyệt đối lúc build.** Chắc nhất — dùng đúng Python đang chạy lệnh
   build. Đổi lại bundle gắn chặt với máy dựng, tức lan bệnh P3 từ agy sang cả 3 host; bù lại
   nếu P2 được sửa thì cổng gác sẽ bắt được việc copy nhầm.
4. **Dùng `node` thay Python cho lớp vỏ.** Claude Code luôn có Node, nên `node` chắc chắn phân
   giải được ở cả 3 hệ. Nhưng Codex và agy không bảo đảm có Node, và phải viết lại 8 hook —
   đắt nhất, và đổi ngôn ngữ chỉ vì một tên lệnh.

Cách 2 và 3 kết hợp được: sinh theo hệ đích cho bundle, còn `hooks/hooks.json` xử lý riêng.

### P2, P3, P4 — không có ngã rẽ nào, sửa thế nào đã rõ

- **P2:** parse JSON rồi chỉ soi dấu `~` trong các giá trị `command`, thay vì quét văn bản thô
  cả file. Vài dòng, và có thể viết test đỏ trước rất gọn.
- **P3:** thêm cảnh báo vào README bundle agy + để cổng gác P2 nổ thật. Không đổi cách nướng
  `$HOME` vì cách đó đúng.
- **P4:** hết theo P1. Có thể siết thêm: từ chối dòng `Test:` chứa toán tử shell (`&&`, `|`,
  `>`), vì cú pháp đó khác nhau giữa cmd.exe và sh.

### Lộ trình

`analyze` → `spec` → `plan` → `implement` → `qc` → `report`. Repo này KHÔNG có phase `diagram`
(không có trong `PHASE_TABLE` của `tdq_state.py`, không có skill `tdq-diagram`) — đã xác nhận ở
request 1648.

Nghiệm thu: vì vẫn không có máy Windows, mỗi thứ sửa phải có một test CHẠY ĐƯỢC TRÊN macOS mà
vẫn chứng minh được hành vi Windows — ví dụ gọi thẳng hàm sinh `command` với tham số hệ điều
hành giả lập, thay vì tin vào mắt.

## Hỏi đáp

**Hỏi 1 — chọn pipeline nào?** → **1A**: chế độ chuyên sâu (deep).

**Hỏi 2 — sửa P1 thế nào?** → **1A**: sinh `command` theo hệ đích cho bundle codex + agy
(`py -3` trên Windows, `python3` nơi khác); riêng `hooks/hooks.json` của Claude Code — file
nguồn viết tay, dùng chung mọi máy — thêm một lệnh sinh lại tại máy đích.

**Hỏi 3 — sửa hết bốn lỗi hay chỉ phần chắc ăn?** → **2A**: sửa cả P1–P4.

**Hỏi 4 — nghiệm thu tới mức nào khi không có máy Windows?** → **3A**: test gọi thẳng hàm sinh
`command` với tham số hệ điều hành GIẢ LẬP. Đây là ràng buộc thiết kế, không chỉ là cách kiểm:
mọi chỗ quyết định tên lệnh phải nhận hệ điều hành làm THAM SỐ, không được đọc thẳng
`sys.platform` bên trong — có thế mới kiểm được hành vi Windows từ macOS.
