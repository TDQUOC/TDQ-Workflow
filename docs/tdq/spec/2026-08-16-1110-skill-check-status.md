# SPEC — Skill `tdq-check-status`: dò request đang dở và tiếp tục không mất dữ liệu

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-16 · Bản: 1.0 · Brief: ../brief/2026-08-16-1110-skill-check-status.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: thêm skill `tdq-check-status` để một agent vừa vào cuộc — session mới, máy
  khác, hoặc sau khi agent ngoài làm hộ một phase — dựng lại được ngữ cảnh request đang mở
  chỉ từ đĩa, báo cáo theo một khuôn cố định, rồi tiếp tục đúng chỗ sau MỘT lần user gật.
  Không ghi đè, không xoá, không mở lại request.
- Trong phạm vi:
  - Skill `skills/tdq-check-status/` + 2 file reference (khuôn báo cáo, bảng ca lệch).
  - CLI mới `scripts/tdq_checkstatus.py`: gom bằng chứng, chấm từng ca lệch, in báo cáo và
    in nguyên văn các lệnh vá đề xuất. Script KHÔNG tự ghi state.
  - Nguồn bằng chứng: `docs/tdq/state.json` · `docs/tdq/{brief,spec,plan,qc,reports}/<slug>.md`
    · git (`log`, `status`) · working log hôm nay.
  - Bản chép cho agent ngoài: `portable/workflow/05-check-status.md` + một dòng trong bảng
    phase của `portable/AGENTS.md`.
  - Test riêng cho từng ca lệch; đăng ký trần dòng skill mới vào `doc_lint` và test hình dạng.
- NGOÀI phạm vi (chép từ brief `### Phạm vi đã chốt`, mặt LOẠI, cộng 3 câu trả lời đóng):
  - Bảo mật — skill chỉ đọc file trong repo của chính user, không có dữ liệu nhạy cảm.
  - Hiệu năng runtime — trừ đúng một ngưỡng ở §5.
  - An toàn (safety) và đa nền tảng ngoài cặp Claude Code + agent ngoài.
  - Đọc transcript session cũ (user chốt câu 3: loại, vì transcript không đi theo khi đổi máy).
  - Request mồ côi — slug còn file nhưng không còn trong state (user chốt câu 5: chỉ lo
    request đang mở).
  - Thay thế hay sửa hành vi skill `tdq-status` (user chốt câu 2: hai skill riêng).

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | việc thuần nội bộ, mọi dữ kiện nằm trong repo này |
| Vòng scope | CÓ | đã chạy ở analyze, dấu hiệu 1 và 2 |
| Interview chi tiết | CÓ | đã chạy 1 vòng 6 câu, hết câu hỏi làm đổi kết quả |
| Spec riêng + plan checkbox | CÓ | khung bất biến của lane full |
| Chia subagent | BỎ | task nối nhau trên cùng bộ file, tách worktree chỉ đẻ xung đột |
| QC độc lập bằng agent | CÓ | luật khôi phục sai là mất dữ liệu — cần một lượt kiểm độc lập |
| Review sâu `tdq-reviewer` | BỎ | phạm vi đã khoá bằng 10 câu trả lời qua 2 vòng |
| Report | CÓ | khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Skill mới, đúng hình dạng bắt buộc | `skills/tdq-check-status/SKILL.md` | `pytest tests/test_skill_shape.py -k check_status` |
| 2 | Khuôn báo cáo cố định | `skills/tdq-check-status/references/report-template.md` | `pytest tests/test_check_status.py -k khuon_bao_cao` |
| 3 | Bảng 11 ca lệch → chẩn đoán → lệnh vá | `skills/tdq-check-status/references/bang-lech.md` | `pytest tests/test_check_status.py -k bang_lech` |
| 4 | CLI gom bằng chứng, in báo cáo | `scripts/tdq_checkstatus.py` (`report`, `--json`) | `pytest tests/test_check_status.py -k bao_cao` |
| 5 | Chấm đúng 11 ca lệch D1–D11 | cùng file trên | `pytest tests/test_check_status.py -k "ca_lech"` |
| 6 | Khối lệnh vá đề xuất, không tự chạy | cùng file trên | `pytest tests/test_check_status.py -k lenh_va` |
| 7 | Bản chép cho agent ngoài | `portable/workflow/05-check-status.md` + `portable/AGENTS.md` | `pytest tests/test_check_status.py -k portable` |
| 8 | Đăng ký trần dòng skill mới | `scripts/doc_lint.py` `SKILL_LINE_LIMITS` | `python3 scripts/doc_lint.py skills/tdq-check-status/SKILL.md` exit 0 |
| 9 | Log service của CLI mới | `scripts/tdq_checkstatus.py` | `TDQ_LOG=0 python3 scripts/tdq_checkstatus.py report 2>err`, `err` rỗng |
| 10 | Phát hành | `CHANGELOG.md` + `.claude-plugin/plugin.json` 0.21.0 | `grep -c "0.21.0"` cả hai ≥ 1 |

## 3. Cách tiếp cận & lý do

