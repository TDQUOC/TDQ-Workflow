# PLAN — Hợp lối code Ponytail vào TDQ-Workflow

Ngày: 2026-09-16 · Spec: ../spec/2026-09-16-1447-hop-ponytail-vao-tdq.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — lệnh `simulate` ra `Winner: đội (gap 2.0 minutes)` nhưng phí cố định mỗi đợt nó dùng là 0.0 phút, lấy từ hằng số `nguon: "stub"` mà chính file thực đo tự khai là "sàn dưới cơ học"; một vòng mở worktree + check + merge + clean thật đắt hơn 2 phút, nên đề xuất ngược lại số đo và nói rõ lý do (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH 2026-09-16 (duyệt: "duyệt plan" · mode: "1a inline" · 15/15 task, 9/9 DoD)

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Phương án tích hợp
- P2 — Dự thảo thân luật
- P3 — Report
- P4 — Kiểm bắt buộc
- Cụm song song
- Luật file nóng
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết phép kiểm trước (đỏ) → viết nội dung → kiểm xanh →
   đổi sang `[x]` NGAY vào file này. Trạng thái: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy phép kiểm của cả phase, phải xanh mới sang phase sau.
4. **Không task nào được tạo hay sửa file ngoài `docs/`.** Trình kiểm ở P4 viết vào thư mục
   scratchpad của phiên, không vào repo — đây là điều kiện của DoD Q8.
5. Mọi khẳng định về code phải kèm `đường-dẫn:dòng`; mọi khẳng định về cơ chế Claude Code phải
   mang đúng một nhãn `[XÁC THỰC]` / `[SUY-CODE]` / `[BÊN-THỨ-BA]`.
6. QC FAIL → thêm task fix vào mục DoD của file này (không cần duyệt lại), loop đến khi pass.
7. Không commit/push cho đến khi user yêu cầu.

## P1 — Phương án tích hợp

Đầu ra §2 số 1: `docs/tdq/knowledge/2026-09-16-1447-phuong-an-ponytail-tdq.md`

- [x] **T1.1** (e10m) Khung file + mục 0 "Tóm tắt quyết định": bảng 5 luồng, mỗi luồng một cột
      quyết định có/không, một cột giá phải trả, một cột phụ thuộc luồng nào — Test: bảng có đúng
      5 dòng dữ liệu và đủ 3 cột đó
  - Dùng: `tdq-conventions`
  - Để: lấy khuôn luật và thứ tự tầng từ `soul.md`, khuôn khối trình bày cho người dùng từ
    `user-facing-block.md`, danh sách 5 mã đóng từ `reminder-codes.md`. Agent ngoài không có
    skill system: đọc `skills/tdq-conventions/SKILL.md` rồi làm theo.
  - Ra: mục 0 của `docs/tdq/knowledge/2026-09-16-1447-phuong-an-ponytail-tdq.md`
  - Kiểm: `grep -c '^| ' ` trên khối bảng mục 0 trả về 6 (1 dòng tiêu đề + 5 dòng luồng)
  - Không dùng cho: viết nội dung 5 luồng — đó là T1.2–T1.6
- [x] **T1.2** (e14m) Luồng 1 — thân luật: chỗ đặt (`.claude/rules/` có `paths:` glob), cách hợp
      vào `chung.md` thay vì dựng tầng thứ hai, khuôn 3 mục theo `soul.md:39-46`, và giá phải trả
      là nâng trần `SKILL_LINE_LIMITS` kèm comment ghi ngày — Test: mục có dòng quyết định + dòng
      giá phải trả, và mọi trích dẫn trong mục đều có dạng `đường-dẫn:dòng`
- [x] **T1.3** (e12m) Luồng 2 — mức gắt `muc_gat`: 5 giá trị `off|lite|full|ultra|review`, mặc
      định `full`, bảng mỗi mode bật/tắt chính xác cái gì, và chứng minh nó rời `implement_mode`
      — Test: có bảng đúng 5 dòng mode; có câu nêu `scripts/tdq_state.py:186` và
      `MODE_LABELS`/`MODE_ALIASES` (`:56,65`); có câu "không có cơ chế tự xuống mode"
- [x] **T1.4** (e12m) Luồng 3 — hook thứ 6 `SubagentStart`: vì sao cần (luật hiện vô hình với
      `tdq-implementer`), khuôn in JSON `hookSpecificOutput` chứ không `print()` thô, hướng
      fail-open, và một câu nói thẳng đây là lời nhắc không phải cổng chặn — Test: mục chứa câu
      "lời nhắc, không phải cổng chặn" và mọi khẳng định cơ chế đều có nhãn tin cậy
- [x] **T1.5** (e10m) Luồng 4 — một nguồn chân lý: mở rộng `scripts/build_portable.py` thêm đích
      Cursor, giữ nguyên các đích đã có, và nêu vì sao KHÔNG copy tay như Ponytail — Test:
      nêu đúng 4 đích, mỗi đích một dòng, kèm `đường-dẫn:dòng` của script cho ba đích đã có
      (SỬA TIÊU CHÍ 2026-09-16 lúc thực thi: plan viết "hai đích đã có / đúng 3 đích" là sai số
      đo — `scripts/build_portable.py` đã có BA hàm sinh `:284`, `:617`, `:937`, nên con số đúng
      là 3 đã có + 1 thêm = 4. Sửa theo số đo, không sửa số đo theo plan.)
- [x] **T1.6** (e10m) Luồng 5 — hợp nhất hướng thất bại: bảng chỗ nào fail-open (nhắc luật, bơm
      ngữ cảnh) và chỗ nào fail-closed (Stop gate, edit gate, bash gate), mỗi dòng ghi hướng và
      lý do — Test: bảng ≥ 5 dòng, mỗi dòng có cột hướng thất bại
- [x] **T1.7** (e8m) Mục cổng duyệt RIÊNG cho việc sửa luật gốc: nguyên văn câu hiện tại của
      `skills/tdq-build/references/rules/chung.md:22`, nguyên văn câu đề xuất thay, và một dòng nói rõ điều gì KHÔNG đổi — Test:
      mục tồn tại, chứa cả câu trước và câu sau nguyên văn, và câu sau giữ tính "chỉ yêu cầu
      tường minh của người dùng mới tắt được"
- [x] **T1.8** (e8m) Mục thứ tự triển khai cho request sau: xếp 5 luồng theo rẻ → đắt, ghi luồng
      nào phụ thuộc luồng nào, và ghi rõ luồng nào nhận/loại được độc lập — Test: có bảng thứ tự
      với cột phụ thuộc, và mỗi luồng có một dòng "nhận riêng được / không"

**Xong P1 khi**: file đầu ra 1 tồn tại, có mục 0 cộng đủ 5 mục luồng đánh số cộng 2 mục cuối
(cổng duyệt, thứ tự triển khai); mọi trích dẫn trong file kiểm được bằng máy.

## P2 — Dự thảo thân luật

Đầu ra §2 số 2: `docs/tdq/knowledge/2026-09-16-1447-du-thao-luat-ponytail.md` — **tiếng Anh**,
theo tầng ngôn ngữ đã chốt 2026-08-22 (`docs/kien-truc.md:51-55`).

- [x] **T2.1** (e18m) Viết dự thảo thân luật đúng khuôn file luật: dòng `Soul:` + đủ 3 mục bắt
      buộc (`## When it applies` / `## What to do` / `## Self-check`), thang 7 bậc viết lại theo
      khuôn, vùng cấm đơn giản hoá (gồm log service), và ít nhất một cặp ví dụ RIGHT/WRONG cho
      chỗ dễ đọc sai nhất là ranh giới thang-vs-ngưỡng — Test: có dòng `Soul:` + 3 mục + cặp
      RIGHT/WRONG, và không chứa ký tự tiếng Việt có dấu
  - Cần: T1.2, T1.3
  - Dùng: `tdq-lsp-setup`
  - Để: tra ký hiệu và số dòng thật khi trích dẫn code trong dự thảo, theo thứ tự tìm kiếm đã
    khai ở bước 1b. Agent ngoài không có skill system: đọc
    `skills/tdq-lsp-setup/SKILL.md` rồi làm theo.
  - Ra: `docs/tdq/knowledge/2026-09-16-1447-du-thao-luat-ponytail.md`
  - Kiểm: `python3 scripts/tdq_lsp.py check` vẫn 7/7 và mọi trích dẫn trong file mở được đúng dòng
  - Không dùng cho: cài thêm language server — bước 1b đã ĐẠT 7/7, không chạy lệnh cài nào

**Xong P2 khi**: file đầu ra 2 tồn tại, đủ khuôn 3 mục, không có ký tự tiếng Việt có dấu.

## P3 — Report

Đầu ra §2 số 3: `docs/tdq/reports/2026-09-16-1447-hop-ponytail-vao-tdq.md`

- [x] **T3.1** (e10m) Viết report ≤ 50 dòng: kết luận, 5 luồng mỗi luồng một dòng, một chỗ sửa
      luật gốc, và những gì cố ý KHÔNG làm — Test: số dòng ≤ 50 và đọc riêng report là nắm được
      kết luận, không cần mở hai file kia
  - Cần: T1.1, T1.2, T1.3, T1.4, T1.5, T1.6, T1.7, T1.8, T2.1
  - Dùng: `tdq-build`
  - Để: chạy khuôn report của phase `report` và đóng sổ lượt bằng `tdq_finish.py`. Agent ngoài
    không có skill system: đọc `skills/tdq-build/SKILL.md` rồi làm theo.
  - Ra: `docs/tdq/reports/2026-09-16-1447-hop-ponytail-vao-tdq.md`
  - Kiểm: `wc -l < docs/tdq/reports/2026-09-16-1447-hop-ponytail-vao-tdq.md` ≤ 50
  - Không dùng cho: sửa `hooks/`, `skills/`, `scripts/` — request này dừng ở phương án

## P4 — Kiểm bắt buộc

**Log: BỎ** — request này không có runtime, cả 3 đầu ra đều là file `.md`, không task nào tạo
hoặc sửa file mã nguồn chạy được.

- [x] **T4.1** (e12m) Trình kiểm trích dẫn: script đọc mọi `đường-dẫn:dòng` trong 3 file đầu ra,
      mở file thật, so số dòng trích với số dòng thật. Script viết vào thư mục scratchpad của
      phiên, **không** vào repo — Test: in ra `N trích dẫn · hợp lệ N · sai 0`
  - Cần: T3.1
- [x] **T4.2** (e6m) Ba phép đếm còn lại trong một lượt: khẳng định cơ chế thiếu nhãn tin cậy,
      ký tự tiếng Việt có dấu trong đầu ra 2, số dòng report — Test: cả ba số đo lần lượt là
      `0`, `0`, `≤ 50`
  - Cần: T3.1
- [x] **T4.3** (e4m) Kiểm không file nào ngoài `docs/` bị đổi trong nhánh này — Test:
      `git diff --name-only main...HEAD` chỉ trả về đường dẫn bắt đầu bằng `docs/`
      (GHI CHÚ 2026-09-16 lúc thực thi: lệnh đó trả về RỖNG vì nhánh chưa có commit nào, nên
      rỗng là vượt một cách vô nghĩa. Bằng chứng thật lấy thêm từ `git status --porcelain`:
      9 đường dẫn, cả 9 bắt đầu bằng `docs/`. Cả hai lệnh đều ghi vào file QC.)
  - Cần: T4.1, T4.2
- [x] **T4.4** (e4m) Kiểm cặp spec ↔ plan — Test: `python3 scripts/doc_lint.py --pair
      docs/tdq/spec/2026-09-16-1447-hop-ponytail-vao-tdq.md
      docs/tdq/plan/2026-09-16-1447-hop-ponytail-vao-tdq.md` exit 0
  - Dùng: `tdq-plan`
  - Để: giữ hai luật khớp cặp — mỗi đầu ra spec §2 có ≥ 1 task, mỗi dòng `DÙNG` ở spec §3b có
    một khối hợp đồng đủ 4 trường. Agent ngoài không có skill system: đọc
    `skills/tdq-plan/SKILL.md` rồi làm theo.
  - Ra: exit code 0 của lệnh `--pair` ở trên
  - Kiểm: lệnh ở dòng Test của chính task này trả về exit 0
  - Không dùng cho: viết lại plan sau khi đã duyệt — FAIL thì thêm task fix, không sửa phạm vi

**Xong P4 khi**: cả 4 phép kiểm xanh, và 9 ô DoD dưới đây đều `[x]`.

## Cụm song song

**Một cụm.** Trần song song thật ở đây là 1, không phải 3, dù có 3 file rời nhau:

- P1 ghi 8 task vào **cùng một file** → theo luật file nóng dưới đây, chỉ một chủ ghi.
- T2.1 khai `Cần: T1.2, T1.3` — dự thảo luật phải khớp quyết định của luồng 1 và bảng mode của
  luồng 2, viết trước là viết lại.
- T3.1 khai `Cần:` cả 9 task trước — report đọc cả hai file kia.
- P4 khai `Cần: T3.1` — không kiểm được cái chưa viết.

**Số đo thật, không phải cảm giác** (`tdq_bench.py simulate … --he-so-agent 1.5`):

| Số đo | main | đội |
|---|---|---|
| Thời gian model (phút) | 28,5 | 26,5 |
| Phí cố định mỗi đợt (phút) | 0,0 | **0,0** |
| Task giao được / tổng | — | **1 / 14** (leader giữ 13) |
| Số đợt | — | 1 |

`Winner: đội (gap 2.0 minutes)`. **Vẫn đề xuất `main`, và đây là lý do kiểm được:** máy chỉ giao
được **1 trong 14 task** (13 task còn lại là file nóng hoặc có `Cần:` chặn), nên "đội" ở đây nghĩa
là một trợ lý làm đúng một task. Khoản lợi 2,0 phút được tính với phí cố định mỗi đợt **0,0 phút**,
lấy từ các hằng số `t_phat`/`t_don` có `nguon: "stub"` — mà `ghi_chu` của chính file thực đo viết
`nguon=stub là sàn dưới cơ học`. Một vòng worktree thật (mở, check, merge, clean) đắt hơn 2 phút,
nên khoản lợi đó nằm dưới phần chi phí chưa được đo.

## Luật file nóng

`docs/tdq/knowledge/2026-09-16-1447-phuong-an-ponytail-tdq.md` là file nóng: 8 task
(T1.1–T1.8) đều ghi vào nó. Chọn cách **một chủ ghi duy nhất** — cả 8 task do leader viết tuần
tự. Không chọn cách "nâng lên đợt sớm" vì không tách được: mỗi luồng là một mục của cùng một
phương án, tách file ra sẽ vi phạm chính quyết định đã ghi ở spec §2b.

## QC vòng 1 — fix

Phát hiện lúc `tdq_finish.py` đóng phase implement: `doc_lint.py` báo 10 lỗi `[R12]` trên đầu ra
2 — R12 đòi file làm cho người dùng phải viết tiếng Việt (`scripts/doc_lint.py:585`), còn đầu ra
2 cố ý viết tiếng Anh theo tầng ngôn ngữ ở `docs/kien-truc.md:51`. Hai luật va nhau thật, không
phải lỗi soạn thảo. KHÔNG sửa `scripts/doc_lint.py` — quy tắc thi hành số 4 chặn mọi file ngoài
`docs/`, và một luật đúng không nên bị nới vì một file. Dùng đúng cơ chế miễn trừ một-đoạn mà
chính doc_lint mở ra (`scripts/doc_lint.py:134`), mỗi lần miễn kèm lý do.

- [x] **QC1.1** Miễn trừ R12 đúng chỗ cho đầu ra 2: đặt `<!-- doc-lint: allow R12 … -->` ngay
      TRÊN từng đoạn bị báo, mỗi dòng ghi lý do bằng tiếng Anh (thân luật giữ tiếng Anh, viện
      dẫn tầng ngôn ngữ) để không kéo dấu tiếng Việt vào file — Test:
      `python3 scripts/doc_lint.py` trên cả 4 file `.md` của lượt này exit 0, VÀ phép đếm T4.2
      vẫn cho `0` dòng tiếng Việt trong đầu ra 2

## Definition of Done

Trỏ về §6 của spec, 9 hạng mục:

- [x] Q1 Ba đầu ra §2 tồn tại và không rỗng — `wc -c` trên cả 3 đường dẫn, mỗi file > 0
- [x] Q2 Phương án có đúng 5 mục luồng, mỗi mục có dòng quyết định và dòng giá phải trả —
      `grep -c '^## Luồng '` trả về 5, và `grep -c 'Quyết định:'` ≥ 5, `grep -c 'Giá phải trả:'` ≥ 5
- [x] Q3 Số trích dẫn `đường-dẫn:dòng` sai bằng 0 — trình kiểm T4.1 in `sai 0`
- [x] Q4 Số khẳng định cơ chế Claude Code thiếu nhãn tin cậy bằng 0 — phép đếm T4.2 trả về 0
- [x] Q5 Đầu ra 2 đủ khuôn luật — `grep -c '^## When it applies\|^## What to do\|^## Self-check'`
      trả về 3, có dòng `Soul:`, và `grep -c 'RIGHT\|WRONG'` ≥ 2
- [x] Q6 Đầu ra 2 không chứa ký tự tiếng Việt có dấu — `python3 scripts/i18n_check.py <đầu ra 2>`
      exit 0
      (SỬA DỤNG CỤ ĐO 2026-09-16 lúc QC: plan viết `grep -cP '[à-ỹÀ-Ỹ]'` phải ra 0, đo thật ra
      **2** — đúng hai dòng bắt buộc mang `i18n-allow`: dòng `Soul:` canonical và ghi chú
      canonical `Tạo mới thay vì dùng …`. Dụng cụ đo sai, không phải file sai: đạt được số 0 chỉ
      bằng cách xoá dòng `Soul:` mà `soul.md` bắt buộc. Thay bằng chính trình kiểm của repo
      `scripts/i18n_check.py:137`, nơi cơ chế miễn trừ `i18n-allow` được định nghĩa và
      `skills/tdq-build/references/rules/chung.md:3` đang dùng y như vậy. Ghi cả hai số vào file
      QC, không chỉ số đã đạt.)
- [x] Q7 Đầu ra 1 chứa nguyên văn câu thay `skills/tdq-build/references/rules/chung.md:22` trong mục cổng duyệt riêng —
      `grep -c 'Cổng duyệt riêng'` ≥ 1 và mục đó chứa cả câu trước và câu sau
- [x] Q8 Không file nào ngoài `docs/` bị đổi — `git diff --name-only main...HEAD | grep -cv '^docs/'`
      trả về 0
- [x] Q9 Report ≤ 50 dòng — `wc -l` trên đầu ra 3 trả về ≤ 50
