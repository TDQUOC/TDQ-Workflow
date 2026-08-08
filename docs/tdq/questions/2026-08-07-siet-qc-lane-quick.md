# QUESTIONS — Siết QC và vòng fix cho lane quick

Request: ../requests/2026-08-07-siet-qc-lane-quick.md · Lane: full

## Vòng 1 — 2026-08-07 16:24

1. Ngưỡng nhẹ của QC quick gồm những gì? (`qc.md` full lane có 6 hạng mục: full suite,
   hạng mục spec §6, biên & đường lỗi, log service, không placeholder, hợp đồng skill)
- A (đề xuất): 3 hạng mục — test từng task pass + đối chiếu từng dòng DoD + biên & đường lỗi cơ bản — bỏ full-suite-toàn-repo, log service, hợp đồng skill
- B: 2 hạng mục — chỉ test từng task + DoD — nhẹ nhất, nhưng bug ở input rỗng/file thiếu sẽ lọt
- C: 4 hạng mục — A cộng "không placeholder" (grep TODO/FIXME/mock)
- D: dùng nguyên 6 hạng mục của `qc.md` nhưng cho phép ghi gọn trong chat — hết "nhẹ hơn full"

Đáp: (chờ)

2. Bằng chứng QC quick ghi ở đâu?
- A (đề xuất): append mục `## QC` vào chính `docs/tdq/plan/<slug>.md` (lệnh + kết quả + PASS/FAIL), tóm tắt trong chat — không tạo file `qc/`
- B: chỉ trình trong chat, không ghi file — mất dấu vết, turn sau không tra được
- C: vẫn tạo `docs/tdq/qc/<slug>.md` nhưng dạng rút gọn — quick lại có 2 file, mất tính "gộp 1 file"

Đáp: (chờ)

3. Quick có ép red → green (viết/chạy check thấy FAIL trước, rồi code) như full không?
- A (đề xuất): có, ép — cùng luật với full, vì đây là thứ chặn "test giả pass"
- B: không ép, chỉ cần test pass cuối task — nhanh hơn nhưng dễ có test không bao giờ đỏ
- C: ép có điều kiện — task sửa code thì ép, task chỉ sửa tài liệu thì không

Đáp: (chờ)

4. Vòng fix khi FAIL có trần số vòng không?
- A (đề xuất): trần 3 vòng; vượt → DỪNG, báo user kèm chẩn đoán và đề xuất chuyển full
- B: không trần, lặp đến hết FAIL — đúng tinh thần "luôn luôn fix" nhưng có thể quay vòng vô hạn/cháy token
- C: trần 2 vòng — siết hơn, dễ bị escalate oan với bug nhỏ nhiều chỗ

Đáp: (chờ)

5. Quick external (engine ngoài trả FAIL) xử lý thế nào?
- A (đề xuất): cùng luật vòng fix, nhưng vòng fix do hội thoại chính tự làm — không giao lại engine đã fail
- B: giao lại engine ngoài vòng fix — có thể fail lặp, tốn thời gian
- C: chưa quy định trong request này, để NGOÀI phạm vi

Đáp: (chờ)

6. Ép bằng máy tới đâu?
- A (đề xuất): ép ở 4 nguồn sự thật văn bản (`quick-lane.md`, `tdq-intake/SKILL.md`, `PHASE_TABLE["quick"]` trong `tdq_state.py`, bản `portable/`) + test khẳng định 4 nguồn khớp nhau — không đụng `doc_lint.py`
- B: A cộng rule mới trong `doc_lint.py` soi file plan quick phải có mục `## QC` — chặt nhất nhưng chỉ soi được sau khi implement xong
- C: A cộng chặn ở `hooks/scripts/stop_gate.py`: lane quick đã approve mà plan chưa có mục `## QC` thì không cho kết thúc turn

Đáp: (chờ)

7. Bạn muốn bổ sung thêm gì không?
- A (đề xuất): Không, đủ rồi — làm tiếp đi.
- B: Có — tôi nói thêm.

Đáp: **B** — nguyên văn: "tôi muốn là ở quick thì sẽ hỏi người dùng cần QC ko thay vì tự có QC"

### Đáp vòng 1 (2026-08-07 16:41) — nguyên văn: "1A; 2A; 3.A; 4.A; 5A; 6.A; 7.B …"

