# Brief — `run` chấm fail dù Codex làm đúng (model không theo output-schema)
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

Người dùng chọn "2a" cho câu hỏi: "Có mở request riêng để sửa lỗi `run` bị chấm fail vì model
không theo schema không?" — phát hiện ngoài phạm vi ở QC của request
`2026-09-14-1213-sua-check-codex-bat-co`:

> `run` chấm `trang_thai: fail` cả hai lượt dù Codex làm đúng — model `ag/gemini-3.8-flash-medium`
> ghi `ket-qua.json` bằng câu văn thường chứ không theo JSON schema. Nghĩa là với model này, mọi
> lượt `codex implement` sẽ bị chấm fail.

### Đọc lần đầu

- **Mục tiêu:** một lượt `tdq_codex.py run` làm đúng việc thì được chấm `xong`; làm sai, không rõ,
  bị chặn hoặc quá hạn thì vẫn chấm đúng `fail`/`deny`/`timeout` như bây giờ.
- **Phạm vi đoán:** `scripts/tdq_codex.py` (`_cli_run`, `doc_ket_qua`, `phan_quyet`, có thể
  `dung_lenh` hoặc prompt), test `tests/test_codex_run.py`, sinh lại bundle.

### Bằng chứng đã có (log, không đoán)

| Lượt | exit | `ket-qua.json` (nguyên văn) | Việc thật | Chấm |
|---|---|---|---|---|
| Q13-PROBE | 0 | `The write was denied with an "operation not permitted" error.` | đúng: bị sandbox chặn, file ngoài repo không có | `fail` |
| Q21B-PROBE-124119 | 0 | ``The file `docs/tdq/qc/q21b-probe.txt` contains the string `Q21B-PROBE-124119`.`` | đúng: file mang đúng mã | `fail` |

- Dòng quyết định: `scripts/tdq_codex.py:446-459` `doc_ket_qua` trả `None` khi JSON hỏng →
  `phan_quyet` (`:462-479`) nhánh `not isinstance(ket_qua, dict)` → `fail`.
- Lệnh gọi có `--output-schema <home>/schema.json` (`{"xong": boolean}` bắt buộc) và `-o <home>/ket-qua.json`.
- Provider máy: `model_provider = "9router"`, `wire_api = "responses"` (một router đứng trước model Gemini).

### Chỗ chưa rõ (phải làm rõ ở phân tích, chưa được đoán)

1. Gốc lỗi nằm ở đâu: `codex` không gửi schema qua provider tuỳ chỉnh, router 9router bỏ trường
   schema khi chuyển sang Gemini, hay model nhận schema mà vẫn trả văn thường?
2. Hướng sửa: ép JSON trong prompt, đọc JSON lẫn trong văn bản, hay đổi cách xác định `xong`
   (vd. dựa vào test leader chạy lại) — mỗi hướng đụng tới nguyên tắc "không biết thì phải FAIL".
3. Có cần phân biệt "model không theo schema" thành một trạng thái/lý do riêng để người dùng thấy, thay vì `fail` trơn?

### Kiểm lớp tìm kiếm

- `tdq_lsp.py check` → 7/7 bậc ĐẠT.
- Kiểm hiệu ứng trên `dat_co_dong_y`: LSP `find_references` 17 tham chiếu (namespace `scripts` 4,
  `tests` 13); grep theo file: `tdq_codex.py` 3 + `tdq_checkportable.py` 1 = 4, `test_codex_cli.py`
  10 + `test_codex_run.py` 3 = 13 → cùng 4 file, LSP ≥ grep → PASS.

## Hiểu & kiến thức

