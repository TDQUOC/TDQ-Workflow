# RESEARCH — Khi nào chia task lập trình cho nhiều subagent song song thắng single agent

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Truy vấn đã chạy
1. Anthropic/Claude Code: multi-agent orchestration, subagent, parallel agents, git worktree isolation.
2. Kết quả đo thật: multi-agent LLM có nhanh/tốt hơn single agent không, token cost tăng bao nhiêu.
3. Thất bại multi-agent coding: xung đột file, mất ngữ cảnh, nguyên nhân gốc.
4. Cách chia task để song song hoá: file-ownership, dependency graph, critical path.

## Nguồn
- aakashx.com, Parallel Claude Code Agents — https://www.aakashx.com/blog/parallel-claude-code-agents — `isolation: worktree` cho subagent ghi file; agent chỉ đọc thì không cần, tốn setup vô ích.
- addyosmani.com, Code Agent Orchestra — https://addyosmani.com/blog/code-agent-orchestra — subagent cần brief rõ + file ownership; luôn có quality gate, không tin output chưa verify.
- hidekazu-konishi.com, Claude Code Subagents Guide — https://hidekazu-konishi.com/entry/claude_code_subagents_and_orchestration_guide.html — worktree dành riêng cho agent thật sự ghi file song song, tránh trạng thái half-applied.
- zylos.ai, Git Worktree Isolation Patterns — https://zylos.ai/research/2026-02-22-git-worktree-parallel-ai-development — worktree CI song song giảm ~63% thời gian build; merge lại mới là phần khó nhất, không phải cô lập.
- Medium mjgmario, Single-Agent vs Multi-Agent Systems — https://medium.com/@mjgmario/single-agent-vs-multi-agent-systems-when-coordination-helps-hurts-and-pays-off-57735ee7916d — multi-agent tốn ~4x token; ca thực tế 94.3% vs 92.2% accuracy nhưng chi phí 47k so với 22.7k USD/tháng.
- arXiv 2604.02460, Single-Agent LLMs Outperform Multi-Agent — https://arxiv.org/html/2604.02460v1 — cùng ngân sách token suy luận, single agent bằng hoặc thắng multi-agent trên multi-hop reasoning, trừ khi context bị suy giảm sẵn.
- Galileo AI, Why Multi-Agent Systems Fail — https://galileo.ai/blog/why-multi-agent-systems-fail — chi phí phối hợp tăng theo cấp số nhân: 4 agent có 6 điểm lỗi tiềm năng, 10 agent có 45.
- Atlan, Agent Harness Failures 13 Anti-Patterns — https://atlan.com/know/agent-harness-failures-anti-patterns — 65% lỗi agent doanh nghiệp do context drift; ngữ cảnh suy giảm ~2%/bước, sau 5 vòng còn dưới 60%.
- GitHub vectara/awesome-agent-failures — https://github.com/vectara/awesome-agent-failures — case thật: các phiên Claude Code song song ghi đè lẫn nhau vì không khoá file, không phát hiện xung đột.
- arXiv 2503.13657, Why Do Multi-Agent LLM Systems Fail — https://arxiv.org/pdf/2503.13657 — liệt kê failure mode: mất lịch sử hội thoại (2.8%), lặp bước (15.7%), bỏ qua input agent khác (1.9%), sai lệch reasoning-action (13.2%).
- arXiv 2606.00953, Cohesion-Aware Task Partitioning — https://arxiv.org/html/2606.00953v1 — mô hình hoá orchestration đa agent như graph partitioning; chia nhỏ giảm critical-path nhưng dependency chéo tốn chi phí chuyển ngữ cảnh, có thể triệt tiêu lợi ích.
- MindStudio, Parallel Agentic Development With Git Worktrees — https://www.mindstudio.ai/blog/parallel-agentic-development-git-worktrees — lập bản đồ file-ownership trước khi chạy là bước quan trọng nhất; task chung file phải chạy tuần tự, không song song.
- explainx.ai, task-coordination-strategies — https://explainx.ai/skills/wshobson/agents/task-coordination-strategies — 4 chiến lược chia task (layer, chức năng, cross-cutting, file-ownership) kèm mẫu dependency graph independent/sequential/diamond.

