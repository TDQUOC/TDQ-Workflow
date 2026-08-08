# Knowledge — 2026-08-08-giam-over-engineer-workflow

Ngày: 2026-08-08 · Request: ../requests/2026-08-08-giam-over-engineer-workflow.md · Lane: full

## Năng lực dùng được

Phân vân → DÙNG. Không xoá bảng này kể cả khi mọi dòng là KHÔNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-conventions, tdq-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy, đồng thời là ĐỐI TƯỢNG bị sửa |
| mem0-memory | user | DÙNG | chốt xong ghi 1 fact về quyết định kiến trúc "lazy-load reference + trần test" |
| superpowers:test-driven-development | plugin:superpowers | DÙNG | mọi task sửa code lõi làm red→green |
| graphify | user | KHÔNG | spec §3 đã chọn cách khác tốt hơn: số liệu lấy trực tiếp bằng `wc`/`grep`/chạy thật, đã đo xong ở 2 turn phân tích |
| lumen | plugin:lumen | KHÔNG | spec §3 đã chọn cách khác tốt hơn: repo nhỏ, đã có bản đồ file đầy đủ |
| skill-creator, plugin-dev:skill-development, plugin-dev:hook-development | plugin | KHÔNG | khác lĩnh vực: việc này CẮT bớt skill/hook sẵn có, không tạo mới |
| figma-*, canva-*, adobe-*, hyperframes-*, dataviz, frontend-design | plugin | KHÔNG | khác lĩnh vực |
| cloudflare-*, mongodb-*, postman-*, astronomer-*, base44-*, qt-*, huggingface-*, datarobot-*, unreal-*, unity | plugin | KHÔNG | khác lĩnh vực |
| tavily-*, firecrawl-* | plugin | KHÔNG | khác lĩnh vực: việc thuần nội bộ, không có ẩn số bên ngoài |
| chrome-devtools-*, playwright, desktop-commander, computer-use | plugin | KHÔNG | khác lĩnh vực |
| sonarqube-*, code-review, security-review, code-simplifier | plugin | KHÔNG | spec §3 đã chọn cách khác tốt hơn: QC của chính workflow đã phủ, thêm lớp review nữa là lặp lại đúng lỗi đang sửa |

## Đã đọc

Đo trực tiếp trên repo tại 0.9.0, không suy đoán.

| Vùng | Số liệu đo được |
|---|---|
| Bề mặt ship | 74 file / 7.881 dòng: scripts 4.685 · skills 1.755 · portable 1.251 · hooks 801 · agents 189 |
| Lõi chạy mọi turn | `tdq_state.py` 1.110 + `tdq_finish.py` 209 + `doc_lint.py` 376 + 5 hook 746 = 2.441 dòng |
| Nửa tuỳ chọn | `external_task` 772 + `search_task` 652 + `claude_export` 617 + `token_audit` 312 + `plugin_tiers` 191 + `external_models` 169 + `skill_inventory` 168 = 2.881 dòng (63% script) |
| Context 1 vòng full | 48.091 byte ≈ 12.022 token, chỉ tính file skill được nạp |
| File nặng nhất | `tdq-conventions/SKILL.md` 7.345 byte, nạp ở MỌI phase |
| Mật độ luật | 168 mệnh lệnh tuyệt đối trong `skills/`; riêng conventions 44 luật / 120 dòng |
| Test | 618 test / 55 giây; hook 156 test cho 746 dòng; 72 test chỉ assert chuỗi .md; 257 test (42%) cho nửa tuỳ chọn |
| Output 1 request | 7 file / 417 dòng / 37,6 KB để giao 617 dòng / 26,8 KB code |

## Quyết định đã chốt

1. **Lõi không đụng.** Hook injection (500 ký tự SessionStart, 200 ký tự mỗi prompt),
   `state.json` 949 byte, gate duyệt spec/plan, `phases.md` tự sinh từ `PHASE_TABLE`:
   đã đo là gọn và đúng. Giữ nguyên.
2. **Trục cắt là nửa tuỳ chọn và mật độ luật**, không phải lõi.
3. **`doc_lint` áp sai phạm vi — đây là lỗi, không phải tuỳ chọn.**
   `lint_file` (dòng 333) chỉ miễn R1–R7 cho thư mục `spec/`. Bảy thư mục output còn
   lại (`requests`, `knowledge`, `questions`, `research`, `plan`, `qc`, `reports`) vẫn
   chịu đủ luật văn phong dành cho doc hướng dẫn. Các file này chứa trích nguyên văn
   lời user và output test thật, là thứ cấm sửa.
4. **Cửa thoát `allow` hỏng với R5 — lỗi thứ hai.** `rule_r5` gộp các dòng liền nhau
   thành một buffer, nuốt luôn dòng comment, nên `state["start"]` trỏ vào comment và
   `allowed()` soi nhầm dòng phía trên. Kết quả đo được: 42 từ thành 47 từ.