| Câu | Chọn | Nghĩa đã chốt |
|---|---|---|
| 1 | A | QC quick = 3 hạng mục: test từng task pass · đối chiếu từng dòng DoD · biên & đường lỗi cơ bản |
| 2 | A | bằng chứng append mục `## QC` vào chính `docs/tdq/plan/<slug>.md`, không tạo file `qc/` |
| 3 | A | ép red → green như lane full |
| 4 | A | trần 3 vòng fix; vượt → DỪNG, báo user + đề xuất chuyển full |
| 5 | A | quick external FAIL → vòng fix do hội thoại chính tự làm, không giao lại engine đã fail |
| 6 | A | ép ở 4 nguồn sự thật văn bản + test parity; KHÔNG đụng `doc_lint.py`, KHÔNG đụng `stop_gate.py` |
| 7 | B | bổ sung: QC ở quick phải **HỎI user** có cần QC không, thay vì tự động luôn có |

**Xung đột cần làm rõ:** đáp 7 (hỏi user) đứng ngược với đáp 1+2 (QC bắt buộc 3 hạng mục,
bằng chứng ghi vào plan). Phải chốt: hỏi ở đâu trong luồng, mặc định là gì, và khi user
nói "không cần QC" thì vòng fix bắt buộc (câu 4) còn hiệu lực không → vòng 2.

## Vòng 2 — 2026-08-07 16:42

8. Hỏi user "có cần QC không" ở ĐÂU trong luồng quick?
- A (đề xuất): gộp vào chính gate duyệt — dòng `➤ Duyệt` có thêm biến thể `"duyệt quick không QC"`; nhắn "duyệt quick" trơn = CÓ QC
- B: thêm 1 câu hỏi riêng trong vòng interview trước khi viết mini-plan — thêm 1 lượt chat, có thể phải chờ user 2 lần
- C: hỏi sau khi implement xong, ngay trước khi chạy QC — user thấy được kết quả rồi mới quyết, nhưng lúc đó turn đã dài

Đáp: (chờ)

9. Mặc định khi user KHÔNG nói gì về QC là gì?
- A (đề xuất): mặc định CÓ QC — im lặng = làm QC 3 hạng mục; muốn bỏ phải nói rõ
- B: mặc định KHÔNG QC — im lặng = bỏ, muốn có phải nói rõ; nhẹ nhất nhưng dễ trôi về hiện trạng cũ
- C: không có mặc định — thiếu ý user thì DỪNG hỏi lại; an toàn nhất nhưng chặn luồng một-turn của quick

Đáp: (chờ)

10. User chọn "không cần QC" thì vòng fix bắt buộc (câu 4) còn hiệu lực không?
- A (đề xuất): CÒN, luôn luôn — bỏ QC chỉ bỏ 3 hạng mục kiểm chủ động; hễ thấy bug/test đỏ là VẪN phải fix, trần 3 vòng
- B: hết hiệu lực luôn — user tự chịu; nhưng trái hẳn ý "khi có bug thì luôn luôn bắt buộc fix" ở turn trước
- C: còn hiệu lực nhưng chỉ với test của task (đỏ thì fix), không tính bug phát hiện ngoài test

Đáp: (chờ)

11. "Không QC" thì mục `## QC` trong file plan xử lý sao?
- A (đề xuất): vẫn append mục `## QC` với đúng 1 dòng `BỎ theo yêu cầu user: "<nguyên văn>"` — giữ dấu vết, ai đọc lại cũng biết vì sao trống
- B: không ghi gì cả — file plan gọn hơn, nhưng sau này không phân biệt được "bỏ có chủ đích" với "quên làm"

Đáp: (chờ)

12. Bạn muốn bổ sung thêm gì không?
- A (đề xuất): Không, đủ rồi — viết spec đi.
- B: Có — tôi nói thêm.

### Đáp vòng 2 (2026-08-07 16:46) — nguyên văn: "8A; 9A ; 10A; 11:A ; 12A"

| Câu | Chọn | Nghĩa đã chốt |
|---|---|---|
| 8 | A | hỏi gộp vào gate duyệt: thêm biến thể `"duyệt quick không QC"`; `"duyệt quick"` trơn = CÓ QC |
| 9 | A | mặc định CÓ QC — im lặng = làm đủ 3 hạng mục |
| 10 | A | bỏ QC KHÔNG bỏ vòng fix: test đỏ / thấy bug là vẫn phải fix, trần 3 vòng |
| 11 | A | "không QC" vẫn append `## QC` với 1 dòng `BỎ theo yêu cầu user: "<nguyên văn>"` |
| 12 | A | hết câu hỏi — sang spec |

**Kết luận interview:** hết chỗ đoán. Xung đột vòng 1 đã giải: QC là **mặc định bật, user
opt-out có chủ đích qua gate duyệt**; vòng fix thì **không opt-out được**.
