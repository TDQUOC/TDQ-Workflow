# RÀ SOÁT — bộ workflow TDQ đã quốc tế hoá tới đâu

Ngày: 2026-08-21 · Spec: ../spec/2026-08-21-2311-workflow-da-ngon-ngu.md (bản 1.1, ĐÃ DUYỆT)
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Câu hỏi của user: cổng duyệt có còn bắt buộc gõ đúng chữ tiếng Việt không, hay đã nhận được
câu trả lời theo chữ cái (`A. duyệt` · `B. góp ý thêm`) không phụ thuộc ngôn ngữ.

Cách chấm: 12 mã kiểm K1–K12 chốt trong spec TRƯỚC khi đọc code · lượt 1 chấm và ghi bằng
chứng `file:dòng` · lượt 2 phản chứng từng mã · chỉ phán quyết sau lượt 2 mới vào báo cáo.

## Mốc

- Commit HEAD lúc bắt đầu: `f620094`
- Full test suite lúc bắt đầu: **37 failed · 1166 passed · 1369 subtests passed** (88,46s).
  Toàn bộ 37 lỗi nằm ở `tests/test_skill_router.py` — có sẵn từ trước request này, do các
  skill plugin figma/datarobot/postman đã gỡ khỏi máy nên bảng định tuyến không mở được
  đường dẫn của chúng. Không lỗi nào thuộc `hooks/`, `scripts/` hay bộ luật `skills/`.
- `git status --short` lúc bắt đầu: 7 file `M` (`docs/tdq/STATE.md`, `docs/tdq/timing.jsonl`,
  `docs/workinglog/2026-08-19.md`, `graphify-out/graph.json`, `graphify-out/manifest.json`,
  `scripts/build_portable.py`, `tests/test_build_portable.py`) + 16 mục `??` — tất cả là dấu
  vết của request trước và của chính request này, không phải do việc rà soát.

## Bảng tổng

| Mã | Mặt | Điều đang kiểm | Lượt 1 | Sau phản chứng |
|---|---|---|---|---|
| K1 | A cổng duyệt | cổng `spec` nhận chữ cái | CHƯA | CHƯA (giữ) |
| K2 | A cổng duyệt | cổng `plan` nhận chữ cái | CHƯA | CHƯA (giữ) |
| K3 | A cổng duyệt | cổng `quick` nhận chữ cái | CHƯA | CHƯA (giữ) |
| K4 | A cổng duyệt | có đường không cần từ vựng ngôn ngữ | ĐẠT (chỉ cổng `mode`) | **ĐỔI** — ĐẠT chỉ với chữ cái TRẦN, 1/4 cổng |
| K5 | A cổng duyệt | một nguồn nhận diện duy nhất | ĐẠT | ĐẠT (giữ) — một điểm sửa duy nhất |
| K6 | B khuôn in | khuôn `➤ Duyệt:` mời chữ cái | CHƯA | CHƯA (giữ, nặng thêm: interview dạy chữ cái) |
| K7 | B khuôn in | khuôn có nguồn duy nhất | CHƯA (9 dòng chép tay ở 6 file) | CHƯA (giữ) |
| K8 | C ngôn ngữ | có luật bám ngôn ngữ user | CHƯA | CHƯA (giữ) |
| K9 | C ngôn ngữ | luật tiếng Việt là luật cứng | CHƯA (1 luật gốc + 6 dòng nhắc lại) | CHƯA (giữ) |
| K10 | D lưới an toàn | test khoá chuỗi tiếng Việt | 17 file / 26 lần | **ĐỔI** — 26 lần, chỉ ~1 file khoá hành vi |
| K11 | D lưới an toàn | có lưới tương thích ngược | ĐẠT | ĐẠT (giữ) |
| K12 | D lưới an toàn | bộ ca có ngôn ngữ khác | CHƯA | CHƯA (giữ) |

