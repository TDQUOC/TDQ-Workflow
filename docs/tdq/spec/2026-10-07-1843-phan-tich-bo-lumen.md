# SPEC — Phân tích: bỏ Lumen thì TDQ trên Claude Code và Codex còn chạy ổn không

Ngày: 2026-10-07 · Bản: 1.0 · Brief: ../brief/2026-10-07-1843-phan-tich-bo-lumen.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: ĐÃ DUYỆT

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
- Mục tiêu: trả lời có bằng chứng câu "gỡ plugin + binary Lumen (giữ ollama) thì TDQ workflow trên Claude Code và trên Codex còn chạy ổn không", gồm (a) mọi điểm phụ thuộc Lumen được xếp loại GÃY / ỒN / ỔN, (b) số đo chất lượng tìm kiếm có và không có Lumen trên 2 repo, (c) danh sách đề xuất sửa cụ thể theo file.
- Trong phạm vi:
  - Chức năng: hook (`search_gate`, `search_observe`, `session_start`), các bước phase, `tdq_finish`, `tdq_lsp check`, `tdq_setup`, `setup_status`.
  - Tương thích: cột riêng cho Claude Code và Codex (Codex chạy qua provider 9router), gồm cả việc `~/.codex/config.toml` trỏ `[mcp_servers.lumen]` vào binary trong cache plugin Claude Code.
  - Chất lượng tìm kiếm: phép đo 2 nhánh trên TDQ-Workflow và `claudecodeui`.
  - Bảo trì: test, luật chữ (skill, CLAUDE.md, PHASE_TABLE), tài liệu còn nhắc Lumen.
- NGOÀI phạm vi:
  - Hiệu năng máy (RAM/CPU của ollama — ollama được giữ), bảo mật.
  - Sửa mã/luật thật — chỉ đề xuất; sửa ở request sau.
  - Gỡ thật plugin/binary — chỉ giả lập rồi trả máy về đúng trạng thái cũ.
  - Repo `excalidraw`.

## 1b. Lộ trình
| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | câu hỏi nội bộ; hành vi Codex khi MCP hỏng đo trực tiếp rẻ hơn tra |
| Interview | CÓ | đã chạy 2 vòng |
| spec → plan | CÓ | khung bất biến |
| Implement bằng subagent | CÓ | 4 agent đo chất lượng chạy song song |
| QC độc lập (agent) | BỎ | mức QC `full` không đòi; đầu ra là báo cáo, không có mã |
| Report + hỏi commit | CÓ | khung bất biến |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Bản đồ phụ thuộc Lumen: mỗi điểm (file:dòng) → loại GÃY/ỒN/ỔN × Claude Code/Codex, kèm bằng chứng | `docs/tdq/research/2026-10-07-1843-phan-tich-bo-lumen.md` | mọi file trong danh sách `grep -ril lumen` của mã/skill/test/hook có mặt hoặc có lý do loại |
| 2 | Bộ đo chất lượng: câu hỏi + đáp án + kết quả thô 2 nhánh × 2 repo | `docs/tdq/bench/2026-10-07-1843-chat-luong-lumen/` | đủ 4 lần chạy, mỗi câu có trúng/trượt, lượt tool, token |
| 3 | Biên bản thử 2 host khi Lumen vắng | `docs/tdq/bench/2026-10-07-1843-hai-host-khong-lumen/` | có output thật của Claude Code và Codex, kèm lệnh đã chạy; máy đã trả về trạng thái cũ |
| 4 | Báo cáo kết luận + đề xuất sửa | `docs/tdq/report/2026-10-07-1843-phan-tich-bo-lumen.md` | trả lời có/không cho từng host, mỗi đề xuất trỏ tới file và một bằng chứng ở đầu ra 1–3 |

## 2b. Ranh giới module

Request không sửa mã, nên module là vùng tài liệu đầu ra; ranh giới lấy theo nguồn bằng chứng, không theo cây thư mục mã.

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| ban-do | `docs/tdq/research/2026-10-07-1843-phan-tich-bo-lumen.md` | không | 1 |
| do-chat-luong | `docs/tdq/bench/2026-10-07-1843-chat-luong-lumen/` | không | 2 |
| thu-hai-host | `docs/tdq/bench/2026-10-07-1843-hai-host-khong-lumen/` | ban-do (biết điểm nào cần quan sát) | 3 |
| bao-cao | `docs/tdq/report/2026-10-07-1843-phan-tich-bo-lumen.md` | ban-do, do-chat-luong, thu-hai-host | 4 |

