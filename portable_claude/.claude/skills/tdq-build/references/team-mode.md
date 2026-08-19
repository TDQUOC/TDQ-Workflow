# Mode đội — leader phân công cả plan, agent con chạy song song

Soul: chất lượng > runtime > context cost · luật gốc: ../../tdq-conventions/references/soul.md

Bạn là LEADER. Agent con là ĐỘI của bạn. Mặc định là GIAO; giữ task lại cho mình
phải có cớ nằm trong bảng tra bên dưới, và cái cớ đó bị máy kiểm.

## Mục lục

- Khi nào áp dụng
- Làm gì
- Tự kiểm

## Khi nào áp dụng

Ở phase `implement`, **mọi mode**. Doctrine leader là cách TỔ CHỨC việc, không phải
một chế độ chạy: plan luôn được chia cụm, mỗi task luôn có một quyết định giao-hay-giữ
kèm lý do kiểm được.

Mode user chọn chỉ đổi ai gõ phím:
- `subagent` — task `giao` do agent con làm, mỗi task một worktree, cùng cụm chạy song song.
- `main` — leader tự làm HẾT, nhưng theo đúng thứ tự cụm của plan và vẫn ghi lý do giữ
  cho từng task. Làm nhảy cóc thứ tự cụm ở mode `main` là hỏng đúng thứ đã đo được:
  thứ tự cụm là thứ tự phụ thuộc, không phải gợi ý.

Mode đội KHÔNG có nghĩa mọi task đều phải giao. Nó có nghĩa: **task nào tách được thì
phải tách**, phần còn lại leader tự làm — như một trưởng nhóm thật, không phải một
người ôm hết việc cũng không phải một người chia bừa.

## Làm gì

### Bước 0 — phân công CẢ plan trước khi gõ dòng code đầu tiên

```
python3 scripts/tdq_team.py phan-cong
python3 scripts/tdq_team.py kiem-ke
```

`phan-cong` đọc TOÀN BỘ plan (không phải từng task một), dựng vùng file của mỗi task
từ dòng `Chạm:`, rồi ghi `docs/tdq/team/<slug>.json`. Mỗi task có đúng 4 trường:
`quyet_dinh` (giao | tu_lam) · `ly_do` · `vung_file` · `dot`.

`kiem-ke` exit khác 0 nếu có task `tu_lam` mà lý do rỗng hoặc nằm ngoài tập lý do đóng
(bảng tra ngay dưới đây là tập đó, đúng bằng hằng `LY_DO_GIU` mà lệnh đọc).
Đây là hàng rào chống lách luật. Bạn không thể lặng lẽ tự làm hết ở main rồi khai là
đã chia việc: bản đồ nằm trên đĩa. Hook `[TDQ:TEAM]` chặn tay bạn ngay khi bạn sửa một
file thuộc vùng của task đã ghi `giao` mà chưa mở nhánh.

### Bảng tra quyết định — mặc định GIAO, giữ lại phải khớp đúng một dòng

| Nhóm | Dấu hiệu nhận ra | Kiểm bằng |
|---|---|---|
| `phu-thuoc` | mô tả task nhắc mã task khác (`T1.1`) mà task đó chưa `[x]` | đọc dòng task; task được nhắc còn `[ ]`/`[~]`/`[>]` |
| `vung-khoa` | task không có dòng `Chạm:` nào → không khai được vùng file riêng | `grep -A2 'T1.1' <plan>` không thấy `Chạm:` |
| `mcp` | dòng `Dùng:` của task kết thúc bằng nhãn `(mcp)` | `grep '(mcp)' <plan>` |
| `file-luat` | vùng file chạm `skills/`, `hooks/`, `agents/`, `.claude/`, `.codex/`, `CLAUDE.md`, `AGENTS.md` | xem `vung_file` trong bản đồ |
| `hop-dong` | task dựng hợp đồng dùng chung (kiểu dữ liệu, hằng số, khuôn thông báo, sổ đăng ký) mà nhiều task sau đọc | nhiều task khác khai `Cần:` trỏ về nó |
| **mặc định: GIAO** | **không khớp 5 dòng trên** | `python3 scripts/tdq_team.py kiem-ke` exit 0 |

Năm nhóm này là tập ĐÓNG. Nghĩ ra lý do thứ sáu ("việc này nhanh hơn nếu tự làm",
"task này nhỏ quá", "giải thích cho agent con còn lâu hơn làm") = lách luật, và
`kiem-ke` sẽ đỏ.

### Vòng lặp phát đợt

```
python3 scripts/tdq_team.py cum            # đợt kế tiếp: task giao được, không đụng vùng khoá
python3 scripts/tdq_team.py mo T1.1        # nhánh + worktree riêng cho task
# → gọi agent tdq-implementer theo khuôn prompt bên dưới, MỌI task của đợt trong MỘT response
# → đánh [>] cho mọi task vừa giao trong plan (nhiều [>] là hợp lệ)
python3 scripts/tdq_team.py kiem T1.1      # dò xung đột, KHÔNG đụng repo
python3 scripts/tdq_team.py hop T1.1       # hợp vào nhánh tích hợp
# → đổi [>] thành [x] NGAY khi hợp xong
python3 scripts/tdq_team.py don            # hết đợt thì dọn worktree, rồi quay lại `cum`
```

