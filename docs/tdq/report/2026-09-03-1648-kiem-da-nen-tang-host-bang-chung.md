# BẰNG CHỨNG — Kiểm đa nền tảng host
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Output nguyên văn của các lần chạy thật trên macOS. Đây là lớp bằng chứng `giả lập`: nó tái
hiện đúng cơ chế hỏng, nhưng KHÔNG thay được một lần chạy trên máy Linux/Windows thật.

## GL1 — Chạy đúng `command` của hook khi PATH không có `python3`

Lệnh chạy (lấy nguyên văn `command` đầu tiên trong `hooks/hooks.json`):

```
env -i PATH=<thư mục rỗng> CLAUDE_PLUGIN_ROOT="$PWD" /bin/sh -c \
  'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/session_start.py"'
```

Kết quả:

```
/bin/sh: python3: command not found
```

Đây đúng là thứ PowerShell thuần sẽ gặp, chỉ khác câu chữ. Hook không chạy, và host không có
cách nào biết là nó đã không chạy.

## GL2 — In tiếng Việt ra pipe khi code page không phải UTF-8

```
echo '{}' | env PYTHONIOENCODING=cp1252 python3 -c "print('Cổng chặn: nhánh chưa phân công')"
```

```
UnicodeEncodeError: 'charmap' codec can't encode character 'ổ' in position 1:
character maps to <undefined>
```

## GL3 — Chạy THẬT hook `session_start.py` với cùng code page

```
echo '{"session_id":"x","cwd":"<repo>"}' | env PYTHONIOENCODING=cp1252 python3 hooks/scripts/session_start.py
```

```
UnicodeEncodeError: 'charmap' codec can't encode character '✓' in position 76:
character maps to <undefined>
```

Đáng chú ý: ký tự làm vỡ ở đây là `✓` (U+2713), không phải dấu tiếng Việt. Nghĩa là ngay cả khi
người dùng đặt locale tiếng Việt (cp1258), hook vẫn có thể chết vì các ký tự trang trí.

## P2 — Cảnh báo "bundle dựng ở máy khác" không bao giờ nổ

```
python3 scripts/tdq_checkportable.py check --root antigravity_portable
```

```
NOTE     hooks.json still holds an unexpanded `~` — agy needs an absolute command
CLEAN    86 file(s) match the manifest
```

Trong khi đó, đếm thật trên chính file đó:

```
so command: 2
command co ~: 0
python3 /Users/truongdinhquoc/.gemini/config/plugins/tdq-workflow/hooks/scripts/agy_pretooluse_gate.py
```

Hai dữ kiện này cạnh nhau là toàn bộ lỗi P2: **không `command` nào còn `~`** (dấu `~` chỉ nằm
trong chuỗi mô tả của file), nhưng điều kiện `if "~" in noi_dung` quét cả file nên luôn đúng →
nhánh `elif` phát hiện "bundle dựng dưới thư mục nhà của người khác" không bao giờ chạy tới.
Dòng `command` in ra cũng là bằng chứng của P3: thư mục nhà của máy dựng bị nướng cứng.
