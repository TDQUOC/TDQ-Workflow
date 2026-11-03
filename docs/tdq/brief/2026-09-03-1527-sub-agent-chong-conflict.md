# BRIEF — Chống conflict khi chạy sub-agent implement

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay bây giờ mở request deep phân tích và đề xuất phương án xử lí vấn đề sau. khi chạy bằng
> sub-agent implement thì hay có trường hợp gây xung đột và conflict. tôi muốn xử lí lại là phân
> tích và đề xuất phương án để ở sub-agent mode khi lên plan sẽ như một team develop chuyên
> nghiệp, mỗi người mỗi nhánh riêng sẽ develop và merge vào để hạn chế conflict hoặc xung đột gây
> tốn thời gian và tài nguyên xử lí. để có thể làm việc ổn định . request này phân tích deep
> research và cho tôi đề xuất chưa thực thi ở mode này

### Đọc lần đầu

- **Mục tiêu:** mode `subagent` chạy ỔN ĐỊNH — hết cảnh nhiều agent đụng nhau, merge phải gỡ tay,
  tốn thời gian và token.
- **Phạm vi đoán:** `scripts/tdq_team.py` (chia đợt, worktree, merge), `skills/tdq-plan` (cách
  viết `Chạm:` và cụm song song), `skills/tdq-build/references/team-mode.md` (luật lãnh đạo).
- **Ranh giới rõ ràng do user đặt:** request này DỪNG ở đề xuất. Không sửa code, không thực thi.
- **Chỗ chưa rõ (chuyển sang `## Hỏi đáp`):** conflict thật đã xảy ra ở đâu, dạng gì; user muốn
  đề xuất dừng ở mức tài liệu hay kèm cả plan sẵn để duyệt sau.

## Hiểu & kiến thức

### Hệ hiện có đã làm được gì (đọc code, không đoán)

`scripts/tdq_team.py` (1177 dòng) đã dựng gần đủ mô hình "team dev chuyên nghiệp" mà user mô tả:

- `lenh_mo` (dòng 767) — mỗi task một **nhánh riêng** `_ten_nhanh(slug, ma)` + một **worktree
  riêng**, base là nhánh tích hợp `_nhanh_tich_hop(slug)`. Đúng ý "mỗi người mỗi nhánh".
- `chia_dot` (dòng 259) — chia đợt theo đồ thị phụ thuộc `Cần:`, và `_dot_som_nhat` (dòng 278)
  **cấm hai task chạm cùng file nằm chung một đợt**. Đây chính là cơ chế chống conflict chính.
- `_do_xung_dot` (dòng 809) — dò trước bằng `git merge-tree` ba chiều, KHÔNG đụng index/worktree.
- `lenh_hop` (dòng 856) — dò lại lần nữa, conflict thì CHẶN merge; sạch thì `merge --no-ff` vào
  nhánh tích hợp, bật `rerere.enabled`, rồi dọn worktree.
- `edit_gate.py` (dòng 108–134) — chặn LÃNH ĐẠO tự gõ code của task đã hứa giao đi.
- Trần 4 nhánh chạy đồng thời (dòng 64), lý do ghi rõ: điểm phối hợp tăng theo n(n−1)/2.

Kết luận: vấn đề KHÔNG phải "thiếu nhánh riêng". Nhánh riêng đã có từ lâu. Conflict còn xảy ra
là do bốn lỗ hở bên dưới.

### Bốn lỗ hở nghi là nguồn conflict

| # | Lỗ hở | Bằng chứng trong code | Hậu quả |
|---|---|---|---|
| H1 | `Chạm:` là lời KHAI bằng tay, không ai kiểm | `_dot_som_nhat` chỉ so `t.vung_file`; không có gate nào chặn sub-agent sửa file NGOÀI vùng khai | Hai agent cùng đợt sửa trúng một file không khai → conflict lúc `hop` |
| H2 | Không rebase trước khi merge | `lenh_hop` merge nhánh nguyên trạng; nhánh mở từ đầu đợt, agent thứ 2 merge sau agent thứ 1 thì base đã cũ | Conflict "chồng lấn thời gian", đúng thứ nghiên cứu ngoài gọi là phải rebase-trước-merge |
| H3 | Không có luật file nóng / chủ sở hữu duy nhất | không có khái niệm hotspot trong `tdq_team.py` | File kiểu `index`, `__init__`, bảng đăng ký, `manifest` bị mọi task chạm |
| H4 | Conflict xảy ra thì chỉ CHẶN, không có đường gỡ | `lenh_hop` trả 1 và bảo "resolve trong worktree" | Lãnh đạo gỡ tay, tốn đúng thời gian + token mà user than |