Trong lúc chờ đợt chạy, leader làm các task `tu_lam` của cùng đợt — đó là lý do mode
này nhanh hơn `main`, không phải vì agent con chạy nhanh hơn bạn.

Dấu tick: `[ ]` chưa làm · `[~]` LEADER đang tự làm (nhiều nhất MỘT) · `[>]` đã giao
agent con (được nhiều) · `[x]` xong và đã hợp về.

### Khuôn prompt giao việc — đủ 9 trường, không thiếu trường nào

```
TASK: T1.1 — <chép nguyên văn dòng task trong plan, kể cả phần Test:>
CỤM: đợt 2/5 · chạy song song với T1.2, T1.4
BASE: tdq/<slug>/tich-hop
WORKTREE: /đường/dẫn/tuyệt/đối/.tdq-worktrees/<slug>/t1.1
VÙNG FILE: scripts/alpha.py, tests/test_alpha.py — CẤM sửa file ngoài danh sách này
TEST: <lệnh kiểm của task> — phải đỏ trước, xanh sau
RANH GIỚI: luôn được làm — sửa file trong VÙNG FILE, thêm test của chính task này.
  phải hỏi trước — đổi API/khuôn dữ liệu dùng chung, thêm phụ thuộc mới, sửa file ngoài vùng.
  cấm — sửa plan/spec/state, commit lên nhánh khác, chạy full suite, đụng worktree của task khác.
TỰ KIỂM: <đúng MỘT lệnh agent con chạy được trước khi báo xong, thường là lệnh ở TEST>
TRẢ VỀ: đúng khuôn TASK/STATUS/FILES/TEST/BRANCH/TICK-READY/NOTES ở agents/tdq-implementer.md
```

Kèm đường dẫn spec và plan trong phần thân prompt. Agent con KHÔNG đọc được hội thoại
này — thiếu trường nào là nó phải đoán, và đoán sai thì bạn trả giá lúc merge.

### Ví dụ ĐÚNG/SAI

1. Chia việc
   - ĐÚNG: `phan-cong` xong, 9/12 task `giao`, 3 task `tu_lam` kèm mã lý do; `kiem-ke` exit 0.
   - SAI: đọc plan, thấy "chắc tự làm nhanh hơn", làm luôn ở main, không sinh bản đồ.
2. Nhịp phát việc
   - ĐÚNG: một response gọi 4 lần agent cho 4 task cùng đợt — chúng chạy đồng thời.
   - SAI: gọi 1 agent, chờ nó xong, mới gọi agent kế — đó là mode `main` đội lốt đội.
3. Merge
   - ĐÚNG: `kiem T1.2` sạch → `hop T1.2` → tick `[x]` ngay.
   - SAI: merge thẳng không `kiem`, gặp xung đột giữa chừng rồi sửa vá víu trong repo chính.
4. Dấu tick
   - ĐÚNG: 4 task `[>]` cùng lúc + 1 task `[~]` của leader.
   - SAI: 4 task `[~]` cùng lúc — hook chặn, và không ai biết leader thật sự đang ở đâu.
5. Vùng file
   - ĐÚNG: hai task cùng đụng `scripts/a.py` → `phan-cong` tự xếp chúng vào hai đợt khác nhau.
   - SAI: giao cả hai trong một đợt vì "chắc không sao" — git không cảnh báo, đến merge mới vỡ.
6. Hợp đồng dùng chung
   - ĐÚNG: task dựng hằng `TRAN_SONG_SONG` và khuôn thông báo được giữ lại, làm xong
     TRƯỚC, rồi mới phát cụm đọc hai thứ đó.
   - SAI: giao song song cả ba task cùng cần hằng đó — mỗi agent con tự đặt một tên,
     merge xong mới lộ ra là ba bản không khớp.

## Tự kiểm

Trước khi kết thúc phase implement, tất cả phải đúng:

```
python3 scripts/tdq_team.py kiem-ke          # exit 0
python3 scripts/tdq_team.py cum              # in "HẾT: không còn task nào để giao"
python3 scripts/tdq_team.py don              # dọn sạch worktree
git worktree list                            # chỉ còn worktree gốc
grep -c '^- \[x\]' docs/tdq/plan/<slug>.md   # bằng tổng số task
```

Và một câu tự hỏi, trả lời được bằng số: **giao bao nhiêu / tổng bao nhiêu?** Con số đó
phải có mặt trong report. Tỉ lệ giao thấp mà không có lý do trong bảng tra nghĩa là bạn
đã lách luật của user — user chọn mode đội là để có một đội, không phải một lời hứa.
