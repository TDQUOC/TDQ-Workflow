# LỆNH KIỂM — bạn tự chạy trên máy Linux và máy Windows
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Báo cáo phát hiện: `2026-09-03-1648-kiem-da-nen-tang-host-tuong-thich.md`

Tôi không có máy Linux/Windows nên không chạy được những lệnh này. Mỗi lệnh có mã `L#`, và hai
dòng nói rõ **đạt là thấy gì** / **hỏng là thấy gì** — bạn chỉ cần dán kết quả về, không cần
tự phán đoán. Nhóm Windows viết bằng PowerShell thuần: không lệnh nào cần cài thêm gì.

## Nhóm Linux

**L1 — Python có sẵn tên lệnh `python3` không.**
```
command -v python3 && python3 -V
```
- Đạt: in ra một đường dẫn và một số phiên bản 3.x.
- Hỏng: không in gì → mọi hook sẽ chết im lặng, giống hệt bệnh P1 của Windows.

**L2 — Dựng lại bundle tại chính máy đó rồi kiểm.**
```
python3 scripts/build_portable.py && python3 scripts/tdq_checkportable.py check --root antigravity_portable
```
- Đạt: dòng cuối là `CLEAN <n> file(s) match the manifest`.
- Hỏng: có dòng `MISSING` / `DIFF`, hoặc lệnh dựng ném traceback.

**L3 — Hook chạy thật và trả JSON hợp lệ.**
```
echo '{"session_id":"x","cwd":"'$PWD'"}' | python3 hooks/scripts/session_start.py; echo "exit=$?"
```
- Đạt: `exit=0` và phần in ra đọc được, có tiếng Việt hiển thị đúng dấu.
- Hỏng: `exit` khác 0, hoặc traceback, hoặc chữ tiếng Việt hiện thành ký tự lạ.

## Nhóm Windows (PowerShell thuần)

**L4 — Tên lệnh `python3` có phân giải được không.** Đây là lệnh quan trọng nhất, kiểm P1.
```
Get-Command python3 -ErrorAction SilentlyContinue; Get-Command python -ErrorAction SilentlyContinue; Get-Command py -ErrorAction SilentlyContinue
```
- Đạt: dòng cho `python3` có `CommandType` là `Application` và `Source` trỏ vào một file
  `python.exe` thật.
- Hỏng: không có dòng nào cho `python3`, hoặc `Source` trỏ vào
  `...\WindowsApps\python3.exe` — đó là stub của Microsoft Store, nó mở cửa hàng ứng dụng chứ
  không chạy Python. Cả hai ca đều xác nhận P1 là lỗi thật trên máy bạn.

**L5 — Python in tiếng Việt ra pipe có vỡ không.** Kiểm C1.
```
python -c "import sys; print(sys.stdout.encoding); print('Cổng chặn ✓')" | Out-String
```
- Đạt: dòng đầu in `utf-8` và dòng sau hiện đúng `Cổng chặn ✓`.
- Hỏng: dòng đầu in `cp1252`/`cp1258`/`cp437`, hoặc lệnh ném `UnicodeEncodeError` — khi đó C1
  chuyển từ "chưa chốt" thành phát hiện thật, và 18 chỗ `subprocess` thiếu `encoding=` phải sửa.

**L6 — Hook Codex nhận JSON qua stdin có nguyên vẹn không.** Kiểm C3.
```
'{"cwd":"C:\\repo","tool_name":"Edit"}' | python hooks/scripts/edit_gate.py; "exit=$LASTEXITCODE"
```
- Đạt: `exit=0` (hoặc mã chặn có chủ ý của hook) và không traceback.
- Hỏng: `JSONDecodeError`, hoặc thông báo cho thấy dấu nháy đã bị nuốt → lỗi truyền JSON của
  Codex trên Windows native có ảnh hưởng tới TDQ.

**L7 — agy tìm plugin ở thư mục nào.** Kiểm C2 — chạy trên máy CÓ cài agy, hệ nào cũng được.
```
Get-ChildItem -Recurse -Filter hooks.json "$HOME\.gemini" | Select-Object FullName
```
- Đạt: đường dẫn in ra khớp với `~/.gemini/config/plugins/<tên>/hooks.json` mà repo đang dùng.
- Hỏng: đường dẫn nằm ở `~/.gemini/antigravity-cli/plugins/...` → tài liệu công khai đúng và
  `build_portable.py` đang ghi sai chỗ.

**L8 — Dựng lại bundle ngay trên máy Windows.** Kiểm P3.
```
python scripts\build_portable.py; python scripts\tdq_checkportable.py check --root antigravity_portable
```
- Đạt: `CLEAN`, và mở `antigravity_portable\hooks.json` thấy `command` trỏ vào
  `C:\Users\<bạn>\...` chứ không phải `/Users/truongdinhquoc/...`.
- Hỏng: vẫn thấy đường dẫn `/Users/truongdinhquoc/...` → bundle đang là bản copy chứ chưa dựng
  lại, đúng bệnh P3 mà cổng gác P2 không cảnh báo được.