## Điều rút ra
1. Song song chỉ thắng khi các task không chạm chung file và có thể chạy độc lập trên critical path (mindstudio.ai; explainx.ai).
2. Nên dùng `isolation: worktree` riêng cho agent thật sự ghi file song song; agent chỉ đọc thì không cần, tốn chi phí vô ích (hidekazu-konishi.com; aakashx.com).
3. Cùng ngân sách token suy luận, single agent bằng hoặc thắng multi-agent trên bài multi-hop reasoning, trừ khi ngữ cảnh single agent đã suy giảm sẵn (arXiv 2604.02460).
4. Multi-agent tốn trung bình khoảng 4 lần token so với single agent trong ca thực tế đo được (medium.com/@mjgmario).
5. Số điểm lỗi phối hợp tăng theo cấp số nhân với số agent: 4 agent có 6 điểm, 10 agent có 45 (galileo.ai).
6. Không khoá file hoặc không chia ownership rõ khiến các phiên agent song song ghi đè lẫn nhau, mất việc (github.com/vectara/awesome-agent-failures).
7. Chia task nên dựa dependency graph và cô lập các file "in-hub" dùng chung riêng để không kéo dài critical path của nhóm nào (arXiv 2606.00953).
8. Ngữ cảnh drift qua nhiều bước là nguyên nhân gốc phổ biến nhất của lỗi agent doanh nghiệp, chiếm khoảng 65% (atlan.com).

## Ngược với giả định
- Giả định "song song luôn nhanh và tốt hơn" bị bác: dưới ngân sách token cố định, single agent bằng hoặc thắng multi-agent, multi-agent chỉ có lợi khi ngữ cảnh single agent đã suy giảm (arXiv 2604.02460).
- Chi phí phối hợp tăng theo cấp số nhân với số agent, nên thêm agent không chắc thêm tốc độ, có thể thêm lỗi (galileo.ai).
- Multi-agent có thể tốn gấp khoảng 4 lần token dù chỉ cải thiện độ chính xác vài điểm phần trăm, đổi lấy chi phí vận hành lớn hơn nhiều (medium.com/@mjgmario).

## Vòng 2 — lịch trình đợt và chất lượng khi song song

Hai agent research chạy song song, mỗi agent 4 truy vấn qua `tavily-primary`.

### Nguồn — lịch trình và chia đợt

- MindStudio, agent teams — https://mindstudio.ai/blog/claude-code-agent-teams-shared-task-list — trần 2 đến 4 agent là điểm ngọt thực dụng, thêm nữa không tăng tốc tương xứng.
- Stanford CS244C, DAG-aware scheduling — https://scs.stanford.edu/26wi-cs244c/proj/dag_sched_agent.pdf — không dùng trần cố định, dispatch động theo số call đang bay; lấy barrier làm baseline để so, không phải đích.
- DynTaskMAS — https://arxiv.org/html/2503.07675v1 — đồ thị task được sửa và mở rộng lúc chạy, nên đợt tĩnh sẽ lệch khi kế hoạch phình ra giữa chừng.
- MDPI, Dynamic Task Graph — https://www.mdpi.com/2079-9292/15/11/2475 — thực nghiệm tới 32 agent một node, ưu tiên đánh giá lại độ ưu tiên lúc chạy.
- HEFT list scheduling — https://web.fe.up.pt/~jbarbosa/JBetal_vecpar08.pdf — xếp theo b-level, độ phức tạp bậc hai theo số nút, hợp cho đồ thị 10 đến 20 task.
- LDCTF — https://thesai.org — ưu tiên task nằm trên đường găng trước, phần còn lại xếp theo thời điểm kết thúc sớm nhất.
- Đồng bộ pipeline — https://umich.edu — càng nhiều điểm barrier càng mất phần tăng tốc lý tưởng.
- MindStudio, parallel workflows — https://mindstudio.ai/blog/claude-code-agent-teams-parallel-workflows — ownership theo thư mục, worktree cách ly, danh sách việc chung có khoá và cờ phụ thuộc.
- Hidekazu Konishi, orchestration guide — https://hidekazu-konishi.com — mục 9.5 về phát hiện xung đột trước khi chạy.
- Vibe Kanban, ghi nhận thực tế — https://www.youtube.com/watch?v=W45XJWZiwPM — ba agent song song vẫn xung đột trên file registry chung dù logic nằm ở file riêng.
- Aakash, parallel Claude Code agents — https://aakashx.com/blog/parallel-claude-code-agents — định nghĩa hợp đồng dùng chung tuần tự trước, rồi mới tách agent.

