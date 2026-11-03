# PLAN — Luôn tổ chức modular, ưu tiên sub-agent chạy song song

Ngày: 2026-08-18 · Spec: ../spec/2026-08-18-1744-uu-tien-subagent-song-song.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — `mo-phong` (hệ số agent 1.5) ĐỀ XUẤT đội, chênh 6,1 phút; user chốt `main` (B)
Trạng thái plan: HOÀN THÀNH — 39/39 task tick, QC vòng 1 đóng hết 10 mục fix

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Mọi test mới của request này đặt trong `tests/test_uu_tien_song_song.py`, trừ test của
   `chia_dot` và lệnh `cum` (đặt trong `tests/test_team_mode.py`), test của linter (đặt
   trong `tests/test_doc_lint.py`), test của hook (đặt trong `tests/test_edit_gate.py`).
8. Đính chính lúc thi hành: plan viết `tests/test_tdq_team.py`, tên thật trong repo là
   `tests/test_team_mode.py`. Mọi chỗ đã sửa lại theo tên thật.
9. Sửa file trong `skills/` xong thì PHẢI chạy `python3 scripts/build_portable.py`, nếu
   không bản portable lệch bản gốc và Q16 sẽ đỏ.
10. Đính chính lúc thi hành (T6.1): phép kiểm "chạy build rồi `git status --short
    portable_*` không in dòng nào" chỉ đúng khi bản portable đã commit. Trong request
    này portable ĐANG đổi theo nguồn nên git status luôn có dòng. Phép kiểm thay thế,
    cùng ý nghĩa: chạy build hai lần, `git status` lần hai giống hệt lần một
    (bản sinh ổn định, không trôi).

## P1 — Khuôn tài liệu

- [x] **T1.1** (e15m) Thêm mục `## 2b. Ranh giới module` vào khuôn spec, đặt ngay sau mục `## 2. Đầu ra cụ thể` trong khối markdown mẫu. Mục gồm một câu dẫn và một bảng 4 cột: `Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào`. Thêm một dòng luật: lane full bắt buộc có mục này, lane quick thì bỏ — Test: `grep -c "2b. Ranh giới module" skills/tdq-spec/references/spec-template.md` ra 1
  - Chạm: `skills/tdq-spec/references/spec-template.md` → khuôn spec, chưa node code nào phụ thuộc
- [x] **T1.2** (e10m) Thêm dòng nhắc mục `2b` vào bước 1 của `skills/tdq-spec/SKILL.md`, trong danh sách "Mục bắt buộc" — Test: `grep -c "Ranh giới module" skills/tdq-spec/SKILL.md` ra ít nhất 1; `python3 scripts/doc_lint.py skills/tdq-spec/SKILL.md` exit 0
  - Chạm: `skills/tdq-spec/SKILL.md` → thân skill spec
- [x] **T1.3** (e20m) Thêm trường `Cần:` vào khuôn plan. Đặt cùng chỗ với khối mô tả dòng `Chạm:`. Cú pháp một dòng, nằm dưới task, dạng `- Cần: T1.1, T1.2` — mã task nằm ngoài backtick, phân cách bằng dấu phẩy. Viết rõ: task nào ĐỌC đầu ra của task khác thì bắt buộc khai; không khai thì máy lùi về luật cũ theo tên phase — Test: `grep -c "Cần: T" skills/tdq-plan/references/plan-template.md` ra ít nhất 1
  - Chạm: `skills/tdq-plan/references/plan-template.md` → khuôn plan, `scripts/tdq_team.py` đọc khuôn này
- [x] **T1.4** (e12m) Trong cùng file, đổi mục `## Cụm song song` thành BẮT BUỘC luôn có trong mọi plan, kể cả khi kết luận chỉ một cụm. Xoá câu "Dưới 3 thì đề xuất mode `main` cho lành" và thay bằng câu trỏ sang lệnh `mo-phong`. Giữ nguyên 3 luật chia nhỏ theo file — Test: `grep -c "Dưới 3 thì đề xuất" skills/tdq-plan/references/plan-template.md` ra 0
  - Chạm: `skills/tdq-plan/references/plan-template.md` → cùng file với T1.3, phải làm sau T1.3
  - Cần: T1.3

