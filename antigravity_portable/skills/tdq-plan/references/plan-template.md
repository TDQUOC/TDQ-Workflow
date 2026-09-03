# The plan shape

Copy the whole block into `docs/tdq/plan/<slug>.md` and fill it in.

## Table of contents

- The minute estimate `(eNm)`
- The `Mode thực thi` line <!-- i18n-allow: canonical line name of the plan -->
- Check before presenting

<!-- i18n-allow: plan template written in the default document language -->
```markdown
# PLAN — <tên việc>

Ngày: YYYY-MM-DD · Spec: ../spec/<slug>.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — <lý do 1–2 câu> (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: CHỜ DUYỆT

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — <tên phase>
- P2 — <tên phase>
- Dòng `Chạm:` (đặt NGAY DƯỚI mọi task TẠO hoặc SỬA file mã nguồn)
- Luật file nóng (một file, nhiều task chạm)
- Dòng `Cần:` (khai phụ thuộc giữa các task)
- Cụm song song
- Khuôn khối hợp đồng skill (đặt NGAY DƯỚI dòng task dùng skill đó, ≤6 dòng)
- Px — Log & test bắt buộc
- Definition of Done
- Ước tính phút `(eNm)`
- Dòng `Mode thực thi`
- Kiểm trước khi trình

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — <tên phase>
- [ ] **T1.1** (e6m) <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
- [ ] **T1.2** (e12m) <việc cụ thể> — Test: <...>

**Xong P1 khi**: <điều kiện đo được>

## P2 — <tên phase>
- [ ] **T2.1** (e20m) <...> — Test: <...>

## Dòng `Chạm:` (đặt NGAY DƯỚI mọi task TẠO hoặc SỬA file mã nguồn)
- [ ] **T<x.y>** <việc sửa hàm/file sẵn có> — Test: <...>
  - Chạm: `<đường/dẫn/file.py>`, `<tests/test_file.py>` → <node bị ảnh hưởng> (nguồn: `graphify affected "<X>" --depth 2`)
- [ ] **T<x.z>** <việc tạo file mới> — Test: <...>
  - Chạm: `<đường/dẫn/file-moi.py>` → file mới, chưa node nào phụ thuộc

Dòng này có HAI người đọc. Người thứ nhất là bạn: nó trả lời "sửa chỗ này thì vỡ chỗ
nào". Người thứ hai là máy: `~/.gemini/config/plugins/tdq-workflow/scripts/tdq_team.py assign` đọc các đường dẫn trong
backtick để dựng vùng file của task, rồi xếp task đụng chung file vào hai đợt khác nhau.

Vì vậy **mọi task tạo hoặc sửa file mã nguồn đều phải có dòng `Chạm:`**, kể cả task tạo
file mới. Đường dẫn phải nằm trong backtick và phải là đường dẫn thật tính từ gốc repo.
Task thiếu dòng này sẽ bị `assign` xếp vào `tu_lam` với lý do `vung-khoa` — tức là
leader phải tự làm, mất chỗ chạy song song. Task chỉ sửa tài liệu thì bỏ dòng này.
Node nằm trong mục `## Hub` của `docs/kien-truc.md` → task phải thêm một dòng DoD kiểm
hồi quy riêng cho node ấy.

## Dòng `Cần:` (khai phụ thuộc giữa các task)

Đặt ngay dưới task, sau dòng `Chạm:` nếu có. Một dòng, mã task ngoài backtick, phân cách
bằng dấu phẩy:

- [ ] **T3.2** việc đọc đầu ra của task khác — Test: <...>
  - Cần: T3.1, T1.3

Task nào ĐỌC đầu ra của task khác thì BẮT BUỘC khai. Ví dụ: task gọi hàm mà task khác vừa
viết, task sinh lại bản portable sau khi task khác sửa skill.

Máy đọc dòng này để xếp đợt: task chỉ được phát khi mọi mã trong `Cần:` đã xong. Plan
KHÔNG khai `Cần:` ở bất kỳ task nào thì máy lùi về luật cũ — thứ tự phase là thứ tự phụ
thuộc. Luật lùi này giữ cho plan viết trước đây chạy y như cũ.

Cấm khai vòng: A cần B mà B cần A thì máy báo lỗi và dừng, không tự gỡ.

## Cụm song song

Mục này BẮT BUỘC có trong mọi plan, mọi lane, mọi mode — kể cả khi kết luận là chỉ một
cụm. Lý do: tính modular là thuộc tính của TÀI LIỆU, không phải của mode thi hành. Viết
"một cụm vì <lý do>" vẫn hợp lệ; bỏ trắng mục thì `doc_lint --pair` báo lỗi.

Mode `subagent` chia task thành từng đợt. Hai task cùng đợt chạy đồng thời ở hai worktree
khác nhau, nên chúng KHÔNG được đụng chung một file — git không hề cảnh báo, tới lúc
merge mới vỡ. Máy tự chia đợt từ dòng `Chạm:`, nhưng bạn viết plan mới là người biết ý
đồ, nên hãy giúp máy chia đúng:

- Gom task cùng chạm một file vào cùng một phase, đặt kề nhau, để thứ tự đọc ra được.
- Task phụ thuộc task khác thì nhắc mã task đó trong phần mô tả (vd "sau `T1.1`").
  `assign` đọc mã này để giữ đúng thứ tự.
- Chia nhỏ theo FILE, đừng chia theo bước thời gian. "Viết `a.py`" + "viết test cho
  `a.py`" là một task; "viết `a.py`" + "viết `b.py`" là hai task chạy song song được.
