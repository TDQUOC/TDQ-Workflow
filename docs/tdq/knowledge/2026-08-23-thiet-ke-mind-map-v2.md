# THIẾT KẾ — lớp sơ đồ giải thuật (mind-map v2) cho tdq-workflow

Ngày: 2026-08-23 · Spec: ../spec/2026-08-23-1341-build-mind-map-v2.md · Nguồn ý tưởng:
2026-08-23-diagram-truoc-khi-code.md, mục `Bản sửa đổi v2`
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Tài liệu này là ĐỀ XUẤT. Không một dòng nào trong `scripts/`, `hooks/`, `skills/` bị sửa ở
request này. Mục đích: request build sau đọc xong là làm được ngay, không phải quyết định lại.

## Mục lục

- 1. Công cụ `scripts/tdq_mindmap.py`
- 2. Khuôn file sơ đồ
- 3. Phase `diagram` và gate `diagram_approved`
- 4. Chặn phase `qc` khi sơ đồ lệch
- 5. Luật khuôn trong `scripts/doc_lint.py`
- 6. Skill `tdq-diagram` và khối trình bày
- Bàn giao — bảng việc cho request build sau

## 1. Công cụ `scripts/tdq_mindmap.py`

File mới, thuần stdlib, không thư viện ngoài, không gọi mạng. Chỉ ĐỌC `docs/tdq/state.json`,
không bao giờ ghi — quyền ghi state thuộc riêng `scripts/tdq_state.py`.

### Lệnh `sinh`

- Cú pháp: `python3 scripts/tdq_mindmap.py sinh <slug>`
- Đối số: `slug` là slug của request đang mở.
- Việc: tạo `docs/tdq/mind-map/<slug>.md` từ khuôn rỗng ở mục 6, có sẵn tiêu đề và một bước mẫu.
- Mã thoát: `0` tạo xong · `1` file đã tồn tại · `2` slug sai khuôn.

### Lệnh `kiem`

- Cú pháp: `python3 scripts/tdq_mindmap.py kiem <đường-dẫn.md>`
- Đối số: đường dẫn file sơ đồ. Bỏ trống thì lấy sơ đồ của request đang mở trong state.
- Việc: kiểm file có đúng khuôn ở mục 2 hay không, in từng dòng vi phạm kèm số dòng và mã luật.
- Mã thoát: `0` sạch · `1` có vi phạm khuôn · `2` không đọc được file.

### Lệnh `doi-chieu`

- Cú pháp: `python3 scripts/tdq_mindmap.py doi-chieu <đường-dẫn.md> [--graph graphify-out/graph.json]`
- Đối số: đường dẫn file sơ đồ; `--graph` trỏ tới đồ thị, mặc định `graphify-out/graph.json`.
- Việc: đối chiếu từng cặp `file::hàm` trong sơ đồ với đồ thị, in bảng ba cột bước, cặp, trạng thái.
- Mã thoát: `0` mọi cặp khớp · `1` có cặp lệch · `3` không đọc được đồ thị.

### Lệnh `xem`

- Cú pháp: `python3 scripts/tdq_mindmap.py xem <đường-dẫn.md> [--ra <đường-dẫn.html>]`
- Đối số: đường dẫn file sơ đồ; `--ra` là nơi ghi HTML, mặc định cùng tên đổi đuôi.
- Việc: sinh một trang HTML tự chứa, không tài nguyên ngoài, mỗi bước một hàng, nhánh lỗi in lệch.
- Mã thoát: `0` ghi xong · `1` sơ đồ sai khuôn nên không dựng được · `2` không ghi được file.

### Thuật toán của `doi-chieu`

Nguồn dữ liệu là `graphify-out/graph.json`, đọc bằng `json.load`, không cần LSP và không cần
mạng. Repo này hiện có 1171 node, trong đó 673 node là hàm.

Mỗi node hàm mang ba trường dùng được: `label` là tên hàm, `source_file` là đường dẫn file tính
từ gốc repo, `source_location` là số dòng dạng `L87`. Node nào thiếu `source_location` thì không
phải hàm, bỏ qua khi dựng bảng tra.

Các bước:

1. Đọc `graph.json`, duyệt `nodes`, giữ node có cả `source_file` lẫn `source_location`.
2. Dựng `dict` khoá là cặp `(source_file, label)`, giá trị là `source_location`.
3. Đọc sơ đồ, tách mỗi dòng bước lấy phần trong ngoặc đơn cuối dòng.
4. Tra từng cặp vào `dict`, chấm một trong ba trạng thái.

Ba trạng thái kết quả:

| Trạng thái | Điều kiện | Ý nghĩa |
|---|---|---|
| khớp | cặp có trong bảng tra | bước này trỏ đúng một hàm đang tồn tại |
| lệch | dòng có cặp nhưng tra không ra | hàm đã đổi tên, đổi chỗ, hoặc bị xoá |
| chưa có | dòng ghi dấu `(?)` | hàm chưa viết, hợp lệ lúc duyệt, phải hết trước phase `qc` |

Đồ thị cũ hơn code là rủi ro thật. Vì vậy `doi-chieu` đọc `built_at_commit` trong `graph.json`,
so với `HEAD`, và in một dòng cảnh báo khi hai giá trị khác nhau. Nó không tự chạy lại graphify.

## 2. Khuôn file sơ đồ

Một sơ đồ là một file `docs/tdq/mind-map/<slug>.md`, viết tay, và là nguồn sự thật duy nhất.
Bản `.json` và bản `.html` đều sinh ra từ nó, không ai chép tay.

Bảy luật dưới đây là toàn bộ khuôn. Mỗi luật có mã, để `kiem` in ra được và để người đọc tra lại.

| Mã | Luật | Bắt lỗi có thật nào |
|---|---|---|
| L1 | Dòng đầu file là `# <tên nghiệp vụ>`, đúng một dòng | sơ đồ không tên thì không tra được nó tả việc gì |
| L2 | Mỗi bước một dòng, mở đầu bằng `B<số>` rồi tới ` · ` | bước gộp nhiều việc vào một dòng thì không đối chiếu được với hàm |
| L3 | Số bước tăng dần từ 1, không nhảy cóc, không trùng | số trùng làm người duyệt và máy hiểu khác nhau về thứ tự |
| L4 | Nhánh lỗi ghi `B<số>!`, đặt ngay dưới bước nó chặn | quên nhánh lỗi là lỗi phổ biến nhất, và là thứ user muốn duyệt nhất |
| L5 | Mỗi dòng kết thúc bằng đúng một cặp `(file::hàm)` hoặc `(?)` | hai cặp trên một dòng nghĩa là bước còn to, phải tách thành hai dòng |
| L6 | Phần mô tả giữa `·` và ngoặc đơn viết bằng lời nghiệp vụ, không tên hàm | mô tả bằng tên hàm thì sơ đồ chỉ là bản chép lại của code |
| L7 | File có ít nhất một dòng nhánh lỗi | sơ đồ chỉ có đường thành công là sơ đồ chưa nghĩ tới lúc hỏng |

Ví dụ một khối hợp lệ, trích từ file mẫu `docs/tdq/mind-map/vi-du-login.md`:

```
# Đăng nhập
B1 · Nhập email và mật khẩu (src/pages/login.tsx::LoginForm.onSubmit)
B2 · Kiểm tra tại chỗ trước khi gửi (src/lib/validators.ts::validateCredentials)
B2! · email sai khuôn hoặc mật khẩu ngắn thì báo lỗi tại ô nhập và dừng (src/lib/form-ui.ts::showFieldError)
```

Luật L7 cố ý mềm ở chỗ này: nó đòi ít nhất một nhánh lỗi cho cả file, không đòi mỗi bước một
nhánh. Đòi chặt hơn thì người viết sẽ chế nhánh lỗi giả cho đủ số, và luật mất tác dụng.

## 3. Phase `diagram` và gate `diagram_approved`

Vị trí trong luồng: sơ đồ đứng TRƯỚC spec ở lane full, và trước mini-plan ở lane quick. Lý do:
sơ đồ là đầu vào giúp spec và plan viết đúng, nên nó phải có trước. Tầng `nhỏ` miễn hoàn toàn.

```
lane full   analyze → [diagram] → spec → plan → mode → implement → qc → report
lane quick  intake  → [diagram] → mini-plan → implement → qc
```

Ba chỗ cắm trong `scripts/tdq_state.py`, cả ba đều đã đọc và xác minh:

1. `VALID_PHASES` ở dòng 68 là một `set` phẳng. Thêm chuỗi `"diagram"` vào đó.
2. `PHASE_TABLE` mở ở dòng 884. Thêm một hàng khoá `"diagram"`, đủ sáu trường như mọi hàng khác.
3. Khối khởi tạo state quanh dòng 146 có ba cặp trường theo khuôn `<target>_approved`,
   `<target>_approved_at`, `<target>_approved_by`. Thêm bộ thứ tư cho `diagram`.

Hàng `PHASE_TABLE` đề xuất, viết đúng giọng tiếng Anh của các hàng sẵn có:

```python
"diagram": {
    "entry": "Analysis is finished (lane full) or the request has just opened (lane quick)",
    "action": "Write the business diagram, register diagram_file, present it and STOP for approval",
    "cmd": "python3 scripts/tdq_state.py approve diagram --by \"<the user's sentence verbatim>\"",
    "checklist": [
        "Run: python3 scripts/tdq_mindmap.py sinh <slug>",
        "Fill in the steps and at least one error branch, one file::function pair per line",
        "Run: python3 scripts/tdq_mindmap.py kiem docs/tdq/mind-map/<slug>.md",
        "Run: python3 scripts/tdq_state.py set diagram_file=docs/tdq/mind-map/<slug>.md",
        "Present the diagram in chat, print the approval invite, then STOP",
    ],
    "done_when": "diagram_approved = true",
    "forbidden": "Writing the spec or any plan before the diagram is approved",
},
```

Lệnh `approve` phải nhận thêm đích `diagram`. Chỗ sửa là danh sách đích hợp lệ quanh dòng 1387
và 1393, nơi đang báo lỗi `Invalid approval target: {target}`.

Gate chặn ngược: `approve spec` phải từ chối khi `diagram_approved` còn `False`. Cùng khuôn với
hàm kiểm cổng sẵn có ở dòng 856, nơi đang đọc `state.get(f"{cong}_approved")`.

## 4. Chặn phase `qc` khi sơ đồ lệch

Chỗ chặn KHÔNG nằm ở hook. `hooks/scripts/stop_gate.py` chỉ in lời nhắc, nó không giữ phase lại.
Cổng chặn thật là hàm `_chan_worktree_con_mo` ở `scripts/tdq_state.py` dòng 1524, gọi `_fail`.

Hàm mới đi kèm nó, đặt ngay dưới, cùng khuôn và cùng chỗ gọi:

```python
def _chan_so_do_con_lech(cwd):
    """Gate `qc`: a diagram still holding an unknown pair stops the phase from moving.

    A missing diagram file is NOT evidence of drift, so it never blocks: a false block
    here would teach people to route around the gate.
    """
    duong_dan = _doc_state(cwd).get("diagram_file")
    if not duong_dan or not os.path.exists(duong_dan):
        return
    lech = _cham_so_do(duong_dan)
    if not lech:
        return
    _fail(f"{len(lech)} step(s) in the diagram no longer match the code: {lech}. "
          "Check with: python3 scripts/tdq_mindmap.py doi-chieu " + duong_dan)
```

### Cửa thoát

Hai cửa, cố ý mở sẵn, vì một cổng chặn không có cửa thoát sẽ bị người ta đi vòng:

- Request không khai `diagram_file`, hoặc file đã bị xoá, thì gate không áp và trả về ngay.
  Đây đúng nguyên tắc đã viết trong docstring của hàm cũ: thiếu bằng chứng không phải là bằng
  chứng có lỗi.
- Bị chặn nhầm vì đồ thị cũ hơn code thì chạy lại `graphify extract . --code-only` rồi thử lại.
  Còn nhầm nữa thì sửa cặp `file::hàm` trong sơ đồ cho đúng, vì lúc đó sơ đồ mới là cái sai.

Dấu `(?)` được phép tồn tại lúc duyệt sơ đồ, nhưng phải hết trước `qc`. Đó là toàn bộ ý nghĩa
của cổng này: nó không bắt bạn biết trước tên hàm, nó bắt bạn quay lại điền khi đã viết xong.

## 5. Luật khuôn trong `scripts/doc_lint.py`

Luật mới tên `rule_r13`, kiểm file trong `docs/tdq/mind-map/` theo đúng bảy luật ở mục 2.

Chỗ cắm có một cái bẫy, và đây là phần quan trọng nhất của mục này. `OUTPUT_DIRS` ở dòng 448
chứa `docs/tdq`. Hàm `lint_file` ở dòng 593 tính `is_output` ở dòng 601, rồi ở dòng 602 chỉ chạy
`[rule_r8, rule_r10, rule_r11, rule_r12]` cho file output.

Nghĩa là thêm `rule_r13` vào danh sách `RULES` ở dòng 444 thì luật KHÔNG chạy, vì file sơ đồ nằm
trong `docs/tdq/`. Phải thêm vào chính nhánh `is_output` ở dòng 602.

Luật chỉ áp cho file có `docs/tdq/mind-map/` trong đường dẫn, các file output khác bỏ qua ngay
dòng đầu. Mã vi phạm in ra dùng lại đúng mã `L1` đến `L7` ở mục 2, để hai công cụ nói cùng ngôn ngữ.

## 6. Skill `tdq-diagram` và khối trình bày

