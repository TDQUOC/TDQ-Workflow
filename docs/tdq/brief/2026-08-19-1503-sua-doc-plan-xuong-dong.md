# Brief — sửa doc_plan() mất sub-bullet khi mô tả task xuống dòng

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

Yêu cầu user: "okay mở request làm A đi".

A là việc tôi đề xuất ở turn trước, nguyên văn: sửa nợ kỹ thuật
`tdq_team.py doc_plan()` — mô tả task xuống dòng làm mất `Chạm:`/`Cần:`, khiến
`tdq_bench.py mo-phong` đọc sai gần hết plan (request trước ra "1/19 task khai
`Cần:`" trong khi thật là 15/19).

### Cách hiểu đầu tiên

Mục tiêu: bộ đọc plan phải giữ đúng mọi sub-bullet của task, kể cả khi dòng mô tả
task bị ngắt xuống dòng thứ hai. Khuôn plan hiện tại KHÔNG cấm xuống dòng; luật
lint R5 (câu ≤ 40 từ) còn đẩy người viết ngắt dòng. Vậy lỗi nằm ở parser.

Phạm vi đoán: `scripts/tdq_team.py` (hàm `doc_plan`) + test cho nó. Có thể phải
đồng bộ sang `portable_claude/` và `portable_codex/` qua `build_portable.py`.

### Bằng chứng tái hiện

File thử `<scratchpad>/plan-tai-hien.md`: T1.1 có mô tả 2 dòng, T1.2 mô tả 1 dòng.
Kết quả chạy `tdq_team.doc_plan`:

```
T1.1 | vùng file: [] | text: ['(e10m) Việc gì đó rất dài nên mô tả phải xuống dòng thứ hai']
T1.2 | vùng file: ['scripts/b.py'] | text: ['(e5m) Việc một dòng — Test: `pytest -q` xanh', 'Chạm: `scripts/b.py`', 'Cần: T1.1']
phụ thuộc: {'T1.1': set(), 'T1.2': {'T1.1'}}
```

T1.1 mất sạch `Chạm:` và `Cần:`; T1.2 giữ đủ.

### Gốc lỗi

`scripts/tdq_team.py:124-158`, vòng lặp trong `doc_plan`. Dòng nối tiếp của mô tả
là dòng có thụt lề nhưng KHÔNG bắt đầu bằng `- `, nên rơi vào nhánh cuối
`else: hien_tai = None`. Task bị đóng sớm, mọi sub-bullet sau đó bị bỏ.

### Ảnh hưởng

- `tdq_bench.py mo-phong` gọi đúng `doc_plan` này (`scripts/tdq_bench.py:131`).
- Mất `Cần:` → đồ thị phụ thuộc thưa giả → mô phỏng tưởng chạy song song được nhiều.
- Mất `Chạm:` → `dem_cap_chong` (`scripts/tdq_bench.py:139`) không thấy hai task
  dùng chung file. Đây là rủi ro thật: khuyến nghị mode `đội` cho hai task cùng
  sửa một file.

### Đính chính mức ảnh hưởng (đo lại 2026-08-19 15:15)

Câu "đọc sai gần hết plan (1/19 task khai `Cần:`)" KHÔNG tái hiện được. Chạy
`doc_plan` trên toàn bộ `docs/tdq/plan/*.md`: 1245 task, không mất dòng
`Chạm:`/`Cần:` nào. Riêng plan hướng B đọc ra 16/20 task có `Cần:`, đúng bằng số
dòng trong file. Con số 1/19 ở turn trước không có bằng chứng lưu lại, tôi rút.

Mức ảnh hưởng thật: đây là lỗi TIỀM ẨN. Người viết plan hiện đang viết mô tả task
trên một dòng dài duy nhất, nên chưa dính. Không có luật nào bắt phải thế; lint R5
đếm từ trong câu chứ không đếm ký tự trong dòng. Ai ngắt dòng cho dễ đọc là mất dữ
liệu, im lặng, không cảnh báo. Các plan cũ có 496 dòng nối tiếp thụt lề — chúng đóng
task sớm thật, chỉ là các plan đó chưa dùng `Chạm:`/`Cần:` nên chưa mất gì.

### Đính chính lần hai (15:41) — phép đo trên SAI

Phép đo "0 dòng bị mất" ở trên dùng regex thiếu cờ `re.M`, nên `^` chỉ khớp đầu chuỗi
và đếm ra 0 ở mọi file. Đo lại đúng cách: **60 dòng `Chạm:`/`Cần:` bị nuốt trên 10 file
plan**. Lỗi có thật và đang cắn, không phải tiềm ẩn. Chi tiết trong plan mục `## QC`.

### Chỗ chưa rõ

- Có nên chấp nhận dòng nối tiếp KHÔNG thụt lề không.
- Có cần cảnh báo (lint) khi plan có task mô tả nhiều dòng không, hay chỉ sửa parser.

## Hiểu & kiến thức

## Hỏi đáp
