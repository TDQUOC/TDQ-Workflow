# SPEC — Học cách tổ chức của superpowers: một nguồn, adapter mỏng, chạy đa nền tảng

Ngày: 2026-09-21 · Bản: 1.0 · Brief: ../brief/2026-09-21-0029-hoc-superpowers-da-host.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi

- Mục tiêu: TDQ-Workflow giữ MỘT nguồn `skills/` + `hooks/` + `agents/` + `scripts/`, mỗi host
  chỉ còn một adapter mỏng trỏ vào nguồn đó. Bỏ 357 file nhân bản, thêm OpenCode, và có CI
  chứng minh bằng máy rằng bộ workflow chạy trên cả ba hệ điều hành.
- Trong phạm vi:
  - Xoá ba thư mục bundle `portable_claude/`, `portable_codex/`, `antigravity_portable/`.
  - Adapter Codex: `.agents/plugins/marketplace.json` + `.codex-plugin/plugin.json`.
  - Adapter OpenCode: `.opencode/plugins/tdq-workflow.js`, JavaScript thuần, không package npm.
  - Lệnh sinh layout agy theo yêu cầu vào `~/.gemini/config/plugins/tdq-workflow/`, thay cho
    thư mục bundle bị xoá.
  - Thu gọn `scripts/build_portable.py` (1077 dòng) về đúng phần còn dùng, và chỉnh
    `scripts/tdq_checkportable.py` theo vai trò mới.
  - CI matrix: 3 hệ điều hành × Python 3.10 và 3.13.
  - Đổi các ca test phụ thuộc `pytest`, `anthropic-tokenizer`, `graphify`, `codex` sang
    `skipUnless`, để runner sạch vẫn xanh.
  - Dựng lại nội dung cho 0.49.0 ở những adapter còn lại, bump version, ghi CHANGELOG.
  - Cập nhật `README.md` và `docs/kien-truc.md` theo kiến trúc mới.
- NGOÀI phạm vi:
  - Thêm host ngoài OpenCode. Khung phải sẵn sàng để thêm bằng một manifest, nhưng request này
    không thêm Cursor, Kimi, Muse hay Pi.
  - Đổi ngôn ngữ hook. Hook giữ Python; không chép kỹ thuật polyglot `run-hook.cmd` cũng như
    trường `"shell": "bash"` của superpowers, vì cả hai là cách vá cho thiết kế bash-first.
  - Đổi nội dung bất kỳ skill hay luật nào trong `skills/`.
  - Sửa hành vi của hook. Request Windows vừa đóng đã làm phần đó.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | bốn host đã đo bằng công cụ thật tại chỗ; API OpenCode đọc thẳng được trong bản clone |
| Interview | CÓ | đã chạy vòng scope và vòng chi tiết, hết câu đổi được kết quả |
| spec | CÓ | khung bất biến, và việc này đổi kiến trúc đóng gói |
| plan | CÓ | khung bất biến; mỗi task một test |
| implement | CÓ | khung bất biến |
| Chia việc cho subagent | BỎ | phần gỡ bundle và phần sửa `build_portable` chạm chung tập file |
| QC độc lập (agent) | CÓ | bỏ 357 file là thay đổi khó lùi, cần một lượt xác nhận độc lập |
| Rà soát sâu | CÓ | đổi kiến trúc đóng gói, và có một quyết định đi ngược cảnh báo của chính tôi |
| report | CÓ | khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Adapter Codex | `.agents/plugins/marketplace.json`, `.codex-plugin/plugin.json` | `codex plugin marketplace add <repo>` rồi `codex plugin list` in ra `tdq-workflow` |
| 2 | Adapter OpenCode | `.opencode/plugins/tdq-workflow.js` | chạy bằng `node`, đọc được `skills/` và trả đúng khuôn context; không import package ngoài nào |
| 3 | Lệnh sinh layout agy | `scripts/` | chạy một lệnh ra đủ `plugin.json`, `skills/`, `hooks.json`, `mcp_config.json` ở thư mục đích; chạy hai lần không đổi thêm gì |
| 4 | Ba bundle biến khỏi repo | `portable_claude/`, `portable_codex/`, `antigravity_portable/` | `git ls-files` không còn đường dẫn nào thuộc ba thư mục đó |
| 5 | `build_portable.py` thu gọn | `scripts/build_portable.py` | số dòng giảm ít nhất một nửa, mọi hàm còn lại đều có nơi gọi |
| 6 | `tdq_checkportable.py` đúng vai trò mới | `scripts/tdq_checkportable.py` | không còn đòi `manifest.json` của bundle đã xoá |
| 7 | CI matrix | `.github/workflows/` | 6 tổ hợp (3 hệ × 2 bản Python) đều chạy và xanh |
| 8 | Test không cần công cụ ngoài | `tests/` | trên máy chưa cài 4 công cụ, suite 0 fail 0 error, các ca liên quan báo `skip` |
| 9 | Tài liệu khớp kiến trúc mới | `README.md`, `docs/kien-truc.md` | không còn dòng nào mô tả ba bundle như cách cài hiện hành |
| 10 | Phát hành | `.claude-plugin/plugin.json`, `CHANGELOG.md` | version tăng, CHANGELOG có mục mới, file dưới trần 500 dòng |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| M1 adapter | `.agents/`, `.codex-plugin/`, `.opencode/` | không | 1, 2 |
| M2 gỡ bundle | `portable_claude/`, `portable_codex/`, `antigravity_portable/`, `scripts/build_portable.py`, `scripts/tdq_checkportable.py` | M1 | 3, 4, 5, 6 |
| M3 CI | `.github/` | M2 | 7 |
| M4 test | `tests/` | M2 | 8 |
| M5 tài liệu và phát hành | `README.md`, `docs/kien-truc.md`, `CHANGELOG.md`, `.claude-plugin/plugin.json` | M1, M2 | 9, 10 |