- [x] **T1.5** (e10m) Việc phát sinh khi chạy suite sau P1: chèn dòng vào 3 file skill làm lệch 25 trên 329 số dòng trong `docs/tdq/audit/luat-hien-co.md`, vượt ngưỡng cảnh báo 5%. Dò lại vị trí theo chữ neo và cập nhật số dòng; không sửa nội dung luật nào. Xoá thêm một file rác `.DS_Store` ở gốc repo làm đỏ `test_no_ds_store` — Test: `python3 -m pytest tests/test_luat_skill.py tests/test_docs_consistency.py -q` xanh
  - Chạm: `docs/tdq/audit/luat-hien-co.md` → bảng tra cứu luật, chỉ đổi số dòng
  - Cần: T1.1, T1.2, T1.3, T1.4

**Xong P1 khi**: `python3 scripts/doc_lint.py skills/tdq-spec/references/spec-template.md skills/tdq-plan/references/plan-template.md skills/tdq-spec/SKILL.md` exit 0.

## P2 — Linter ép khuôn mới

- [x] **T2.1** (e25m) Viết test đỏ cho luật R10 trong `tests/test_doc_lint.py`: file trong `docs/tdq/spec/` có dòng `Lane: full` mà thiếu chuỗi `## 2b. Ranh giới module` thì `doc_lint` phải báo một dòng chứa `[R10]`; file `Lane: quick` thiếu mục đó thì KHÔNG báo. Chạy để thấy đỏ trước — Test: `python3 -m pytest tests/test_doc_lint.py -q -k r10` đỏ ở bước này
  - Chạm: `tests/test_doc_lint.py` → test của linter
- [x] **T2.2** (e30m) Viết hàm `rule_r10(doc, out)` trong `scripts/doc_lint.py` và thêm vào hằng `RULES`. Chỉ áp cho file nằm dưới `docs/tdq/spec/`. Dùng lại hàm `_report` sẵn có, cấm tự in ra. Không đọc lại file, dùng đối tượng `doc` — Test: `python3 -m pytest tests/test_doc_lint.py -q` xanh toàn bộ
  - Chạm: `scripts/doc_lint.py` → hàm `rule_r10`, hằng `RULES`, mọi lệnh lint trong repo (nguồn: `RULES` là điểm vào chung)
  - Cần: T2.1
- [x] **T2.3** (e20m) Bổ sung phép kiểm của `--pair spec plan`: plan thiếu mục `## Cụm song song` thì báo lỗi. Viết test đỏ trước trong `tests/test_doc_lint.py` — Test: `python3 -m pytest tests/test_doc_lint.py -q -k pair` xanh
  - Chạm: `scripts/doc_lint.py`, `tests/test_doc_lint.py` → phần `--pair`
  - Cần: T2.2

**Xong P2 khi**: `python3 -m pytest tests/test_doc_lint.py -q` xanh và `python3 scripts/doc_lint.py docs/tdq/spec/*.md` exit 0.

## P3 — Lịch trình trong `tdq_team.py`

- [x] **T3.1** (e20m) Viết hàm `doc_phu_thuoc(plan)` đọc dòng `- Cần: T1.1, T2.3` dưới mỗi task, trả `dict` mã task sang tập mã task cần trước. Task không có dòng này trả tập rỗng. Viết test đỏ trước trong `tests/test_team_mode.py` — Test: `python3 -m pytest tests/test_team_mode.py -q -k phu_thuoc` xanh
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py` → hàm mới, chưa node nào phụ thuộc
- [x] **T3.2** (e40m) Viết lại `chia_dot(tasks, quyet_dinh)`: bỏ vòng lặp theo phase, xếp đợt theo hai ràng buộc — task phải nằm sau mọi task trong `Cần:` của nó, và hai task chạm chung file không nằm chung đợt. Plan KHÔNG khai `Cần:` ở bất kỳ task nào thì lùi về luật cũ theo tên phase, để plan cũ chạy y như trước. Giữ nguyên chữ ký hàm vì `tdq_bench.py` đang gọi — Test: `python3 -m pytest tests/test_team_mode.py -q -k chia_dot` xanh; thêm ca plan cũ không khai `Cần:` cho ra đúng số đợt như bản cũ
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py` → `chia_dot`, `lenh_phan_cong`, `lenh_cum`, `scripts/tdq_bench.py` (nguồn: `chia_dot` là điểm vào chung của cả bench)
  - Cần: T3.1