## 3. Cách tiếp cận & lý do
- Chọn:
  1. **Bản đồ tĩnh**: đi qua mọi file nhắc Lumen (LSP `find_references` cho ký hiệu như `_binary_lumen`, `LUMEN`, `step_reindex`; grep cho chuỗi trong luật chữ), xếp loại: GÃY = workflow dừng/sai/chấm lỗi oan; ỒN = vẫn chạy nhưng in cảnh báo, ghi nợ, tốn token; ỔN = tự rơi êm.
  2. **Đo chất lượng 2 nhánh**: cùng 12 câu hỏi khái niệm/repo (câu không có sẵn tên ký hiệu để grep, ví dụ "chỗ nào ghi thời điểm duyệt"). Nhánh CÓ: agent được dùng lumen + LSP + graphify + grep. Nhánh KHÔNG: agent chỉ được LSP + graphify + grep. Mỗi repo × nhánh = 1 agent. Chấm: trúng nếu câu trả lời chứa vị trí đáp án; ghi lượt tool và token mỗi agent. Lumen phải sống thật cho nhánh CÓ (đánh thức ollama, index lại 2 repo).
  3. **Luật kết luận chất lượng** (định trước để không chấm theo cảm giác): "giảm đáng kể" khi nhánh KHÔNG trượt nhiều hơn nhánh CÓ ít nhất 2 câu trên 12 ở cùng repo, HOẶC token nhánh KHÔNG ≥ 1,5× nhánh CÓ. Dưới cả hai → "không giảm đáng kể". Kết luận nêu tách theo repo.
  4. **Thử 2 host bằng ghi đè theo lần chạy**: Claude Code `claude -p --settings` tắt plugin lumen; Codex `codex exec -c` trỏ `mcp_servers.lumen` vào binary không tồn tại (giống hệt sau khi gỡ plugin). Script TDQ (`tdq_lsp check`, `tdq_finish`, `tdq_setup`) chạy với `USERPROFILE` tạm và PATH không có lumen để `_binary_lumen` trả rỗng. Quan sát: phiên có khởi động không, search gate có mở khoá qua LSP/graphify không, cảnh báo/nợ in ra gì.
  5. **Hồi quy**: không sửa mã, nên trọn bộ test phải giữ đúng mốc đỏ hiện có (3 module, 2 nguyên nhân đã biết) — không thêm module đỏ nào.
- Vì: số đo trong repo chưa từng so trực tiếp lumen với grep/LSP (dòng lumen trong `uu-tien-tim-kiem.md` suy ra từ điểm yếu của LSP); ghi đè theo lần chạy giữ đúng ý 7A (giả lập, trả lại) mà không chạm file cấu hình của user.
- Đã loại:
  - So lumen top-k thô với grep thô — không phản ánh agent thật làm việc ra sao.
  - Một agent mỗi câu (48 agent) — tốn ~10× mà không thêm thông tin.
  - Sửa `~/.codex/config.toml` / `settings.json` để giả lập — chỉ dùng khi ghi đè theo lần chạy không ăn, lúc đó có bản sao và khôi phục.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake / tdq-spec / tdq-plan / tdq-build | project | NỀN | khung workflow đang chạy |
| tdq-setup (tham chiếu `uu-tien-tim-kiem.md`, `lumen.md`) | project | DÙNG | nguồn luật 4 tầng và cấu hình lumen cho bản đồ phụ thuộc |
| lumen:doctor | plugin:lumen | DÙNG | đo sức khoẻ Lumen trước nhánh CÓ |
| lumen:reindex | plugin:lumen | DÙNG | index lại 2 repo trước khi đo |
| Đã xét 17 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — request chỉ ra tài liệu và số đo, không có task tạo/sửa mã chạy được.
- Không placeholder, không TODO stub, không số đo bịa: mọi con số trong báo cáo trỏ về file kết quả thô.
- Unit test riêng: BỎ — không có thành phần mã mới; hồi quy đo bằng trọn bộ test hiện có.
- Clean code / SOLID: không áp — không viết mã.

