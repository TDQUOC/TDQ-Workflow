# PLAN — Chống conflict và chống việc dội ngược cho leader ở mode sub-agent

Ngày: 2026-09-03 · Spec: ../spec/2026-09-03-1527-sub-agent-chong-conflict.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — `simulate` đo lại trên bản 1.1: 20 task, 11 đợt, đội thắng 7,0 phút (33,7 so với 40,7). P0 nới rộng khoảng cách vì T0.3/T0.4 chạm script khác hẳn, tách đợt được (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: ĐÃ DUYỆT (bản 1.1) · mode: main (làm trực tiếp)

**Lưu ý phạm vi:** spec §1b ghi rõ request này DỪNG sau pha `plan`. Plan này là sản phẩm giao,
không chạy ngay. Build ở request sau, sau khi user duyệt.

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- Bảng đổi tên lệnh
- P0 — Đổi tên lệnh sang tiếng Anh (đầu ra 13–15)
- P1 — Kiểm chứng kết quả agent con (H5)
- P2 — Cưỡng chế vùng file (H1)
- P3 — Rebase và gỡ conflict (H2, H4)
- P4 — Cảnh báo file nóng (H3)
- P5 — Luật và tài liệu
- P6 — Log & test bắt buộc
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]`
   NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. **Mốc đỏ có sẵn: 100 ca đỏ / 1478 xanh** (đo 2026-09-03). Mọi lệnh full suite so với mốc này;
   vượt 100 là hồi quy do mình gây ra, phải sửa chứ không được ghi nhận.

## Bảng đổi tên lệnh

Tên mới là tên chính thức, chỉ nó hiện trong `--help`. Tên cũ giữ làm **bí danh ẩn** để mọi thứ
đang chạy (hook, bundle, tài liệu chưa quét tới) không gãy.

| Script | Tên cũ | Tên mới |
|---|---|---|
| `tdq_team.py` | `phan-cong` · `kiem-ke` · `cum` · `mo` · `kiem` · `hop` · `soat` · `don` | `assign` · `audit` · `wave` · `open` · `check` · `merge` · `sweep` · `clean` |
| `tdq_bench.py` | `dung-plan` · `thuc-do` · `mo-phong` · `quet` | `gen-plan` · `calibrate` · `simulate` · `scan` |
| `tdq_eval.py` | `dung-nhanh` · `chay` · `cham` · `bao-cao` | `setup` · `run` · `score` · `report` |
| `tdq_lsp.py` | `kiem` · `danh-thuc` · `nha` | `check` · `wake` · `release` |
| `tdq_state.py` | `tam-hoan` · `tiep-tuc` | `pause` · `resume` |

Lệnh gỡ conflict sinh ra ở T3.2 mang tên tiếng Anh ngay từ đầu: **`resolve`**, không qua tên Việt.

## P0 — Đổi tên lệnh sang tiếng Anh (đầu ra 13–15)

Chạy TRƯỚC mọi phase khác: mọi hành vi máy và mọi câu tài liệu phía sau đều nhắc tên lệnh. Đổi
tên sau nghĩa là viết một lần bằng tên cũ rồi sửa lại lần nữa.

- [x] **T0.1** (e12m) Viết một hàm phân giải bí danh dùng chung cho cả 5 script: nhận tên người gõ, trả tên chính thức; bảng đối chiếu đặt đúng một chỗ, các script import về — Test: `python3 -m pytest tests/test_team_chong_conflict.py -q -k doi_ten` xanh, gồm ca tên mới, ca tên cũ, ca tên không tồn tại
  - Chạm: `scripts/tdq_ten_lenh.py` (module MỚI), `tests/test_team_chong_conflict.py`
  - Tạo mới `scripts/tdq_ten_lenh.py` thay vì đặt bảng trong `scripts/tdq_team.py` vì `tdq_team` đã import `tdq_state`; đặt bảng ở `tdq_team` sẽ bắt `tdq_state` import ngược lại → vòng import.
- [x] **T0.2** (e10m) `tdq_team.py` dùng 8 tên mới trong `LENH`, nhận 8 tên cũ qua bí danh; `--help` chỉ in tên mới — Test: `python3 scripts/tdq_team.py --help` không chứa chuỗi tên Việt nào của bảng trên, và `python3 -m pytest tests/test_team_mode.py -q` không thêm ca đỏ
  - Chạm: `scripts/tdq_team.py`
  - Cần: T0.1
- [x] **T0.3** (e10m) Áp cùng cách cho `tdq_bench.py` (4 lệnh) và `tdq_eval.py` (4 lệnh) — Test: `python3 scripts/tdq_bench.py simulate --help` thoát 0 và `python3 scripts/tdq_bench.py mo-phong --help` cũng thoát 0
  - Chạm: `scripts/tdq_bench.py`, `scripts/tdq_eval.py`
  - Cần: T0.1
- [x] **T0.4** (e8m) Áp cùng cách cho `tdq_lsp.py` (3 lệnh) và `tdq_state.py` (`tam-hoan`/`tiep-tuc`) — Test: `python3 scripts/tdq_lsp.py check` và `python3 scripts/tdq_lsp.py kiem` cho cùng đầu ra
  - Chạm: `scripts/tdq_lsp.py`, `scripts/tdq_state.py`
  - Cần: T0.1
- [x] **T0.5** (e12m) Quét `skills/`, `hooks/`, `agents/` đổi mọi chỗ nhắc tên cũ sang tên mới; bảng đối chiếu ở `skills/tdq-conventions/references/` là chỗ DUY NHẤT còn được giữ tên cũ — Test: tìm 8 tên cũ của `tdq_team.py` trong 3 thư mục đó ra 0 lần ngoài bảng đối chiếu, và `python3 scripts/doc_lint.py` thoát 0 trên mọi `.md` đã sửa
  - Chạm: `skills/`, `hooks/`, `agents/`
  - Cần: T0.2, T0.3, T0.4

**Xong P0 khi**: `--help` của cả 5 script chỉ in tên tiếng Anh, mọi tên cũ vẫn gọi được, và
không còn tên cũ nào trong `skills/`+`hooks/`+`agents/` ngoài bảng đối chiếu.

## P1 — Kiểm chứng kết quả agent con (H5)

Làm trước vì đây là lỗ hở nặng nhất theo `soul.md`: code chưa kiểm vào nhánh tích hợp thì mọi
thứ phía sau đứng trên nền hỏng.

- [x] **T1.1** (e14m) Viết hàm đọc lệnh sau `Test:` của một task từ plan và chạy nó trong worktree của task, trả về (mã thoát, lệnh đã chạy, đầu ra) — Test: `python3 -m pytest tests/test_team_chong_conflict.py -q -k lay_lenh_test` xanh, gồm 1 ca lấy đúng lệnh và 1 ca task không có `Test:` trả về `None`
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_chong_conflict.py` → file test mới, chưa node nào phụ thuộc
- [x] **T1.2** (e12m) `check <task>` gọi hàm T1.1 sau bước dò conflict; phân biệt hai ca hỏng: lệnh không chạy được (lỗi PLAN, nêu mã task) và lệnh chạy nhưng đỏ (lỗi CODE) — Test: `python3 -m pytest tests/test_team_chong_conflict.py -q -k kiem_chay_test` xanh, gồm ca xanh, ca đỏ, ca lệnh sai
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_chong_conflict.py`
  - Cần: T1.1
- [x] **T1.3** (e10m) `merge <task>` từ chối merge khi T1.2 chưa xanh; nhánh tích hợp không nhận commit nào — Test: `python3 -m pytest tests/test_team_chong_conflict.py -q -k hop_chan_test_do` xanh, khẳng định số commit của nhánh tích hợp không đổi
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_chong_conflict.py`
  - Cần: T1.2