- [x] **T3.3** (e25m) Viết hàm `b_level(tasks, phu_thuoc)` tính chiều dài đường dài nhất từ mỗi task tới hết đồ thị, dùng số phút `eNm` khi có, mặc định 1 khi không có. Test đỏ trước — Test: `python3 -m pytest tests/test_team_mode.py -q -k duong_gang` xanh
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py` → hàm mới
  - Cần: T3.1
- [x] **T3.4** (e35m) Sửa `lenh_cum`: bỏ lọc theo `dot_min`. Thay bằng danh sách sẵn sàng — task được phát khi mọi task trong `Cần:` đã xong VÀ không có file nào nằm trong vùng đang khoá. Sắp danh sách theo `b_level` giảm dần rồi mới cắt theo trần. Vẫn in dòng `HOÃN` cho task chưa sẵn sàng, kèm lý do cụ thể là thiếu task nào hoặc đụng file nào — Test: `python3 -m pytest tests/test_team_mode.py -q -k lien_tuc` xanh, có ca task đợt sau được phát ngay khi vùng file rảnh
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py` → `lenh_cum`
  - Cần: T3.2, T3.3
- [x] **T3.5** (e20m) Thêm trần trên 4 vào `lenh_cum`: hằng số `TRAN_SONG_SONG = 4` ở đầu file kèm chú thích nêu nguồn. Danh sách phát cắt còn nhiều nhất 4 task, phần dư in thành dòng `CHỜ SLOT`. Trần là trần TRÊN, ít task sẵn sàng hơn thì phát ít hơn, cấm chờ cho đủ 4 — Test: `python3 -m pytest tests/test_team_mode.py -q -k tran` xanh, phủ ca 9 task rời nhau ra 4 và ca 2 task rời nhau ra 2
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py` → `lenh_cum`, hằng `TRAN_SONG_SONG`
  - Cần: T3.4
- [x] **T3.6** (e15m) Thêm lý do giữ task thứ năm `hop-dong` vào tập lý do đóng của `lenh_kiem_ke` và mọi chỗ liệt kê 4 lý do trong `scripts/tdq_team.py`. Nghĩa: task định nghĩa hợp đồng dùng chung (kiểu dữ liệu, hằng số, khuôn thông báo, sổ đăng ký) mà nhiều task sau đọc — Test: `python3 -m pytest tests/test_team_mode.py -q -k ly_do` xanh
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py` → `lenh_kiem_ke`
- [x] **T3.7** (e25m) Viết test đo số đợt trên 4 plan thật trong `docs/tdq/plan/`: với mỗi plan, số đợt sau khi sửa phải nhỏ hơn hoặc bằng số đợt bản cũ. Ghi số cụ thể vào thông báo assert để đọc được khi đỏ — Test: `python3 -m pytest tests/test_uu_tien_song_song.py -q -k so_dot` xanh
  - Chạm: `tests/test_uu_tien_song_song.py` → file test mới
  - Cần: T3.2

**Xong P3 khi**: `python3 -m pytest tests/test_team_mode.py tests/test_bench.py -q` xanh và
`python3 scripts/tdq_bench.py mo-phong --plan docs/tdq/plan/2026-08-17-1139-codex-native-layers.md --thuc-do docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json` exit 0.

## P4 — Luật trong các skill

- [x] **T4.1** (e20m) Sửa bước 1 của `skills/tdq-plan/SKILL.md`: thay luật "trên 6 task mà đụng file rời nhau" bằng luật chạy lệnh `python3 scripts/tdq_bench.py mo-phong --plan <file plan> --thuc-do docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json --he-so-agent 1.5`, rồi lấy dòng `Thắng:` của lệnh làm đề xuất mode. Nêu rõ hệ số 1.5 là giả định bảo thủ — Test: `grep -c "he-so-agent 1.5" skills/tdq-plan/SKILL.md` ra ít nhất 1; `python3 scripts/doc_lint.py skills/tdq-plan/SKILL.md` exit 0
  - Chạm: `skills/tdq-plan/SKILL.md` → thân skill plan
  - Dùng: `tdq-plan`
  - Để: đổi luật đề xuất mode ở bước 1 sang chạy lệnh, nạp skill TRƯỚC bước đỏ. Agent
    ngoài không có skill system: đọc `skills/tdq-plan/SKILL.md` rồi làm theo.
  - Ra: `skills/tdq-plan/SKILL.md` có dòng lệnh `mo-phong --plan` ở bước 1
  - Kiểm: `grep -c "he-so-agent 1.5" skills/tdq-plan/SKILL.md` ra ít nhất 1
  - Không dùng cho: khuôn plan ở `references/plan-template.md` — việc đó là T1.3 và T1.4