Lượt phản chứng đổi phán quyết của **2/12 mã**: K4 (hẹp lại — chỉ nhận chữ cái trần, và chỉ ở cổng `mode`) và K10 (26 lần xuất hiện nhưng chỉ khoảng 1 file thật sự khoá hành vi nhận diện). 10 mã còn lại giữ nguyên sau khi thử bác.

### K1 — A cổng duyệt

Câu hỏi: Cổng `spec` có nhận được câu trả lời chỉ gồm một chữ cái không?
Bằng chứng: `hooks/scripts/prompt_context.py:54-73` — `looks_like_approval(prompt, "spec")` đi tuần tự: chặn câu hỏi (dòng 57), nhánh `target == "mode"` (dòng 59-62) KHÔNG áp cho spec, nhánh quick (63) không áp, rồi dòng 65 `if not AGREE.search(prompt): return False`. `AGREE` (dòng 31-32) chỉ nhận `duyệt|duyet|ok|oke|okay|đồng ý|dong y|chốt|chot|approve|làm đi|lam di|tiến hành|tien hanh`. Chuỗi `"A"` không khớp từ nào.
Phán quyết: **CHƯA** — cổng spec bắt buộc một từ đồng ý tiếng Việt hoặc tiếng Anh; chữ cái bị loại ở dòng 65.
Phản chứng: Thử tìm đường cho "A" lọt cổng `spec`: `LETTER` chỉ được gọi ở `prompt_context.py:62` (nhánh `target == "mode"`) và `:87` (`mode_from_answer`); nhánh spec đi qua `:65 if not AGREE.search(prompt): return False` nên chết tại đó. Cổng thứ hai `bash_gate.py:75` không tự nhận diện lại mà đọc `matched` — không có đường vòng. Giữ CHƯA.
### K2 — A cổng duyệt

Câu hỏi: Cổng `plan` có nhận được chữ cái không?
Bằng chứng: Cùng hàm, cùng đường: `hooks/scripts/prompt_context.py:65` chặn trước khi tới `OBJECT` (dòng 33) — `plan` chỉ được xét SAU khi đã có từ đồng ý. `"B"` trượt ngay dòng 65.
Phán quyết: **CHƯA** — cổng plan giống hệt cổng spec.
Phản chứng: Cùng một thân hàm với K1, cổng `plan` không có nhánh riêng nào trước `:65`. Thử câu "B" và "chọn A" đều rơi vào `AGREE` rồi trả False. Giữ CHƯA.
### K3 — A cổng duyệt

Câu hỏi: Cổng `quick` có nhận được chữ cái không?
Bằng chứng: `hooks/scripts/prompt_context.py:37-39` — `APPROVE_FAST` đòi cặp `(duyệt|duyet|chốt|chot|approve)` + `(chế độ nhanh|che do nhanh|nhanh|express)`; `"A"` không có vế nào. Rơi tiếp xuống dòng 65 rồi `return False`.
Phán quyết: **CHƯA** — cổng quick đòi hai từ khoá, cả hai đều là từ vựng Việt/Anh.
Phản chứng: Thử "A" ở cổng `quick`: `APPROVE_FAST` (`:37`) đòi ĐỒNG THỜI một từ duyệt và một từ nhanh, không có nhánh chữ cái; hụt thì rơi tiếp xuống `:65`. Giữ CHƯA.
### K4 — A cổng duyệt

