# PLAN — Hoàn thiện product document trên Excalidraw

Ngày: 2026-08-12 · Spec: ../spec/2026-08-12-hoan-thien-doc-excalidraw.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — mọi task ghi vào CÙNG một canvas Excalidraw qua MCP, thứ tự tạo quyết định z-order; sub-agent trong git worktree không thấy canvas và cũng không có MCP tool này.
Trạng thái plan: ĐÃ DUYỆT (2026-08-12 12:21, mode main)

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. **Cấm `update_element` cho `x`/`y`/`width`/`height`/`text`** (spec §3): đã tái hiện 2
   lần lỗi silent-fail. Dùng `delete_element` + `batch_create_elements`, xác minh bằng
   `get_element`.
8. Chữ tiếng Việt: bề rộng ≥ `số ký tự dòng dài nhất × fontSize × 0.75`, label ≤ 70% bề
   rộng ô, xuống dòng bằng `\n` thủ công khi > 30 ký tự.

## Lưới toạ độ đã chốt

Một cột dọc, mọi **khung chương** (`ch<N>-frame`) rộng 2640px tại `x = 40`, chừa ≥120px
giữa hai chương. Khối cũ hẹp hơn 2640px thì **giữ nguyên bề rộng nội dung và canh giữa**
trong khung — không phóng to nội dung (phóng to sẽ vỡ tỉ lệ chữ/hộp đã cân trước đó).

Chiều cao chương 2/5/7/9/10 = chiều cao thật của khối cũ (đo ở P1) + 2×20px đệm; các
chương mới là ước lượng, chốt lại sau khi vẽ bằng `--contain`.

| Ch | Tên | y bắt đầu | Cao | Nguồn |
|---|---|---|---|---|
| 0 | Mục lục | 0 | 560 | (tự sinh từ 13 tiêu đề) |
| 1 | Tổng quan sản phẩm | 680 | 620 | README.md, plugin.json |
| 2 | Ưu điểm & lợi ích cho dev | 1420 | 1000 | khối CŨ (nội dung 760×960) |
| 3 | Getting Started | 2540 | 700 | docs/notes/user-level-install.md §1 |
| 4 | State machine + schema | 3360 | 1000 | tdq_state.py PHASE_TABLE, state.json |
| 5 | Flow lane quick/full | 4490 | 1990 | khối CŨ (nội dung 1313×1857, gồm 2 nhãn ở x âm) |
| 6 | Ví dụ thực tế 1 request | 6600 | 800 | docs/tdq/reports/2026-08-11-*.md |
| 7 | Sequence diagram | 7520 | 1600 | khối CŨ (nội dung 2640×1560) |
| 8 | Kiến trúc & cấu trúc thư mục | 9240 | 900 | ls hooks/ scripts/ skills/ |
| 9 | Manifest & Dependency | 10260 | 1520 | khối CŨ (nội dung 760×1480) |
| 10 | Nền tảng & Test/Dev | 11900 | 775 | khối CŨ (nội dung 760×735) |
| 11 | Giới hạn đã biết | 12800 | 760 | reports + user-level-install.md |
| 12 | Troubleshooting / FAQ | 13680 | 860 | user-level-install.md "Lưu ý an toàn" |
| 13 | Roadmap & Changelog | 14660 | 760 | CHANGELOG.md |

## Số liệu gốc đo ở P1 (mốc so sánh khi di chuyển)

Gom nhóm bằng union-find (đệm 30px) trên 214 element của scene backup — id không tin
được vì bound label do frontend sinh mang id ngẫu nhiên, nên **đếm theo vùng**
(`--count-by-region`) chứ không theo prefix:

| Khối cũ | n | Vùng nguồn x0,y0,x1,y1 | Về chương |
|---|---|---|---|
| Ưu điểm & lợi ích | 55 | `1120,-110,1880,850` | 2 |
| Flow làm việc (gồm 2 nhãn mũi tên "còn"/"hết" ở x âm) | 65 | `-220,-215,1080,1635` | 5 |
| Sequence diagram | 60 | `40,1780,2680,3340` | 7 |
| Manifest & Dependency | 19 | `1920,-110,2680,1370` | 9 |
| Nền tảng & Test/Dev | 15 | `1120,900,1880,1635` | 10 |

Tổng 214 — sau P2 tổng số element phải vẫn là 214.

## P1 — Backup + script kiểm (dựng red→green trước khi động vào canvas)