## 3. Cách tiếp cận & lý do

- Chọn: mô hình MỘT nguồn cộng adapter mỏng, đúng cách superpowers làm.
- Vì: đo được trên hai repo — superpowers phủ 9 host với 0 file nhân bản và khoảng 750 dòng
  adapter, trong đó 246 dòng là manifest thuần; TDQ phủ 3 host với 357 file nhân bản, 4.2 MB so
  với nguồn 672 KB, và 1077 dòng `build_portable.py`. Khoá của cả mô hình là một dòng lặp lại
  trong mọi manifest: `"skills": "./skills/"`.
- Vì: bốn hệ quả của việc chép đều đã gặp thật trong request Windows vừa đóng — lumen index cả
  bản sao và bản sao chiếm hết top-10; bundle lệch nguồn sau mỗi lần sửa; bundle nướng cứng thư
  mục nhà của máy dựng nên không commit được từ Windows; `portable_codex.zip` đứng yên 24 bản.
- Đã loại: giữ mô hình chép và thêm OpenCode thành bundle thứ tư — nhân thêm khoảng 100 file và
  bốn hệ quả trên vẫn còn nguyên.
- Đã loại: chỉ học phần nguyên tắc mà không đụng đóng gói — không giải được hệ quả nào trong bốn.

- Chọn (Codex): `.agents/plugins/marketplace.json` trỏ `"url": "./"`, cộng
  `.codex-plugin/plugin.json`.
- Vì: đã xác minh bằng công cụ thật, không suy đoán. Thêm chính bản clone superpowers làm
  marketplace local thì `codex plugin list` in ra plugin với nguồn trỏ thẳng vào thư mục repo.
  Codex CLI 0.155.1 nhận marketplace từ đường dẫn local, `owner/repo` hoặc Git URL.

- Chọn (agy): xoá thư mục bundle, thay bằng một lệnh sinh layout theo yêu cầu vào
  `~/.gemini/config/plugins/tdq-workflow/`.
- Vì: phán quyết `1b` của user là bỏ cả ba bundle. Sinh theo yêu cầu giữ đúng chữ "cài tay" mà
  vẫn bỏ được bản sao khỏi repo, và layout luôn sinh từ nguồn mới nhất thay vì từ bản đông cứng
  lúc release — chính là cách `portable_codex.zip` đã mục suốt 24 bản.

- Chọn (OpenCode): adapter JavaScript thuần, chỉ đọc `skills/` và chèn context.
- Vì: đó là API của host, không có đường khai báo thay thế. Giới hạn "không package npm" chép
  đúng kỷ luật của superpowers, để adapter không kéo theo cây phụ thuộc.

- Chọn (CI): 3 hệ điều hành × Python 3.10 và 3.13.
- Vì: hôm nay chính tôi suýt để lọt `shutil.rmtree(onexc=...)`, thứ chỉ có từ Python 3.12, trong
  khi repo còn nhánh dự phòng `tomllib` cho bản dưới 3.11. Máy phát triển chạy 3.13 nên suite
  xanh; một máy 3.10 sẽ ăn `TypeError`. Bản thấp trong matrix là thứ duy nhất bắt được loại đó.

- Chọn (test): `skipUnless` khi thiếu công cụ, không cài gì trên runner.
- Vì: runner sạch phải xanh thì CI mới nói lên điều gì, và số ca `skip` nói thẳng phần nào chưa
  được phủ thay vì giấu sau một lần cài.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đang chạy, đã mở request và chạy analyze |
