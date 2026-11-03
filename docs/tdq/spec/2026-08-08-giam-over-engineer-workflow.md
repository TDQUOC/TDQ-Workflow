# SPEC — Giảm over-engineer & over-test cho TDQ workflow

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-08 · Bản: 1.0 · Request: ../requests/2026-08-08-giam-over-engineer-workflow.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- **Mục tiêu:** giảm token nạp và thời gian Claude chạy một request TDQ, bằng cách chỉ
  nạp và chỉ chạy đúng thứ request đó cần. Không mất rào an toàn nào đang có giá trị.
  Đo bằng: byte skill nạp mỗi vòng, số file output mỗi request, số test, thời gian suite.
- **Nguyên tắc xuyên suốt (theo trả lời 6 của user):** minimal. Không viết nếu không
  thật sự cần. Không test nếu xác suất lỗi thấp. QC là kiểm output có đúng yêu cầu
  không, không phải chạy cho nhiều hạng mục.

**Trong phạm vi** — 8 đầu ra, chi tiết ở §2:

- D1 — tầng `nhỏ` và luật tự nhận định cỡ request.
- D2 — QC bám Definition of Done thay cho checklist cố định 3 hạng mục.
- D3 — xoá hẳn nhánh external (kèm deep search, xem giả định G1).
- D4 — xoá hẳn `portable/`.
- D5 — gộp `requests` + `knowledge` + `questions` thành `brief/<slug>.md`.
- D6 — rút gọn `tdq-conventions/SKILL.md` và các SKILL.md nặng.
- D7 — sửa `doc_lint`: phạm vi áp luật, và bug cửa thoát `allow` với R5.
- D8 — dọn bộ test: xoá test của nhánh bị bỏ, xoá test chỉ assert chuỗi .md, làm hermetic.

**NGOÀI phạm vi:**

- Lõi không đụng: hook injection (500 ký tự SessionStart, 200 ký tự mỗi prompt), cơ chế
  ghi `state.json` (chỉ bỏ các khoá của external), gate duyệt spec/plan,
  `phases.md` tự sinh từ `PHASE_TABLE`. Đã đo là gọn và đúng.
- `claude_export.py`, `token_audit.py`, `plugin_tiers.py`, `skill_inventory.py`: giữ
  nguyên code. User không nêu tên chúng ở câu 2. Chỉ gỡ khỏi đường nạp mặc định của skill.
- Không viết lại workflow từ đầu.

**Giả định đã nêu rõ — user phủ quyết được khi duyệt spec:**

- **G1.** Deep search bị xoá theo external. Lý do đo được: `scripts/search_task.py`
  gọi trực tiếp `agy` CLI và `scripts/external_models.py`. Xoá external là mất engine
  của nó. Giữ lại thì phải viết engine mới, trái nguyên tắc minimal.
- **G2.** `plugin_tiers.py` giữ nguyên, dù `CLAUDE.md` §8 ghi từ 2026-08-06 mọi plugin
  đã bật sẵn và `plugin-tiers.json` để rỗng. User chưa nêu tên nó. Muốn xoá thì nói khi duyệt.
- **G3.** "Tạm thời" xoá external nghĩa là xoá khỏi bản ship, không xoá khỏi lịch sử git.
  Muốn khôi phục thì `git revert` commit tương ứng.

## 1b. Lộ trình