- [x] **T1.1** (n2) Export scene hiện tại làm backup ra `docs/diagrams/_backup-2026-08-12.excalidraw` — Test: `python3 -c "import json;d=json.load(open('docs/diagrams/_backup-2026-08-12.excalidraw'));print(len(d['elements']))"` in ra số > 0
  - Dùng: `excalidraw-skill` (mcp)
  - Để: gọi `export_scene` lấy JSON scene đang có, ghi ra file backup TRƯỚC khi xoá bất
    kỳ element nào. Nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc
    `/Users/truongdinhquoc/.claude/skills/excalidraw-skill/SKILL.md` rồi làm theo.
  - Ra: `docs/diagrams/_backup-2026-08-12.excalidraw`
  - Kiểm: `test -s docs/diagrams/_backup-2026-08-12.excalidraw && echo OK`
  - Không dùng cho: sinh nội dung chữ của chương — nội dung phải trích từ file repo, không do skill vẽ tự nghĩ ra.
- [x] **T1.2** (n5) Viết `scripts/check_canvas_layout.py` — đọc scene JSON, hỗ trợ 6 cờ `--chapters --overlap --contain --order --toc --count-by-prefix`, chỉ dùng stdlib — Test: `python3 scripts/check_canvas_layout.py --help` exit 0
- [x] **T1.3** (n5) Viết `tests/test_check_canvas_layout.py` với scene giả: 1 ca đúng, 1 ca chồng lấn, 1 ca tràn khung, 1 ca sai thứ tự, 1 ca mục lục lệch — Test: `python3 -m pytest tests/test_check_canvas_layout.py -q` PASS
- [x] **T1.4** (n3) Chạy script trên backup để lấy số phần tử theo prefix của 5 khối cũ, ghi vào plan mục `## Số liệu trước khi di chuyển` — Test: `python3 scripts/check_canvas_layout.py docs/diagrams/_backup-2026-08-12.excalidraw --count-by-prefix` in ra bảng prefix

**Xong P1 khi**: backup tồn tại, `pytest tests/test_check_canvas_layout.py` xanh, đã có số phần tử gốc của từng khối cũ.

## P2 — Di chuyển 5 khối cũ về đúng chương

Chạy CẢ 5 task bằng một lệnh: `python3 scripts/canvas_layout_apply.py` (bảng `MOVES`
trong script chép từ bảng lưới ở trên). Dời từng khối một là SAI: khung chương rộng
2640px nên khối vừa dời rơi vào vùng nguồn của khối kế tiếp và bị cuốn theo — đã xảy ra
thật, ch2 mất 36 phần tử vào lệnh dời ch7, phải `import --replace` từ backup để khôi
phục. Script tính mọi phép dời trên CÙNG một ảnh chụp scene rồi mới ghi một lần, và
chặn trước nếu một element bị hai vùng cùng chọn.

Công cụ nền: `scripts/canvas_move_block.py` — đọc `GET /api/elements`, chọn element theo **tâm
nằm trong vùng nguồn**, dịch (dx, dy) canh giữa khung 2640px, đổi id sang `ch<N>-frame` /
`ch<N>-title` / `ch<N>-e<i>` kèm ánh xạ lại `containerId` · `boundElements` ·
`startBinding` · `endBinding`, rồi `DELETE` từng element cũ + `POST /api/elements/batch`.
Chọn theo vùng chứ không theo prefix id vì bound label mang id ngẫu nhiên (luật 7).

- [x] **T2.1** (n5) Chuyển khối về Ch.2 — `python3 scripts/canvas_move_block.py --chapter 2 --region 1120,-110,1880,850 --target-y 1420 --title "2. Ưu điểm & lợi ích cho dev"` — Test: `check_canvas_layout.py http://127.0.0.1:17739/api/elements --count-by-region` cho chương 2 = 55, và `get_element ch2-title` trả đúng chuỗi mới.
- [x] **T2.2** (n5) Chuyển khối về Ch.5 — `python3 scripts/canvas_move_block.py --chapter 5 --region -220,-215,1080,1635 --target-y 4580 --title "5. Flow làm việc — lane quick & full"` — Test: `check_canvas_layout.py http://127.0.0.1:17739/api/elements --count-by-region` cho chương 5 = 65, và `get_element ch5-title` trả đúng chuỗi mới.
- [x] **T2.3** (n8) Chuyển khối về Ch.7 — `python3 scripts/canvas_move_block.py --chapter 7 --region 40,1780,2680,3340 --target-y 7520 --title "7. Sequence diagram — trình tự 1 request"` — Test: `check_canvas_layout.py http://127.0.0.1:17739/api/elements --count-by-region` cho chương 7 = 60, và `get_element ch7-title` trả đúng chuỗi mới. Thêm: còn đủ 19 label và 19 arrow.
- [x] **T2.4** (n5) Chuyển khối về Ch.9 — `python3 scripts/canvas_move_block.py --chapter 9 --region 1920,-110,2680,1370 --target-y 10260 --title "9. Manifest & Dependency"` — Test: `check_canvas_layout.py http://127.0.0.1:17739/api/elements --count-by-region` cho chương 9 = 19, và `get_element ch9-title` trả đúng chuỗi mới.
- [x] **T2.5** (n5) Chuyển khối về Ch.10 — `python3 scripts/canvas_move_block.py --chapter 10 --region 1120,900,1880,1635 --target-y 11900 --title "10. Nền tảng & cách Test/Dev"` — Test: `check_canvas_layout.py http://127.0.0.1:17739/api/elements --count-by-region` cho chương 10 = 15, và `get_element ch10-title` trả đúng chuỗi mới.