- [x] **T4.2** (e20m) Sửa mục `Khi nào áp dụng` của `skills/tdq-build/references/team-mode.md`: xoá câu khoá theo `implement_mode = subagent`. Thay bằng: doctrine leader áp cho MỌI mode; mode `main` nghĩa là leader tự làm hết nhưng theo đúng thứ tự cụm của plan và ghi lý do giữ cho từng task — Test: `grep -c "implement_mode = subagent" skills/tdq-build/references/team-mode.md` ra 0
  - Chạm: `skills/tdq-build/references/team-mode.md` → doctrine leader
  - Dùng: `tdq-build`
  - Để: gỡ khoá doctrine leader khỏi điều kiện mode, nạp skill TRƯỚC bước đỏ. Agent ngoài
    không có skill system: đọc `skills/tdq-build/SKILL.md` rồi làm theo.
  - Ra: `skills/tdq-build/references/team-mode.md` không còn câu khoá theo mode
  - Kiểm: `grep -c "implement_mode = subagent" skills/tdq-build/references/team-mode.md` ra 0
  - Không dùng cho: phần QC và report của cùng skill — request này không đụng hai phần đó
- [x] **T4.3** (e15m) Trong cùng file, thêm dòng thứ năm `hop-dong` vào bảng lý do giữ task, kèm một ví dụ ĐÚNG và một ví dụ SAI — Test: `python3 -m pytest tests/test_uu_tien_song_song.py -q -k ly_do_bang` xanh, kiểm bảng có đúng 5 dòng lý do
  - Chạm: `skills/tdq-build/references/team-mode.md`, `tests/test_uu_tien_song_song.py` → cùng file với T4.2
  - Cần: T4.2
- [x] **T4.4** (e25m) Trong cùng file, mở rộng khuôn prompt giao việc từ 7 trường thành 9: thêm `RANH GIỚI` (ba tầng — luôn được làm, phải hỏi trước, cấm) và `TỰ KIỂM` (đúng một lệnh agent con chạy được trước khi báo xong) — Test: `python3 -m pytest tests/test_uu_tien_song_song.py -q -k ranh_gioi` xanh
  - Chạm: `skills/tdq-build/references/team-mode.md`, `tests/test_uu_tien_song_song.py` → khuôn prompt
  - Cần: T4.3
- [x] **T4.5** (e25m) Thêm đường song song vào `skills/tdq-intake/references/quick-lane.md`: mini-plan phải khai `Chạm:`; đếm số task chạm file rời nhau, từ 3 trở lên thì được sinh agent con `tdq-implementer`, trần trên 4, không dựng worktree cho agent chỉ đọc; dưới 3 thì chạy inline như cũ. Giữ nguyên số bước của mục `## Chín bước thi hành`, chỉ sửa nội dung bước thi hành — Test: `grep -c "agent con" skills/tdq-intake/references/quick-lane.md` ra ít nhất 1; `python3 scripts/doc_lint.py skills/tdq-intake/references/quick-lane.md` exit 0
  - Chạm: `skills/tdq-intake/references/quick-lane.md` → lane quick
- [x] **T4.6** (e15m) Nới `SKILL_LINE_LIMITS` trong `scripts/doc_lint.py` nếu và chỉ nếu file skill nào vượt trần sau P4, kèm chú thích một dòng nêu ngày và lý do theo mẫu sẵn có. Không vượt trần thì bỏ task này và ghi lý do vào plan — Test: `python3 scripts/doc_lint.py skills/*/SKILL.md` exit 0
  - Chạm: `scripts/doc_lint.py` → hằng `SKILL_LINE_LIMITS`
  - Cần: T4.1, T4.2, T4.5

**Xong P4 khi**: `python3 scripts/doc_lint.py skills/tdq-plan/SKILL.md skills/tdq-build/references/team-mode.md skills/tdq-intake/references/quick-lane.md` exit 0.

## P5 — Vá hook chặn nhầm agent con