Câu hỏi: Có đường qua cổng nào KHÔNG cần một từ tiếng Việt hay tiếng Anh cụ thể không?
Bằng chứng: `hooks/scripts/prompt_context.py:48-51,59-62` — `LETTER = ^\s*(?:chọn |chon )?([ab])\b...$` và nhánh `if target == "mode": return bool(MODE.search(prompt) or LETTER.match(prompt))`. Đây là đường DUY NHẤT trong repo qua được cổng mà không cần một từ vựng ngôn ngữ nào — `"A"` trần trụi là hợp lệ. `mode_from_answer` (dòng 78-95) dịch chữ cái ra mode: A = mode plan đề xuất, B = mode còn lại.
Phán quyết: **ĐẠT nhưng chỉ 1/4 cổng** — cổng `mode` đã không bám ngôn ngữ; ba cổng `spec`, `plan`, `quick` thì chưa. Cơ chế user muốn ĐÃ TỒN TẠI và đã chạy thật, chỉ chưa được nối vào ba cổng kia.
Phản chứng: Thử làm gãy phán quyết ĐẠT: `MODE` (`:47`) khớp `main|inline|subagent|sub-agent` — token trung tính, không phải từ vựng tiếng Việt, còn `LETTER` nhận chữ cái trần. Nhưng `LETTER` neo `^…$` và chỉ tha tiền tố `chọn|chon`, nên "choose A", "pick B", "опция A" đều trượt. Sửa phán quyết thành: ĐẠT nhưng chỉ cho dạng chữ cái TRẦN, và chỉ ở 1/4 cổng.
### K5 — A cổng duyệt

Câu hỏi: `bash_gate` chặn `approve` có dùng cùng hàm nhận diện với `prompt_context` không?
Bằng chứng: `hooks/scripts/prompt_context.py:144-146` ghi kết quả nhận diện vào sổ turn (`turn_log_append(..., "signal", target=pending, matched=matched, ...)`); `hooks/scripts/bash_gate.py:64-82` không tự nhận diện lại mà đọc dòng signal gần nhất (`_latest_signal`) rồi chặn khi `matched is False`. `grep -rn looks_like_approval` toàn repo chỉ ra 1 định nghĩa trong `hooks/scripts/prompt_context.py:54` (bản `portable_claude/` là bản sinh tự động, không phải nguồn) và 4 chỗ gọi trong `tests/`.
Phán quyết: **ĐẠT** — một nguồn nhận diện duy nhất, `bash_gate` ăn theo qua sổ turn. Sửa `looks_like_approval` là cả hai cổng đổi theo, không có bản chép tay thứ hai phải sửa song song.
Phản chứng: Thử tìm bộ nhận diện thứ hai để bác "một nguồn duy nhất": `bash_gate.py:58 APPROVE_CLI` chỉ khớp chuỗi LỆNH `tdq_state.py approve …`, không đọc câu user; `tdq_state.py:734` và `_common.py:29` là chuỗi HIỂN THỊ. Không có bộ nhận diện thứ hai. Giữ ĐẠT — một điểm sửa duy nhất là `looks_like_approval`.
### K6 — B khuôn in cho user

Câu hỏi: Khuôn `➤ Duyệt:` có mời user trả lời bằng chữ cái không?
Bằng chứng: Không dòng `➤ Duyệt:` nào mời chữ cái. `skills/tdq-spec/SKILL.md:54` = `nhắn "duyệt spec"`; `skills/tdq-plan/SKILL.md:80` = `nhắn "duyệt plan"`; `skills/tdq-intake/references/quick-lane.md:56,135` = `nhắn "duyệt nhanh"`; `skills/tdq-status/SKILL.md:42` = `nhắn "duyệt <spec|plan|quick>"`; `skills/tdq-conventions/references/user-facing-block.md:110,128` = `nhắn "duyệt spec"`. Chữ cái CHỈ xuất hiện ở hai cổng không phải cổng duyệt: `skills/tdq-plan/references/mode-gate.md:21` (`➤ Trả lời: nhắn "A" / "inline" hoặc "B" / "sub-agent"`) và `skills/tdq-intake/references/lane-decision.md:66` (`➤ Trả lời: nhắn "A" hoặc "B"`).
Phán quyết: **CHƯA** — khuôn duyệt mời gõ một câu tiếng Việt; khuôn chữ cái đã có sẵn nhưng chỉ dùng cho cổng lane và cổng mode.
Phản chứng: Thử tìm chỗ khác dạy user trả lời bằng chữ cái ở cổng duyệt: `tdq-intake/references/interview.md:78` có dòng "Trả lời bằng chữ cái" nhưng gắn cho vòng option A/B/C (lane, mode), không gắn cho khối `➤ Duyệt:`. Phản chứng làm phán quyết NẶNG thêm: dòng đó dạy một thói quen mà cổng spec/plan không nhận (K1, K2). Giữ CHƯA.
### K7 — B khuôn in cho user