### Nguồn — chất lượng khi song song

- O'Reilly Radar, spec cho agent — https://www.oreilly.com/radar/how-to-write-a-good-spec-for-ai-agents — brief cần mục tiêu, ranh giới ba tầng, và phép tự kiểm.
- Addy Osmani, good spec — https://addyosmani.com/blog/good-spec — đưa đủ ngữ cảnh module, đừng cắt nửa vời; dùng LLM chấm cho tiêu chí chủ quan.
- Addy Osmani, workflow 2026 — https://medium.com/@addyosmani/my-llm-coding-workflow-going-into-2026 — task cần 4 module thì đưa cả 4.
- Panel nhiều giám khảo — https://arxiv.org/html/2603.28488v1 — panel 3 giám khảo tăng 3,3 điểm nhưng tốn khoảng 11 lần token; đổi vai trong tranh luận làm giảm 4,2 điểm.
- CollabEval — https://assets.amazon.science — vòng tranh luận thứ ba làm điểm tụt, lợi ích giảm dần.
- Harvard, modularity cho sinh mã — https://namin.seas.harvard.edu/pubs/lmpl-modularity.pdf — spec modular giúp điểm benchmark tăng tới 30%.
- CodePori và MAGIS — https://arxiv.org/html/2508.00083v1 — quản lý phân rã, nhiều agent viết module song song, một agent kiểm tích hợp.
- Fast.io, phân rã task — https://fast.io/resources/multi-agent-task-decomposition-patterns — chia 4 agent tốn 35 nghìn token cho việc một agent làm hết chỉ tốn 10 nghìn; một agent làm tốt 80% thì đừng tách.
- Amazon Science, phân rã task — https://www.amazon.science — thêm agent làm tăng độ phức tạp điều phối, cảnh báo tránh làm quá tay.

### Điều rút ra — vòng 2

1. Trần cố định 4 được một nguồn ủng hộ, nhưng ba nguồn khác nói nên xếp theo độ rộng thật của đồ thị, không ép đủ số.
2. Barrier cứng là baseline, không phải đích; phát liên tục theo danh sách sẵn sàng là bản tốt hơn.
3. Luật xếp thứ tự đáng dùng nhất cho 10 đến 20 task là ưu tiên đường găng, phần còn lại theo kết thúc sớm nhất.
4. File dùng chung vẫn xung đột dù chia ownership theo thư mục, nên hợp đồng dùng chung phải làm tuần tự trước.
5. Prompt giao việc cần ranh giới ba tầng và phép tự kiểm, không chỉ mô tả việc.
6. Panel nhiều giám khảo tăng chất lượng ít mà tốn nhiều; không nên đưa vào bản này.
7. Spec modular có bằng chứng làm điểm sinh mã tăng tới 30 phần trăm.
8. Chia quá nhỏ tốn khoảng 3,5 lần token; dấu hiệu là subtask không mô tả nổi trong hai câu.

### Ngược với giả định — vòng 2

- Giả định "trần cố định là đủ tốt" bị ba nguồn phản bác; nên là trần trên, không phải chỉ tiêu.
- Giả định "thêm lớp kiểm chéo thì chất lượng tăng" sai ở ca đổi vai, giảm 4,2 điểm.
- Giả định "chia càng nhỏ càng song song được" sai khi phí bàn giao vượt phần tiết kiệm.
