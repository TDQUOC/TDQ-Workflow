# Khuôn plan

Copy nguyên khối vào `docs/tdq/plan/<slug>.md` rồi điền.

```markdown
# PLAN — <tên việc>

Ngày: YYYY-MM-DD · Spec: ../spec/<slug>.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — <lý do 1–2 câu> (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: CHỜ DUYỆT

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
nào". Người thứ hai là máy: `scripts/tdq_team.py phan-cong` đọc các đường dẫn trong
backtick để dựng vùng file của task, rồi xếp task đụng chung file vào hai đợt khác nhau.

Vì vậy **mọi task tạo hoặc sửa file mã nguồn đều phải có dòng `Chạm:`**, kể cả task tạo
file mới. Đường dẫn phải nằm trong backtick và phải là đường dẫn thật tính từ gốc repo.
Task thiếu dòng này sẽ bị `phan-cong` xếp vào `tu_lam` với lý do `vung-khoa` — tức là
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
  `phan-cong` đọc mã này để giữ đúng thứ tự.
- Chia nhỏ theo FILE, đừng chia theo bước thời gian. "Viết `a.py`" + "viết test cho
  `a.py`" là một task; "viết `a.py`" + "viết `b.py`" là hai task chạy song song được.
- Ước lượng nhanh: đếm số task có `Chạm:` không giao nhau. Con số đó là trần tốc độ của
  mode đội. Đừng đoán bên nào thắng — chạy lệnh `mo-phong` ở bước 1 của
  [tdq-plan/SKILL.md](../SKILL.md) và lấy dòng `Thắng:` làm đề xuất.

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
Trỏ về §6 của spec. Liệt kê lại từng hạng mục QC + lệnh kiểm.
```

## Ước tính phút `(eNm)`

Đặt **ngay sau mã task**, trước phần việc: `- [ ] **T2.1** (e12m) việc — Test: ...`.
`eNm` = số **phút** Claude ước tính mình cần để tự THỰC THI xong task ấy (thời gian agent
chạy, không phải thời gian người chờ). Đơn vị luôn là phút, số nguyên 1–999, không viết
`1h` hay `0.5m`. ETA của cả plan = tổng `eNm` các task chưa xong.

Luật:
- Chấm ngay lúc viết task, không chấm bù sau.
- Ước tính thời gian LÀM, không tính thời gian chờ user duyệt hay interview.
- Phân vân → chấm số mình thật sự tin, đừng đệm thêm cho an toàn.
- `eNm` là **tuỳ chọn**: thiếu thì bỏ qua task đó khi cộng ETA, không chặn plan chạy.
- `eNm` KHÔNG đổi luật tick `[ ] [~] [x]` và không phải cam kết thời gian với user.

## Dòng `Mode thực thi`

- Phải nằm **một dòng riêng**, không ghép vào dòng header khác — công cụ đọc dòng này.
- Giá trị ghi ở đây là **định danh máy**: `main` hoặc `subagent`. Nhãn user đọc thấy ở
  cổng `mode` là "làm trực tiếp (inline implement)" và "giao trợ lý (sub-agent
  implement)" — xem [mode-gate.md](mode-gate.md).
- Đây chỉ là **đề xuất** của Claude. User duyệt plan xong, phase `mode` mới hỏi chọn;
  mode ghi vào state là mode user NÓI, không tự lấy đề xuất làm chốt. Câu duyệt đã kèm
  sẵn mode thì bỏ qua cổng đó, vào thẳng implement.

## Kiểm trước khi trình

- Mỗi đầu ra trong spec §2 ánh xạ tới ≥ 1 task.
- Mỗi task có đúng một việc và một cách kiểm đo được — không có task kiểu "hoàn thiện X".
- Task đầu của mỗi phase dựng được đường đi red → green sớm.
- Không task nào phụ thuộc task nằm sau nó.