Câu hỏi: Bao nhiêu file luật đang chép tay khuôn `➤ Duyệt:`, có nguồn duy nhất không?
Bằng chứng: **7 nơi giữ khuôn này, chỉ 1 nơi là máy sinh.** Máy sinh: `hooks/scripts/_common.py:176-183` (`approve_hint`) đọc hằng `APPROVE_HINTS` ở `_common.py:28-40`. Sáu nơi còn lại chép tay: `skills/tdq-spec/SKILL.md:54` · `skills/tdq-plan/SKILL.md:80` · `skills/tdq-intake/references/quick-lane.md:56,135` · `skills/tdq-status/SKILL.md:42` · `skills/tdq-conventions/references/user-facing-block.md:110,128` · `scripts/tdq_state.py:734,837` (trường `say` của PHASE_TABLE). Tổng 9 dòng chép tay. (Các bản trong `portable_claude/`, `portable_codex/` là bản sinh của `build_portable.py`, không tính.)
Phán quyết: **CHƯA** — không có nguồn duy nhất. Đổi câu mời duyệt phải sửa tay 9 dòng ở 6 file, trong khi hằng `APPROVE_HINTS` đã sẵn sàng đóng vai nguồn duy nhất đó.
Phản chứng: Thử coi 9 dòng chép tay là bản render từ `APPROVE_HINTS`: không phải — `_common.py:176 approve_hint()` chỉ sinh chuỗi cho hook in ra, còn 9 dòng kia là văn bản tĩnh trong file `SKILL.md`/reference do model đọc. Hai bản độc lập, sửa một bên không kéo bên kia. Giữ CHƯA.
### K8 — C ngôn ngữ output

Câu hỏi: Có luật nào cho phép trả lời theo ngôn ngữ user đang nhắn không?
Bằng chứng: `grep -rn "ngôn ngữ|language" skills/` (bỏ bản portable) trả về 4 dòng, tất cả nói về NGÔN NGỮ LẬP TRÌNH: `skills/tdq-build/SKILL.md:37`, `skills/tdq-conventions/references/plugin-routing.md:42`, `skills/tdq-conventions/references/clean-code.md:45`, `skills/tdq-spec/references/spec-template.md:85`. Không dòng nào nói tới ngôn ngữ tự nhiên của user. Trong khi đó phần luật lý luận của các skill `tdq-*` đã viết bằng tiếng Anh (vd `skills/tdq-plan/SKILL.md:8` là câu tiếng Anh nhưng vẫn chốt output là tiếng Việt) — tức bộ luật đã tách được hai lớp, chỉ chưa mở lớp output.
Phán quyết: **CHƯA** — không có bất kỳ luật nào cho phép trả lời theo ngôn ngữ user đang nhắn.
Phản chứng: Thử tìm bất kỳ luật nào nói bám theo ngôn ngữ user: rà `skills/tdq-conventions/` chỉ thấy chiều ngược lại — "Mọi output cho user: tiếng Việt". Không có luật nào lấy ngôn ngữ user làm biến. Giữ CHƯA.
### K9 — C ngôn ngữ output