Pipeline: deep (người dùng chọn "1a") · loại `bugfix` · nhánh `bugfix/run-cham-fail-sai-schema` từ `main`.
Vòng scope: BỎ — request nằm gọn trong một vùng (phán quyết một lượt `run` của `scripts/tdq_codex.py`), không có nhiều vùng để chọn.

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-09-14: 10 skill trên đĩa (lọc giữ 8, ẩn 2 khác lĩnh vực), cộng skill built-in
trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-conventions, tdq-lsp-setup, tdq-status, tdq-check-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy |
| graphify | user | DÙNG | cuối turn có sửa code: `graphify extract . --code-only` giữ graph mới |
| Đã xét 1 skill khác (browsermcp) + skill built-in trong context | user/built-in | KHÔNG | khác lĩnh vực |

### Tái hiện (chạy thật, không mock)

| # | Cách gọi | Prompt | `ket-qua.json` nguyên văn | Việc thật | `phan_quyet` |
|---|---|---|---|---|---|
| R1 | `codex exec --output-schema … -o …` qua 9router | "Is 2+2 equal to 4?" (không dặn JSON) | `Yes, 2 + 2 is equal to 4.` | — | `fail` |
| R2 | như R1, lượt 1 | khuôn prompt cố định của `codex-mode.md:96-103` (có câu "trả JSON đúng khuôn") | ```` ```json\n{\n  "xong": true\n}\n``` ```` | `hello.txt = hi`, test xanh (20.0s) | `fail` |
| R3 | như R2, lượt 2 | như R2 | giống R2 | xanh (30.9s) | `fail` |
| R4 | `codex exec` trỏ vào server giả `127.0.0.1` ghi lại body | "say hi" | — | — | — |

R4 là bằng chứng quyết định chỗ gãy: body gửi tới `/v1/responses` CÓ
`"text": {"format": {"type": "json_schema", "strict": true, "schema": {…"xong"…}, "name": "codex_output_schema"}}`.
Vậy `codex` 0.154.0 gửi schema đúng cả với provider tuỳ chỉnh; schema bị mất hiệu lực ở phía sau
(router 9router hoặc model Gemini) — lỗi KHÔNG nằm ở lệnh ta dựng.

Codex còn in cảnh báo `Model metadata for ag/gemini-3.8-flash-medium not found. Defaulting to fallback metadata`.

### Gốc lỗi trong code