**Xong P2 khi**: 5 khối cũ nằm đúng `y` trong bảng lưới, số phần tử không đổi so với P1, tiêu đề đều có tiền tố số chương.

## P3 — Vẽ 4 chương mới phần đầu (overview → concepts)

- [x] **T3.1** (n5) Vẽ Ch.1 Tổng quan sản phẩm (`y = 680`): 4 ô — vấn đề giải quyết, đối tượng dùng, giá trị cốt lõi, vị trí sản phẩm; dữ kiện từ `README.md` + `.claude-plugin/plugin.json` — Test: `--contain` cho chương 1 exit 0; screenshot không cắt chữ
- [x] **T3.2** (n5) Vẽ Ch.3 Getting Started (`y = 2540`): 3 bước cài (`marketplace add` → `plugin install` → kiểm bằng `tdq-status`), nguyên văn lệnh từ `docs/notes/user-level-install.md` §1 — Test: `--contain` exit 0; 3 lệnh trên canvas khớp từng ký tự với file nguồn
- [x] **T3.3** (n8) Vẽ Ch.4 State machine (`y = 3360`): sơ đồ 7 phase `no_state → analyze → spec → plan → implement → qc → report → idle` + nhánh `quick`, mỗi node ghi điều kiện chuyển; đối chiếu `PHASE_TABLE` — Test: số node = 8, khớp `VALID_PHASES` + `no_state`
- [x] **T3.4** (n5) Vẽ bảng schema `state.json` v3 trong Ch.4: 21 field, mỗi field một dòng tên + ý nghĩa — Test: đếm 21 dòng, khớp `python3 -c "import json;print(len(json.load(open('docs/tdq/state.json'))))"`

**Xong P3 khi**: 4 chương mới hiển thị đủ, `--contain` exit 0 cho từng chương.

## P4 — Vẽ 2 chương mới phần giữa (tutorial → architecture)

- [x] **T4.1** (n5) Vẽ Ch.6 Ví dụ thực tế (`y = 6600`): timeline một request có thật `2026-08-11-cai-tdq-project-level` — từ intake đến report, mỗi bước ghi file sinh ra; nguồn `docs/tdq/reports/2026-08-11-cai-tdq-project-level.md` — Test: mọi đường dẫn nêu trên canvas đều `test -e` thấy file thật
- [x] **T4.2** (n5) Vẽ Ch.8 Kiến trúc & cấu trúc thư mục (`y = 9240`): cây thư mục + mũi tên hook→script, đúng 6 hook script / 11 script / 6 skill — Test: đếm trên canvas khớp `ls -1 hooks/scripts/*.py | wc -l`, `ls -1 scripts/*.py | wc -l`, `ls -1d skills/*/ | wc -l`

**Xong P4 khi**: 2 chương hiển thị đủ, mọi đường dẫn trên canvas trỏ tới file có thật.

## P5 — Vẽ 3 chương mới phần đuôi + mục lục

- [x] **T5.1** (n5) Vẽ Ch.11 Giới hạn đã biết (`y = 12800`): ≥5 giới hạn, mỗi cái ghi kèm file nguồn — Test: ≥5 mục, mỗi mục có tên file truy được
- [x] **T5.2** (n5) Vẽ Ch.12 Troubleshooting/FAQ (`y = 13680`): ≥5 cặp hỏi-đáp từ mục "Lưu ý an toàn" của `user-level-install.md` — Test: ≥5 cặp, nội dung khớp file nguồn
- [x] **T5.3** (n5) Vẽ Ch.13 Roadmap & Changelog (`y = 14660`): mốc 0.11.0 / 0.11.1 / 0.11.2 đúng ngày trong `CHANGELOG.md`, không bịa mốc tương lai — Test: 3 mốc + ngày khớp `grep '^## 0\.' CHANGELOG.md | head -3`
- [x] **T5.4** (n5) Vẽ Ch.0 Mục lục (`y = 0`): 14 dòng (Ch.0–Ch.13), mỗi dòng `<số>. <tiêu đề chương>` khớp tiêu đề thật — Test: `--toc` exit 0