Câu hỏi: Luật "Mọi output cho user: tiếng Việt" nằm ở bao nhiêu file, có phải luật cứng không?
Bằng chứng: 7 dòng ở 6 file (bỏ bản portable): `skills/tdq-conventions/SKILL.md:10` (`Mọi output cho user viết **tiếng Việt**.` — luật gốc) · `skills/tdq-intake/SKILL.md:8` · `skills/tdq-status/SKILL.md:8` · `skills/tdq-spec/SKILL.md:3,9` · `skills/tdq-plan/SKILL.md:8` · `skills/tdq-build/references/report-template.md:9,48`. Bốn dòng sau tự nhận là "nhắc lại có chủ ý — bản gốc ở `skills/tdq-conventions/SKILL.md`", nên chỉ có MỘT luật gốc.
Phán quyết: **CHƯA (là luật cứng)** — tiếng Việt bị chốt cứng, không có cổng bật/tắt và không có nhánh nào theo ngôn ngữ user. Nhưng đây là một luật gốc + 6 dòng nhắc lại, nên sửa một chỗ là đủ về mặt ngữ nghĩa, phần còn lại chỉ là đồng bộ câu chữ.
Phản chứng: Thử tìm cổng bật/tắt để hạ luật tiếng Việt xuống mức tuỳ chọn: không có cờ config, không có biến môi trường, không có nhánh lane nào nới luật này. Nó là văn bản luật cứng, được nhắc lại ở `tdq-intake` và `tdq-plan`. Giữ CHƯA.
### K10 — D lưới an toàn

Câu hỏi: Bao nhiêu file test khoá chuỗi tiếng Việt của cổng duyệt?
Bằng chứng: `grep -rln "duyệt spec|duyệt plan|duyệt nhanh|duyệt quick" tests/*.py` → **17 file**: test_check_status · test_bash_gate · test_compliance_protocol · test_context_hooks · test_gate_merge · test_claude_md_core · test_e2e_chain · test_mode_phase · test_lane_label · test_prompt_context · test_phase_table · test_quick_qc · test_ranh_gioi · test_state · test_state_file · test_tdq_eval · test_user_facing_block. Riêng chuỗi `"duyệt spec"` xuất hiện 26 lần.
Phán quyết: **17 file / 26 lần chỉ riêng "duyệt spec"** — lưới test bám rất chặt câu chữ tiếng Việt. Đây là chi phí thật của request sửa sau, và cũng là lưới giữ tương thích ngược.
Phản chứng: Thử bác con số 26 bằng cách hỏi "bao nhiêu lần thật sự KHOÁ hành vi": phần lớn là chuỗi `--by "duyệt spec"` (dữ liệu vào, đổi luật vẫn xanh). Chỗ khoá thật nằm ở `tests/test_prompt_context.py` — chỉ 2 lần chữ "duyệt" và một bộ assert âm `test_answer_rejects_noise`. Sửa số: 26 lần xuất hiện, nhưng chỉ ~1 file khoá hành vi nhận diện.
### K11 — D lưới an toàn

Câu hỏi: Có test nào khẳng định "câu duyệt cũ vẫn qua cổng" đủ làm lưới tương thích ngược không?
Bằng chứng: `tests/test_lane_label.py:84-99` có cả bộ dương (`DUONG`) và bộ âm (`AM`) chạy qua `looks_like_approval(prompt, "quick")`, cộng `test_bi_danh_khong_duyet_lam_cho_spec_plan` (dòng 97-99) khoá việc `"duyệt nhanh"` KHÔNG được tính là duyệt spec/plan. `tests/test_prompt_context.py:72-100` khoá việc câu duyệt phải được ghi vào sổ turn (`matched`) — chính là đường `bash_gate` đọc. `tests/test_prompt_context.py:141-164` đã có sẵn ba test cho cổng mode: nhận tên cũ/mới, **nhận chữ cái** (`test_answer_accepts_option_letters`), và **từ chối nhiễu** (`test_answer_rejects_noise`).
Phán quyết: **ĐẠT** — lưới tương thích ngược đủ dùng: có bộ dương, bộ âm, và có sẵn mẫu test chữ cái ở cổng mode để nhân bản sang ba cổng còn lại. Thêm chữ cái mà làm hỏng câu duyệt cũ thì 17 file test này đỏ ngay.
Phản chứng: Thử làm gãy phán quyết ĐẠT: `test_answer_rejects_noise` giữ "Ai làm cũng được" phải trả False — nếu sau này nới `LETTER` thành mọi chữ cái đơn thì câu này có gãy không? Không: `LETTER` neo `^…$` và dùng `([ab])\b`, "Ai" không có ranh giới từ sau "A". Lưới vẫn bắt đúng ca nguy hiểm. Giữ ĐẠT.
### K12 — D lưới an toàn