## 5. Ràng buộc & rủi ro
Ràng buộc kiến trúc phải giữ: không chạm dòng nào — request không sửa mã; dòng `search_gate` chặn chứ không nhắc (`docs/kien-truc.md` mục 2026-10-03) chỉ được ĐỌC để xếp loại.

- Không cài/gỡ gì. Cần ollama chạy (đã có, model `qwen3-embedding:0.6b`) và lumen index được 2 repo; Codex dùng provider 9router sẵn có.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Agent nhánh KHÔNG vẫn lén gọi lumen | số đo nhánh KHÔNG đẹp giả | agent liệt kê mọi tool đã gọi; câu nào có lumen bị loại khỏi nhánh đó và ghi rõ |
| Đáp án do agent chính tự soạn → thiên lệch | chấm sai | user xem bộ câu + đáp án trong plan trước khi đo |
| Lumen không sống được (ollama/host) | nhánh CÓ không chạy | dùng `OLLAMA_HOST=http://localhost:11434`; vẫn chết → báo cáo ghi rõ, phần chất lượng chỉ còn số đo cũ |
| Ghi đè theo lần chạy không ăn | giả lập sai | rơi về sửa file có bản sao, khôi phục, so `sha256` trước/sau |
| 12 câu là mẫu nhỏ | kết luận yếu thống kê | báo cáo nói rõ cỡ mẫu, không ngoại suy ra mọi repo |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Bản đồ phụ thuộc đủ | mọi file mã/skill/hook/test nhắc lumen (ngoài `docs/`, `graphify-out/`, `claude-export/`) có dòng xếp loại hoặc lý do loại | đếm 2026-10-07: 51 file khớp `grep -ril lumen` | — |
| Q2 | Bộ đo đủ | mỗi repo có ít nhất 12 câu hỏi khái niệm kèm đáp án file:dòng, cả 4 lần chạy có kết quả từng câu | chưa đo; ước lượng soạn được 12–15 câu/repo từ cỡ repo (TDQ 129 module, claudecodeui 995 file) | repo nào không đủ 12 câu đúng nghĩa khái niệm → dùng số soạn được, ghi `lech add` |
| Q3 | Kết luận chất lượng theo luật định trước | báo cáo áp đúng luật §3 mục 3 (chênh trượt ≥ 2 câu/12, hoặc token ≥ 1,5×) cho từng repo, có số trúng/trượt và token | chưa đo; số đo cũ duy nhất: LSP xếp đích hạng 13/62 (report 2026-09-03-0017) | một repo chạy hỏng một nhánh → kết luận chỉ cho repo còn đủ 2 nhánh, ghi `lech add` |
| Q4 | Thử Claude Code không lumen | có output thật của một phiên `claude -p` đã tắt plugin lumen, ghi rõ khởi động, search gate, cảnh báo | — | — |
| Q5 | Thử Codex không lumen | có output thật của `codex exec` với lumen trỏ vào binary không tồn tại, ghi rõ khởi động và search gate | — | — |
| Q6 | Script TDQ khi binary vắng | `tdq_lsp check`, `tdq_finish`, `tdq_setup` chạy với binary vắng: ghi output, không traceback | — | — |
| Q7 | Máy trả về như cũ | `~/.codex/config.toml`, `~/.claude/settings.json` cùng `sha256` trước/sau; plugin lumen vẫn bật | — | — |
| Q8 | Hồi quy | trọn bộ test: tập module đỏ không lớn hơn mốc trước khi làm (3 module, nguyên nhân đã ghi ở brief) | đo 2026-10-07: 3 module đỏ, 7 phút 5 giây | — |
| Q9 | Báo cáo đủ | trả lời có/không cho Claude Code và Codex; mỗi đề xuất sửa trỏ file + bằng chứng ở đầu ra 1–3 | — | — |

DoD: Q1–Q9 PASS; báo cáo ở `docs/tdq/report/2026-10-07-1843-phan-tich-bo-lumen.md`; máy về đúng trạng thái trước khi đo.

## 7. Câu hỏi còn mở