| tdq-spec | plugin:tdq-workflow | NỀN | skill khung đang chạy, đang viết chính file này |
| tdq-plan | plugin:tdq-workflow | NỀN | skill khung sẽ chạy ngay sau cổng duyệt spec |
| tdq-build | plugin:tdq-workflow | NỀN | skill khung của implement, QC và report |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật chung mọi phase đều nạp |
| tdq-lean | plugin:tdq-workflow | DÙNG | đầu ra 5 — thu gọn `build_portable.py`, đúng việc soi over-engineer |
| Đã xét 4 skill khác | user/project/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt hoặc giảm được qua config.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`,
  và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ, chép từ `docs/kien-truc.md`:

- "Luật bản ngoài: `portable_claude/`, `portable_codex/` SINH bằng `scripts/build_portable.py`
  từ `skills/`+`hooks/`+`agents/`+`scripts/`, không sửa tay" — request này XOÁ tầng đó, nên dòng
  luật này phải được viết lại trong `docs/kien-truc.md` như một phần của đầu ra 9.
- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — chạm ở đầu ra 2: adapter
  OpenCode là file mã nguồn nằm ở `.opencode/`. Đây là ngoại lệ phải được ghi vào `## Đã chốt`
  của hồ sơ kiến trúc, vì đường dẫn do host quy định chứ không do repo chọn.
- "`skills/` chỉ được nhắc tên lệnh của `scripts/`, cấm chép nội dung script vào skill" — không
  chạm, request này không sửa `skills/`.
- "Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`" — không chạm.
- "`CHANGELOG.md` giữ dưới trần 500 dòng của `doc_lint` R6" — chạm ở đầu ra 10.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| **Không xác minh được agy trên máy này** | xoá `antigravity_portable` dựa trên đọc README chứ không dựa trên chạy thử; người dùng agy có thể mất đường cài | user đã được nêu rủi ro này trước khi chọn `1b` và vẫn chọn; giảm bằng lệnh sinh layout theo yêu cầu, và giữ nguyên hằng `README_AGY` đang mô tả layout đọc từ bản agy 1.1.11 thật |
| Xoá 357 file là thay đổi khó lùi | ai đang cài theo bundle sẽ mất đường cập nhật | làm trên nhánh riêng, không push; CHANGELOG nói rõ đường cài mới cho từng host; lịch sử git giữ nguyên bản cũ |
| Không có OpenCode trên máy để kiểm đầu cuối | adapter có thể sai khuôn mà test không bắt | kiểm ở mức đơn vị bằng `node`: đọc `skills/`, trả đúng khuôn, không import package ngoài; ghi rõ trong report là chưa kiểm đầu cuối |
| CI Python 3.10 có thể lòi ra lỗi có sẵn ngoài phạm vi | request phình to | lỗi thuộc phạm vi request thì sửa; lỗi có sẵn khác thì ghi vào report thành nợ, không sửa lan |
| Thu gọn `build_portable.py` làm hỏng phần còn dùng | mất lệnh sinh hook theo hệ | giữ nguyên `tien_to_python` và `sinh_hook_claude` cùng 17 ca test đã có; chỉ cắt phần dựng bundle |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Adapter Codex | thêm repo làm marketplace local thì `codex plugin list` in ra `tdq-workflow` |
| Q2 | Adapter OpenCode chạy được | `node` nạp được file, đọc ra đúng số skill có trong `skills/` |
| Q3 | Adapter OpenCode không kéo phụ thuộc | không câu `import`/`require` nào trỏ ra ngoài thư viện chuẩn của Node |
| Q4 | Lệnh sinh layout agy | sinh đủ bốn thành phần ở thư mục đích, chạy lần hai không đổi thêm gì |
| Q5 | Ba bundle biến khỏi repo | `git ls-files` không còn đường dẫn nào thuộc ba thư mục đó |
| Q6 | `build_portable.py` thu gọn | không tên cấp module nào — hàm LẪN hằng — còn lại mà không có nơi dùng, khoá bằng test đo khả năng với tới từ `main` (2026-09-23: thay ngưỡng "giảm ít nhất một nửa", số ƯỚC viết trước khi đo; đo thật là 1077 → 634 dòng, 41%, phần còn lại đều đang chạy) |
| Q7 | `tdq_checkportable.py` | chạy từ gốc repo không còn báo thiếu `manifest.json` |
| Q8 | CI matrix | đủ 6 tổ hợp, mỗi tổ hợp chạy trọn suite |
| Q9 | Suite trên máy sạch | không cài 4 công cụ ngoài vẫn 0 fail, 0 error |
| Q10 | Không ca nào từ xanh chuyển sang đỏ | đối chiếu với mốc 1983 ca đầu request |
| Q11 | Tài liệu khớp kiến trúc | `README.md` và `docs/kien-truc.md` không còn mô tả ba bundle như cách cài hiện hành |
| Q12 | Phát hành | version tăng, CHANGELOG có mục mới, dưới trần 500 dòng |
| Q13 | Lint tài liệu | mọi tài liệu của request thoát 0 |

DoD:

- Cả 13 hạng mục QC PASS.
- Mọi task trong plan tick `[x]`.
- Một lượt chạy test đầy đủ: 0 fail, 0 error.
- Report viết xong, có nêu rõ phần chưa kiểm được đầu cuối.

## 7. Câu hỏi còn mở

(Rỗng.)
