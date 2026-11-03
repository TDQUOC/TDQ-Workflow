# BRIEF — Hướng C: nạp reference theo nhu cầu

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> A và mở request tiếp tục

Bối cảnh: user đã chốt tách đề án tối ưu context thành nhiều request theo thứ tự
D → C → B → A(hybrid) → E. Hướng D vừa đóng ở request `2026-08-19-0046`. "Mở request
tiếp tục" = hướng C — nạp reference theo nhu cầu (mục 3 của
[de-an-toi-uu-context.md](../audit/de-an-toi-uu-context.md)).

**Hiểu đầu tiên:**
- Mục tiêu: giảm token thân skill + reference bị nạp trong một request lane full, mà
  không đổi một chữ nào của luật.
- Phạm vi đoán: đo lại phần reference bằng số thật, tìm file reference đủ lớn để tách
  tiếp, rồi tách — nội dung giữ nguyên, chỉ đổi thời điểm nạp.
- Chỗ chưa rõ: (a) mức tách sâu tới đâu thì dừng, (b) có patch thật vào `skills/`
  luôn trong request này hay chỉ đo + đề xuất như hai vòng trước, (c) đo trước/sau
  bằng cách nào để không tạo ra mức "tiết kiệm" ảo.

**Cảnh báo đã ghi sẵn trong đề án, phải tôn trọng:** 70.924 token là TRẦN TRÊN (cộng cả
25 reference), không phải lượng một request thật tiêu — lấy trần đi so với số thật sau
tối ưu sẽ ra mức tiết kiệm ảo. Và bài học vừa rút từ hướng D: kiểm tiền đề bằng tài liệu
chính thức TRƯỚC khi tin bất kỳ con số tiết kiệm nào.

## Hiểu & kiến thức

### Năng lực dùng được

| Skill/công cụ | Nguồn | Phán quyết | Vì sao |
|---|---|---|---|
| `tdq-intake`, `tdq-spec`, `tdq-plan`, `tdq-build` | plugin:tdq-workflow | DÙNG | chạy đúng phase của request |
| `tdq-conventions` | plugin:tdq-workflow | NỀN | skill khung |
| `tdq-status`, `tdq-check-status` | plugin:tdq-workflow | KHÔNG | báo trạng thái, không liên quan |
| `scripts/skill_tokens.py` | project | DÙNG | đo token thân + reference bằng tokenizer thật |
| `scripts/skill_inventory.py` | project | DÙNG | kiểm kê năng lực (B0) |
| `mcp__tavily-primary__*` | MCP | DÙNG | đã chạy 1 truy vấn kiểm tiền đề |
| Đã xét 278 skill khác | plugin/built-in | KHÔNG | khác lĩnh vực |

### Phát hiện 1 (chặn đường) — tách sâu thêm là ĐI NGƯỢC hướng dẫn chính thức

Tiền đề của hướng C trong đề án cũ là "vài file reference đủ lớn để tự chúng nên tách
tiếp". Hướng dẫn chính thức của Anthropic
(`platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`) và hai nguồn
độc lập nói ngược lại: **giữ reference đúng MỘT tầng từ SKILL.md**. Nguyên văn nguồn thứ
hai: *"Claude may partially read files when they're referenced from other referenced
files"* và *"Do not create reference files that point to other reference files. If your
knowledge structure is that deep, reorganize it into multiple skills or flatten the
hierarchy."*

Nghĩa là tách sâu thêm không chỉ không tiết kiệm — nó đẩy luật xuống tầng mà model có thể
chỉ đọc MỘT PHẦN. Rủi ro đó nằm trên trục `chất lượng`, trục cao nhất của soul.

### Phát hiện 2 — đo bằng đồ thị link: 14/37 reference nằm ở tầng ≥ 2

Dựng đồ thị link giữa 7 `SKILL.md` và 37 file reference (giải cả link tương đối cùng thư mục):

| Chỉ số | Số |
|---|---|
| Reference được một `SKILL.md` trỏ THẲNG (đúng một tầng) | 23/37 |
| Reference chỉ tới được qua reference khác (tầng ≥ 2) | **14/37** |
| Link reference → reference | **36** |
| Chuỗi sâu nhất | **tầng 4**: `SKILL.md` → `clean-code.md` → `rules/chung.md` → `rules/index.md` → `rules/<ngôn ngữ>.md` |

Tám file không có link markdown nào trỏ tới: `rules/cpp` · `rules/csharp` · `rules/go` ·
`rules/html` · `rules/rust` · `measure-scenario.md` · `plugin-routing.md` ·
`issue-triage.md`. Thư mục `rules/` tới được nhưng bằng đường KHÁC — `clean-code.md` và
`spec-template.md` nhắc đường dẫn dạng chữ thường, không phải link — nên nó nằm ở tầng 3-4,
đúng chỗ hướng dẫn cảnh báo model "có thể chỉ đọc một phần".

### Phát hiện 3 — `skill_tokens.py` đo thiếu 14.554 token

