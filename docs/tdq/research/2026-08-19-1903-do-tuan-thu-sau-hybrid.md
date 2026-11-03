# RESEARCH — đo tuân thủ luật sau hybrid

Ngày: 2026-08-19 · Request: 2026-08-19-1903-do-tuan-thu-sau-hybrid
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ba hướng tra: (1) công cụ chấm sẵn có ngay trong Claude Code, (2) độ tin của chấm bằng LLM,
(3) cần bao nhiêu mẫu thì số mới có nghĩa.

## 1. `claude plugin eval` — công cụ đã có sẵn, không phải tự dựng

Nguồn: `claude plugin eval --help` và `claude plugin eval init --help` chạy trên chính máy này
(2026-08-19). Đây là nguồn mạnh nhất vì là bản CLI đang cài, không phải tài liệu trên mạng.

Những gì lệnh này làm sẵn:

- Ca kiểm là `evals/**/case.yaml`, hoặc cặp `prompt.md` + `graders/*.md`.
- `--runs <n>` chạy lại mỗi ca nhiều lần, mặc định `case.runs ?? 3` — đúng thứ cần để
  chống nhiễu ngẫu nhiên.
- `--ablation with-without` tự thêm một nhánh KHÔNG có plugin để so.
- `--judge-model` đổi model chấm (mặc định haiku), `--max-cost-usd` chặn trần tiền,
  `--threshold` để rớt ngưỡng thì exit 1, `--json` xuất toàn bộ điểm từng lần chạy.
- Target nhận **đường dẫn**, nên chạy được trên một worktree ở commit bất kỳ.

Hệ quả: cặp so "bản Việt (`ea0cdbd`) ↔ bản thể lai (`f620094`)" làm được bằng cách chạy CÙNG
một bộ ca trên hai worktree, thay vì dựng khung chấm riêng. Nhánh `--ablation` có sẵn là
so plugin/không-plugin, KHÔNG phải so hai phiên bản — nên phần A/B theo phiên bản vẫn phải
tự ghép ở ngoài.

Chưa có `evals/` trong repo; `plugin.json` chưa khai `experimental.evals`.

## 2. Chấm bằng LLM — checklist thắng thang điểm

- Viswanathan et al. (2025), arXiv:2507.18624: rubric dạng **checklist** cho kết quả tốt hơn
  reward model thang điểm ở đúng bài toán instruction-following.
  Nguồn: https://medium.com/@adnanmasood/rubric-based-evals-llm-as-a-judge-methodologies-and-empirical-validation-in-domain-context-71936b989e80
- Cùng nguồn, LLMBar (ICLR 2024, arXiv:2310.07641) và SAGE (2025, arXiv:2512.16041): ngay cả
  model mạnh vẫn tự mâu thuẫn ở ~25% ca khó khi đóng vai giám khảo.
- Thực hành được nhắc lại ở nhiều nguồn: bắt giám khảo viết lý do TRƯỚC khi ra nhãn; định kỳ
  đối chiếu điểm máy với điểm người để biết giám khảo lệch bao nhiêu.
  Nguồn: https://www.reddit.com/r/AIEval/comments/1q59aaj/best_llmasajudge_practices_from_2025
- DeepEval khuyến nghị tách một giám khảo rộng thành cây quyết định nhiều nút nhỏ để bớt nhiễu.
  Nguồn: https://deepeval.com/blog/llm-as-a-judge

Rút ra cho request này: luật TDQ phần lớn kiểm được bằng **dấu vết máy đọc được** (có gọi
`tdq_state.py` không, có file spec không, có dừng ở cổng duyệt không). Ưu tiên grader tất
định; chỉ để giám khảo LLM lo phần thật sự cần đọc hiểu.

## 3. Bao nhiêu mẫu thì số có nghĩa — đây là ràng buộc chặn đường

- https://tianpan.co/blog/2026-04-15-statistical-power-llm-evals: cùng một câu hỏi chạy hai
  lần cùng tham số vẫn ra kết quả khác nhau; nhiễu có hai tầng (giữa các ca, và trong cùng
  một ca). Muốn bắt chênh lệch ~3 điểm phần trăm cần cỡ **1.200 ca** dù đã ghép cặp.
- https://dev.to/gabrielanhaia/eval-set-sizing-the-statistical-power-math-behind-llm-ab-tests-4gpc:
  thiết kế **ghép cặp** (cùng bộ câu hỏi cho cả hai nhánh) cần ít mẫu hơn hẳn hai nhánh độc
  lập, vì tín hiệu nằm ở các cặp lệch nhau. 4/100 ca đổi chiều là nằm trong nhiễu.
- https://github.com/ianarawjo/promptstats (`evalstats`): thư viện thống kê cho eval mẫu nhỏ,
  chạy được từ 15 mẫu, có kiểm định ghép cặp và phân tích ổn định giữa các lần chạy.

Rút ra: **cấm đặt mục tiêu bắt chênh lệch nhỏ.** Với ngân sách thật của một repo cá nhân,
phép đo này chỉ đủ sức phát hiện **sụt lớn** (kiểu một luật đang gần như luôn được tuân thủ
tụt xuống còn quá nửa). Phải nói thẳng giới hạn đó trong spec, thay vì in ra một con số
chênh 3% rồi kết luận.
