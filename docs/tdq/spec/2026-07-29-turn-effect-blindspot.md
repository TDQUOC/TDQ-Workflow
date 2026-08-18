# SPEC — Vá điểm mù của verify-by-effect (sổ turn chỉ thấy Edit/Write)

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->
<!-- doc-lint: allow R8 -->  <!-- spec viết trước 0.3.3, chưa có mục 3b -->

Ngày: 2026-07-29 · Request: `docs/tdq/requests/2026-07-29-turn-effect-blindspot.md` · Trạng thái: **CHỜ DUYỆT**

## 1. Bối cảnh & triệu chứng

Cuối turn implement 0.3.0, Stop hook chặn với:

```
[TDQ:LOG] Turn này đổi repo (…) nhưng docs/workinglog/2026-07-29.md chưa được append.
```

trong khi working log **đã** được append thật. Phải append lại bằng công cụ Edit thì
Stop mới cho qua. Đây là chặn oan trên chính bộ 0.3.0, xảy ra ngay lần dùng thật đầu tiên.

## 2. Nguyên nhân gốc

Sổ turn `docs/tdq/.tdq-turn.jsonl` chỉ nhận dòng `observe` từ hai nguồn:

| Nguồn | Ghi được gì |
|---|---|
| `edit_gate.py` (PreToolUse của Edit/Write/MultiEdit/NotebookEdit) | `edit`, `log_written` |
| `bash_gate.py` (PreToolUse của Bash) | `state_cli`, `next_run` |

Nghĩa là **mọi thay đổi file thực hiện qua shell đều vô hình** với sổ turn. Hệ quả hai chiều:

- **Chặn oan (false positive)** — đã gặp: append log bằng `cat >>` / `tee` / `printf >>` /
  `sed -i` / `python3 - <<EOF` → không có `log_written` → `stop_gate` chặn dù đã ghi log đúng.
- **Bỏ lọt (false negative)** — chưa gặp nhưng cùng gốc: sửa repo hoàn toàn bằng shell
  (`sed -i`, `mv`, `git apply`, script sinh file, subagent chạy lệnh) → không có `edit` →
  `stop_gate` **không** chặn dù turn đổi repo mà chưa ghi log. Gate im lặng đúng lúc cần nói.

Gốc chung: hook đang suy ra "có hiệu ứng gì" từ **tên tool được gọi**, chứ không nhìn
**hiệu ứng thật trên đĩa**. Trái đúng tinh thần verify-by-effect mà 0.3.0 đặt ra.

## 3. Các phương án đã cân nhắc

| PA | Cách làm | Đánh giá |
|---|---|---|
| A | `bash_gate` bắt regex lệnh ghi vào `docs/workinglog/` → `observe log_written` | Rẻ, nhưng **không bao giờ đủ**: heredoc, pipe, biến, `python3 -c`, script gọi script, alias. Đúng-sai đều bịa: `grep docs/workinglog/x.md` cũng khớp → cấp `log_written` giả, làm hỏng gate duy nhất còn hiệu lực. Chỉ vá chiều false positive, không vá chiều bỏ lọt. |
| B | Chụp trạng thái đĩa đầu turn, so lại lúc Stop | Không phụ thuộc cú pháp shell, vá **cả hai** chiều, đúng nghĩa verify-by-effect. Chi phí: 1 lần `git status --porcelain` + 1 lần `sha256` ở mỗi đầu/cuối turn. |
| C | A + B | B đã bao trọn A; thêm A chỉ thêm mặt để sai. |

**Chọn B.** `bash_gate.py` giữ nguyên, không thêm regex đoán lệnh.

## 4. Thiết kế

### S1 — Ảnh chụp đầu turn (`prompt_context.py`)

Ngay sau `turn_log_clear`, ghi đúng **một** dòng `kind="turn_start"` vào sổ turn:

```json
{"kind":"turn_start","session":"…","log_rel":"docs/workinglog/2026-07-29.md",
 "log_sha":"<sha256|null>","repo_sha":"<sha256 của git status --porcelain|null>"}
```

- `log_sha`: `sha256` của file log hôm nay; file chưa tồn tại → `null`.
- `repo_sha`: `sha256` của stdout `git -C <cwd> status --porcelain` (bao gồm cả file
  chưa track). Không phải git repo / không có `git` / timeout → `null`.
- Ghi bằng `turn_log_append` (đã nuốt lỗi I/O sẵn) nên không bao giờ làm hỏng hook.

### S2 — Đối chiếu cuối turn (`stop_gate.py`)

Đọc dòng `turn_start` của session hiện tại (nếu có nhiều thì lấy dòng **đầu**), rồi:

```
logged = có observe log_written  OR  (snapshot có  AND  sha256(log hôm nay) != log_sha)
edited = có observe edit (ngoài docs/workinglog)  OR  (snapshot có  AND  repo_sha đổi)
```

- Không có dòng `turn_start` (turn mở bằng SessionStart, sổ bị xoá, hook cũ) → rơi về
  đúng hành vi hiện tại, không hồi quy.
- `repo_sha` là `null` (repo không phải git) → chỉ chiều `logged` được vá; chiều `edited`
  giữ nguyên như 0.3.0. Ghi rõ trong `references/reminder-codes.md` là giới hạn đã biết.
- Khi chặn cần nêu tên file: ưu tiên path từ dòng `observe edit`; nếu chỉ có bằng chứng
  git thì lấy path đầu tiên trong `git status --porcelain` khác với đầu turn, cắt ≤60 ký tự.