- [x] **T5.1** (e20m) Viết test đỏ trong `tests/test_edit_gate.py`: payload có `cwd` là thư mục tạm ngoài project dir của state, phase là `implement`, plan chưa có dấu `[~]` — hook phải KHÔNG gọi `block`. Ca đối chứng: cùng payload nhưng `cwd` nằm trong project dir thì vẫn `block` như cũ — Test: `python3 -m pytest tests/test_edit_gate.py -q -k ngoai_project` đỏ ở bước này
  - Chạm: `tests/test_edit_gate.py` → test của hook
- [x] **T5.2** (e30m) Sửa `hooks/scripts/edit_gate.py`: trước khi vào nhánh chặn `TDQ:TICK`, so `abs_target` với project dir mà state đang dùng. Nằm ngoài thì bỏ qua nhánh chặn và ghi một dòng log nêu lý do. Dùng lại hàm `within` sẵn có, cấm viết lại phép so đường dẫn. Chỉ bỏ CHẶN, vẫn giữ nguyên phần quan sát và phần nhắc — Test: `python3 -m pytest tests/test_edit_gate.py -q` xanh toàn bộ
  - Chạm: `hooks/scripts/edit_gate.py`, `tests/test_edit_gate.py` → `main()` của hook
  - Cần: T5.1
- [x] **T5.3** (e15m) Chạy lại bộ test bền của hook để chắc không nới quá tay — Test: `python3 -m pytest tests/test_hook_resilience.py tests/test_plan_tick.py -q` xanh
  - Cần: T5.2

**Xong P5 khi**: `python3 -m pytest tests/test_edit_gate.py tests/test_hook_resilience.py -q` xanh.

## P6 — Đồng bộ bản ngoài và tổng kiểm

- [x] **T6.1** (e10m) Sinh lại bản portable — Test: `python3 scripts/build_portable.py && git status --short portable_claude portable_codex` không in dòng nào
  - Chạm: `portable_claude/`, `portable_codex/` → sinh tự động, cấm sửa tay
  - Cần: T1.1, T1.2, T1.3, T1.4, T4.1, T4.2, T4.3, T4.4, T4.5
- [x] **T6.2** (e15m) Chạy toàn bộ suite đúng một lần và dán kết quả thật — Test: `python3 -m pytest -q` 0 đỏ, tổng số test lớn hơn 704
  - Cần: T6.1
- [x] **T6.3** (e10m) Lint mọi file tài liệu đã sửa trong request này — Test: `python3 scripts/doc_lint.py` trên danh sách file đã sửa, exit 0
  - Cần: T6.1

**Xong P6 khi**: suite xanh, lint exit 0, bản portable khớp bản gốc.

## Px — Log & test bắt buộc

- [x] **Tx.1** (e10m) Ba file mã nguồn bị sửa (`scripts/tdq_team.py`, `scripts/doc_lint.py`, `hooks/scripts/edit_gate.py`) đều dùng LẠI hàm log sẵn có của chính file đó, không tự cài thêm cơ chế log mới. Mọi nhánh quyết định mới (bỏ chặn, cắt trần, lùi về luật phase cũ) đều in đúng một dòng log nêu lý do — Test: `grep -c "_log(" scripts/tdq_team.py` lớn hơn số cũ; đọc tay xác nhận không có hàm log thứ hai
  - Chạm: `scripts/tdq_team.py`, `scripts/doc_lint.py`, `hooks/scripts/edit_gate.py`
  - Cần: T3.5, T4.6, T5.2
- [x] **Tx.2** (e10m) Mỗi thành phần mới có unit test riêng chạy bằng một lệnh — Test: `python3 -m pytest tests/test_uu_tien_song_song.py tests/test_team_mode.py tests/test_doc_lint.py tests/test_edit_gate.py -q` xanh
  - Cần: Tx.1

## QC vòng 1 — fix

Nguồn: agent `tdq-qc-tester` (Q19) trả 12 phát hiện; mỗi phát hiện đã tự chạy lại để xác nhận
trước khi mở task fix. D11 không mở task: chèn dòng miễn trừ R10 vào 57 spec cũ là hệ quả bắt
buộc của T2.1, ghi vào report thay vì sửa.

