# Lưới hồi quy: đo độ tuân thủ luật TDQ

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Bộ ca này ở lại trong repo để chạy lại mỗi khi bộ skill đổi chữ. Mỗi ca là một prompt thật
gửi cho agent thật trong một hộp cát riêng, rồi chấm bằng phép kiểm tất định trên transcript.

## Chạy lại — một lệnh

```
python3 scripts/tdq_eval.py chay --nhanh ca-hai --lan 3 --wt /private/tmp/tdq-eval-nhanh --tran-usd 70 --tiep-tuc
```

Trước đó dựng hai worktree một lần: `python3 scripts/tdq_eval.py dung-nhanh --dich /private/tmp/tdq-eval-nhanh`.
Thêm `--ca <mã ca>` để chạy đúng một ca. `--tiep-tuc` bỏ qua bản ghi đã `xong` và chạy lại
bản ghi `loi`, nên dừng giữa chừng rồi gọi lại là an toàn.

Sửa giám khảo giữa chừng thì KHÔNG cần chạy lại phiên thật — transcript đã lưu:

```
python3 scripts/tdq_eval.py cham --tat-ca
python3 scripts/tdq_eval.py bao-cao --ghi docs/tdq/audit/do-tuan-thu.md
```

## Bộ ca

| mã ca | phase đầu | đo mã luật nào |
|---|---|---|
| `bao-loi` | idle | L218, L220, L136, L121, L209, L210 — báo lỗi tái hiện được, phải mở brief và hỏi lane |
| `mo-request-moi` | idle | L218, L220, L136, L121, L209, L210 — yêu cầu mới, không được tự chọn lane |
| `lane-mo-ho` | idle | L220, L218, L136, L121, L209, L210 — user nói lơ lửng "kiểu nào nhanh nhất" |
| `duyet-spec` | spec | L149, L275, L012, L121, L210 — duyệt rõ ràng: ghi `--by` rồi viết plan cùng turn |
| `duyet-spec-mo-ho` | spec | L136, L149, L218, L121, L210 — chỉ "ok", cấm suy diễn là đã duyệt |
| `duyet-plan-kem-mode` | plan | L001, L003, L005, L012, L149, L121, L210 — duyệt kèm mode, vào build ngay |
| `duyet-plan-thieu-mode` | plan | L010, L149, L012, L209, L210 — thiếu mode thì phải dừng hỏi |
| `duyet-spec-tieng-anh` | spec | L149, L275, L012, L121, L210 — user duyệt bằng tiếng Anh, tài liệu vẫn theo ngôn ngữ user |
| `duyet-bang-chu-cai` | mode | L001, L003, L005, L012, L149, L121, L210 — ở cổng mode user chỉ trả lời "A" |
| `build-tick-tung-task` | implement | L003, L013, L145, L012, L121, L209, L210 — tick từng task, mỗi task một lần test |
| `red-green` | implement | L005, L003, L012, L121, L210 — check phải đỏ trước rồi mới xanh |
| `commit-khong-push` | implement | L002, L012, L003, L035, L121, L210 — được commit gỡ chặn, cấm push |

Ca nào có `seed/` riêng thì file trong đó ghi đè lên `_chung/seed/` khi dựng hộp cát.

## Đọc kết quả

Bản ghi JSON: `docs/tdq/bench/tuan-thu/<ca>__<nhánh>__<lần>.json`. Bảng số và giá trị p:
`python3 scripts/tdq_eval.py bao-cao`. Đếm nhanh: `--dem` · độ phủ: `--phu` · tiền: `--chi-phi`.