- Ngày đổi giữa turn (turn qua nửa đêm): so **file ghi trong `log_rel` của snapshot**, không
  tính lại theo ngày hiện tại — nếu file của ngày mới xuất hiện thì `repo_sha` cũng đã đổi,
  nên bổ sung: log của **ngày hiện tại** tồn tại mà đầu turn chưa có ⇒ `logged=True`.

### S3 — Hàm dùng chung (`scripts/tdq_state.py`)

Thêm hai helper thuần stdlib, dùng được cho cả hai hook và test:

- `repo_status_digest(cwd)` → `str|None`: chạy `git -C cwd status --porcelain`
  (`timeout=2`, `stderr` nuốt); rc≠0 / `FileNotFoundError` / `TimeoutExpired` → `None`.
- `turn_snapshot(cwd)` → `dict`: gói `log_rel`, `log_sha`, `repo_sha` theo S1.

Lý do đặt ở `tdq_state.py`: hook đã import sẵn module này; tránh code trùng ở 2 hook.

### S4 — Hiệu năng & an toàn

- Thêm tối đa **2** lần gọi `git status --porcelain` mỗi turn (đầu + cuối), timeout 2 s.
- Repo lớn: `status --porcelain` là lệnh nhanh nhất trong họ status; vẫn đo thời gian
  trong QC và ghi số thật vào report.
- Không đọc nội dung file nào ngoài file log hôm nay (đọc để băm).
- Không lệnh nào ghi ra ngoài `docs/tdq/.tdq-turn.jsonl`.
- Mọi lỗi (git, I/O, decode) → coi như không có snapshot, tuyệt đối không raise.

### S5 — Ngân sách token

Không đổi: dòng `turn_start` nằm trong sổ turn (file), **không** in ra context.
`prompt_context` vẫn ≤3 dòng/240 ký tự, `stop_gate` vẫn ≤4 dòng/300 ký tự.

### S6 — Doc phải cập nhật

- `skills/tdq-conventions/references/reminder-codes.md`: mô tả lại cách `TDQ:LOG` được
  xác minh (ledger **hoặc** đĩa) + giới hạn khi không phải git repo.
- `portable/workflow/references/reminder-codes.md`: đồng bộ y hệt.
- `README.md` mục verify-by-effect: nói rõ hook nhìn hiệu ứng trên đĩa, không nhìn tên tool.
- `CHANGELOG.md`: mục `0.3.1`.

## 5. Ngoài phạm vi

- Không đụng `bash_gate.py`, không thêm regex đoán lệnh.
- Không đổi 5 mã đóng, không thêm mã mới.
- Không đổi định dạng `state.json`, không đổi `PHASE_TABLE`.
- Không thay đổi hành vi `deny` (vẫn không có `deny` ở bất kỳ hook nào).

## 6. Phạm vi test (mỗi task 1 test, red → green)

| # | Test | Kỳ vọng |
|---|---|---|
| T1 | `repo_status_digest` trong repo git sạch vs sau khi tạo file | digest đổi |
| T2 | `repo_status_digest` ở thư mục không phải git / `git` không tồn tại | `None`, không raise |
| T3 | `turn_snapshot` khi chưa có file log | `log_sha=None` |
| T4 | `prompt_context` ghi đúng 1 dòng `turn_start` sau khi clear | có dòng, đúng session |
| T5 | **Chặn oan**: snapshot → append log bằng `open(...,'a')` (mô phỏng shell) → Stop | **không** chặn |
| T6 | **Bỏ lọt**: snapshot → tạo file `src/a.py` bằng Python (không qua Edit) → Stop | chặn `[TDQ:LOG]`, reason có tên file |
| T7 | Không có dòng `turn_start` | hành vi y hệt 0.3.0 (test cũ vẫn xanh) |
| T8 | Repo không phải git + append log bằng shell | không chặn (chiều `logged` vẫn vá được) |
| T9 | Đổi repo + đã ghi log qua Edit | không chặn (không hồi quy) |
| T10 | Toàn bộ suite hiện có | 162 test cũ vẫn OK |

## 7. Definition of Done

1. `python3 -m unittest discover tests` — toàn bộ OK, số test ≥ 172.
2. `python3 scripts/doc_lint.py skills portable` — exit 0.
3. `claude plugin validate . --strict` — PASS, version `0.3.1`.
4. Smoke trên bản cài user-level, đúng kịch bản đã gây lỗi: mở turn → `cat >>` vào
   `docs/workinglog/<hôm nay>.md` → Stop **không** chặn.
5. Smoke chiều ngược: mở turn → `sed -i` sửa 1 file code, không ghi log → Stop **chặn**.
6. QC ghi bằng chứng vào `docs/tdq/qc/2026-07-29-turn-effect-blindspot.md`; report ≤50 dòng.
7. Working log 2026-07-29 có entry; `graphify extract . --code-only` đã chạy lại.

## 8. Rủi ro & giảm thiểu

| Rủi ro | Giảm thiểu |
|---|---|
| `git status` chậm trên repo rất lớn → hook trễ | timeout 2 s, quá hạn coi như `None`, đo thật trong QC |
| File bị sửa bởi tiến trình khác trong turn (formatter, watcher) → chặn oan kiểu mới | Chặn chỉ nhắc ghi log — chi phí thấp; và log vốn nên ghi khi repo đổi |
| `.gitignore` che file bị đổi → `repo_sha` không đổi | Chấp nhận: đúng ngữ nghĩa "thay đổi repo"; `observe edit` vẫn bắt được |
| Sổ turn không xoá (turn không mở bằng user prompt) → snapshot cũ | `turn_log_read` đã bỏ dòng quá 6 giờ; lấy dòng `turn_start` đầu tiên của session |