- [x] **QC1.1** (e15m) `chia_dot` văng `KeyError` khi `Cần:` khai vòng — nhánh gỡ vòng gán đợt trước khi task phụ thuộc có đợt. Dùng `.get(c, 0)` ở nhánh đó và ghi log nêu rõ đã cắt vòng — Test: `python3 -m pytest tests/test_team_mode.py -q -k vong_lap` xanh
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py`
- [x] **QC1.2** (e20m) Trần 4 nhánh chỉ đếm task phát trong một lượt, bỏ qua task `[>]` đang bay → thực tế chạy 7 nhánh. Đếm cả task đang bay vào trần — Test: `python3 -m pytest tests/test_team_mode.py -q -k tran` xanh, có ca 3 task `[>]` + 9 task rời nhau chỉ phát thêm 1
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py`
- [x] **QC1.3** (e20m) Luật đá nhau: `skills/tdq-build/SKILL.md` còn "1 trong 4 nhóm", "khuôn prompt 7 trường" và chỉ trỏ `team-mode.md` ở nhánh `subagent`; `skills/tdq-plan/references/mode-gate.md` liệt kê đúng 4 nhóm — cấm chính `hop-dong` vừa thêm. Sửa cả hai file cho khớp — Test: `python3 -m pytest tests/test_uu_tien_song_song.py -q -k luat_khop` xanh
  - Chạm: `skills/tdq-build/SKILL.md`, `skills/tdq-plan/references/mode-gate.md`, `tests/test_uu_tien_song_song.py`
- [x] **QC1.4** (e15m) `mode-gate.md` vẫn dạy đoán mode bằng 4 căn cứ đọc mắt, chỏi luật mới bắt chạy `mo-phong`. Đổi thành: chạy lệnh, lấy dòng `Thắng:`, bốn căn cứ chỉ còn để VIẾT lý do — Test: `grep -c "mo-phong" skills/tdq-plan/references/mode-gate.md` ít nhất 1
  - Chạm: `skills/tdq-plan/references/mode-gate.md`
- [x] **QC1.5** (e15m) Hook còn chặn nhánh `TDQ:TEAM` với file ngoài project dir — cùng lỗi đã vá cho `TDQ:TICK`. Dùng lại biến `trong_project` — Test: `python3 -m pytest tests/test_edit_gate.py -q -k ngoai_project` xanh, có ca `TDQ:TEAM`
  - Chạm: `hooks/scripts/edit_gate.py`, `tests/test_edit_gate.py`
- [x] **QC1.6** (e15m) `scripts/doc_lint.py` không có log service nào, trong khi spec §4 đòi cả ba file mã nguồn đều có. Thêm log 1 dòng theo đúng khuôn của repo (`TDQ_LOG=0` tắt được, timestamp ISO, ra stderr) — Test: `python3 -m pytest tests/test_doc_lint.py -q -k log` xanh
  - Chạm: `scripts/doc_lint.py`, `tests/test_doc_lint.py`
- [x] **QC1.7** (e15m) Test đo số đợt lấy "4 plan mới nhất theo tên" — thêm 2 plan nữa là bom nổ chậm, test đỏ dù code không hỏng. Ghim danh sách plan theo tên cụ thể — Test: `python3 -m pytest tests/test_uu_tien_song_song.py -q -k so_dot` xanh
  - Chạm: `tests/test_uu_tien_song_song.py`
- [x] **QC1.8** (e10m) Lane quick bơm agent con nhưng vẫn khai "3 trạng thái" checkbox và nêu tên hằng nội bộ `TRAN_SONG_SONG` (kiến trúc chỉ cho nêu TÊN LỆNH). Thêm `[>]` cho lane quick, trỏ trần về file luật — Test: `python3 scripts/doc_lint.py skills/tdq-intake/references/quick-lane.md` exit 0 và `grep -c "TRAN_SONG_SONG" skills/tdq-intake/references/quick-lane.md` ra 0
  - Chạm: `skills/tdq-intake/references/quick-lane.md`
- [x] **QC1.9** (e10m) Spec §6 ghi sai hai lệnh kiểm: Q3 `-k cum` (đúng là `-k pair`), Q14 `tests/test_hooks.py` (đúng là `tests/test_edit_gate.py`). Sửa spec cho khớp plan — Test: `python3 scripts/doc_lint.py --pair <spec> <plan>` exit 0
  - Chạm: `docs/tdq/spec/2026-08-18-1744-uu-tien-subagent-song-song.md`
- [x] **QC1.10** (e10m) File qc thiếu bảng số đợt trước/sau của 4 plan thật mà DoD Q5 đòi. Thêm bảng với số thật, kể cả 3/4 plan không giảm — Test: `grep -c "trước/sau" docs/tdq/qc/2026-08-18-1744-uu-tien-subagent-song-song.md` ít nhất 1
  - Chạm: `docs/tdq/qc/2026-08-18-1744-uu-tien-subagent-song-song.md`

