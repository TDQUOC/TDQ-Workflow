# REPORT — Vì sao spec hay bị sửa sau khi đã duyệt (`2026-08-18-2050-spec-doi-sau-khi-duyet` · lane quick · 4/4 task)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Báo cáo dài hơn khuyến nghị 10-20 dòng vì đây là request PHÂN TÍCH: bảng tần suất và
bảng nguyên nhân là sản phẩm chính, cắt đi thì không còn gì để đọc. Không sửa một dòng
mã hay luật nào — đúng yêu cầu "chưa tự ý sửa gì".

## 1. Tần suất — không phải sự cố cá biệt

| Ngày | Request | Ca gì | Nguồn |
|---|---|---|---|
| 2026-07-31 | hybrid-deep-search | sửa header `ĐÃ DUYỆT` sau khi approve → sha lệch | `docs/workinglog/2026-07-31.md:155` |
| 2026-08-04 | toi-uu-token-workflow | y hệt: tự sửa dòng `Trạng thái` sau khi ghi duyệt | `docs/workinglog/2026-08-04.md:186-197` |
| 2026-08-05 | bump-version-va-export | lỗi công cụ: `_cli_approve` return sớm, không làm mới sha → cảnh báo treo vĩnh viễn | `docs/workinglog/2026-08-05.md:106-111` |
| 2026-08-07 | siet-qc-lane-quick | spec sửa theo 17 finding của `tdq-reviewer` sau khi đã duyệt bản 1.0 → DỪNG xin duyệt lại | `docs/workinglog/2026-08-07.md:126` · `docs/tdq/spec/2026-08-07-siet-qc-lane-quick.md:6` |
| 2026-08-08 | giam-over-engineer | báo động GIẢ: nội dung không đổi, cảnh báo vẫn kêu | `docs/workinglog/2026-08-08.md:26` |
| 2026-08-15 | toi-uu-thoi-gian-phase | QC phát hiện DoD Q15 trỏ `tests/test_portable_sync.py` không tồn tại → sửa spec ở phase qc | `docs/workinglog/2026-08-15.md:38,41` |
| 2026-08-18 | uu-tien-subagent-song-song | QC phát hiện §6 ghi sai lệnh kiểm Q3/Q14 + thêm §2b → duyệt lại | `docs/tdq/qc/2026-08-18-1744-*.md` |

Bảy ca trên 58 request có spec ≈ **12%**. Nhưng cùng lỗi này đã được ghi nhận từ
2026-07-31 dưới mã **A29** trong audit toàn workflow: "qc.md bước 6 bắt sửa spec §3b ĐÃ
DUYỆT → lệch `spec_sha256` → hook lập tức đòi duyệt lại: **làm đúng QC thì tự kích kẹt
duyệt**" (`docs/tdq/qc/2026-07-31-audit-full-workflow.md:110`). Tức workflow đã BIẾT và
đã chọn sống chung với nó, chỉ vá phần công cụ chứ không vá phần thiết kế.

## 2. Cơ chế — nó bắt cái gì

- Lúc duyệt, `scripts/tdq_state.py` băm **toàn bộ file** spec và lưu `spec_sha256` (`sha256_file`, dòng 1245).
- Mỗi lần bạn gửi prompt, hook `hooks/scripts/prompt_context.py:188-198` băm lại file và so; lệch thì in `[TDQ:APPROVE] ⚠️ Spec đã đổi sau khi duyệt`.
- Băm cả file nghĩa là **một dòng metadata cũng tính là "spec đã đổi"** — nó không phân biệt "sửa phạm vi" với "sửa dấu chấm phẩy".

## 3. Nguyên nhân gốc, xếp theo số ca