Câu hỏi: Bộ ca `evals/tuan-thu/` có ca nào chấm cổng duyệt bằng ngôn ngữ khác không?
Bằng chứng: `evals/tuan-thu/` có 10 ca; 7 ca có prompt duyệt và **tất cả đều tiếng Việt**: `duyet-spec/ca.json` (`"duyệt spec"`), `duyet-plan-kem-mode/ca.json` (`"duyệt plan, làm trực tiếp đi"`), `duyet-plan-thieu-mode/ca.json` (`"duyệt plan"`), `duyet-spec-mo-ho/ca.json` (`"ok"`), `build-tick-tung-task/ca.json` (`"làm tiếp đi"`), `commit-khong-push/ca.json`, `red-green/ca.json`. Không ca nào gõ tiếng Anh, và không ca nào trả lời cổng bằng chữ cái.
Phán quyết: **CHƯA** — bộ ca hồi quy đo tuân thủ hoàn toàn bằng tiếng Việt; sau khi sửa sẽ không có ca nào chứng minh cổng chạy đúng với ngôn ngữ khác.
Phản chứng: Thử tìm ca eval không phải tiếng Việt trong `evals/tuan-thu/`: 7 thư mục ca (`duyet-spec`, `duyet-spec-mo-ho`, `duyet-plan-kem-mode`, `duyet-plan-thieu-mode`, `lane-mo-ho`, `bao-loi`, `commit-khong-push`, …) đều dùng câu tiếng Việt trong `ca.json`. Không có ca nào bằng ngôn ngữ khác. Giữ CHƯA.

## Điểm khoá cứng

Chuỗi tiếng Việt nằm trên đường đi DUY NHẤT của một cổng — bỏ nó đi thì cổng gãy, không có
đường dự phòng. Đây là danh sách phải sửa trong request sau, không phải danh sách mọi chỗ có
tiếng Việt.