Chép từ `knowledge/2026-08-08-giam-over-engineer-workflow.md` mục "Lộ trình".
User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Phân tích | CÓ | đã xong, số liệu đo trực tiếp trên repo tại 0.9.0 |
| Research web | BỎ | việc thuần nội bộ, không có ẩn số bên ngoài |
| Deep search | BỎ | không đạt dấu hiệu nào của `deep-search.md` |
| Interview | CÓ | đã xong 1 vòng 5 câu, user đã trả lời đủ |
| Spec | CÓ | khung bất biến |
| Plan | CÓ | khung bất biến |
| Implement | CÓ | khung bất biến |
| Chia subagent | CHỜ | user chốt mode lúc duyệt plan |
| QC độc lập bằng agent `tdq-qc-tester` | CÓ | việc này sửa chính bộ kiểm, cần một lượt chạy không do người sửa tự chấm |
| Review sâu bằng `tdq-reviewer` | BỎ | thêm một lớp kiểm cho việc bớt lớp kiểm là lặp lại đúng lỗi đang sửa |
| Report | CÓ | khung bất biến, và là nơi ghi số đo trước/sau |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| D1 | Tầng `nhỏ` + dòng tự nhận định cỡ request | `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/lane-decision.md` | Có mục "Tầng nhỏ" với 4 điều kiện vào và luật thoát. QC phân loại lại 5 request cũ trong `docs/tdq/requests/`, ghi kết quả vào `qc/<slug>.md` |
| D2 | QC bám DoD | `skills/tdq-build/references/qc.md`, `skills/tdq-intake/references/quick-lane.md`, `PHASE_TABLE` trong `scripts/tdq_state.py` | Không còn chuỗi "3 hạng mục" trong `skills/`. `test_quick_qc.py` xanh sau khi sửa theo luật mới |
| D3 | Xoá nhánh external + deep search | xoá 6 file `scripts/`, 4 file `agents/`, 3 file `skills/**/references/`; sửa `tdq_state.py`, 3 file `hooks/scripts/`, 9 file skill | `grep -ril external skills hooks agents scripts` không ra kết quả nào ngoài `docs/`. `VALID_MODES == ("main", "subagent")` |
| D4 | Xoá `portable/` | xoá 19 file; chuyển `portable/claude-md/CLAUDE.md` thành `docs/claude-md-mau.md` | Thư mục `portable/` không còn. `docs/claude-md-mau.md` tồn tại và đã cập nhật theo D1/D2/D5 |
| D5 | Gộp output thành `brief/` | `docs/tdq/brief/<slug>.md`; sửa `PHASE_TABLE`, `tdq-intake/SKILL.md`, `analyze-full.md`, `tdq-conventions/SKILL.md` §5 | Chạy thử một request giả trong `TDQ_PROJECT_DIR` tạm: sinh đúng 1 file brief thay cho 3 file |
| D6 | Rút gọn skill nặng | `skills/tdq-conventions/SKILL.md` và reference mới `references/context-budget.md` | `tdq-conventions/SKILL.md` không còn mục 10 dạng liệt kê dài. Tổng byte skill nạp mỗi vòng full đo lại và ghi vào report |
| D7 | Sửa `doc_lint` | `scripts/doc_lint.py` hàm `lint_file` và `rule_r5` | File bất kỳ trong `docs/tdq/` chỉ chịu R8. Test red→green: đặt `<!-- doc-lint: allow R5 -->` ngay trên đoạn dài thì R5 im |
| D8 | Dọn bộ test | `tests/` | `python3 -m unittest discover -s tests -t tests -q` xanh. Chạy được với `HOME=/nonexistent`. Số test và giây ghi vào report |

## 3. Cách tiếp cận & lý do

**Chọn: cắt bề mặt, giữ lõi.** Số đo ở knowledge cho thấy lõi (2.441 dòng) đã gọn và
đúng, còn nửa tuỳ chọn chiếm 63% mã script và 42% test. Cắt đúng chỗ dày thì được nhiều
mà rủi ro thấp.

**Chọn: right-sizing bằng luật viết trong skill, không bằng script.** Viết thêm một
script chấm điểm request là lặp lại đúng lỗi đang sửa. Luật 4 dòng trong `tdq-intake`
đủ để phân tầng, và người đọc luật là model chứ không phải máy.

**Chi tiết D1 — tầng `nhỏ`.** Vào tầng này khi cả 4 điều kiện đúng:

1. Không đổi hành vi sản phẩm, hoặc chỉ đổi đúng một chỗ hiển nhiên (typo, hằng số,
   chuỗi hiển thị, số phiên bản).
2. Không thêm hay xoá file mã nguồn.
3. Không đụng hook, state, gate duyệt.
4. Xong trong một turn, không có chỗ nào cần user chốt.

Ở tầng `nhỏ`: trả lời hoặc sửa luôn. Không mở request, không `init` state, không plan,
không QC. Có đổi repo thì vẫn chạy `tdq_finish.py --log`. Vi phạm bất kỳ điều kiện nào
giữa chừng thì dừng, mở request bình thường, nói rõ vì sao thoát tầng.

**Chi tiết D1 — dòng tự nhận định.** Mọi request mới in đúng một dòng trước khi hỏi lane:

```
Cỡ: <nhỏ|quick|full> · Cần: <research | interview | subagent | QC độc lập | skill ngoài | không>
```

Cột `Cần` chỉ liệt kê thứ có thể bỏ. Thứ luôn chạy thì không liệt kê, để dòng này ngắn.

**Chi tiết D2 — QC mới.** QC không còn danh sách hạng mục cố định. Số hạng mục QC bằng
số dòng DoD của chính plan đó, mỗi dòng DoD một phép kiểm chạy bằng lệnh. Bỏ luật "chạy
lại đủ 3 hạng mục mỗi vòng fix": vòng fix chỉ chạy lại hạng mục đã FAIL cộng hạng mục
mà bản fix có thể làm hỏng. Bỏ luật "vòng fix bắt buộc kể cả khi user tắt QC": user tắt
QC thì không có FAIL để mà fix, luật cũ tự mâu thuẫn. Giữ trần 3 vòng.

**Đã loại:**

- Viết lại workflow từ đầu — lõi đã đo là tốt, viết lại vứt luôn phần đang đúng.
- Chỉ cắt test, giữ nguyên skill — không giảm token runtime, test không nằm trong context.
- Chỉ cắt skill, giữ nguyên test — 72 test assert chuỗi .md sẽ chặn đúng việc rút gọn skill.
- Sinh `portable/` tự động từ `skills/` — user chọn bỏ hẳn, rẻ hơn nhiều.
- Đặt ngưỡng số làm cổng PASS — user chọn 1B, đo để báo cáo chứ không để chặn.

## 3b. Năng lực & công cụ

Chép từ `knowledge/2026-08-08-giam-over-engineer-workflow.md`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-conventions, tdq-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy, đồng thời là ĐỐI TƯỢNG bị sửa |
| mem0-memory | user | DÙNG | chốt xong ghi 1 fact về quyết định kiến trúc "tầng nhỏ + QC bám DoD + bỏ external" |
| superpowers:test-driven-development | plugin:superpowers | DÙNG | D7 và D2 làm red→green |
| graphify | user | KHÔNG | spec §3 đã chọn cách khác tốt hơn: số liệu lấy trực tiếp bằng `wc`/`grep`/chạy thật |
| lumen | plugin:lumen | KHÔNG | spec §3 đã chọn cách khác tốt hơn: repo nhỏ, đã có bản đồ file đầy đủ |
| skill-creator, plugin-dev:skill-development, plugin-dev:hook-development | plugin | KHÔNG | khác lĩnh vực: việc này CẮT bớt skill/hook sẵn có, không tạo mới |
| figma-*, canva-*, adobe-*, hyperframes-*, dataviz, frontend-design | plugin | KHÔNG | khác lĩnh vực |
| cloudflare-*, mongodb-*, postman-*, astronomer-*, base44-*, qt-*, huggingface-*, datarobot-*, unreal-*, unity | plugin | KHÔNG | khác lĩnh vực |
| tavily-*, firecrawl-* | plugin | KHÔNG | khác lĩnh vực: việc thuần nội bộ, không có ẩn số bên ngoài |
| chrome-devtools-*, playwright, desktop-commander, computer-use | plugin | KHÔNG | khác lĩnh vực |
| sonarqube-*, code-review, security-review, code-simplifier | plugin | KHÔNG | spec §3 đã chọn cách khác tốt hơn: QC của chính workflow đã phủ |

## 4. Yêu cầu bắt buộc

- Không có service mới nào được viết, nên không phát sinh log service mới. Các script bị
  sửa giữ nguyên cách log hiện có: cảnh báo ra stderr, exit code có nghĩa,
  `tdq_finish.py` ghi working log có timestamp.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- D7 và D2 có unit test riêng, chạy bằng một lệnh `python3 -m unittest discover -s tests -t tests -q`.
- D1, D3, D4, D5, D6 là thay đổi tài liệu và xoá file. Theo nguyên tắc minimal của user,
  KHÔNG viết test mới cho chúng — kiểm bằng lệnh `grep`/`ls` ghi ở §6.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Xoá external làm hỏng đường chạy mà user còn cần | Mất tính năng giao việc cho codex/agy | G3: xoá bằng commit riêng, `git revert` là khôi phục được. Report ghi rõ commit đó |
