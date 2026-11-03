# PLAN — Quét instruction Claude Code: chuyển gì vào plugin, xoá bớt gì

Ngày: 2026-09-01 · Spec: ../spec/2026-09-01-2301-quet-instruction-vao-plugin.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: ĐÃ DUYỆT (spec + plan, by "1a") · mode main
Mode thực thi: main — `tdq_bench.py mo-phong --he-so-agent 1.5` ra `Winner: đội (gap 2.0
minutes)`, 28.5 phút so 26.5 phút. Vẫn đề xuất `main`, và nói rõ vì sao lệch máy đo: bench
chia đợt theo dòng `Chạm:`, mà plan này chỉ có ĐÚNG MỘT task có `Chạm:` (T4.1) — 11 task còn
lại cùng ghi vào một bảng phán quyết duy nhất nên không tách được thật. 2.0 phút là mức
chênh máy đo thấy trên giấy, không phải mức tách được trong thực tế; chi phí brief cho agent
đã lớn hơn thế. User chốt lại ở cổng `mode`.

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Dựng bằng chứng
- P2 — Phán quyết từng dòng
- P3 — Phương án chuyển vào plugin
- P4 — Viết báo cáo
- Cụm song song
- Px — Log & test bắt buộc
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: `[~]` khi bắt đầu → làm → kiểm → `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy lại lệnh kiểm của phase đó, xanh mới sang phase sau.
4. `~/.claude/CLAUDE.md` và `~/.claude/settings.json` là vùng **CHỈ ĐỌC** — mọi task chỉ
   được đọc, cấm mọi lệnh ghi vào hai file đó.
5. Cấm in giá trị API key ra báo cáo, log, lệnh shell hay prompt gửi model.
6. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
7. Không commit/push cho đến khi user yêu cầu.

## P1 — Dựng bằng chứng

- [x] **T1.1** (e8m) Trích 57 dòng `~/.claude/CLAUDE.md` thành bảng thô (số dòng + nguyên
  văn) vào file làm việc tạm trong scratchpad — Test: file tạm có đúng 57 dòng dữ liệu,
  đếm bằng một lệnh
- [x] **T1.2** (e14m) Dò từng luật xem đã sống ở đâu trong `skills/` + `hooks/`: mỗi dòng
  ra 0 hoặc nhiều cặp `<file>:<dòng>` — Test: mỗi cặp dẫn ra được kiểm lại bằng grep và
  thấy thật, không cặp nào chết
  - Dùng: `tdq-lsp-setup`
  - Để: giữ đúng thứ tự tìm — ký hiệu code thì gọi song song `mcp__lsp__*` + lumen rồi mới
    grep; ở đây đối tượng là câu luật trong markdown nên lumen là lớp chính, grep lớp cuối.
  - Ra: bảng đối chiếu trong file tạm, cột `nguồn còn sống`
  - Kiểm: mọi giá trị cột đó chạy `sed -n '<dòng>p' <file>` đều ra đúng câu luật
  - Không dùng cho: quyết định GIỮ/XOÁ — đó là T2.1, không phải việc của bước dò
- [x] **T1.3** (e6m) Liệt kê chính xác hook nào nói luật gì, ở lượt nào (SessionStart /
  UserPromptSubmit / PreToolUse / Stop) — Test: mỗi dòng dẫn `hooks/scripts/<file>:<dòng>`,
  kiểm lại bằng `sed -n` thấy đúng
- [x] **T1.4** (e5m) Kiểm chứng "hook chạy ở mọi project": xác nhận `prompt_context.py` in
  `[TDQ:INTAKE]` khi `state is None` — Test: chạy hook với `cwd` là thư mục tạm không có
  `docs/tdq/`, thấy dòng `[TDQ:INTAKE]` ở đầu ra

**Xong P1 khi**: 57 dòng đều có cột `nguồn còn sống` (kể cả giá trị rỗng), và 4 lệnh kiểm
trên đều xanh.

## P2 — Phán quyết từng dòng

- [x] **T2.1** (e16m) Áp hai câu hỏi của spec §3 cho từng dòng → phán quyết GIỮ / CHUYỂN /
  XOÁ + lý do một câu — Test: 57/57 dòng có phán quyết thuộc đúng 3 giá trị đó và lý do
  không rỗng
- [x] **T2.2** (e8m) Với MỌI dòng XOÁ: gắn bằng chứng luật còn sống (`<file>:<dòng>` từ
  T1.2/T1.3) — Test: không dòng XOÁ nào thiếu bằng chứng; mỗi bằng chứng grep lại thấy thật
- [x] **T2.3** (e7m) Tách riêng nhóm "mồi khởi động": các dòng phải GIỮ vì cần đúng ở cửa
  sổ TRƯỚC khi skill đầu tiên nạp — Test: mỗi dòng trong nhóm nêu được tình huống cụ thể nó
  phải sống sót (ví dụ tầng `nhỏ` trả lời tại chỗ, không gọi skill nào)

**Xong P2 khi**: bảng phán quyết đủ 57 dòng, đầu ra §2 mục 1 và mục 5 của spec đã có dữ liệu.

## P3 — Phương án chuyển vào plugin

- [x] **T3.1** (e12m) Với mỗi dòng CHUYỂN: chỉ đúng MỘT đích — file skill có thật, hook có
  thật, hoặc "đích MỚI" kèm lý do vì sao chỗ cũ không chứa được — Test: mọi đích là đường
  dẫn tồn tại, hoặc có nhãn "đích MỚI" + lý do; kiểm bằng một lệnh `test -f` chạy vòng
- [x] **T3.2** (e10m) Soát phương án theo 3 ràng buộc kiến trúc ở spec §5 (luật thuộc
  `skills/`; hook chỉ nhắc mã và chặn; skill chỉ nhắc TÊN lệnh của `scripts/`) — Test: mỗi
  đề xuất có một dòng nói nó không phạm ràng buộc nào trong 3 dòng đó
- [x] **T3.3** (e6m) Nêu cái giá của phương án: dòng nào chuyển đi thì mất hiệu lực ở cửa
  sổ nào, bundle portable nào phải dựng lại — Test: mục "cái giá" có mặt, nêu đủ 2 ý

**Xong P3 khi**: đầu ra §2 mục 2 của spec đã có dữ liệu, không đích nào chết.

## P4 — Viết báo cáo

- [x] **T4.1** (e14m) Viết `docs/tdq/report/2026-09-01-2301-quet-instruction-vao-plugin.md`
  gồm 5 đầu ra của spec §2 — Test: `python3 scripts/doc_lint.py <báo cáo>` thoát 0
  - Chạm: `docs/tdq/report/2026-09-01-2301-quet-instruction-vao-plugin.md` → file mới,
    chưa node nào phụ thuộc
- [x] **T4.2** (e9m) Dựng bản `CLAUDE.md` đề xuất, dán được nguyên khối — Test: số dòng bản
  mới < 57, và mọi luật bị bỏ đều xuất hiện ở cột CHUYỂN hoặc XOÁ của bảng
  - Cần: T2.1, T3.1
- [x] **T4.3** (e5m) Viết mục `settings.json`: API key ở dạng chữ (KHÔNG in giá trị),
  `defaultMode: bypassPermissions`, `skipDangerousModePermissionPrompt` — Test:
  `grep -c 'tvly-' <báo cáo>` trả 0
- [x] **T4.4** (e4m) Ghi 1 fact vào mem0 về chỗ đứng của luật (instruction vs plugin) —
  Test: `search_memories` với project `TDQWorkflow` trả về fact vừa ghi
  - Dùng: `mem0-memory` (mcp)
  - Để: chốt quyết định kiến trúc "luật ở đâu" thành trí nhớ dài hạn, gọi sau khi báo cáo xong
  - Ra: một fact ngắn trong mem0, project `TDQWorkflow`
  - Kiểm: `search_memories` trả về đúng fact đó
  - Không dùng cho: lưu nội dung báo cáo hay bất kỳ giá trị credential nào

**Xong P4 khi**: báo cáo tồn tại, 5 đầu ra đủ, doc_lint xanh.

## Cụm song song
- Cụm A: T1.1 → T1.2 → T1.3 → T1.4 (T1.2 và T1.3 độc lập nhau, T1.4 độc lập cả hai).
- P2, P3, P4 phụ thuộc tuyến tính vào P1 — không cắt song song được vì cùng ghi một bảng.
- Số task có `Chạm:` không giao nhau: 1 → trần tốc độ song song là 1, tức không có lợi ích
  từ chế độ đội.

## Px — Log & test bắt buộc
Log: BỎ — request này không đẻ ra runtime nào, đầu ra duy nhất là một file báo cáo markdown.
Không có task test đơn vị vì không có mã nguồn mới; việc kiểm nằm ở dòng `Test:` của từng
task và ở Definition of Done.

## Definition of Done
Trỏ về §6 spec.

- [x] Q1 Bảng phán quyết có đúng 57 dòng, không thiếu phán quyết/lý do — đếm dòng bảng bằng
  một lệnh `grep -c` trên báo cáo
- [x] Q2 Mọi dòng XOÁ đều dẫn `<file>:<dòng>` còn sống — chạy vòng `sed -n` trên từng dẫn
- [x] Q3 Mọi dòng CHUYỂN có đích tồn tại hoặc nhãn "đích MỚI" — chạy vòng `test -f`
- [x] Q4 Không lộ credential — `grep -c 'tvly-' <báo cáo>` trả 0
- [x] Q5 Bản CLAUDE.md đề xuất < 57 dòng và nhất quán với bảng — đếm dòng khối mã
- [x] Q6 Không vượt phạm vi — `git status --short` chỉ có file của request này; hai file
  trong `~/.claude/` giữ nguyên mtime
- [x] Q7 `python3 scripts/doc_lint.py` trên brief + spec + plan + báo cáo thoát 0

## QC
- Q1 bảng phán quyết: **PASS** — đếm bằng lệnh trên báo cáo, bảng có đúng **57** dòng dữ
  liệu, mỗi dòng đủ cột phán quyết + lý do. Phân bố đếm bằng máy (`awk … | uniq -c`):
  XOÁ 10 · GIỮ 21 · GIỮ (rút gọn) 12 · CHUYỂN 5 · dòng rỗng 9.
- Q2 bằng chứng dòng XOÁ: **PASS** — 14 dẫn `<file>:<dòng>` của 10 dòng XOÁ đều chạy lại
  `sed -n '<dòng>p' <file>` và ra đúng câu luật, không dẫn nào chết.
- Q3 đích dòng CHUYỂN: **PASS** — vòng `test -f` xanh cho cả hai đích:
  `skills/tdq-conventions/references/approval.md`, `skills/tdq-conventions/SKILL.md`.
- Q4 credential: **PASS** — `grep -c 'tvly-'` trên báo cáo trả **0**; mục settings.json chỉ
  gọi tên khoá, không in giá trị.
- Q5 bản đề xuất: **PASS** — khối mã CLAUDE.md đề xuất **29 dòng** < 57 (giảm 49%); mọi
  luật bị bỏ đều có mặt ở cột XOÁ hoặc CHUYỂN của bảng.
- Q6 phạm vi: **PASS** — `git status --short` chỉ có 4 file của request này cùng các file
  sinh tự động; `~/.claude/CLAUDE.md` giữ mtime 22-08, `settings.json` giữ mtime 31-08 —
  không file nào ngoài repo bị ghi.
- Q7 lint: **PASS** — `doc_lint.py` trên brief + spec + plan + báo cáo → `0 violation(s)
  total`, thoát 0.
- Ghi nhận: hai lần đếm đầu tiên của tôi sai (XOÁ 9/CHUYỂN 8, "31 dòng"); sửa lại sau khi
  đếm bằng lệnh trên chính bảng. Luật rút ra đã ghi vào báo cáo: **đếm bằng lệnh, không
  bằng mắt**.
