# PLAN NHANH — Không có API Tavily thì workflow tra web bằng gì
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-09-05 · Lane: quick · Brief: ../brief/2026-09-05-1241-khong-co-tavily-web-search.md
**Trạng thái:** ĐÃ DUYỆT (user nhắn "duyệt nhanh")

## Phạm vi

Trong: một báo cáo điều tra trả lời hai câu của user (chưa có key Tavily thì workflow làm gì;
còn tra web được không), bằng chứng `file:dòng`, kèm đề xuất vá hai lỗ hổng đã thấy.
Ngoài: KHÔNG sửa luật, cấu hình MCP, bundle hay key — user chốt `3a`: chỉ điều tra + đề xuất.
Bỏ B0: đất cũ, đã có report chạm `skills/tdq-conventions/`, không cần kiểm kê năng lực.
Bỏ B2: ẩn số ngoài repo duy nhất ("WebSearch có độc lập với MCP không") trả lời được tại chỗ.
Cấm: không in giá trị key Tavily ra báo cáo, log hay lệnh shell — chỉ nói CÓ/KHÔNG.

## Task

- [x] **T1** (e12m) Viết `docs/tdq/report/2026-09-05-1241-khong-co-tavily-web-search.md`: mục 1
  trả lời thẳng hai câu; mục 2 chuỗi failover ba tầng kèm `file:dòng`; mục 3 hai lỗ hổng
  (`tavily.md` không kể ca tool KHÔNG TỒN TẠI; ba bundle cho primary và backup dùng chung
  một biến `TAVILY_API_KEY`); mục 4 đề xuất vá từng lỗ hổng, ghi rõ CHƯA THỰC THI — Test: file
  tồn tại và `grep -c 'references/tavily.md'` ≥ 1
  - Chạm: `docs/tdq/report/2026-09-05-1241-khong-co-tavily-web-search.md` → file mới

- [x] **T2** (e4m) Kiểm bằng máy — Test: `doc_lint.py` exit 0 trên báo cáo, và
  `grep -riE 'tvly-[A-Za-z0-9]'` trên báo cáo không ra dòng nào (không chạm file mã nguồn)

**Ước tính sẽ dùng skill:** không skill ngoài; chỉ đọc file trong repo + `doc_lint.py`.

## Definition of Done

1. Mục 1 trả lời "còn tra web được không" bằng một câu khẳng định — đọc mục 1.
2. Mỗi khẳng định về luật có `file:dòng` — `grep -cE '(md|py|json):?[0-9]*'` ≥ 5; nêu đủ hai
   lỗ hổng — `grep -c 'Lỗ hổng'` = 2.
3. Mỗi lỗ hổng có đề xuất và ghi CHƯA THỰC THI — `grep -c 'Đề xuất'` ≥ 2.
4. Không key nào lọt vào tài liệu — `grep -riE 'tvly-[A-Za-z0-9]' docs/tdq/report/` rỗng.
5. `doc_lint.py` exit 0 trên plan và báo cáo.
6. Không đổi mã nguồn — `git status --porcelain -- skills scripts hooks` rỗng.

## QC

Báo cáo: `docs/tdq/report/2026-09-05-1241-khong-co-tavily-web-search.md`. 6/6 PASS.

1. PASS — mục 1 mở đầu bằng "**Có, vẫn tra web được.**" (grep khớp 1).
2. PASS — `grep -cE '\.(md|py|json):[0-9]+'` = 10 (≥ 5); `grep -c '^\*\*Lỗ hổng'` = 2 đúng hai
   lỗ hổng (lệnh thô trong DoD ra 3 vì đếm cả tiêu đề `## 3. Lỗ hổng phát hiện được`).
3. PASS — `grep -c '^\*\*Đề xuất'` = 2, mỗi lỗ hổng một đề xuất; nhãn CHƯA THỰC THI nằm ở
   tiêu đề `## 4. Đề xuất vá — CHƯA THỰC THI`, phủ cả hai.
4. PASS — `grep -riE 'tvly-[A-Za-z0-9]' docs/tdq/report/` ra 0 dòng.
5. PASS — `doc_lint.py` exit 0 trên cả plan lẫn báo cáo.
6. PASS — `git status --porcelain -- skills scripts hooks` rỗng, không mã nguồn nào bị đổi.
