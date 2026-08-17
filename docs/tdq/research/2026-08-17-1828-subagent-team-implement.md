# RESEARCH — chạy nhiều subagent song song có worktree riêng

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Request: `2026-08-17-1828-subagent-team-implement` · phase analyze · 2 truy vấn qua `tavily-primary`.

## Truy vấn 1 — trần song song của subagent trong Claude Code

- `github.com/anthropics/claude-code/issues/15487` (27-12-2025): **không có trần cứng**.
  Người báo lỗi ghi nhận **24 tiến trình subagent sinh trong 2 phút** làm treo cả VPS, phải
  reboot cứng. Đề nghị thêm `maxParallelAgents` vào settings — tới thời điểm bài viết CHƯA có.
  Cùng issue xác nhận: **nhiều lệnh `Task` trong MỘT response = chạy đồng thời**.
- `github.com/anthropics/claude-code/issues/3013`: đề xuất chế độ phân rã đệ quy + pha
  (huge → 15-25 subtask, large → 8-15…), mỗi pha khai `parallel_agents`. Vẫn là feature
  request, không phải tính năng có sẵn.
- `cloudzero.com/blog/claude-code-agents`: **chi phí tuyến tính** — 10 agent song song đốt
  quota nhanh gấp 10. Không có billing riêng cho agent; Pro cạn cửa sổ 5 giờ trong dưới một
  giờ với 5 agent. "How many agents in parallel? No hard cap — trần thật là quota và rate limit."

**Rút ra:** trần phải do CHÍNH workflow đặt, không trông vào nền tảng. Một con số cấu hình
được (đợt bao nhiêu agent) là bắt buộc, không phải tuỳ chọn.

## Truy vấn 2 — worktree và chiến lược merge cho nhiều agent

- `augmentcode.com/guides/git-worktrees-parallel-ai-agent-execution`: git **không có cơ chế
  cảnh báo khi hai worktree sửa cùng một file** trên hai nhánh. Phải **phân vùng file không
  chồng nhau TRƯỚC khi giao việc**. Bật `git rerere` để ghi nhớ cách giải xung đột lặp lại.
  Dọn bằng `git worktree remove`, không `rm -rf` (để lại rác trong `.git/worktrees/`).
- `zylos.ai/research/…git-worktree-parallel-ai-development`: ba chiến lược merge —
  (1) **hợp tuần tự** vào main từng nhánh một, an toàn nhất; (2) **rebase trước khi merge**,
  được khuyến nghị rộng rãi nhất; (3) **dò xung đột trước** bằng
  `git merge-tree $(git merge-base A B) A B` — ba chiều, KHÔNG đụng repo, chạy được ngay khi
  agent còn đang làm để orchestrator kịp đổi hướng.
- `mindstudio.ai/blog/parallel-agentic-development-git-worktrees`: "**Lập bản đồ sở hữu file
  từ đầu là bước quan trọng nhất. Bỏ qua nó thì trả giá lúc merge.**" Khuyên bảng
  `Task | Agent | Primary Files | Dependencies | Integration Point`. Mốc quy mô: PR-mỗi-agent
  ổn tới 4–5 agent song song; đông hơn thì cần hàng đợi + lập lịch theo phụ thuộc.
- `termdock.com/en/blog/git-worktree-conflicts-ai-agents`: ba luật giảm xung đột —
  **một-người-ghi** cho file điểm nóng (file route, file index), **merge sớm và thường xuyên**
  (nhánh xong trước vào main rồi các nhánh còn lại rebase), và **chỉ thêm, không sửa**
  (thêm file mới thay vì sửa file chung — phần thêm gần như không bao giờ xung đột).
- `parallelcode.app/blog/parallel-ai-agents`: 5 agent cùng repo không đụng thư mục làm việc;
  xung đột dồn về lúc tích hợp và được giải **từng cái một** thay vì rối vào nhau.

**Rút ra:** ba thứ phải có trong thiết kế, theo đúng thứ tự quan trọng —
1. plan phải khai được **file mỗi task chạm** để leader phân vùng không chồng nhau;
2. leader **dò xung đột bằng `git merge-tree` trước khi merge**, không merge mù;
3. **hợp tuần tự từng nhánh** vào nhánh tích hợp, rebase nhánh còn lại sau mỗi lần merge.

## Điều KHÔNG tìm thấy

Không nguồn nào nói về workflow có state/gate duyệt như TDQ, cũng không nguồn nào bàn
chuyện hook chặn tick khi nhiều agent cùng chạy. Phần đó là bài toán riêng của repo này,
phải tự thiết kế — xem `## Hiểu & kiến thức` trong brief.