- Ước lượng nhanh: đếm số task có `Chạm:` không giao nhau. Con số đó là trần tốc độ của
  mode đội. Đừng đoán bên nào thắng — chạy lệnh `simulate` ở bước 1 của
  [tdq-plan/SKILL.md](../SKILL.md) và lấy dòng `Winner:` làm đề xuất.

## Luật file nóng (một file, nhiều task chạm)

`assign` đếm số task khai mỗi đường dẫn ở dòng `Chạm:`; đường dẫn nào từ 2 task trở lên bị in
ra dưới nhãn `HOT FILE` kèm mã các task. Worktree KHÔNG cứu được loại file này: mọi nhánh đều
phải sửa nó, nên đợt nào cũng đụng nhau (nghiên cứu N3 của brief).

Cách nhận diện khi đang viết plan: file kiểu bảng đăng ký, `index`, `__init__`, `manifest`,
bảng hằng số — thứ mà "thêm một mục" là bước bắt buộc của nhiều task.

Hai cách xử lý, chọn một, không có cách thứ ba:

- **Nâng lên đợt sớm**: tách phần sửa chung thành MỘT task riêng, đặt ở phase trước; các task
  sau nhánh ra từ file đã ổn định. Đây là cách mặc định.
- **Một chủ ghi duy nhất**: nếu không tách được, để đúng MỘT task khai file đó ở `Chạm:`, các
  task còn lại không được chạm; ai cần thay đổi ở đó thì báo để gộp vào task chủ.

## Khuôn khối hợp đồng skill (đặt NGAY DƯỚI dòng task dùng skill đó, ≤6 dòng)
- [ ] **T<x.y>** <việc của task> — Test: <...>
  - Dùng: `<tên skill>`
- [ ] **T<x.z>** <task mà skill cần MCP tool> — Test: <...>
  - Dùng: `<tên skill>` (mcp)
  - Để: <việc cụ thể skill lo trong task này>, nạp skill TRƯỚC bước đỏ. Agent ngoài
    không có skill system: đọc `<đường dẫn>/SKILL.md` rồi làm theo.
  - Ra: <artifact phải tồn tại sau task, có đường dẫn>
  - Kiểm: <một lệnh chạy được, PASS đo được>
  - Không dùng cho: <việc kề bên mà skill này KHÔNG được lan sang>

Luật nhãn `(mcp)` — BẮT BUỘC ghi ngay khi lập plan: skill nào cần MCP tool lúc
chạy (gọi server MCP, ví dụ tavily/notion) → dòng `Dùng:` phải kết thúc bằng nhãn
` (mcp)` NGOÀI backtick, cuối dòng, đúng cú pháp spec §1. `split-plan` đọc nhãn
này để biết task nào buộc phải do Claude tự làm, không giao sub-agent thiếu MCP.

## Px — Log & test bắt buộc
Phase này bắt buộc **chỉ khi việc này có runtime** — tức có ít nhất một task tạo hoặc sửa
file mã nguồn chạy được. Không có runtime (chỉ sửa tài liệu, khuôn mẫu, cấu hình) → bỏ
task log, giữ task test, và ghi đúng một dòng `Log: BỎ — <lý do một câu>`.

- [ ] **Tx.1** Log service bật mặc định (timestamp, mức log, tắt được qua config) — Test: <...>
- [ ] **Tx.2** Unit test cho từng thành phần, chạy bằng một lệnh — Test: <lệnh>

## Definition of Done
Trỏ về §6 của spec. Liệt kê lại từng hạng mục QC + lệnh kiểm, MỖI DÒNG MỘT Ô TICK:

- [ ] Q1 <điều kiện đủ> — <lệnh kiểm>
- [ ] Q2 <điều kiện đủ> — <lệnh kiểm>
```

These boxes are **the close-out evidence**, not decoration: mark `[x]` when that item PASSes
and its evidence already sits in the qc file. The machine counts them — `dod_tick_state()`
reads this section on its own, and hook `Stop` fires `[TDQ:DOD]` when the books close on an
open box while QC has passed everything. A DoD written without boxes still runs, it just
loses that net.

## The minute estimate `(eNm)`

Goes **right after the task code**, before the work itself: `- [ ] **T2.1** (e12m) <work> — Test: ...`.
`eNm` = the number of **minutes** Claude estimates it needs to EXECUTE that task itself (agent
runtime, not human waiting time). The unit is always minutes, an integer 1–999, never `1h` or
`0.5m`. The ETA of the whole plan = the sum of `eNm` over unfinished tasks.

Rules:
- Score it as you write the task, never score it later.
- Estimate the time spent WORKING, not the time waiting for approval or interview answers.
- Unsure → score the number you actually believe, do not pad for safety.
- `eNm` is **optional**: missing on a task means that task is skipped in the ETA sum, and the
  plan still runs.
- `eNm` changes nothing about the tick rule `[ ] [~] [x]` and is not a promise of time to user.

## The `Mode thực thi` line <!-- i18n-allow: canonical line name of the plan -->

- It MUST sit on **a line of its own**, never merged into another header line — tooling reads it.
- The value here is the **machine identifier**: `main` or `subagent`. The label the user reads at
  gate `mode` is "làm trực tiếp (inline implement)" and "giao trợ lý (sub-agent implement)" — <!-- i18n-allow: user-facing mode labels -->
  see [mode-gate.md](mode-gate.md).
- This is only Claude's **proposal**. After the user approves the plan, phase `mode` asks; the
  mode written into state is the one the user SAID, never the proposal taken as settled. An
  approval sentence that already names a mode skips that gate and goes straight to implement.

## Check before presenting

- Every output in spec §2 maps to ≥ 1 task.
- Every task holds exactly one piece of work and one measurable check — no task shaped like
  "finish X".
- The first task of each phase opens a red → green path early.
- No task depends on a task placed after it.