| # | Vị trí | Chuỗi/luật khoá cứng | Bỏ đi thì gãy gì |
|---|---|---|---|
| H1 | `hooks/scripts/prompt_context.py:31` (`AGREE`) | `duyệt·duyet·đồng ý·chốt·làm đi·tiến hành` + `ok·approve` | Cổng `spec`/`plan`/`quick` không còn cách nào nhận duyệt: dòng `:65` trả False cho MỌI câu. Đây là nút thắt duy nhất của 3 trong 4 cổng. |
| H2 | `hooks/scripts/prompt_context.py:33` (`OBJECT`) | `spec·plan·quick·mini-plan` | Không phân biệt được "duyệt spec" với "duyệt plan"; user duyệt nhầm cổng mà máy không thấy. |
| H3 | `hooks/scripts/prompt_context.py:37` (`APPROVE_FAST`) | `duyệt + chế độ nhanh/nhanh/express` | Cổng `quick` mất lối tắt riêng, rơi về `AGREE` nên "duyệt nhanh" phải kèm đại từ mới lọt. |
| H4 | `hooks/scripts/prompt_context.py:50` (`LETTER`) | tiền tố `chọn·chon` + đúng chữ `a·b` | Cổng `mode` mất dạng trả lời bằng chữ cái — đường DUY NHẤT hiện không cần từ vựng tiếng Việt (K4). |
| H5 | `hooks/scripts/prompt_context.py:40` (`PRONOUN`) | đại từ tiếng Việt | Câu duyệt không nêu đối tượng (`ok`, `duyệt`) hết đường qua nhánh `:73`. |
| H6 | `hooks/scripts/_common.py:28-40` (`APPROVE_HINTS`) | `nhắn "duyệt spec"` … | Hook hết câu mời; user không biết phải gõ gì. Đây là nguồn MÁY duy nhất của dòng mời. |
| H7 | `skills/tdq-spec/SKILL.md:54` · `tdq-plan/SKILL.md:80` · `tdq-status/SKILL.md:42` · `tdq-conventions/references/user-facing-block.md:110,128` · `tdq-intake/references/quick-lane.md:56,135` | 9 dòng `➤ Duyệt: nhắn "…"` chép tay | Model in câu mời khác với câu máy nhận → user gõ đúng theo màn hình mà cổng vẫn từ chối. Sửa H6 KHÔNG kéo theo 9 dòng này (K7). |
| H8 | `scripts/tdq_state.py:734,837` | chuỗi hướng dẫn `In: ➤ Duyệt: …` trong bảng bước kế tiếp | `tdq_state.py next` in hướng dẫn lệch với thực tế cổng. |
| H9 | `skills/tdq-conventions/SKILL.md:10` | "Mọi output cho user viết **tiếng Việt**." | Luật gốc, không có cổng tắt (K9). Mọi khuôn in đều dẫn về đây; đổi luật ngôn ngữ mà không đổi dòng này thì các skill vẫn ép tiếng Việt. |

## Đề xuất cho request sửa sau

Tám mã còn CHƯA sau lượt phản chứng, mỗi mã đúng một đề xuất. Ràng buộc chung: **thêm
đường, không thay đường** — mọi câu duyệt tiếng Việt cũ phải chạy y hệt (yêu cầu `3a` và
`5` của user).

### Đề xuất Đ1 — cổng `spec` nhận chữ cái (mã K1)
Trong `looks_like_approval`, thêm một nhánh TRƯỚC dòng `:65`: `target in ("spec","plan","quick")`
và câu khớp một regex `CHOICE` mới (chữ cái đơn `a`–`d`, cho phép tiền tố trung tính
`chọn|chon|choose|pick|option|opt` và hậu tố dấu câu) → trả True. Vì `bash_gate` đọc lại
`matched` (K5), sửa một chỗ là cả hai cổng cùng đổi.
Tương thích ngược: `tests/test_prompt_context.py::test_answer_rejects_noise` phải vẫn xanh —
đặc biệt ca `"Ai làm cũng được"` (an toàn nhờ neo `^…$` và `\b`), và mọi ca `duyệt spec`/
`duyệt plan` hiện có.

### Đề xuất Đ2 — cổng `plan` nhận chữ cái (mã K2)
Không viết nhánh riêng: dùng chung `CHOICE` của Đ1, chỉ mở rộng danh sách `target`. Lý do:
K5 đã chứng minh chỉ có một bộ nhận diện, tách nhánh theo cổng sẽ đẻ ra bộ thứ hai.
Tương thích ngược: bộ ca `duyet-plan-kem-mode` và `duyet-plan-thieu-mode` trong
`evals/tuan-thu/` phải giữ nguyên kết quả (chữ cái KHÔNG được nuốt mất phần khai mode).

