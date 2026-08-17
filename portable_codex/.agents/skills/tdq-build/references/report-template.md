# Khuôn report

## Bốn bước thi hành

Đây là toàn bộ Phần C của [SKILL.md](../SKILL.md) — chuyển về đây để thân skill không phải
nạp nhánh này mỗi lần gọi. Vào phase `report` là **bắt buộc** đọc hết bốn bước dưới đây
trước khi viết report; cấm làm theo trí nhớ.

7. Viết `docs/tdq/reports/<slug>.md` — tiếng Việt, KHÔNG giới hạn cứng số dòng, khuyến
   nghị ~10-20 dòng. Khuôn: mục `## Khuôn` cùng file này. Bảng thời gian là **bắt buộc**:
   chạy `tdq_timing.py show` rồi dán nguyên bảng vào report, không tự ước lượng số.

8. Đóng sổ: tick nốt checkbox còn sót, đổi header plan thành HOÀN THÀNH, rồi chạy
   `tdq_finish.py --files <file vừa sửa> --log "<tóm tắt report>"` (working log + graphify).

9. Trình report trong chat (nguyên văn hoặc tóm tắt ngắn gọn + đường dẫn).

10. **Hỏi user có commit không** — bắt buộc, không tự commit thành quả cuối (ngoại lệ duy
    nhất: commit gỡ chặn giữa build theo Luật cứng, phải liệt kê trong report). Gộp chung
    với bước 9 thành MỘT khối theo
    [user-facing-block.md](../../tdq-conventions/references/user-facing-block.md):
    ```
    Tôi đã làm xong yêu cầu của bạn.

    **Đã làm:** <gạch đầu dòng ngắn>.
    **Kết quả kiểm:** <số hạng mục QC, kết quả test>.

    Xem đầy đủ tại: `docs/tdq/reports/<slug>.md`

    ---

    **Bạn có muốn tôi commit phần thay đổi này không?**

    ➤ Trả lời: nhắn "commit" (tôi commit, không push) hoặc "chưa" (giữ nguyên chỗ làm việc) · Góp ý: nhắn trực tiếp
    ```
    User đồng ý → message mô tả thay đổi, KHÔNG chứa "generated with …" hay trailer AI;
    branch theo quy ước.

Xong khi: report đã ghi và user đã được hỏi về commit.
Bước kế tiếp: `python3 "./scripts/tdq_state.py" set phase=idle`
(hoặc `reset` nếu user muốn xoá hẳn để sang request mới).

## Khuôn

(nhắc lại có chủ ý — bản gốc ở bước 7 mục `## Bốn bước thi hành` cùng file này.)

`docs/tdq/reports/<slug>.md` — tiếng Việt, KHÔNG giới hạn cứng số dòng. Khuyến nghị
**càng ngắn càng tốt, tầm 10-20 dòng là ổn**; dài hơn thì nói rõ vì sao (nhiều đề xuất,
nhiều task…) thay vì cắt bớt sự thật. Dồn mỗi mục thành MỘT dòng, ngăn ý bằng dấu `·`,
số liệu lấy nguyên từ output thật.

```markdown
# REPORT — <tên việc> (`<slug>` · lane <lane> · mode <mode> · <n> task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** <P1 …> · <P2 …> · <P3 …>
**Kết quả:** <chỉ số> <trước> → <sau> · <chỉ số> <trước> → <sau>
**Kiểm:** <lệnh test + kết quả> · <lint> · QC <PASS x/y mục DoD, defect đã sửa>
**Đầu ra:** <đường dẫn file chính> · Backup: <đường dẫn, nếu có sửa ngoài repo>
**Giới hạn:** <cái gì chưa làm, vì sao, ảnh hưởng gì>
**Git:** <chưa commit / commit nào đã tạo>

## Thời gian

<dán nguyên output của `tdq_timing.py show`: bảng Phase · Treo tường · Model chạy · Số lần vào>
```

Hai cột thời gian cố ý khác nhau: **treo tường** tính cả lúc chờ user duyệt, **model chạy**
chỉ tính lúc máy làm. Lệch lớn ở một phase nghĩa là phase đó tốn thời gian CHỜ, không phải
tốn sức làm — đọc số xong mới biết nên tối ưu chỗ nào.

## Kiểm trước khi trình

- Không giới hạn cứng; khuyến nghị 10-20 dòng, ngắn nhất có thể mà không mất mục nào.
- Mọi con số lấy từ output thật, không ước lượng. Phép đo có điều kiện méo thì nói rõ trong dòng "Kết quả".
- Dòng "Giới hạn" không được bỏ trống khi còn việc dang dở — nói thật, không giấu.
- Kết thúc bằng câu hỏi user có muốn commit không (hỏi trong chat, không viết trong file).