Skill mới `skills/tdq-diagram/SKILL.md`, sở hữu đúng một phase là `diagram`. Nó chỉ được nhắc TÊN
LỆNH của `scripts/tdq_mindmap.py`, cấm chép nội dung script vào skill.

Hai skill sẵn có phải sửa:

- `skills/tdq-intake/SKILL.md`: cuối Part B, bước tiếp theo đổi từ `set phase=spec` sang
  `set phase=diagram`. Ở Part C, chèn bước sơ đồ vào trước mini-plan.
- `skills/tdq-spec/SKILL.md`: thêm một dòng điều kiện vào đầu, `diagram_approved = true`, giống
  cách nó đang đòi `spec_approved` ở `tdq-plan`.

Template file rỗng mà lệnh `sinh` ghi ra, đặt tại `skills/tdq-diagram/references/so-do-mau.md`:

```
# <tên nghiệp vụ>
B1 · <việc người dùng thấy, nói bằng lời nghiệp vụ> (?)
B1! · <chuyện gì xảy ra khi bước 1 hỏng> (?)
```

Khối trình bày để user duyệt, đặt tại `skills/tdq-diagram/references/khoi-trinh-bay.md`:

```
Tôi đã vẽ xong sơ đồ giải thuật cho việc này.

**Nghiệp vụ:** <một câu>.
**Số bước:** <n> bước, trong đó <k> nhánh lỗi.
**Chưa có hàm:** <số dòng còn dấu (?)> — sẽ điền khi code xong, cổng qc sẽ kiểm.

<dán nguyên nội dung file sơ đồ vào đây>

Xem đầy đủ tại: `docs/tdq/mind-map/<slug>.md`

---

**Bạn duyệt sơ đồ này chứ?**

➤ Duyệt: nhắn "duyệt sơ đồ" (duyệt xong tôi viết spec ngay) · Góp ý: nhắn trực tiếp
```

Sơ đồ dán thẳng vào chat, không bắt user mở file. Lý do: cổng này tồn tại để user đọc, mà bắt mở
file là thêm một bước ma sát ngay tại chỗ ta cần user chịu đọc kỹ nhất.

## Bàn giao — bảng việc cho request build sau

Thứ tự 2 → 3 → 1 → 4 do user chốt: công cụ và luật trước, state machine sau cùng. Lý do là state
machine chạm vào mọi request đang có, nên nó phải là thứ cuối cùng đổi, khi các phần dưới đã chạy.

| Thứ tự | Việc | File đích | Xong khi |
|---|---|---|---|
| 1 | Viết công cụ bốn lệnh theo mục 1 | `scripts/tdq_mindmap.py` | bốn lệnh chạy được, có unit test cho `kiem` và `doi-chieu` |
| 2 | Thêm `rule_r13` vào nhánh `is_output` | `scripts/doc_lint.py` | file mẫu sai khuôn cố ý làm lint exit khác 0 |
| 3 | Thêm phase và gate | `scripts/tdq_state.py` | `approve diagram` chạy được, `approve spec` bị chặn khi chưa duyệt sơ đồ |
| 4 | Thêm hàm chặn `qc` theo mục 4 | `scripts/tdq_state.py` | sơ đồ còn dấu chưa có thì `set phase=qc` thất bại |
| 5 | Viết skill mới và sửa hai skill cũ | `skills/tdq-diagram/`, `skills/tdq-intake/`, `skills/tdq-spec/` | chạy thử một request lane quick đi hết luồng |
| 6 | Viết template và khối trình bày | `skills/tdq-diagram/references/` | lệnh `sinh` đọc được template và ghi ra file hợp khuôn |
| 7 | Lệnh `dung-nguoc` dựng khung sơ đồ từ đồ thị | `scripts/tdq_mindmap.py` | để request sau nữa, chưa làm |

Việc 7 tách riêng theo đúng câu trả lời của user. Lý do hoãn: khuôn ở mục 2 chưa chạy thật lần
nào ngoài file mẫu. Dựng ngược hàng loạt lúc này chỉ nhân bản lỗi khuôn ra hàng chục file.

Cũng theo câu trả lời của user, các tính năng đã có sẵn trong repo KHÔNG dựng sơ đồ ngược. Lớp
này chỉ áp cho request mới mở từ lúc build xong trở đi.

### Ba cái giá phải trả, nói thẳng

- Lane quick từ một chặng dừng thành hai. Đó là giá của việc user được duyệt sơ đồ ở mọi lane.
- Mọi request dài thêm một vòng chờ duyệt. Đổi lại spec và plan có đầu vào chính xác hơn.
- Bốn hạng mục đầu chạm vào lõi state. Vì vậy thứ tự build đặt state machine ở gần cuối.
