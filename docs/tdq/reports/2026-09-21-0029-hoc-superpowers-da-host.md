# REPORT — Học cách tổ chức của superpowers: một nguồn, adapter mỏng, chạy đa nền tảng

Ngày: 2026-09-23 · Spec: ../spec/2026-09-21-0029-hoc-superpowers-da-host.md ·
Plan: ../plan/2026-09-21-0029-hoc-superpowers-da-host.md ·
QC: ../qc/2026-09-21-0029-hoc-superpowers-da-host.md
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Đã làm

Repo bỏ mô hình chép. Trước bản này `skills/`, `hooks/`, `agents/` và `scripts/` được nhân ra ba
thư mục bundle — 357 file, 4.2 MB, trong khi nguồn chỉ 672 KB. Nay mỗi host đọc thẳng nguồn
chung qua một manifest mỏng: Claude Code `.claude-plugin/`, Codex `.agents/plugins/` +
`.codex-plugin/`, OpenCode `.opencode/plugins/tdq-workflow.js` (JavaScript thuần, không package
npm). Antigravity là ngoại lệ có lý do: agy chỉ đọc plugin ở đường dẫn cố định dưới `$HOME`, nên
layout của nó được SINH tại chỗ lúc cài bằng `build_portable.py --sinh-agy`, không chép sẵn vào
repo — bản chép sẵn nướng cứng thư mục nhà của máy dựng, thứ vô nghĩa với mọi máy khác.

`build_portable.py` 1077 → 634 dòng, `tdq_checkportable.py` 675 → 560. README viết lại phần cài
cho bốn host, `docs/kien-truc.md` thay tầng "luật bản ngoài" bằng tầng Adapter. Version 0.50.0.

## Lỗi của bản trước, tìm thấy trong request này

Bản 0.49.0 ghi "1983 ca, 0 fail, 0 error trên Windows". Con số đó **sai**: lúc đo máy có sẵn
`PYTHONUTF8=1`. Bỏ biến đó ra là 273 error. Nguyên nhân là 89 lời gọi `subprocess` chế độ văn
bản (20 trong `scripts/`) và 36 `open()` trong test không khai `encoding=`, nên Windows giải mã
đầu ra UTF-8 bằng cp1252 và `proc.stdout` thành `None` — `tdq_finish.py` đọc đầu ra `doc_lint`
là hỏng ngay trên một máy Windows bình thường. Báo cáo đa nền tảng ngày 03/09 đã ghi đúng lỗi
này ở mục C1 và nó vẫn nằm đó qua hai bản. Nay vá hết, khoá bằng `test_ma_hoa_subprocess.py`
(đọc AST nên bắt được cả lời gọi trải nhiều dòng), và CHANGELOG đính chính con số cũ.

Bài học rút ra: một biến môi trường trên máy đo đã che lỗi suốt một request. Từ bản này, CI
không đặt `PYTHONUTF8` và test khoá luôn điều đó.

Hai lỗi khác lộ ra khi chạy trên máy sạch: `build_portable.py` không cờ nào thì dựng lại
`antigravity_portable/` ngay trong repo (nay thoát 2), và dòng nhắc graphify lúc mở phiên bị
trần 600 ký tự cắt còn `graphify is n…` khi đường dẫn project dài (nay nằm ngoài trần).

## QC

13/13 hạng mục cộng QC-F1→F4 PASS, sau một vòng fix. Suite: **1961 ca, 0 fail, 0 error** trên
máy thường; **1937 ca, 0 fail, 0 error, 32 skip** trên máy sạch không có pytest, tokenizer,
graphify, node, codex — mỗi skip ghi rõ thiếu gì.

Q6 đỏ ở vòng 1: spec đòi giảm một nửa, thực tế 41%. Vòng fix cắt thêm 11 hằng chết và một tham
số chết mà lượt đo ở T2.3 bỏ sót vì chỉ đo HÀM. Phần còn lại đều đang chạy, nên user chốt đổi
ngưỡng thành "không tên cấp module nào còn lại mà không có nơi dùng" và duyệt lại spec ngày
2026-09-23. Ngưỡng mới chặt hơn ngưỡng cũ ở đúng chỗ từng để lọt lỗi, và đo bằng máy.

Đối chiếu id ca với `main`: 1983 → 1961, không ca nào xanh chuyển sang đỏ. 66 ca biến mất cùng
thứ chúng kiểm. Trong đó ba ca kiểm CẢ nguồn lẫn bản sao, tôi đã xoá nhầm cả nửa nguồn ở bước
gỡ bundle; soát lại và trả về, một ca chuyển sang kiểm bản agy sinh ra.

## Còn hạn chế

- **CI chưa chạy lần nào.** File `.github/workflows/test.yml` khai 3 hệ × Python 3.10/3.13 và
  được test kiểm khuôn, nhưng chưa push nên GitHub chưa chạy. `gh` cũng chưa đăng nhập.
- **Chưa chạy trên macOS, Linux, hay Python 3.10.** Máy này chỉ có Windows + 3.13. Phần 3.10 mới
  kiểm tĩnh: phân tích cú pháp toàn bộ bằng grammar 3.10 và soát API từ 3.11 trở lên. Hai ca
  `tomllib` sẽ skip trên 3.10 — lần chạy CI đầu tiên là lần đầu thấy chúng skip thật.
- **OpenCode và Antigravity mới kiểm ở mức đơn vị.** Không có hai host đó trên máy này. Adapter
  OpenCode được `node` nạp thật, đọc đúng số skill, log bật/tắt đúng; nhưng chưa ai mở OpenCode
  lên xem skill có hiện không. Với agy, layout sinh ra được kiểm từng thành phần theo README của
  agy 1.1.11, chưa chạy thật.
- **Lumen trên Windows.** `tdq_lsp.py` nay cảnh báo khi plugin lumen thiếu `bin/lumen` và in lệnh
  chép bản `.exe` sang. Đây là lỗi của lumen (script `run` đoán sai tên hệ dưới Git Bash), chưa
  báo ngược lên upstream — hỏi trước khi gửi.
- **Nợ cũ, không sửa lan:** `docs/kien-truc.md` vẫn ghi "NHÁP — chờ user chốt" từ 2026-08-15 dù
  mục `## Đã chốt` đã dài 7 mục — trạng thái file là việc của user, không tự đổi. (Bảng "Cấu
  trúc" của README ghi sai số skill/hook thì đã sửa trong request này: 6 → 9 skill, 5 → 6 hook,
  và `test_bang_cau_truc_dem_dung_so_skill_agent_hook` đếm lại từ đĩa mỗi lần chạy.)
