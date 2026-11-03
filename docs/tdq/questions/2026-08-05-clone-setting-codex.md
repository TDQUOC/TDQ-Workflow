# Hỏi–đáp: clone-setting-codex

## Vòng 1 (20:00, 2026-08-05)

1. Phạm vi nguồn clone?
   - A (đề xuất): chỉ `~/.claude/*` (global)
   - B: cả global lẫn project-level `.claude/`
   - **User chọn: A**

2. Đích chạy trên máy nào?
   - A (đề xuất): chỉ máy hiện tại (ghi thẳng `~/.codex/*` + `.codex/` project)
   - B: hỗ trợ cả cross-machine như `claude_export.py` (build bundle → apply máy khác)
   - **User chọn: B**

3. Cơ chế thực thi của skill?
   - A (đề xuất): script Python xác định (`scripts/codex_clone.py`, có test)
   - B: skill thuần hướng dẫn Claude tự đọc/viết từng lần
   - **User chọn: A**

4. Phần KHÔNG map 1:1 được (agents/, slash-commands, plugin manifest khác, MCP field lạ)?
   - A (đề xuất): bỏ qua + liệt kê rõ trong báo cáo, không convert
   - B: cố convert gần đúng (best-effort)
   - **User chọn: A**

5. Khi đích đã có config Codex từ trước?
   - A (đề xuất): merge có backup (`.bak-<timestamp>`)
   - B: luôn ghi đè toàn bộ
   - **User chọn: B**

6. Secret trong settings.json (Tavily key, MCP token...) khi copy sang config Codex?
   - A (đề xuất): KHÔNG copy giá trị thật — placeholder + hướng dẫn set riêng
   - B: copy nguyên văn giá trị thật
   - **User chọn: B**

7. Bạn muốn bổ sung thêm gì không?
   - A (đề xuất): Không, đủ rồi.
   - **User chọn: A**

## Vòng 2 (20:00, 2026-08-05) — xung đột 2.B × 6.B

8. Bundle cross-machine (2.B) sẽ chứa secret thật (6.B), ngược quy ước "quét secret:
   sạch" đã có sẵn ở `claude_export.py`. Xử lý sao?
   - A (đề xuất): tách theo đích — local giữ 6.B, riêng bundle cross-machine dùng
     placeholder như `claude_export.py`
   - B: giữ 6.B tuyệt đối cho mọi đích, kể cả bundle — chấp nhận rủi ro, tắt bước
     "quét secret: sạch" cho riêng tool `codex_clone.py`
   - C: đổi lại 6.A cho mọi đích (placeholder toàn bộ)
   - **User chọn: B — xác nhận rõ ràng, chấp nhận rủi ro bundle mang secret thật.**

## Chốt phạm vi
Global-only, script-backed, hỗ trợ cả apply-local lẫn build-bundle-cross-machine,
KHÔNG bật secret-scan-block cho tool này (khác `claude_export.py`), overwrite toàn bộ
đích (không merge), phần không map (agents/, commands/, plugin manifest khác) bị bỏ
qua và liệt kê trong report. Không còn câu hỏi nào làm đổi kết quả.