**Xong P1 khi**: một nhánh task có test đỏ không thể vào nhánh tích hợp bằng bất kỳ đường nào
trong `tdq_team.py`.

## P2 — Cưỡng chế vùng file (H1)

- [x] **T2.1** (e14m) Viết hàm trả lời "đường dẫn sắp ghi này có nằm ngoài vùng file của task sở hữu worktree hiện tại không", nhận diện worktree qua đường dẫn `.tdq-worktrees/<slug>/<task>`; trả `None` khi không ở trong worktree nào — Test: `python3 -m pytest tests/test_team_chong_conflict.py -q -k ngoai_vung` xanh, gồm ca trong vùng, ca ngoài vùng, ca không ở worktree
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_chong_conflict.py`
  - Dùng: `tdq-lsp-setup`
  - Để: tìm mọi nơi gọi `canh_bao_lach_luat` và `duong_ban_do` bằng `mcp__lsp__find_references` song song với lumen, trước khi thêm hàm mới cạnh chúng, nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc `skills/tdq-lsp-setup/SKILL.md` rồi làm theo.
  - Ra: danh sách nơi gọi, ghi vào phần mô tả task này
  - Kiểm: `python3 scripts/tdq_lsp.py kiem` thoát 0
  - Không dùng cho: sửa cấu hình LSP hay cài thêm language server
- [x] **T2.2** (e12m) `edit_gate.py` gọi hàm T2.1 và CHẶN khi ngoài vùng; thông báo nêu đủ ba thứ: mã task, vùng file cho phép, đường thoát ("báo leader mở rộng `Chạm:`") — Test: `python3 -m pytest tests/test_team_chong_conflict.py -q -k gate_chan_ngoai_vung` xanh, khẳng định cả ba chuỗi có mặt trong thông báo
  - Chạm: `hooks/scripts/edit_gate.py`, `tests/test_team_chong_conflict.py`
  - Cần: T2.1
- [x] **T2.3** (e6m) Khẳng định cổng mới không đụng mode `main`: ngoài worktree thì hàm T2.1 trả `None` và `edit_gate` chạy y như cũ — Test: `python3 -m pytest tests/test_edit_gate.py -q` không thêm ca đỏ nào so với trước T2.2
  - Chạm: `tests/test_team_chong_conflict.py`
  - Cần: T2.2

**Xong P2 khi**: ghi ra file ngoài `Chạm:` từ trong worktree bị chặn, ghi trong vùng vẫn đi qua,
và mode `main` không đổi hành vi.

## P3 — Rebase và gỡ conflict (H2, H4)

- [x] **T3.1** (e18m) `merge` rebase nhánh task lên nhánh tích hợp mới nhất TRƯỚC khi dò conflict; rebase hỏng thì `git rebase --abort` ngay rồi mới báo lỗi, worktree trả về đúng commit trước đó — Test: `python3 -m pytest tests/test_team_chong_conflict.py -q -k rebase` xanh, gồm ca hai nhánh nối tiếp merge liên tiếp không thao tác tay, và ca rebase hỏng để lại worktree sạch
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_chong_conflict.py`
  - Cần: T1.3