5. **Mâu thuẫn `skills/` vs `portable/` là lỗi đang ship.** Luật task `(mcp)`:
   `skills` nói hard-block không override, `portable` nói user đòi thì làm theo user.
   `test_portable_sync.py` chỉ so bước đánh số của 4 SKILL.md nên không phủ `references/`.
6. **Suite đang ĐỎ vì đọc ra ngoài repo.** `test_claude_md_core.py` so file repo với
   `~/.claude/CLAUDE.md`. Suite phải hermetic.

Sau vòng interview (xem `questions/<slug>.md`):

7. **Không có ngưỡng số làm cổng.** Đo trước/sau, ghi vào report. Con số là bằng chứng,
   không phải điều kiện PASS.
8. **Xoá hẳn nhánh external**, gồm cả deep search vì nó chạy trên cùng engine `agy`.
9. **Xoá hẳn `portable/`.** Hết mâu thuẫn hai bản, khỏi cần test đồng bộ.
10. **Gộp `requests` + `knowledge` + `questions` thành `brief/<slug>.md`.**
11. **Được xoá test.** Xoá test của nhánh bị bỏ và test chỉ assert chuỗi trong .md.
12. **Thêm tầng `nhỏ` trước `quick`.** Việc hiển nhiên không mở request, không state.
    Đây là câu trả lời cho "task rất nhỏ bị làm over".
13. **QC đổi định nghĩa.** QC kiểm đúng các dòng DoD của chính plan đó. Bỏ checklist
    cố định 3 hạng mục và bỏ luật chạy lại đủ 3 hạng mục mỗi vòng fix.

## Phương án đã loại

| Phương án | Lý do loại |
|---|---|
| Viết lại workflow từ đầu | Lõi đã đo là tốt. Viết lại vứt luôn phần đang đúng. |
| Chỉ cắt test, giữ nguyên skill | Không giảm token runtime. Test không nằm trong context lúc chạy. |
| Chỉ cắt skill, giữ nguyên test | Test .md giòn sẽ chặn đúng việc rút gọn skill, vì chúng assert chuỗi trong file bị sửa. |
| Gọi agent review độc lập cho spec này | Lặp lại đúng lỗi đang sửa: thêm một lớp kiểm cho việc bớt lớp kiểm. |

## Nguồn

Đo trực tiếp trên repo, không dùng nguồn ngoài. Việc thuần nội bộ nên bỏ bước research
web theo `analyze-full.md` bước 3. Lệnh đã chạy để lấy số:

- `wc -l`, `wc -c`, `grep -c 'def test_'` — đếm dòng, byte, số test.
- `python3 -m unittest discover -q` — 618 test, 55 giây, 1 fail.
- `python3 scripts/doc_lint.py` — kiểm luật văn phong.
- Chạy trực tiếp `session_start.py` và `prompt_context.py` với state giả trong thư mục tạm.

## Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Phân tích | CÓ | đang làm, số liệu đã đo xong |
| Research web | BỎ | việc thuần nội bộ, không có ẩn số bên ngoài |
| Deep search | BỎ | không đạt dấu hiệu nào của `deep-search.md` |
| Interview | CÓ | còn 5 câu làm đổi kết quả, xem `questions/<slug>.md` |
| Spec | CÓ | khung bất biến |
| Plan | CÓ | khung bất biến |
| Implement | CÓ | khung bất biến |
| Chia subagent | CHỜ | phụ thuộc câu hỏi 5 về mode, user chốt lúc duyệt plan |
| QC bằng agent `tdq-qc-tester` độc lập | CÓ | task này sửa chính bộ kiểm, nên cần một lượt chạy không do người sửa tự chấm |
| Review sâu bằng `tdq-reviewer` | BỎ | đã loại ở bảng phương án, lý do ghi tại đó |
| Report | CÓ | khung bất biến |

## Kiểm cổng

1. **Phạm vi cuối đã rõ chưa?** RỒI. User đã trả lời đủ 5 câu. Hai chỗ còn suy luận
   được ghi thành giả định nêu rõ trong spec, user phủ quyết được lúc duyệt.
2. **Cần model / download / cài đặt gì không?** KHÔNG. Toàn bộ là Python 3 chuẩn và
   `unittest` đã có sẵn trong repo.
3. **Phạm vi QC/test/validate đã có chưa?** CÓ khung, gồm ba điều kiện:
   - Suite phải xanh và hermetic.
   - Số token nạp mỗi vòng phải đo lại bằng đúng cách đã đo ở đây, ghi vào report.
   - Mọi luật bị xoá phải chứng minh là không mất rào an toàn.

   Không có ngưỡng số làm cổng — theo trả lời 1B của user.