### Nghiên cứu ngoài (2026-09-03, `tavily-primary`)

- N1 — augmentcode.com/guides/git-worktrees-parallel-ai-agent-execution: "Git worktrees có **không
  có cơ chế cảnh báo** khi hai worktree sửa cùng file trên hai nhánh. Phải phân agent vào **miền
  file không giao nhau TRƯỚC khi bắt đầu**, và bật `git rerere`." → xác nhận H1 là lỗ hở đã biết
  của chính công cụ, không phải lỗi cấu hình.
- N2 — dev.to/battyterm/git-worktrees-changed-how-i-run-parallel-ai-agents: mẫu chuẩn là
  **lock → rebase lên main mới nhất → merge → nhả lock** cho từng agent, "mỗi merge tính đến mọi
  thứ đã vào trước nó". → xác nhận H2.
- N3 — cùng nguồn N2: "**file cấu hình dùng chung**… mọi nhánh đều phải sửa `Cargo.toml` thì
  worktree không cứu được. Cách chữa: tách thay đổi cấu hình chung thành **một bước riêng, chạy
  trước**." → xác nhận H3, và gợi ý luôn hình dạng lời giải.
- N4 — termdock.com/en/blog/git-worktree-conflicts-ai-agents: ba luật thực chiến — **một người
  ghi duy nhất cho file nóng**; **merge sớm và thường xuyên, rebase các nhánh còn lại**;
  **ưu tiên thêm file mới thay vì sửa file cũ** ("thêm thì hiếm khi conflict").
- N5 — dev.to/mashrulhaque: 5 nhánh song song mỗi ngày trong nhiều tuần, "**dưới 3 conflict**" —
  điều kiện đủ là **chọn task thật sự độc lập**. → chất lượng phân rã task quyết định, không phải
  công cụ git.

### Lộ trình

`analyze` (đang chạy) → `spec` → `plan` → **DỪNG**. User nói rõ "chưa thực thi ở mode này", nên
request này KHÔNG vào pha `implement`. Sản phẩm cuối là bản đề xuất để user đọc và quyết.
Pha `diagram` không chạy — đã gỡ khỏi quy trình từ bản 0.36.0.

## Hỏi đáp

**Vòng phạm vi (2026-09-03 15:34)** — user trả lời `1a 2b … 3a`:

1. **Phạm vi: cả 4 lỗ hở** (H1–H4).
2. **Dạng conflict gặp thật: hai agent sửa trúng cùng một file (B)**, kèm nguyên văn bổ sung:
   *"hoặc có vấn đề khiến việc main agent phải fix, gây tốn tài nguyên, tôi muốn xử lí để hạn chế
   việc sub-agent làm main agent fix"*. → Đây là một lỗ hở THỨ NĂM, không nằm trong 4 cái tôi
   nêu, và là mối bận tâm chính của user.
3. **Sản phẩm: spec + plan đầy đủ**, để duyệt rồi build ở request sau.

### H5 — sub-agent tự chấm điểm chính mình, leader lãnh hậu quả

Truy ngược theo câu bổ sung của user, đọc `agents/tdq-implementer.md` dòng 42–46 và
`lenh_kiem` (`tdq_team.py` dòng 835):

- Agent con trả về `STATUS: done` và `TICK-READY: yes` — **do chính nó tự khai**.
- `kiem <task>` chỉ dò **conflict merge**. Nó KHÔNG chạy lệnh test của task.
- `hop <task>` cũng chỉ dò conflict rồi merge.

Nghĩa là: giữa lúc agent con nói "xong" và lúc code vào nhánh tích hợp, **không có một bước nào
kiểm chứng độc lập rằng test của task thật sự xanh**. Agent con làm ẩu hoặc khai sai thì commit
hỏng đã nằm trong nhánh tích hợp, leader phát hiện muộn và phải tự sửa — đúng cảnh "tốn tài
nguyên" user mô tả. `soul.md` xếp chất lượng trên runtime, nên đây là lỗ hở nặng nhất trong năm.

Đối chiếu nguồn N5: điều kiện để mô hình song song chạy êm là **task thật sự độc lập** và kết quả
**được kiểm trước khi gộp** — ta đang thiếu vế thứ hai.

### Phạm vi chốt

H1 · H2 · H3 · H4 · **H5** (thêm theo câu trả lời 2). Request dừng sau pha `plan`.