- [x] **T3.2** (e14m) Thêm lệnh `resolve <task>`: in từng file kẹt kèm nội dung hai phía và trạng thái nhánh, không tự sửa file nào — Test: `python3 -m pytest tests/test_team_chong_conflict.py -q -k lenh_resolve` xanh, khẳng định đầu ra nêu đúng tên file kẹt và có cả hai phía
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_chong_conflict.py`
  - Cần: T3.1

**Xong P3 khi**: hai nhánh nối tiếp merge được liên tiếp không cần gõ tay, và conflict thật in ra
đủ thông tin để gỡ.

## P4 — Cảnh báo file nóng (H3)

- [x] **T4.1** (e12m) `assign` đếm số task chạm mỗi đường dẫn; đường dẫn nào ở ≥ 2 dòng `Chạm:` thì in cảnh báo nêu đường dẫn và số task, kèm gợi ý nâng lên đợt sớm — Test: `python3 -m pytest tests/test_team_chong_conflict.py -q -k file_nong` xanh, gồm plan có file nóng và plan không có
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_chong_conflict.py`

**Xong P4 khi**: chạy `assign` trên chính plan này in ra cảnh báo cho `scripts/tdq_team.py`.

## P5 — Luật và tài liệu

- [x] **T5.1** (e10m) `team-mode.md`: mỗi hành vi máy mới (T1.2, T1.3, T2.2, T3.1, T3.2, T4.1) có đúng một mục nói cách dùng; sửa vòng lặp đợt cho khớp — Test: `python3 scripts/doc_lint.py skills/tdq-build/references/team-mode.md` thoát 0, và `grep -c "resolve\|rebase\|file nóng"` ra khác 0
  - Dùng: `tdq-build`
  - Để: sửa `references/team-mode.md` của chính skill này cho khớp hành vi máy mới, nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc `skills/tdq-build/SKILL.md` rồi làm theo.
  - Ra: `skills/tdq-build/references/team-mode.md` đã sửa
  - Kiểm: `python3 scripts/doc_lint.py skills/tdq-build/references/team-mode.md` thoát 0
  - Không dùng cho: sửa `SKILL.md`, `qc.md` hay `report-template.md` của cùng skill
- [x] **T5.2** (e8m) `plan-template.md`: thêm mục luật file nóng — cách nhận diện và cách xử lý (nâng lên đợt sớm hoặc giao một chủ ghi duy nhất) — Test: `python3 scripts/doc_lint.py skills/tdq-plan/references/plan-template.md` thoát 0
- [x] **T5.3** (e6m) `agents/tdq-implementer.md`: nói rõ `TICK-READY` không còn là lời tự khai, leader sẽ chạy lại lệnh `Test:` trước khi merge — Test: `python3 scripts/doc_lint.py agents/tdq-implementer.md` thoát 0 và có chuỗi nói về việc bị kiểm lại
- [x] **T5.4** (e6m) Dựng lại 3 bundle portable để chúng mang luật mới — Test: `python3 scripts/tdq_checkportable.py check` ra CLEAN cả 3 bundle
  - Chạm: `antigravity_portable/`, `portable_codex/`, `portable_claude/` → sinh lại toàn bộ, không sửa tay
  - Cần: T5.1, T5.2, T5.3

**Xong P5 khi**: không còn câu nào trong ba file luật mô tả hành vi máy đã bị thay.

## P6 — Log & test bắt buộc

