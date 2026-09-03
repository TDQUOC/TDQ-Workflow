# Báo cáo — Thêm pyrightconfig.json và đo lại LSP

**Ngày:** 2026-09-03 · Lane: quick · Plan: ../plan/2026-09-03-0017-them-pyrightconfig-do-lai.md
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Báo cáo `2026-09-02-2057` kết luận "bỏ LSP mất 0 %" nhưng đo lúc LSP đang thiếu cấu hình.
Request này thêm cấu hình thật rồi đo lại **cùng câu hỏi, cùng ground truth**.

## 1. Thay đổi đã làm

Thêm `pyrightconfig.json` ở gốc repo — file duy nhất của request này:

```json
{
  "include": ["scripts", "hooks", "tests"],
  "exclude": ["**/__pycache__", "portable_claude", "portable_codex", "antigravity_portable"],
  "extraPaths": ["scripts", "hooks/scripts"]
}
```

`extraPaths` khai `scripts/` là gốc import nên pyright resolve được `import tdq_state` từ
`hooks/` và `tests/`. `exclude` loại 3 bundle portable — đây là phần **thêm** so với bản thử
tạm ở request 2255, để kết quả tìm kiếm không lẫn bản sao.

Server khởi động lại bằng `start_lsp` với `root_dir` là gốc repo.

## 2. Ground truth — dựng lại bằng AST, đầy đủ hơn lần trước

Ground truth cũ ghi "27 lệnh gọi ở 12 file". Lần này dựng lại và tách rõ hai dạng gọi:

- dạng thuộc tính `tdq_state.load(...)`: **23 lệnh gọi ở 10 file** (`scripts/tdq_checkstatus.py`,
  `scripts/tdq_team.py`, `scripts/tdq_timing.py`, `tests/helper.py`, `tests/test_check_status.py`,
  `tests/test_compliance_protocol.py`, `tests/test_quick_qc.py`, `tests/test_state.py`,
  `tests/test_state_file.py`, `tests/test_token_budget.py`)
- dạng tên trần `load(cwd)` sau `from tdq_state import load`: **5 file hook**
  (`stop_gate.py`, `prompt_context.py`, `edit_gate.py`, `agy_stop_gate.py`, `session_start.py`)

Tổng: **15 file gọi ngoài `tdq_state.py`**. Con số 12 của lần trước là bản đếm hẹp hơn; số
15 này mới là mốc dùng để chấm điểm dưới đây.

## 3. Kết quả đo — trước và sau

### 3.1 Truy vấn quan hệ — ai gọi `tdq_state.load`

| | Trước (không cấu hình) | Sau (có cấu hình) |
|---|---|---|
| `find_callers` trên `scripts/tdq_state.py:303` | 13 caller, **không caller nào ngoài file** | 35 ký hiệu / 34 cạnh gọi |
| Độ phủ file | **1/15 (7 %)** | **15/15 (100 %)** |

Độ phủ 15/15 được kiểm bằng cách ánh xạ ngược từng tên hàm trong output về file bằng AST —
`find_callers` chỉ in namespace (`TDQWorkflow/scripts.thu_thap`), không in đường dẫn. Đối chiếu:
`thu_thap`→`tdq_checkstatus.py`, `_boi_canh`+`canh_bao_lach_luat`→`tdq_team.py`,
`main`→`tdq_timing.py`, `hooks/scripts.main` ×5 → 5 file hook, còn lại khớp đủ 7 file test.

**Hai giả thuyết ở brief đều sai.** Brief ngờ `tdq_team.py`, `tdq_timing.py`,
`tdq_checkstatus.py` bị thiếu vì output cắt ở 35 ký hiệu, hoặc vì gọi dạng thuộc tính nên xếp
hạng khác. Thực tế cả ba **đều có mặt** ở lần đo 2255 lẫn lần này — tôi đọc sót vì output chỉ
in tên hàm chứ không in file. Đây là lỗi đọc kết quả của tôi, không phải giới hạn của công cụ.
Con số 35 cũng không phải trần cắt: `find_references` cùng lúc trả **45** ký hiệu.

### 3.2 Truy vấn tên chính xác — `bac6_hook_xung_dot` (ground truth 6 vị trí)

| | Trước | Sau |
|---|---|---|
| `find_symbol` | 1 kết quả, bản thật xếp **thứ 3** sau 2 bản portable | 1 kết quả, **đúng bản thật**, không còn bản sao portable · 3,14 s |
| `find_references` | không đo | **6/6 vị trí** (2 trong `scripts/`, 4 trong `tests/`) · 6,26 s |

Hai điều rút ra: `exclude` đã dọn sạch nhiễu portable; và `find_symbol` chỉ trả **định nghĩa**,
muốn đủ 6 vị trí phải dùng `find_references` — so sánh cũ "LSP 1/6" là so nhầm công cụ.

### 3.3 Truy vấn khái niệm mơ hồ — từ khoá `approve`

| | Trước | Sau |
|---|---|---|
| Số kết quả | 78 | 62 |
| Hạng của đích `_cli_approve` | **28** | **13** · 3,83 s |

Khá hơn nhưng vẫn kém: LSP là chỉ mục **tên**, không hiểu khái niệm. Với câu hỏi dạng "chỗ nào
ghi dấu thời điểm duyệt", nó vẫn không phải lớp nên dùng đầu tiên.

## 4. Kết luận

1. **Con số "bỏ LSP mất 0 %" của báo cáo 2057 không còn đứng vững.** Ở truy vấn quan hệ — đúng
   sở trường của LSP — độ phủ đi từ 7 % lên **100 %** chỉ nhờ một file cấu hình. Trước đó grep
   thắng 100 % vs 7 %; giờ hai lớp hoà ở độ phủ, và LSP hơn hẳn về độ chính xác: grep có 6 file
   dương tính giả (precision 67 %), LSP không có cái nào.
2. **Chỗ LSP vẫn thua**: truy vấn khái niệm mơ hồ (hạng 13/62) và tốc độ (3–6 s so với ~0,1 s
   của grep chạy trực tiếp).
3. **Nguyên nhân thật của "1/12" ở báo cáo 2057 là thiếu cấu hình, không phải LSP yếu.** Một
   phần sai số nữa đến từ cách đọc output — xem mục 3.1.
4. **Thang `tdq_lsp.py kiem` vẫn báo 6/6 ĐẠT trong cả hai trạng thái**, trước và sau khi thêm
   cấu hình. Nó không nhìn thấy khác biệt 7 % ↔ 100 %. Khuyến nghị thêm một bậc kiểm bằng hiệu
   ứng thật vẫn còn nguyên giá trị — ngoài phạm vi request này.

## 5. Việc để lại cho request sau

Theo lựa chọn **2c** của user, request này **không sửa luật**. Số đo mới cho thấy nội dung sửa
luật sẽ khác dự đoán ban đầu: LSP không đáng bị hạ xuống "gọi khi cần" ở truy vấn quan hệ, mà
nên bỏ ràng buộc "bắt buộc gọi song song ở **mọi** truy vấn ký hiệu" và phân theo loại truy vấn:
quan hệ/đổi tên → LSP trước; tên chính xác → grep trước; khái niệm mơ hồ → lumen trước.
