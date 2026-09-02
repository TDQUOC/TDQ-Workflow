# Thi hành phương án 2301 — chuyển luật vào skills, cắt CLAUDE.md

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> 2a (mở request sau để thi hành phương án: viết 5 dòng CHUYỂN vào `skills/` → cắt
> CLAUDE.md → dựng lại 3 bundle)

Đọc lần đầu:
- **Mục tiêu**: biến báo cáo `2026-09-01-2301-quet-instruction-vao-plugin.md` thành thay
  đổi thật — 5 dòng CHUYỂN vào `skills/`, rồi cắt `~/.claude/CLAUDE.md` 57 → 29 dòng, rồi
  dựng lại 3 bundle portable.
- **Phạm vi đoán**: ghi vào `skills/tdq-conventions/` (2 đích đã xác định trong báo cáo);
  ghi vào `~/.claude/CLAUDE.md` — file NGOÀI repo; dựng lại `portable_claude/`,
  `portable_codex/`, `antigravity_portable/`.
- **Thứ tự ràng buộc** (báo cáo §8): **chuyển trước, xoá sau**. Không được cắt CLAUDE.md
  trước khi 5 dòng CHUYỂN đã sống trong `skills/`.
- **Chỗ chưa rõ**:
  - Request 2301 chốt "không sửa `~/.claude/CLAUDE.md`" — request này ĐẢO điều đó, cần
    user xác nhận riêng vì đó là file ngoài repo, ảnh hưởng MỌI project.
  - Cắt cả 28 dòng một lần, hay cắt theo đợt để quan sát?
  - 10 dòng XOÁ chỉ an toàn chừng nào hook còn chạy — có cần thêm test canh hook trước
    khi cắt không?

## Hiểu & kiến thức

Nguồn phương án: `docs/tdq/report/2026-09-01-2301-quet-instruction-vao-plugin.md` mục 4
(5 đích), mục 6 (bản CLAUDE.md 29 dòng), mục 8 (cái giá + thứ tự bắt buộc).

### B1 — đọc code, bốn điểm quyết định
1. **Đích có thật, còn chỗ.** `skills/tdq-conventions/SKILL.md` 164 dòng, §7 Git ở dòng 122
   (3 gạch đầu dòng, dòng 126 là "Never commit or push before the user asks" — chỗ đúng để
   đặt ngoại lệ build TDQ ngay sát dưới), §8 Research ở dòng 128 (dòng 134 là câu cấm API
   key). `skills/tdq-conventions/references/approval.md` 54 dòng, có mục
   "NOT an approval" — họ hàng đúng của luật "không tự vào plan mode".
2. **Trần dòng chỉ áp cho `references/`.** `tests/test_token_budget.py:115` chặn mọi file
   trong `skills/*/references/` ở 215 dòng; `approval.md` 54 dòng nên còn thừa chỗ.
   `SKILL.md` không bị test này chặn.
3. **Rủi ro thật: bảng luật lệch số dòng.** `docs/tdq/audit/luat-hien-co.md` neo luật theo
   `<file>:<dòng>`. Chèn dòng vào giữa `tdq-conventions/SKILL.md` sẽ đẩy số dòng của mọi
   luật phía dưới → `test_luat_skill.py` báo lệch. Độ lệch hiện tại 57/329, ngưỡng mềm 5%.
   Phải cập nhật bảng luật trong cùng request, không để trôi.
4. **Cắt CLAUDE.md chỉ ảnh hưởng Claude Code, nơi hook CHẮC CHẮN chạy.** Plugin
   `tdq-workflow` bật ở user scope nên hook có mặt ở mọi project Claude Code — đúng cái điều
   kiện mà 10 dòng XOÁ dựa vào. Codex/Antigravity không đọc `~/.claude/CLAUDE.md`, nên việc
   cắt không đụng tới chúng; chúng dùng bundle riêng, và bundle vẫn phải dựng lại vì
   `skills/` đổi.

BỎ B0: đã có tiền lệ — chính báo cáo 2301 vừa chạm đúng hai khu vực này (`skills/` và
`~/.claude/`), năng lực đã kiểm kê ở request đó, không có gì mới để kiểm kê lại.
BỎ B2: không có ẩn số ngoài repo — toàn bộ đối tượng là file cục bộ đã đọc trực tiếp.
BỎ vòng phạm vi: phạm vi đã đóng sẵn trong mục 4/6/8 của báo cáo 2301, user chỉ nói "thi
hành" nên không có mặt nào để mở thêm.

### Điểm phải user xác nhận
Request 2301 chốt "KHÔNG sửa `~/.claude/CLAUDE.md`". Request này đảo điều đó. File nằm
ngoài repo và nạp vào MỌI phiên của MỌI project, nên việc cắt được ghi thẳng vào mini-plan
để câu duyệt của user chính là lời cho phép — không suy diễn.
Giảm rủi ro: chép `~/.claude/CLAUDE.md` sang `~/.claude/CLAUDE.md.bak-2026-09-02` trước khi
ghi, và cắt SAU khi 5 dòng CHUYỂN đã sống trong `skills/` (thứ tự bắt buộc của mục 8).

NGOÀI phạm vi: hai khoá Tavily trong `settings.json` — đã nêu ở báo cáo 2301, là quyết định
riêng của user, không gộp vào đây.

## Hỏi đáp

Không mở vòng hỏi: phương án đã chốt từng dòng ở báo cáo 2301, câu duyệt mini-plan là cổng
xác nhận duy nhất còn thiếu.