- Chọn: **đĩa là bằng chứng, `state.json` là lời khai.** Script đọc cả hai rồi chấm từng ca
  lệch; chỗ nào lệch thì tin đĩa và đề xuất sửa lời khai cho khớp.
- Vì: file spec/plan/qc là thứ đi theo repo khi bạn đổi máy hay đưa agent khác làm. `state.json`
  thì không đi theo — nó có thể cũ, thiếu trường, hoặc do bản plugin khác ghi.
- Chọn: **script chỉ ĐỌC và ĐỀ XUẤT; mọi lệnh ghi do skill chạy sau khi user gật.**
  Script in nguyên văn từng lệnh `tdq_state.py set …` vào khối `## Lệnh vá đề xuất`.
- Vì: ràng buộc kiến trúc "chỉ `tdq_state.py` được ghi `state.json`" (§5), và luật "chỉ
  NGƯỜI DÙNG duyệt". Một cổng gật duy nhất là đúng câu trả lời 2A của user.
- Chọn: **11 ca lệch D1–D11 liệt kê cứng trong một bảng**, mỗi ca có mã, dấu hiệu, mức
  (`ok` | `canh-bao` | `chan`), câu chẩn đoán và lệnh vá. Skill chỉ việc đọc bảng.
- Vì: user yêu cầu model yếu cũng theo được. Bảng tra cứu chặn được kiểu suy diễn tự do,
  vốn là chỗ model nhỏ chế ra lệnh sai và làm mất dữ liệu.
- Chọn: **ba mức kết luận** — `TIẾP TỤC ĐƯỢC` · `VÁ RỒI TIẾP TỤC` · `CẦN USER QUYẾT`.
- Vì: chỉ ba nhánh thì không có chỗ cho phán đoán mập mờ; mỗi nhánh có đúng một hành động kế.
- Đã loại: đọc transcript session cũ để dựng lại hội thoại — user loại ở câu 3; transcript
  nằm ngoài repo nên vô dụng đúng ở ca "đổi máy".
- Đã loại: cho skill tự chạy lệnh vá không hỏi — phá luật duyệt, và một lệnh `set phase=` sai
  đủ để đẩy request về phase làm lại từ đầu.
- Đã loại: gộp vào `tdq-status` — user chốt câu 2; `tdq-status` là báo nhanh trong lúc đang
  làm, nạp nó cho mọi lần hỏi trạng thái mà kéo theo luật khôi phục là phí context.
- Đã loại: dò slug mồ côi — user loại ở câu 5.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đã chạy phase analyze của request này |
| tdq-spec | plugin:tdq-workflow | NỀN | skill khung đang chạy ở phase này |
| tdq-conventions | plugin:tdq-workflow | DÙNG | skill mới trỏ về đây thay vì chép luật (đầu ra 1) |
| tdq-status | plugin:tdq-workflow | DÙNG | khoá ranh giới: thêm một dòng trỏ sang skill mới khi phát hiện lệch |
| tdq-plan | plugin:tdq-workflow | DÙNG | phase kế tiếp, viết plan checkbox |
| tdq-build | plugin:tdq-workflow | DÙNG | implement + QC + report của chính request này |
| skill-creator | plugin:skill-creator | DÙNG | khuôn tạo skill mới đúng chuẩn (đầu ra 1, 2, 3) |
| plugin-dev:skill-development | plugin:plugin-dev | DÙNG | luật viết `description` dễ trigger cho đầu ra 1 |
| graphify | plugin:graphify | DÙNG | tra node sẵn có trước khi viết hàm mới trong `scripts/` |
| mem0-memory | plugin:mem0 | DÙNG | chốt xong ghi một fact ngắn về cơ chế khôi phục |
| Đã xét 278 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp ra stderr, đủ chi tiết debug, tắt bằng `TDQ_LOG=0` —
  giống `tdq_timing.py`. Áp cho `scripts/tdq_checkstatus.py`.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- **Luật không mất dữ liệu (cứng).** Skill và script mới KHÔNG được gọi `tdq_state.py init`
  hay `reset`, không ghi đè `brief/spec/plan/qc/reports`, không xoá file nào. Lệnh vá chỉ
  được thuộc hai họ: `tdq_state.py set <key>=<value>` và `tdq_state.py approve <spec|plan>`.
- Clean code: BẬT (user chốt 2026-08-16 11:31, đáp án A) — cuối request chạy
  `python3 scripts/code_rule_scan.py` trên file đã đổi, còn LỖI thì fix tới khi sạch.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — bản NHÁP, user chưa chốt, nên ở
đây là ràng buộc tự nguyện):

- "Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`" — chạm ở đầu ra 4 và 6:
  `tdq_checkstatus.py` chỉ đọc state và IN lệnh, không ghi.
- "`skills/` chỉ được nhắc TÊN LỆNH của `scripts/`, cấm chép nội dung script" — chạm ở đầu
  ra 1, 2, 3: skill nhắc `tdq_checkstatus.py report`, không chép logic chấm ca lệch.
- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — `tdq_checkstatus.py` nằm ở `scripts/`.
- "`portable/` phải khớp bước với `skills/`" — chạm ở đầu ra 7: bản portable phải cùng số
  bước và cùng bảng ca lệch với bản `skills/`.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Chẩn đoán sai → lệnh vá đẩy request lùi phase | mất tick, làm lại việc đã xong | lệnh vá chỉ thuộc 2 họ `set`/`approve`; cấm `init`/`reset`; test riêng cho mỗi ca lệch |
| State do bản plugin cũ ghi, thiếu trường mới | script vỡ khi đọc | đọc qua `tdq_state.load()` (đã tự vá field thiếu); ca D9 báo `schema_version` cũ |
| Agent ngoài sửa file mà không ghi state | báo cáo nói "chưa làm" trong khi đã làm | ca D7/D8 đọc git log và working log hôm nay, đối chiếu mốc thời gian với `updated_at` |
| Repo không phải git (hoặc git lỗi) | script chết giữa chừng | nhánh git bọc try/except, ca D7 in `—` kèm lý do, không làm hỏng phần còn lại |
| Nhiều `[~]` trong plan | không biết đang đứng ở task nào | ca D4 hạ mức xuống `canh-bao`, liệt kê đủ mã task, để user chọn |
| Repo lớn, `git log` dài | lệnh chậm khi chỉ muốn xem trạng thái | giới hạn `git log` 20 commit gần nhất; ngưỡng: `report` xong dưới 2,0 giây |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Skill mới đúng hình dạng bắt buộc | `pytest tests/test_skill_shape.py -k check_status` | 1 passed (bước đánh số liên tục, có `Xong khi:`, `Bước kế tiếp:`) |
| Q2 | Không có request → báo đúng, thoát 0 | `pytest tests/test_check_status.py -k ca_lech_d1` | 1 passed |
| Q3 | Phase lệch bằng chứng đĩa (D2) | `pytest tests/test_check_status.py -k ca_lech_d2` | 1 passed |
| Q4 | sha256 spec/plan lệch sau khi duyệt (D3) | `pytest tests/test_check_status.py -k ca_lech_d3` | 1 passed |
| Q5 | Task `[~]` chỉ đúng chỗ dừng (D4) | `pytest tests/test_check_status.py -k ca_lech_d4` | 1 passed, in đúng mã task |
| Q6 | File đã đăng ký nhưng mất trên đĩa (D5) | `pytest tests/test_check_status.py -k ca_lech_d5` | 1 passed, mức `chan` |
| Q7 | Cờ duyệt thiếu người duyệt (D6) | `pytest tests/test_check_status.py -k ca_lech_d6` | 1 passed |
| Q8 | Dấu vết git sau `updated_at` (D7) | `pytest tests/test_check_status.py -k ca_lech_d7` | 1 passed |
| Q9 | Working log hôm nay (D8) | `pytest tests/test_check_status.py -k ca_lech_d8` | 1 passed |
| Q10 | `schema_version` cũ hơn bản hiện tại (D9) | `pytest tests/test_check_status.py -k ca_lech_d9` | 1 passed |
| Q11 | Thiếu mốc thời gian `started_at` (D10) | `pytest tests/test_check_status.py -k ca_lech_d10` | 1 passed |
| Q12 | `state.json` lạc chỗ (D11) | `pytest tests/test_check_status.py -k ca_lech_d11` | 1 passed |
| Q13 | Báo cáo đủ 6 mục cố định | `pytest tests/test_check_status.py -k khuon_bao_cao` | 1 passed |
| Q14 | Khối lệnh vá chỉ có `set`/`approve` | `pytest tests/test_check_status.py -k lenh_va` | 1 passed, không có `init`/`reset`/`rm` |
| Q15 | Bản portable khớp bước với bản skills | `pytest tests/test_check_status.py -k portable` | 1 passed |
| Q16 | Repo không phải git vẫn chạy | `pytest tests/test_check_status.py -k khong_git` | 1 passed, thoát 0 |
| Q17 | Log bật mặc định, tắt bằng `TDQ_LOG=0` | `TDQ_LOG=0 python3 scripts/tdq_checkstatus.py report 2>err >/dev/null; wc -l < err` | 0 dòng; không đặt biến thì ≥ 1 dòng có timestamp |
| Q18 | `report` chạy dưới 2 giây trên repo thật | `time python3 scripts/tdq_checkstatus.py report` | dưới 2,0 giây |
| Q19 | Suite không hồi quy | `python3 -m pytest -q` | không test nào đỏ, số test ≥ 639 |
| Q20 | Lint mọi file tài liệu đã sửa | `python3 scripts/doc_lint.py <các file>` | exit 0 |
| Q21 | Phát hành đúng bản | `grep -c "0.21.0" CHANGELOG.md .claude-plugin/plugin.json` | cả hai ≥ 1 |

DoD: cả 21 hạng mục Q1–Q21 PASS bằng đúng lệnh ghi ở cột giữa; thêm QC-F1 chạy toàn bộ suite,
QC-F2 hồi quy mọi vùng ghi ở dòng `Chạm:` của plan, QC-F3 đối chiếu bốn ràng buộc kiến trúc
§5, và một lượt QC độc lập bằng agent `tdq-qc-tester` theo lộ trình §1b.

## 7. Câu hỏi còn mở

(rỗng)