1. `doc_ket_qua` (`scripts/tdq_codex.py:446-459`) chỉ chấp nhận chuỗi `json.loads` được ngay → JSON bọc
   rào markdown ```` ```json ```` bị coi như JSON hỏng → `None` → `fail`. Đây là ca R2/R3, tức ca của
   luồng thật: mọi lượt `codex implement` với model này đều bị chấm `fail`.
2. **Lỗi ẩn phát hiện thêm:** `phan_quyet` (`:462-479`) chỉ kiểm khoá `xong` CÓ MẶT, không kiểm GIÁ
   TRỊ → `{"xong": false}` bị chấm `xong`. Test hiện có (`tests/test_codex_run.py:107-151`) không có ca này.
   Mâu thuẫn trực tiếp với `codex-mode.md:102` ("khoá `xong` là true/false").

### Tầm ảnh hưởng

- `phan_quyet`: 1 nơi gọi trong `scripts` (`_cli_run`) + 6 tham chiếu test. `doc_ket_qua`: 1 nơi gọi + 3 tham chiếu test (LSP `find_references`).
- Hạ nguồn: `scripts/tdq_bench.py:455-473` chỉ đếm dòng log có trạng thái `xong` làm mẫu thời gian →
  hiện nay mọi lượt thật bị loại khỏi số đo; sửa xong thì lượt `{"xong": false}` cũng phải KHÔNG được đếm.
- Luật: `skills/tdq-build/references/codex-mode.md:105-110` mô tả khuôn kết quả; sửa cách đọc thì đoạn này phải sửa cùng, rồi sinh lại 3 bundle.
- Lumen trả kết quả lạc đề (index đang cập nhật) → tìm theo tên chính xác bằng grep + LSP.

### Research (chi tiết: `docs/tdq/research/2026-09-14-1252-run-cham-fail-sai-schema.md`)

Đã xác nhận bằng mã nguồn:
1. `codex` gửi schema trong body request (`text.format`, `strict: true`) cho MỌI provider, không lọc theo model (codex-rs `codex-api/src/common.rs`, `core/src/client.rs`) — khớp R4.
2. `codex` KHÔNG kiểm đầu ra theo schema: `-o` ghi nguyên văn tin cuối của agent, sai khuôn vẫn exit 0 (`exec/src/event_processor.rs`; issue openai/codex #38545, #15451). → Kiểm khuôn là việc của wrapper ta, không trông vào codex.
3. 9router (github.com/decolua/9router) với tiền tố `ag/` (Antigravity → Gemini) không đọc `text.format`; cấu hình sinh của Gemini chỉ mang temperature/topP/topK/max tokens, không có `responseSchema`. → Schema rơi ở router; lỗi không sửa được từ phía ta ngoài việc đọc đầu ra cho đúng.
4. OpenAI strict mode thật đòi `additionalProperties: false` cho object; thiếu thì trả lỗi 400 rõ ràng. Schema của ta đang thiếu → nếu đổi sang model OpenAI thật, mọi lượt sẽ lỗi 400.

Chưa xác nhận: đọc codex ở nhánh main chứ không đúng tag 0.154.0; chưa bắt request thật của 9router
(R4 chỉ bắt đoạn codex → server giả). Không ảnh hưởng hướng sửa vì hướng sửa nằm ở phía đọc kết quả.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research thêm | BỎ | gốc lỗi đã có 4 lần chạy thật + mã nguồn codex/9router; câu hỏi còn lại là chọn hướng, không phải tìm hiểu |
| Spec → plan | CÓ | khung bất biến |
| Review spec/plan bằng agent `tdq-reviewer` | CÓ | đụng nguyên tắc "không biết thì phải FAIL" — cần mắt thứ hai soi ca biên |
| Chia subagent | BỎ | ≈3 file cùng một vùng (`tdq_codex.py`, `test_codex_run.py`, `codex-mode.md`), tuần tự |
| QC độc lập bằng agent `tdq-qc-tester` | CÓ | kèm một lượt `run` thật với model hiện tại phải ra `xong` |
| Report | CÓ | khung bất biến |

Luồng tính năng: (1) đọc `ket-qua.json` · (2) phán quyết theo giá trị `xong` · (3) khuôn schema gửi đi · (4) luật trong `codex-mode.md` + bundle.

## Hỏi đáp

Người dùng trả lời nguyên văn: "1a 2a 3a 4a" (2026-09-14).

| # | Câu hỏi | Chọn | Hệ quả |
|---|---|---|---|
| 1 | Đọc `ket-qua.json` thế nào | A | nhận JSON trần HOẶC đúng một rào code bao trọn cả file (sau strip); văn thường / JSON lẫn giữa chữ → `fail`; khuôn prompt cố định thêm câu "không bọc trong rào code" |
| 2 | `{"xong": false}` | A | chỉ `xong is True` (boolean thật) mới `xong`; `false`, `"true"`, `1` → `fail` |
| 3 | `additionalProperties: false` | A | thêm vào schema ghi ra `schema.json` |
| 4 | Lý do riêng khi sai khuôn | A | `trang_thai` giữ `fail`; dòng log lượt thêm `ly_do=<mã>` ở CUỐI dòng, `tdq_bench` vẫn parse được |

### Kiểm cổng

- Phạm vi chốt: `doc_ket_qua`, `phan_quyet`, schema trong `_cli_run`, `dong_log_luot`, khuôn prompt + đoạn luật `codex-mode.md`, bundle; không đụng `dung_lenh`, `hau_kiem`, `tdq_bench` (chỉ kiểm tương thích).
- Không cần tải/cài model hay gói nào; dùng Codex + model đã được đồng ý sẵn.
- QC: unit test red→green cho từng ca đọc/phán quyết/log; test `tdq_bench` parse dòng log mới; một lượt `run` thật với `ag/gemini-3.8-flash-medium` phải ra `xong`, một lượt thật cố ý sai (việc không làm được) phải ra `fail`.