- [x] **T6.1** (e6m) Mọi nhánh quyết định mới (chặn ghi ngoài vùng, chặn merge do test đỏ, rebase, phát hiện file nóng) đều ghi một dòng log qua `_log` sẵn có, tắt được qua `TDQ_LOG=0` — Test: `TDQ_LOG=0` thì đầu ra không có dòng log nào; `TDQ_LOG=1` thì có đủ 4 dòng
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_chong_conflict.py`
  - Cần: T4.1
- [x] **T6.2** (e8m) Rà bộ test mới: mỗi hành vi máy ở §2 spec có ít nhất một ca, chạy bằng một lệnh — Test: `python3 -m pytest tests/test_team_chong_conflict.py -q` xanh toàn bộ
  - Chạm: `tests/test_team_chong_conflict.py`
  - Cần: T6.1

## Cụm song song

**Kết luận: 11 đợt, đội thắng 7,0 phút.** Số đo thật từ `tdq_bench.py simulate` trên chính plan
này (bản 1.1): 20 task · giao 13 · leader giữ 7 · **11 đợt** · đội 33,7 phút so với main 40,7 phút.

Vì sao khoảng cách vẫn không lớn: 12/20 task khai `scripts/tdq_team.py` trong dòng `Chạm:`. Luật
`_dot_som_nhat` cấm hai task chạm chung file nằm cùng một đợt, nên chúng bị xếp thành chuỗi đợt
nối nhau. Cột "leader làm xen giữa" ra **0,0 phút** — nghĩa là leader ngồi không suốt lúc chờ,
đúng dấu hiệu của một plan gần như tuần tự. Phần tách được thật sự chỉ có T2.2 (`edit_gate.py`)
và nhóm T5 (chỉ chạm tài liệu), mà T2.2 phải chờ T2.1 còn nhóm T5 phải chờ hành vi máy xong mới
mô tả đúng được.

Đây chính là hiện tượng file nóng mà T4.1 sinh ra để cảnh báo, và request này là ca thử đầu
tiên: chạy `assign` trên plan này PHẢI in cảnh báo cho `scripts/tdq_team.py`.

## Definition of Done

- [x] Q1 Cổng vùng file chặn ghi ngoài `Chạm:`, thông báo nêu đủ mã task + vùng cho phép + đường thoát — `python3 -m pytest tests/test_team_chong_conflict.py -q -k gate_chan_ngoai_vung`
- [x] Q2 Cổng vùng file KHÔNG chặn ghi trong vùng — `python3 -m pytest tests/test_team_chong_conflict.py -q -k ngoai_vung`
- [x] Q3 Mode `main` không đổi hành vi — `python3 -m pytest tests/test_edit_gate.py -q`
- [x] Q4 `check` chạy thật lệnh kiểm của task và nêu tên lệnh — `python3 -m pytest tests/test_team_chong_conflict.py -q -k kiem_chay_test`
- [x] Q5 `merge` chặn khi test của task đỏ, nhánh tích hợp không nhận commit — `python3 -m pytest tests/test_team_chong_conflict.py -q -k hop_chan_test_do`
- [x] Q6 `merge` tự rebase khi base đã cũ — `python3 -m pytest tests/test_team_chong_conflict.py -q -k rebase`
- [x] Q7 Rebase hỏng thì worktree về nguyên trạng — `python3 -m pytest tests/test_team_chong_conflict.py -q -k rebase_hong`
- [x] Q8 Lệnh `resolve` nêu đủ thông tin để gỡ — `python3 -m pytest tests/test_team_chong_conflict.py -q -k lenh_resolve`
- [x] Q9 `assign` cảnh báo file nóng — `python3 -m pytest tests/test_team_chong_conflict.py -q -k file_nong`
- [x] Q10 Ba file luật khớp code — `python3 scripts/doc_lint.py skills/tdq-build/references/team-mode.md skills/tdq-plan/references/plan-template.md agents/tdq-implementer.md`
- [x] Q11 Bộ test đội hình cũ không thêm ca đỏ — `python3 -m pytest tests/test_team_mode.py tests/test_edit_gate.py -q`
- [x] Q12 Mốc đỏ toàn bộ không vượt 100 — `python3 -m pytest -q`
- [x] Q13 Tên lệnh tiếng Anh chạy đúng ở cả 5 script — `python3 -m pytest tests/test_team_chong_conflict.py -q -k doi_ten`
- [x] Q14 Mọi tên cũ vẫn chạy được qua bí danh — `python3 -m pytest tests/test_team_mode.py -q`
- [x] Q15 Không còn tên cũ trong `skills/`+`hooks/`+`agents/` — `grep -rn "phan-cong\|kiem-ke\|mo-phong" skills hooks agents | grep -v ten-lenh`

## Ước tính

Tổng `eNm` của 20 task chưa xong: **208 phút** (156 + 52 của P0).