### Đề xuất Đ3 — cổng `quick` nhận chữ cái (mã K3)
Cùng `CHOICE`, nhưng phải giữ ngữ nghĩa hai mức của cổng nhanh ("duyệt nhanh" vs "duyệt
nhanh bỏ QC"): chữ cái chỉ được ánh xạ sang mức mặc định, mức bỏ QC vẫn đòi câu nói rõ.
Tương thích ngược: `tests/test_quick_qc.py` phải vẫn xanh, và `APPROVE_FAST` giữ nguyên.

### Đề xuất Đ4 — khuôn `➤ Duyệt:` mời chữ cái (mã K6)
Đổi khuôn thành hai lối song song trên cùng một dòng, ví dụ
`➤ Duyệt: nhắn "duyệt spec" hoặc "A" · Góp ý: nhắn trực tiếp`. Không bỏ câu tiếng Việt,
chỉ thêm lối chữ cái đã có ở Đ1 để màn hình khớp với thứ máy nhận.
Tương thích ngược: test nào assert nguyên văn dòng mời (`tests/test_common.py`,
`tests/test_stop_gate.py` nếu có) phải được sửa theo cùng lượt, không để lệch.

### Đề xuất Đ5 — dòng mời có nguồn duy nhất (mã K7)
Đưa `APPROVE_HINTS` (`hooks/scripts/_common.py:28-40`) thành nguồn DUY NHẤT, rồi thay 9 dòng
chép tay ở H7 bằng một câu trỏ về nó ("in đúng dòng hook sinh ra"). Bước này phải làm SAU Đ4,
nếu không sẽ chép lại một khuôn sắp đổi.
Tương thích ngược: `doc_lint` và eval `duyet-spec` phải vẫn xanh; nếu linter đang so khớp
nguyên văn dòng mời trong skill thì nới luật linter cùng lượt.

### Đề xuất Đ6 — luật bám ngôn ngữ user (mã K8)
Thêm vào `skills/tdq-conventions/SKILL.md` một luật: *trả lời bằng ngôn ngữ user đang dùng
trong request đó; không xác định được thì mặc định tiếng Việt*. Ngôn ngữ trở thành biến của
request, không phải hằng của hệ thống — đúng yêu cầu `4b`.
Tương thích ngược: mặc định tiếng Việt giữ mọi request cũ (đều viết bằng tiếng Việt) chạy
không đổi một chữ.

### Đề xuất Đ7 — hạ luật tiếng Việt khỏi mức luật cứng (mã K9)
Sửa `skills/tdq-conventions/SKILL.md:10` từ mệnh lệnh tuyệt đối thành mặc định có điều kiện,
rồi rà 6 dòng nhắc lại ở `tdq-intake`/`tdq-plan` cho khớp. Đây là việc TÀI LIỆU, phải đi kèm
Đ6 trong cùng một request để không có lúc luật gốc và luật nhắc lại nói ngược nhau.
Tương thích ngược: không có test nào assert dòng luật này (đã kiểm ở K9), nên rủi ro nằm ở
hành vi model chứ không ở suite — cần ít nhất một ca eval mới (xem Đ8).

### Đề xuất Đ8 — bộ ca eval có ngôn ngữ khác (mã K12)
Thêm vào `evals/tuan-thu/` hai ca song sinh của `duyet-spec`: một ca user viết tiếng Anh
("approve the spec"), một ca user trả lời đúng một chữ "A". Hai ca này là lưới duy nhất bắt
được hồi quy của Đ1–Đ7, vì phần lớn hành vi ngôn ngữ nằm ở model chứ không ở regex.
Tương thích ngược: 7 ca tiếng Việt hiện có giữ nguyên, không sửa `ca.json` của chúng — ca mới
là thư mục mới.

## Kiểm cuối

- Suite: `python3 -m pytest tests/ -q` → **37 failed · 1166 passed · 1369 subtests** trong 87,07s —
  bằng đúng mốc T1.1 (37 lỗi đều nằm ở `tests/test_skill_router.py`, có từ trước request này).
- Phạm vi ghi: `git status --short` — mọi mục ngoài `docs/tdq/` (`scripts/build_portable.py`,
  `tests/test_build_portable.py`, `evals/`, `scripts/tdq_eval.py`, `tests/mau_transcript/`,
  `tests/test_tdq_eval.py`, `graphify-out/`) đều đã có trong mốc T1.1, tức thuộc request trước.
  Request này chỉ thêm file trong `docs/tdq/` và working log.