Dòng 138 dùng `glob(".../references/*.md")` không đệ quy → **bỏ sót cả thư mục
`references/rules/` (10 file, 14.554 token)** của `tdq-build`. Mọi con số hướng C trong
đề án 2026-08-17 (55.719 token reference) vì thế đều thấp hơn thực tế. Đây đúng kiểu lỗi
đã làm hướng D sai: tin con số mà không kiểm cách đo.

### Phát hiện 4 — số thật của một request, đo lại đầy đủ

| Khối | Token | Ghi chú |
|---|---|---|
| Thân 5 skill | 16.128 | luôn nạp khi chạy lane full |
| Reference THẬT mở (13 file) | 34.668 | lane full · mode main · việc tài liệu |
| **→ một request thật** | **50.796** | |
| Reference KHÔNG mở (12 file) | 24.564 | `quick-lane`, `team-mode`, `clean-code`… |
| `rules/` (10 file) | 14.554 | chỉ mở khi có code đúng ngôn ngữ đó |
| TRẦN đủ file | 93.739 | `skill_tokens.py` đang báo 74.846 |

Progressive disclosure hiện có **đã ăn 46%** trần rồi (93.739 → 50.796). Phần còn cắt
được nằm trong 34.668 token đang thật sự mở, mà phần lớn là khuôn bắt buộc
(`plan-template` 4.437, `spec-template` 3.580, `user-facing-block` 3.402, `qc` 2.970).

### Phát hiện 5 — thân skill đều đạt chuẩn, không phải chỗ để cắt

Chuẩn chính thức: thân SKILL.md dưới 500 dòng. Bộ TDQ: dài nhất là `tdq-conventions`
143 dòng, tổng 7 skill 622 dòng. Không có gì để cắt ở tầng thân.

### Phát hiện 6 (việc rẻ, có nguồn) — 8 file reference > 100 dòng chưa có mục lục

Hướng dẫn: file reference dài hơn 100 dòng nên có mục lục ở đầu để model đọc chọn lọc
thay vì nuốt cả file. Hiện 8/37 file vượt 100 dòng và **không file nào có mục lục**:
`quick-lane` 177 · `plan-template` 142 · `spec-template` 136 · `team-mode` 133 ·
`user-facing-block` 120 · `scope-round` 115 · `clean-code` 105 · `qc` 101.

### Phạm vi đã chốt

- Mặt CHỌN: độ tin cậy của luật (phẳng hoá tầng) · bảo trì công cụ đo (`skill_tokens.py`) · hiệu năng context (mục lục, cắt trùng)
- Mặt LOẠI: bảo mật · hiệu năng runtime của hook/script · trải nghiệm người dùng cuối · tương thích harness ngoài Claude/Codex
- Bối cảnh: 37 file reference · 7 skill · một request lane full tiêu 50.796 token · bộ đang chạy thật hằng ngày, một người giữ
- Mức đầu tư suy ra: vừa — vì bộ đang chạy thật (không phải prototype) nhưng một người giữ và mọi thay đổi đều đảo ngược được bằng git

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Kiểm kê năng lực (B0) | CÓ (xong) | 6/284 skill liên quan |
| Đọc code | CÓ (xong) | đã dựng đồ thị link + đo token từng file |
| Research web | CÓ (xong, 1 truy vấn) | kiểm tiền đề "tách sâu thêm" — và tiền đề sai |
| Vòng scope | CÓ (xong) | user chốt 1ABC 2A 3A |
| Interview chi tiết thêm | BỎ | ba câu scope đã khoá hết chỗ đổi kết quả; cách phẳng hoá là quyết định kỹ thuật, trình ở spec để user bác được ở cổng duyệt |
| QC độc lập (agent) | BỎ | sửa tài liệu luật, có test khoá tự động là bằng chứng mạnh hơn agent đọc lại |
| Chia subagent | BỎ | 5 nhóm task phụ thuộc tuyến tính qua cùng bộ file, tách ra chỉ thêm chi phí merge |

## Hỏi đáp

**Vòng lane:** user chọn chế độ chuyên sâu (deep).

**Vòng scope — trả lời: `1abc 2a 3a`**

1. Mặt bao quanh: A + B + C — độ tin cậy của luật, bảo trì công cụ đo, hiệu năng context.
   Không có mặt nào bị loại trong ba mặt đã hỏi.
2. Dừng ở đâu: A — **patch thật vào `skills/`**, có test khoá, đo lại trước/sau.
3. Ba bản: A — sửa cả ba + dựng test khoá đồng bộ.
   **Đối chiếu code sau khi hỏi:** `portable_claude/` và `portable_codex/` KHÔNG viết tay
   mà **sinh từ `skills/`** bằng `scripts/build_portable.py`, kèm `manifest.json` có
   sha256 từng file. Nên "sửa cả ba bản" thực chất = sửa `skills/` rồi chạy lại
   `build_portable.py`. Phần còn thiếu thật sự là **test khoá mọi file reference của
   `skills/` đều có mặt ở cả hai bản portable** — hiện `test_build_portable.py` kiểm đủ
   thư mục và biến môi trường, chưa kiểm đủ danh sách file reference.