## Cụm song song

Đếm nhanh: 28 task, trong đó nhóm chạm file rời nhau rõ rệt là T1.1, T1.3, T2.1, T3.1,
T4.1, T4.2, T4.5, T5.1 — tám nhánh mở được ngay từ đầu. Ba file mã nguồn bị nhiều task
cùng chạm là `scripts/tdq_team.py` (P3), `scripts/doc_lint.py` (P2 và T4.6) và
`hooks/scripts/edit_gate.py` (P5); các task trong cùng nhóm đó phải nối tiếp nhau.

Hợp đồng dùng chung phải làm TUẦN TỰ trước, leader tự giữ: T1.3 (cú pháp trường `Cần:`)
và T3.1 (hàm đọc trường đó). Mọi task khác của P3 đọc kết quả của hai task này.

Số đo của chính plan này, chạy `python3 scripts/tdq_bench.py mo-phong --plan
docs/tdq/plan/2026-08-18-1744-uu-tien-subagent-song-song.md --thuc-do
docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json --he-so-agent 1.5`:
28 task, giao được 3, leader giữ 25, 3 đợt, main 57,0 phút so với đội 50,9 phút. Đội thắng
6,1 phút. Số giao thấp vì luật chia đợt HIỆN TẠI còn tính theo tên phase — đúng cái mà
P3 sửa. Sau P3, chính plan này chạy lại sẽ giao được nhiều hơn.

## Definition of Done

Trỏ về §6 của spec. Nhắc lại từng hạng mục và lệnh kiểm:

| # | Hạng mục | Lệnh |
|---|---|---|
| Q1 | Khuôn spec có mục ranh giới module | `grep -c "2b. Ranh giới module" skills/tdq-spec/references/spec-template.md` |
| Q2 | Linter chặn spec lane full thiếu mục đó | `python3 -m pytest tests/test_doc_lint.py -q` |
| Q3 | Khuôn plan bắt buộc khối cụm | `python3 -m pytest tests/test_doc_lint.py -q -k pair` |
| Q4 | Trường `Cần:` đổi được thứ tự đợt | `python3 -m pytest tests/test_team_mode.py -q -k phu_thuoc` |
| Q5 | Số đợt 4 plan thật giảm hoặc bằng | `python3 -m pytest tests/test_uu_tien_song_song.py -q -k so_dot` |
| Q6 | Phát liên tục | `python3 -m pytest tests/test_team_mode.py -q -k lien_tuc` |
| Q7 | Ưu tiên đường găng | `python3 -m pytest tests/test_team_mode.py -q -k duong_gang` |
| Q8 | Trần trên 4 | `python3 -m pytest tests/test_team_mode.py -q -k tran` |
| Q9 | Cổng mode nêu lệnh và hệ số | `grep -c "he-so-agent 1.5" skills/tdq-plan/SKILL.md` |
| Q10 | Doctrine hết khoá theo mode | `grep -c "implement_mode = subagent" skills/tdq-build/references/team-mode.md` |
| Q11 | Bảng lý do giữ có 5 dòng | `python3 -m pytest tests/test_uu_tien_song_song.py -q -k ly_do` |
| Q12 | Prompt có ranh giới ba tầng | `python3 -m pytest tests/test_uu_tien_song_song.py -q -k ranh_gioi` |
| Q13 | Lane quick có agent con | `grep -c "agent con" skills/tdq-intake/references/quick-lane.md` |
| Q14 | Hook không chặn ngoài project dir | `python3 -m pytest tests/test_edit_gate.py -q -k ngoai_project` |
| Q15 | Plan cũ thiếu `Cần:` vẫn chạy | `python3 scripts/tdq_bench.py mo-phong --plan docs/tdq/plan/2026-08-17-1139-codex-native-layers.md --thuc-do docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json` |
| Q16 | Portable khớp bản gốc | `python3 scripts/build_portable.py && git status --short portable_claude portable_codex` |
| Q17 | Lint file tài liệu đã sửa | `python3 scripts/doc_lint.py <danh sách file>` |
| Q18 | Toàn bộ suite | `python3 -m pytest -q` |
| Q19 | Kiểm độc lập | agent `tdq-qc-tester` chạy lại Q1 đến Q18 |