**Xong P5 khi**: đủ 14 khối trên canvas (mục lục + 13 chương), `--toc` exit 0.

## P6 — Kiểm toàn cục & export

- [x] **T6.1** (n3) Chạy 5 phép kiểm hình học trên scene sống — Test: `--chapters --overlap --contain --order --toc` đều exit 0
- [x] **T6.2** (n3) Chụp screenshot từng chương, xem từng ảnh tìm chữ bị cắt, sửa ô nào tràn — Test: 14/14 ảnh không có chữ bị cắt
- [x] **T6.3** (n3) Export `docs/diagrams/tdq-workflow-product-doc.excalidraw` — Test: file parse được bằng `json.load`
- [x] **T6.4** (n3) Export `docs/diagrams/tdq-workflow-product-doc.png`; nếu > 20 MB thì giảm scale còn 0.5 và ghi rõ trong report — Test: `ls -la` cho thấy PNG > 100 KB
- [x] **T6.5** (n2) Lưu 1 fact vào mem0 về lỗi `update_element` — Test: `search_memories` trả về fact vừa lưu
  - Dùng: `mem0-memory` (mcp)
  - Để: lưu đúng một fact ngắn "server Excalidraw MCP tại 127.0.0.1:17739: `update_element`
    silent-fail khi đổi geometry/text, phải delete + recreate", project = `TDQWorkflow`.
    Nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc
    `/Users/truongdinhquoc/.claude/skills/mem0-memory/SKILL.md` rồi làm theo.
  - Ra: một memory trong mem0, project `TDQWorkflow`
  - Kiểm: `mcp__mem0__search_memories` với truy vấn "excalidraw update_element" trả ≥ 1 kết quả
  - Không dùng cho: lưu nội dung 13 chương hay dữ kiện repo — những thứ đó đã nằm trong git, không thuộc bộ nhớ dài hạn.

**Xong P6 khi**: Q1–Q8 PASS, hai file trong `docs/diagrams/` tồn tại.

## Px — Log & test bắt buộc

Log: BỎ — việc này không tạo runtime; `scripts/check_canvas_layout.py` là công cụ kiểm QC
chạy một lần, in kết quả kèm số liệu bounding box ra stdout, không phải dịch vụ chạy nền.

- [x] **Tx.1** (n3) Chạy toàn bộ test suite, không có test nào chuyển pass → fail — Test: `python3 -m pytest -q`
- [x] **Tx.2** (n2) Ghi working log `docs/workinglog/2026-08-12.md` cho phase implement — Test: `grep -c '^## ' docs/workinglog/2026-08-12.md` tăng so với trước

## Definition of Done

Trỏ về §6 của spec. Mỗi dòng dưới đây là một hạng mục QC:

- Q1 Đủ 13 chương, số liên tục 1→13 — `python3 scripts/check_canvas_layout.py docs/diagrams/tdq-workflow-product-doc.excalidraw --chapters`
- Q2 Không cặp khung chương nào chồng lấn — `... --overlap`
- Q3 Mọi phần tử nằm trong khung chương của nó — `... --contain`
- Q4 Thứ tự y đúng số chương — `... --order`
- Q5 Mục lục khớp 13 tiêu đề thật — `... --toc`
- Q6 Không tràn chữ ở chương nào — `get_canvas_screenshot` từng chương rồi xem ảnh
- Q7 Số phần tử 5 khối cũ không đổi sau di chuyển — `... --count-by-prefix` so với backup
- Q8 `docs/diagrams/` có `.excalidraw` và `.png` > 100 KB — `ls -la docs/diagrams/`
- Q9 Script kiểm có test và test xanh — `python3 -m pytest tests/test_check_canvas_layout.py -q`
- Q10 Không hồi quy test cũ — `python3 -m pytest -q`
- Q11 Dữ kiện canvas khớp repo ở 4 điểm (số phase, số hook, số skill, version) — đối chiếu `PHASE_TABLE`, `ls hooks/scripts/`, `ls skills/`, `plugin.json`