| Tầng `nhỏ` bị lạm dụng, việc lớn lọt qua không có gate | Sửa sai mà không ai duyệt | 4 điều kiện vào đều là điều kiện chặn, và có luật thoát bắt buộc khi vi phạm giữa chừng |
| Cắt luật ở `tdq-conventions` làm mất rào an toàn | Mất kiểm soát state hoặc working log | §6 Q9 là danh sách 6 rào phải còn, kiểm từng cái bằng lệnh |
| Xoá test làm lọt lỗi thật | Hồi quy im lặng | Chỉ xoá 2 nhóm: test của mã đã xoá, và test chỉ so chuỗi trong .md. Test hành vi giữ nguyên |
| `docs/tdq/` cũ vẫn còn 3 file/request kiểu cũ sau D5 | Lẫn lộn khuôn cũ và mới | Không migrate file cũ. Chỉ đổi khuôn từ request kế tiếp. Ghi rõ trong report |
| Sửa `PHASE_TABLE` làm lệch `phases.md` | Tài liệu sai lệnh | `phases.md` tự sinh; `test_phase_table.py` giữ nguyên và phải xanh |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Tầng `nhỏ` có thật và dùng được | Đọc `skills/tdq-intake/SKILL.md`; phân loại lại 5 file trong `docs/tdq/requests/` | Có đủ 4 điều kiện vào + luật thoát; 5 request được gán cỡ kèm lý do, ghi vào `qc/<slug>.md` |
| Q2 | QC bám DoD | `grep -rn "3 hạng mục" skills/` | Không có kết quả |
| Q3 | External sạch | `grep -ril external skills hooks agents scripts tests` | Không có kết quả |
| Q4 | `portable/` đã xoá | `ls portable` và `ls docs/claude-md-mau.md` | `portable` không tồn tại; `docs/claude-md-mau.md` tồn tại |
| Q5 | Gộp brief chạy được | Chạy một request giả với `TDQ_PROJECT_DIR` là thư mục tạm | Sinh `brief/<slug>.md`; không sinh `requests/`, `knowledge/`, `questions/` |
| Q6 | `doc_lint` đúng phạm vi | `python3 scripts/doc_lint.py docs/tdq/brief/<slug>.md` với một đoạn 60 từ | exit 0 |
| Q7 | Cửa thoát `allow R5` hoạt động | Test mới trong `tests/test_doc_lint.py`: đoạn dài có `<!-- doc-lint: allow R5 -->` ngay trên | Test đỏ trước khi sửa `rule_r5`, xanh sau |
| Q8 | Suite xanh và hermetic | `python3 -m unittest discover -s tests -t tests -q` và `HOME=/nonexistent python3 -m unittest discover -s tests -t tests -q` | Cả hai exit 0 |
| Q9 | 6 rào an toàn còn nguyên | Chạy từng hook với state giả trong thư mục tạm | `[TDQ:NEXT]` vẫn in ở SessionStart và mỗi prompt; Stop hook vẫn chặn khi repo đổi mà working log chưa append; `edit_gate` vẫn chặn sửa tay `state.json`; `bash_gate` vẫn chặn; `approve spec` và `approve plan` vẫn cần `--by`; `init` vẫn xoá state cũ và in cảnh báo |
| Q10 | Số đo trước/sau | Đo lại đúng cách đã đo ở knowledge: `wc -c` byte skill nạp, `wc -l`, đếm test, đo giây suite | Cả 4 số có mặt trong `reports/<slug>.md`, mỗi số kèm giá trị trước và sau. Không có ngưỡng chặn |

**DoD:**

- 8 đầu ra D1–D8 đều có, mỗi cái đạt điều kiện PASS ở bảng trên.
- Q1–Q10 đều PASS, bằng chứng ghi trong `docs/tdq/qc/<slug>.md`.
- `tdq-qc-tester` chạy một lượt độc lập và trả PASS.
- Report ghi đủ: số đo trước/sau, commit xoá external, danh sách test đã xoá kèm lý do,
  và các file `docs/tdq/` kiểu cũ không được migrate.

## 7. Câu hỏi còn mở

Không còn. Ba chỗ suy luận đã chuyển thành giả định G1, G2, G3 ở §1 để user phủ quyết.