| # | Nhóm | Số ca | Bản chất |
|---|---|---|---|
| 1 | **Spec chứa chi tiết chỉ biết được SAU khi code xong** | 2 (08-15, 08-18) | §6 DoD viết sẵn tên file test, tên lệnh `-k ...` — những thứ chỉ đúng khi test đã tồn tại. **42/58 spec (72%) có nêu đường dẫn `tests/test_*` cụ thể**, nên đây là rủi ro hệ thống chứ không phải cẩu thả từng lần |
| 2 | **Sổ sách tự ghi vào chính file bị băm** | 2 (07-31, 08-04) | Đổi `Trạng thái: CHỜ DUYỆT` → `ĐÃ DUYỆT` là ghi lại kết quả của việc duyệt, nội dung §1-§7 không đổi một chữ, nhưng băm vẫn lệch |
| 3 | **Luật QC chủ động ra lệnh sửa spec** | 1 + A29 | `skills/tdq-build/references/qc.md:59-61` viết thẳng: thiếu artifact thì "sửa spec §3b… Sửa spec ở đây làm sha256 lệch → hook sẽ đòi duyệt lại". Quy trình tự sinh ra vi phạm rồi tự dặn cách chịu đựng |
| 4 | **Review/góp ý đến sau lượt duyệt đầu** | 1 (08-07) | `tdq-reviewer` chạy sau khi user đã duyệt bản 1.0; 17 finding đúng → sửa là việc nên làm, không sửa mới là sai |
| 5 | **Lỗi/nhiễu của chính công cụ** | 1 (08-05) + 1 báo giả (08-08) | Nhánh đã-duyệt return sớm nên sha không được làm mới (đã vá 0.7.0); và một lần cảnh báo kêu dù nội dung không đổi |

Nhìn dọc: nhóm 1-3 chiếm 5/7 ca và **đều là hệ quả của thiết kế**, không phải lỗi thao tác.
Gốc chung: `spec_sha256` được dùng như "dấu niêm phong ý định của user", nhưng nó niêm
phong **byte của file**, trong khi file đó lại là nơi workflow ghi sổ sách và ghi cả chi
tiết kỹ thuật chưa thể biết lúc duyệt. Hai vai đó xung đột nhau ngay từ đầu.

## 4. Đề xuất — CHƯA thi hành, chờ bạn quyết

- **Đ1 (gọn nhất): băm phần NỘI DUNG, bỏ vùng sổ sách.** Băm từ heading `## 1.` trở đi, hoặc bỏ các dòng metadata đầu file. Diệt gọn nhóm 2. Đánh đổi: cần một quy ước "ranh giới vùng băm" và test khoá nó.
- **Đ2: cấm spec ghi tên file test / tên lệnh cụ thể.** §6 chỉ ghi ĐIỀU KIỆN PASS, còn lệnh kiểm để plan giữ (plan không bị niêm phong kiểu này). Diệt nhóm 1 — nhóm đông nhất. Đánh đổi: DoD đọc trừu tượng hơn một chút.
- **Đ3: cho phép "sửa spec hạng nhẹ" không cần duyệt lại.** Định nghĩa hẹp và kiểm được bằng máy (chỉ đổi metadata, chỉ sửa lệnh kiểm, không đụng §1-§5), tự ghi lại sha + ghi một dòng vào working log, vẫn báo bạn biết. Đánh đổi: nới một chút quyền tự quyết — phải viết luật thật chặt kẻo thành cửa lách.
- **Đ4: dời cổng duyệt spec ra sau vòng `tdq-reviewer`.** Diệt nhóm 4. Đánh đổi: bạn duyệt muộn hơn vài phút.
- **Đ5: không làm gì.** 12% request phải nhắn thêm một câu "duyệt spec". Chi phí thật là thời gian CHỜ bạn, không phải công sức máy.

Khuyến nghị của tôi: **Đ2 + Đ1** — hai cái này diệt 4/7 ca mà không nới một chút quyền
tự duyệt nào, tức không đụng vào luật "chỉ NGƯỜI DÙNG được duyệt".

## 5. Giới hạn của báo cáo này

Đếm dựa trên dấu vết văn bản trong `docs/workinglog/`, `docs/tdq/qc/`, `docs/tdq/reports/`.
Ca nào xảy ra mà không ai ghi lại thì không nằm trong bảng — con số 7 là **cận dưới**.
