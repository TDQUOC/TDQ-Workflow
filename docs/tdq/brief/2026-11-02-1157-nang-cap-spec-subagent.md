# Yêu cầu — Nâng cấp spec, visual archify và quyền subagent
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> Okay bây giờ tôi muốn update là spec của tdq workflow sẽ luôn phải làm rõ cơ chế đặc tính hiện tại là gì và sau update sau spec là gì (nếu là refactor hoặc update thì phải có hiện tại) kiểu như xem change về kiến trúc, luồng xử lí trước và sau thế nào. Về luồng xử lí thì phải vẽ trực quan 2 graph archify trước và sau r tích hợp vào 1 html file show ra để dev nắm và mô tả dễ hiểu nhất có thể. Luôn tổ chức code và update theo hướng ultra của ponytail (cố gắng code ít nhất, thay đổi ít nhất, nếu có gì đã có có thể dùng thì ko cần code thêm để giữ code và kiến trúc và project minimal nhất). Và khi có change phải có PR kĩ và test case kĩ để đảm bảo tính năng mới hoặc update mới không làm gãy luồng cũ, có thể sreach và prepare design partern để giữ cho project ổn dịnh sau nhiều change. Code cũ đã có nếu không ảnh hướng tới tính năng hoặc yêu cầu request thì không đụng vào. Được toàn quyền khởi tạo nhiều subagent để resreach cũng như phân tích mỗi con làm một việc và ghi report lại cho main agent đọc (nhưng subagent này chưa được phép edit chỉ sreach hoặc phân tích thông tin phụ cho main agent (cho phép khởi tạo ở mọi phase mà main agent cảm thấy cần để tiết kiệm thời gian và phân tích sâu hơn). QC và test case và DoD phải được thiết kế theo nghiệm vụ tính năng của request hoặc project không khởi tạo lan man (nhằm DoD và test case chạm đúng trọng tâm và đúng yêu cầu là đảm bảo hoạt động (vẫn dùng red test green test để khoanh vùng phạm vi)), hãy check và phân tích và cho tôi biết bạn hiểu gì từ yêu cầu này trước khi tiến hành

### Phân tích ban đầu

- **Mục tiêu**: Chuẩn hóa và siết chặt quy chuẩn spec, trực quan hóa luồng trước/sau bằng Archify (2 graph vào 1 HTML), phân quyền subagent chỉ đọc/nghiên cứu ở mọi phase, thiết kế QC/test/DoD trúng đích theo nghiệp vụ, duy trì triết lý Ponytail Ultra (minimal diff, không đụng code cũ không liên quan, chuẩn bị design pattern chống hồi quy).
- **Phạm vi dự kiến**:
  - `skills/tdq-spec/` (template spec, archify-ba reference: bắt buộc bảng Hiện trạng vs Sau update, 2 graph Before/After trong 1 HTML).
  - `skills/tdq-build/` & `scripts/tdq_archify.py` (tạo/bind bundle preview HTML chứa 2 graph trước/sau).
  - `skills/tdq-conventions/` (quy định subagent: toàn quyền tạo ở mọi phase để research/phân tích, giới hạn nghiêm ngặt read-only không edit, ghi report cho main agent; quy chuẩn Ponytail ultra, bảo vệ code cũ).
  - `skills/tdq-plan/` & `skills/tdq-build/` (DoD và test case bám sát nghiệp vụ, red-green test, không lan man, thiết kế design pattern ổn định).
- **Điểm cần làm rõ**: Chưa có điểm mâu thuẫn lớn, cần chốt pipeline và phương án cấu trúc hóa HTML 2 graph (tab chuyển đổi hay so sánh side-by-side).

## Hiểu & kiến thức

Pipeline full (user chọn `1a`), loại feature. Nhánh `feat/nang-cap-spec-subagent`, gốc `dev`. Init dùng `--bo-qua-lsp` vì request chủ yếu sửa luật trong `skills/` (bậc 8 python:. CHUA_KIEM).

### Năng lực dùng được

| Skill | Nguồn | Phán quyết | Dùng ở đâu / lý do |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-conventions | plugin:tdq-workflow | NỀN | Khung pipeline; đồng thời là chính file bị sửa |
| tdq-lean | plugin:tdq-workflow | DÙNG | Soát diff cuối theo Ponytail ultra |
| archify (local, `C:\Users\admin\Documents\archify`) | local installed | DÙNG | Dạng `explainer` đã gộp được nhiều sơ đồ vào một HTML |
| tdq-browser-test | plugin:tdq-workflow | DÙNG | Mở HTML Trước/Sau mẫu để kiểm bằng mắt khi QC |
| 18 skill khác trên đĩa + built-in | user/plugin/built-in | KHÔNG | Khác lĩnh vực |

### Khảo sát code và vùng ảnh hưởng

| Vùng file chạm | Lớp tìm | Hiện trạng | Cần đổi |
|---|---|---|---|
| `skills/tdq-spec/references/spec-template.md` §2c | Read + Grep | Đã có Mermaid + bảng Trước/Sau 3 dòng; chỉ bắt buộc với "cập nhật/tối ưu/refactor" | Bắt buộc mục "Cơ chế hiện tại" (kiến trúc + luồng) cho update/refactor/bugfix; tham chiếu HTML Trước/Sau |
| `skills/tdq-spec/references/archify-ba.md` | Read | Render **1** view `workflow` planned, bind vào spec | Đổi thành explainer gồm 2 sơ đồ Trước (evidence) + Sau (planned) + bảng khác biệt; vẫn render/bind bằng lệnh có sẵn |
| `skills/tdq-spec/references/spec-template-huong-dan.md` | Grep | Checklist có dòng "Trước vs Sau (§2c)" | Thêm dòng kiểm HTML Trước/Sau |
| `skills/tdq-conventions/SKILL.md` §9 + `references/subagent-tuning.md` | Read | Chỉ quy định tên/model/effort; research → subagent ở analyze | Luật: mở subagent đọc ở mọi phase, mỗi con một việc, chỉ đọc, report về main |
| `skills/tdq-spec` §6 / `tdq-plan` DoD | Read | §6 giữ điều kiện, DoD mỗi dòng một lệnh; chưa có luật "chỉ test đúng nghiệp vụ" | Thêm luật: mỗi Q/DoD truy về một hành vi nghiệp vụ hoặc một luồng cũ phải giữ; red→green |
| `skills/tdq-build/references/report-template.md` | Grep | Kết thúc bằng câu hỏi commit; chưa có thân PR | Chờ câu hỏi 4 |
| `scripts/tdq_archify.py`, `archify_*.py` | Read + smoke | `render --type explainer` chạy được; `archify compare architecture` native cũng có | **Không sửa** |
| `tests/test_spec_template.py`, `test_archify_workflow_contract.py`, `test_khao_sat_3_chieu.py` | Grep | Khoá nội dung template hiện tại | Thêm assert cho luật mới; không đổi assert cũ |

Smoke 2026-11-02: candidate `explainer` 2 panel, mỗi panel một `@workflow` → `tdq_archify.py render --type explainer` trả `out.html` + receipt, 2,0 s. Archify cho tối đa 4 sơ đồ native/trang.

### Nghiên cứu

`docs/tdq/research/2026-11-02-1157-nang-cap-spec-subagent.md` (subagent read-only). Rút ra: (1) một trang, hai sơ đồ cạnh nhau/tab, tô phần thêm/sửa; (2) main agent là writer duy nhất, subagent chỉ có tool đọc, phạm vi không chồng, trả digest có dẫn chứng; (3) chống hồi quy: chạy baseline trước khi sửa, AC theo luồng nghiệp vụ chính, không test chi tiết cài đặt.

### Quyết định nháp (chờ user)

- Rung 4 thang Ponytail: Archify đã cài lo được HTML 2 sơ đồ → **không thêm code**, chỉ sửa luật + test khoá luật.
- Subagent đọc: tận dụng loại agent sẵn không có Edit/Write (`Explore`, `Plan`, `tdq-reviewer`) thay vì dựng hook mới.
- Code cũ ngoài phạm vi: luật "surgical" đã có ở `chung.md` dòng 54 → chỉ nhắc chéo, không viết lại.

## Hỏi đáp

### Vòng 1 (2026-11-02)

User trả lời: "1a nhưng thể hiện đầy đủ bằng graph để người dùng dễ nhìn và dễ hiểu, description chỉ mô tả phụ trợ, 2B 3B nhưng vẫn cho phép ghi log hoặc report khi cần chỉ là không tự ý modify project khi chưa được phép (khi chưa ở implement, và lệch plan) 4A 5C"

| # | Câu hỏi | Chốt |
|---|---|---|
| 1 | Loại request bắt buộc Trước/Sau | Mọi request sửa thứ đã có (feature mở rộng, bugfix, refactor, update); dựng mới ghi "Hiện trạng: chưa có". **Graph là nội dung chính**, chữ chỉ phụ trợ |
| 2 | Pipeline áp dụng | Cả hai: deep (spec) và express (mini-plan) đều có HTML 2 sơ đồ |
| 3 | Bảo đảm subagent chỉ đọc | Thêm chặn bằng hook: subagent được ghi `docs/**` (log, report, research); ngoài `docs/` chỉ được ghi khi phase implement/qc, và vẫn bị rào `Chạm:` hiện có chặn khi lệch plan |
| 4 | PR kỹ | Report cuối soạn sẵn thân PR; không tự tạo PR |
| 5 | Mức QC | `ultra` (đã ghi `muc_qc=ultra`) |

### Kiến thức bổ sung sau vòng 1

- Tài liệu Claude Code hooks (đã kiểm 2026-11-02, https://code.claude.com/docs/en/hooks): hook `PreToolUse` chạy bên trong subagent nhận thêm `agent_id` và `agent_type`; ở luồng chính không có `agent_id`. Đây là tín hiệu để hook phân biệt subagent và main agent, không cần đoán theo đường dẫn.
- `hooks/scripts/edit_gate.py` đã có sẵn: miễn `docs/**` (dòng 112), rào `TDQ:TEAM` khi ghi ngoài vùng `Chạm:` (dòng 190–198), `block()` ở `_common.py`. Chỉ cần thêm một nhánh chặn; không thêm hook mới, không sửa `hooks.json`.
- Giới hạn chấp nhận (`ponytail:`): subagent ghi qua shell (`Bash`/`PowerShell`) không bị nhánh này bắt; nâng cấp khi đo được ca thật.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web thêm | BỎ | Đủ nguồn: research file + tài liệu hooks chính thức |
| Interview thêm | BỎ | Vòng 1 đã chốt hết 5 điểm làm đổi kết quả |
| Spec → plan | CÓ | Khung bất biến |
| QC độc lập (agent) | CÓ | `muc_qc=ultra` |
| Chia subagent khi implement | Chờ đo ở plan | Plan đo `tdq_bench.py simulate` rồi mới đề xuất |

Luồng tính năng:
1. Spec (deep): §2c "Cơ chế hiện tại vs Sau" do HTML 2 sơ đồ dẫn dắt, chữ phụ trợ.
2. Mini-plan (express): cùng luật, HTML 2 sơ đồ.
3. Subagent: mở được ở mọi phase; hook chặn ghi ngoài `docs/` khi chưa tới implement/qc.
4. DoD/test: mỗi dòng truy về một hành vi nghiệp vụ hoặc luồng cũ phải giữ; red→green.
5. Report: thêm khối thân PR soạn sẵn.
