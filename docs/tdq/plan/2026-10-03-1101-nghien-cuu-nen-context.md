# PLAN — Báo cáo nghiên cứu: nén context và rút thời gian máy của workflow

Ngày: 2026-10-03 · Spec: ../spec/2026-10-03-1101-nghien-cuu-nen-context.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — đo bằng `tdq_bench.py simulate` trên chính plan này: main thắng 5,2 phút (16,3 so với 21,5), vì 7/8 task cùng ghi một file báo cáo nên đội phải chia 7 đợt tuần tự (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: ĐÃ DUYỆT (2026-10-03, "Duyệt plan" · mode "1b" = subagent) · 8 task · ETA 165 phút

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Kiểm chéo số liệu
- P2 — Thử nghiệm trên bản sao
- P3 — Bảng đề xuất và báo cáo
- P4 — Kiểm chốt
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc: số liệu phải được kiểm (P1) và đo (P2) trước khi vào bảng
   đề xuất (P3).
2. Mỗi task: đánh `[~]` khi bắt đầu → làm → kiểm theo `Test:` → đổi sang `[x]` NGAY vào file này.
3. **Không sửa workflow.** Không ghi vào `skills/ hooks/ scripts/ tests/ agents/`. Mọi thử nghiệm
   chạy trên bản sao ở `%TEMP%\tdq-thu-nghiem\`, xoá sau khi đo. Chạy test cũng chạy trên bản sao:
   chạy trên repo thật sẽ ghi `docs/tdq/stop_streak.json`.
4. Mọi con số trong báo cáo có nguồn sơ cấp hoặc lệnh đo chạy lại được. Số bên ngoài không xác
   minh được thì không làm căn cứ.
5. Ngưỡng trượt (ví dụ một hướng không đo được) → áp cột `Dự phòng nếu trượt` của spec §6, ghi
   `lech add`, làm tiếp — không dừng hỏi.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Kiểm chéo số liệu

- [x] **T1.1** (e30m) Kiểm chéo số bên ngoài: liệt kê mọi con số trong
  `docs/tdq/research/2026-10-03-1101-nghien-cuu-nen-context.md` có thể làm căn cứ đề xuất; mở nguồn
  sơ cấp của từng số (WebFetch), ghi khớp / lệch / không xác minh được. Ưu tiên ba số đáng ngờ:
  giá đọc cache 0,05×, hai bài arXiv 2605.10039 và 2606.10209, trần phía Codex (32 KiB, 8.000 ký
  tự) — Test: `python -c "import re;t=open('docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md',encoding='utf-8').read();r=re.findall(r'^\| N\d+ \|.*\| *(\S[^|]*?) *\|$',t,re.M);assert len(r)>=3,len(r)"` (bảng kiểm chéo có ≥ 3 dòng `N<số>`, ô cuối là kết luận không trống)
  - Chạm: `docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md` → mục "Kiểm chéo số bên ngoài"
- [x] **T1.2** (e20m) Chạy lại ba số nội bộ lớn nhất theo đúng phương pháp ghi trong
  `…-do-noi-bo.md`: context trung bình mỗi lần gọi, tỉ lệ trọn bộ test trong thời gian máy, tỉ lệ
  ghi lại cache nguội — Test: `python -c "t=open('docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md',encoding='utf-8').read();assert '## Bản đồ chi phí' in t;assert 'chạy lại' in t"` (mỗi số chạy lại lệch ≤ 5% so với số trợ lý báo, hoặc ghi lý do lệch)
  - Chạm: `docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md` → mục "Bản đồ chi phí"

**Xong P1 khi**: mọi số sẽ dùng làm căn cứ đã có dòng kiểm chéo hoặc lệnh chạy lại.

## P2 — Thử nghiệm trên bản sao

- [x] **T2.1** (e25m) Nhóm (c) file luật và hook: chép `skills/` sang `%TEMP%\tdq-thu-nghiem\`,
  thử từng cách nén (bỏ chú thích HTML không phải chỉ mục dòng, dời khối ví dụ/khuôn mẫu khỏi tập
  bắt buộc đọc sang file em, rút câu trùng), đếm token tập bắt buộc đọc của lane full/quick trước
  và sau bằng tokenizer thật — Test: `python -c "t=open('docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md',encoding='utf-8').read();assert '## Thử nghiệm' in t;assert 'T2.1' in t"` (bảng trước/sau có lệnh chạy lại; thư mục tạm đã xoá)
  - Chạm: `docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md` → mục "Thử nghiệm"
  - Cần: T1.2
- [x] **T2.2** (e30m) Nhóm (b) thời gian test: trên một bản sao repo ở `%TEMP%`, đo thời gian trọn
  bộ test so với chạy riêng các module vùng chạm của một request mẫu (request 0732), và đo phần
  10 module chậm nhất của trọn bộ — Test: `python -c "t=open('docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md',encoding='utf-8').read();assert '## Thử nghiệm' in t;assert 'T2.2' in t"`
  (bảng giây có lệnh chạy lại; repo thật không đổi — `git status` sạch phần mã)
  - Chạm: `docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md` → mục "Thử nghiệm"
  - Cần: T1.2
- [ ] **T2.3** (e20m) Nhóm (a) hội thoại tích luỹ và cache: từ số đo transcript, ước lượng mức tiết
  kiệm khi (i) tách phiên theo phase hoặc compact có chủ đích sau mỗi phase, (ii) đẩy việc đọc
  nặng (output lệnh, transcript, test) cho trợ lý chỉ trả tóm tắt, (iii) giữ tiền tố ổn định để
  cache không bị ghi lại nguội — báo khoảng (thấp–cao) kèm phương pháp — Test: `python -c "t=open('docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md',encoding='utf-8').read();assert '## Thử nghiệm' in t;assert 'T2.3' in t"`
  (mỗi ước lượng có phương pháp và nguồn số đầu vào)
  - Chạm: `docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md` → mục "Thử nghiệm"
  - Cần: T1.1, T1.2

**Xong P2 khi**: mỗi nhóm (a) (b) (c) có ít nhất một số tiết kiệm đo hoặc ước lượng có nguồn.

## P3 — Bảng đề xuất và báo cáo

- [ ] **T3.1** (e25m) Bảng đề xuất ≥ 3 hướng, mỗi hướng một dòng mã `H<số>`: tiết kiệm (token,
  giây) · cái giá chất lượng/kiểm soát · công sức · rủi ro · áp cho Codex. Có ít nhất một hướng về
  giảm cổng duyệt, ghi rõ cái giá về kiểm soát (user cho phép đề xuất) — Test: `python -c "t=open('docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md',encoding='utf-8').read();assert '## Bảng đề xuất' in t;import re;h=re.findall(r'^\| H\d+ \|',t,re.M);assert len(h)>=3,len(h)"`
  (≥ 3 dòng `H<số>`, phủ đủ ba nhóm (a) (b) (c))
  - Chạm: `docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md` → mục "Bảng đề xuất"
  - Cần: T2.1, T2.2, T2.3
- [ ] **T3.2** (e15m) Thứ tự nên làm và request tiếp theo nên mở, có lý do; phần tóm tắt đầu báo
  cáo và mục giới hạn — Test: `python -c "t=open('docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md',encoding='utf-8').read();assert '## Thứ tự đề xuất' in t;assert 'request' in t.lower()"` (nêu một request tiếp theo)
  - Chạm: `docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md` → mục "Thứ tự đề xuất"
  - Cần: T3.1

## P4 — Kiểm chốt

- [ ] **T4.1** (e5m) Workflow không bị sửa và tài liệu qua lint — Test:
  `git diff main -- skills hooks scripts tests agents` rỗng và
  `python scripts/doc_lint.py docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md` thoát 0
  - Cần: T3.2

## Cụm song song

Một cụm vì mọi task P1–P3 cùng ghi một file `docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md`;
P2 đọc số đã kiểm ở P1, P3 đọc số đo ở P2. Thử nghiệm T2.1 và T2.2 chạy trên hai bản sao tạm riêng
nên có thể chạy song song trong một lượt, nhưng kết quả vẫn ghi tuần tự vào cùng một file.

## Definition of Done

Trỏ về §6 của spec. `R` là `docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md`.

- [ ] Q1 Đủ số hướng — `grep -c "^| H[0-9]" R` ≥ 3, và bảng có cột nhóm phủ (a) (b) (c)
- [ ] Q2 Mỗi hướng có số — `grep "^| H[0-9]" R` không còn ô tiết kiệm trống
- [ ] Q3 Số bên ngoài đã kiểm chéo — `grep -c "^| N[0-9]" R` bằng số số bên ngoài được dùng làm căn cứ
- [ ] Q4 Thử nghiệm chạy lại được — mục "Thử nghiệm" của R ghi lệnh cho mỗi số trước/sau
- [ ] Q5 Workflow không bị sửa — `git diff main -- skills hooks scripts tests agents` rỗng
- [ ] Q6 Có khuyến nghị — `grep -n "## Thứ tự đề xuất" R`
- [ ] Q7 Lint — `python scripts/doc_lint.py R docs/tdq/spec/2026-10-03-1101-nghien-cuu-nen-context.md docs/tdq/plan/2026-10-03-1101-nghien-cuu-nen-context.md` thoát 0
