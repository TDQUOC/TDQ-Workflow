# BÁO CÁO — Quét instruction Claude Code: chuyển gì vào plugin, xoá bớt gì

Ngày: 2026-09-01 · Spec: ../spec/2026-09-01-2301-quet-instruction-vao-plugin.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Mục lục

- 1. Kết luận ngắn
- 2. Hai sự thật nền
- 3. Bảng phán quyết 57 dòng
- 4. Chuyển đi đâu
- 5. Nhóm mồi khởi động — vì sao không xoá được
- 6. Bản CLAUDE.md đề xuất
- 7. settings.json
- 8. Cái giá của phương án

## 1. Kết luận ngắn

`~/.claude/CLAUDE.md` 57 dòng có thể xuống **29 dòng (−49 %)** mà không mất luật nào, ở mức
thận trọng user chốt: chỉ XOÁ dòng vừa trùng vừa được hook/gate **chặn cứng**.

| Phán quyết | Số dòng | Nghĩa |
|---|---|---|
| XOÁ | 10 | luật đã có ở skill VÀ có hook/gate chặn cứng — instruction nhắc lại là thừa |
| GIỮ | 21 | mồi khởi động, hoặc tiêu đề/khung, hoặc dòng trỏ |
| GIỮ (rút gọn) | 12 | trùng ở skill nhưng KHÔNG hook nào chặn — gộp thành dòng trỏ, không xoá hẳn |
| CHUYỂN | 5 | luật CHƯA có ở plugin — phải viết vào skill trước, rồi mới bỏ khỏi instruction |
| (trống) | 9 | dòng rỗng, không tính |

Điểm quan trọng: **5 dòng CHUYỂN chưa chuyển được ngay**. Chúng chưa tồn tại ở plugin, nên
phải làm ở một request sau; báo cáo này chỉ điểm mặt và chỉ đích.

## 2. Hai sự thật nền

**Sự thật 1 — hook là lớp thi hành phổ quát, skill thì không.**
`hooks/scripts/prompt_context.py:139` chạy ở mọi `cwd`: `state = load(cwd)`, `state is None`
thì vẫn in `[TDQ:INTAKE]`. Đã kiểm bằng thực nghiệm: chạy hook với `cwd` là thư mục trống
không có `docs/tdq/`, đầu ra vẫn ra đúng dòng `[TDQ:INTAKE]`. Nghĩa là luật nào có hook đứng
sau thì instruction không cần nhắc — nó tới nơi ở mọi project, mọi lượt, kể cả khi không skill
nào được nạp.

Ba hook thi hành thật (không chỉ nhắc):

| Hook | Lượt | Luật nó bảo đảm |
|---|---|---|
| `hooks/scripts/session_start.py:21` | SessionStart | "state chỉ ghi qua `scripts/tdq_state.py`" |
| `hooks/scripts/prompt_context.py:152` | UserPromptSubmit | "mọi prompt mới → mở intake" |
| `hooks/scripts/bash_gate.py:20`, `:28` | PreToolUse | chặn tên nhánh `claude\|antigravity\|gemini\|codex`; chặn commit chứa "generated with…"/"được tạo bởi…"/Co-Authored-By |
| `hooks/scripts/edit_gate.py:165` | PreToolUse | chặn sửa code khi plan chưa tick — `[TDQ:TICK]` |
| `hooks/scripts/stop_gate.py:271` | Stop | chặn kết lượt khi repo đổi mà chưa ghi working log — `[TDQ:LOG]` |

**Sự thật 2 — `skills/tdq-conventions/SKILL.md` (164 dòng) đã chép gần trọn CLAUDE.md.**
Đối chiếu thật, mỗi dòng kiểm lại bằng `sed -n` thấy đúng:

| CLAUDE.md | Đã sống ở |
|---|---|
| mục 2 tên nhánh | `skills/tdq-conventions/SKILL.md:124` |
| mục 2 commit message | `skills/tdq-conventions/SKILL.md:125` |
| mục 2 chỉ commit khi user bảo | `skills/tdq-conventions/SKILL.md:126` |
| mục 3 tavily-primary | `skills/tdq-conventions/SKILL.md:130` |
| mục 3 mọi kết luận có nguồn | `skills/tdq-conventions/SKILL.md:132` |
| mục 3 cấm lộ API key | `skills/tdq-conventions/SKILL.md:134` |
| mục 5 working log | `skills/tdq-conventions/SKILL.md:115` |
| mục 5 log service | `skills/tdq-conventions/SKILL.md:163` |
| mục 6 sub-agent đặt tên | `skills/tdq-conventions/SKILL.md:138` |
| mục 6 tick `[x]` | `skills/tdq-conventions/SKILL.md:164` |
| mục 1 khuôn option | `skills/tdq-conventions/references/user-facing-block.md:60` |
| mục 1 đánh số câu hỏi | `skills/tdq-conventions/references/user-facing-block.md:63-82` |
| mục 8 plugin ngoài | `skills/tdq-conventions/references/plugin-routing.md:7-11` |

## 3. Bảng phán quyết 57 dòng

Tiêu chí: (a) luật đã có ở skill/hook chưa? (b) có cần đúng ở cửa sổ TRƯỚC khi skill đầu tiên
nạp không? Trùng + có hook chặn cứng → XOÁ. Trùng + cần mồi → GIỮ. Chưa trùng → CHUYỂN.

| Dòng | Nội dung rút gọn | Phán quyết | Lý do |
|---|---|---|---|
| 1 | `# Quy tắc làm việc cho Claude` | GIỮ | tiêu đề file |
| 2 | (rỗng) | — | dòng trắng |
| 3 | `## 1. Quy trình chung` | GIỮ | tiêu đề mục |
| 4 | làm như chuyên gia, không đoán | GIỮ | mồi — chi phối cả câu trả lời ở tầng `nhỏ`, chưa skill nào nạp |
| 5 | interview trước khi rõ; khuôn option | GIỮ | mồi — câu hỏi có thể xuất hiện trước khi conventions nạp |
| 6 | khuôn `- A (đề xuất)`, cấm gộp đoạn văn | GIỮ (rút gọn) | trùng `user-facing-block.md:60`, nhưng là mồi |
| 7 | đánh số câu hỏi `1.`, `2.` | GIỮ (rút gọn) | trùng `user-facing-block.md:63`, nhưng là mồi |
| 8 | số chạy liên tục, để trả lời `1a 2b` | XOÁ | phần giải thích, đã đủ ở `user-facing-block.md:66` |
| 9 | gửi xong soát lại | XOÁ | đã có ở `user-facing-block.md:81-82` |
| 10 | plan → tự review → chờ user duyệt | GIỮ | mồi — quyết định có mở request hay không |
| 11 | không tự vào plan mode | CHUYỂN | CHƯA có ở plugin; `approval.md` chỉ nói cách NHẬN BIẾT duyệt |
| 12 | (rỗng) | — | dòng trắng |
| 13 | `## 2. Git & worktree` | GIỮ | tiêu đề mục |
| 14 | chưa có git → được init; kiểm merge worktree | CHUYỂN | CHƯA có ở plugin |
| 15 | tên nhánh không bắt đầu bằng claude/… | XOÁ | `SKILL.md:124` + `bash_gate.py:20` **chặn cứng** |
| 16 | commit message không chứa dấu vết AI | XOÁ | `SKILL.md:125` + `bash_gate.py:28` **chặn cứng** |
| 17 | chỉ commit/push khi user yêu cầu | XOÁ | `SKILL.md:126`, và không lệnh nào chạy được nếu chưa qua `bash_gate` |
| 18 | ngoại lệ: build TDQ bị chặn → tự commit | CHUYỂN | CHƯA có ở plugin — mất dòng này là mất đường thoát |
| 19 | (rỗng) | — | dòng trắng |
| 20 | `## 3. Research & độ tin cậy` | GIỮ | tiêu đề mục |
| 21 | search nhiều hướng; tavily-primary | GIỮ (rút gọn) | trùng `SKILL.md:130` nhưng KHÔNG có hook chặn |
| 22 | cấm đưa API key vào câu trả lời/log/prompt | GIỮ | trùng `SKILL.md:134`, nhưng hậu quả không đảo ngược được → giữ ở mức thận trọng |
| 23 | mọi kết luận phải có nguồn | GIỮ (rút gọn) | trùng `SKILL.md:132`, không hook chặn |
| 24 | (rỗng) | — | dòng trắng |
| 25 | `## 4. Trình bày` | GIỮ | tiêu đề mục |
| 26 | ngắn gọn nhất có thể | GIỮ | mồi — áp cho mọi câu trả lời, kể cả ngoài TDQ |
| 27 | (rỗng) | — | dòng trắng |
| 28 | `## 5. Log` | GIỮ | tiêu đề mục |
| 29 | khi develop: log đủ, có timestamp | GIỮ (rút gọn) | trùng `SKILL.md:163`, không hook chặn |
| 30 | sản phẩm build có log service, tắt qua config | GIỮ (rút gọn) | trùng `SKILL.md:163` |
| 31 | turn đổi repo → ghi `docs/workinglog/` | XOÁ | `SKILL.md:115` + `stop_gate.py:271` **chặn cứng** kết lượt |
| 32 | (rỗng) | — | dòng trắng |
| 33 | `## 6. TDQ Workflow — mặc định tuyệt đối` | GIỮ | tiêu đề mục |
| 34 | mọi prompt mới → skill `tdq-intake` | XOÁ | `prompt_context.py:152` in `[TDQ:INTAKE]` **mỗi lượt, mọi project** |
| 35 | thấy `[TDQ:INTAKE]` → mở intake trước | XOÁ | `session_start.py:21` in đúng luật này mỗi phiên |
| 36 | chỉ NGƯỜI DÙNG duyệt; mơ hồ thì hỏi lại | GIỮ | mồi — sai ở đây là hỏng cả request, hook chỉ cảnh báo chứ không chặn |
| 37 | ghi state chỉ qua `tdq_state.py` | XOÁ | `session_start.py:22` in nguyên câu này mỗi phiên |
| 38 | gộp gate: duyệt spec → viết plan ngay | GIỮ (rút gọn) | trùng tinh thần `tdq-spec/SKILL.md`, nhưng chi phối nhịp trả lời |
| 39 | duyệt plan → hỏi mode ngay turn đó | GIỮ (rút gọn) | như trên |
| 40 | câu duyệt có sẵn mode → ghi cả hai | GIỮ (rút gọn) | như trên |
| 41 | spec/plan/report tiếng Việt; tick `[x]` | XOÁ | ngôn ngữ: `SKILL.md:19-22` (`doc_lang`); tick: `SKILL.md:164` + `edit_gate.py:165` **chặn cứng** |
| 42 | cuối turn đổi code → `graphify extract` | GIỮ (rút gọn) | `tdq_finish.py` làm hộ, nhưng KHÔNG hook nào chặn nếu quên gọi |
| 43 | sub-agent đặt tên `<model>-<effort>-<việc>` | GIỮ (rút gọn) | trùng `SKILL.md:138`, không hook chặn |
| 44 | (rỗng) | — | dòng trắng |
| 45 | `## 7. Chi tiết ở đâu` | GIỮ | tiêu đề mục — đây là khối trỏ, đúng vai |
| 46 | quy ước chung ở `tdq-conventions/` | GIỮ | dòng trỏ, đúng vai |
| 47 | lane, tầng `nhỏ`, khuôn spec/plan ở `tdq-*` | GIỮ | dòng trỏ, đúng vai |
| 48 | (rỗng) | — | dòng trắng |
| 49 | `## 8. Plugin ngoài` | GIỮ | tiêu đề mục |
| 50 | plugin đã bật → không phải xin phép | GIỮ (rút gọn) | trùng `plugin-routing.md:7`, là mồi (quyết định trước khi skill nạp) |
| 51 | vẫn hỏi trước khi cài plugin mới | GIỮ | mồi, hậu quả ra ngoài máy |
| 52 | …OAuth, ghi/xoá ra dịch vụ ngoài | GIỮ | mồi, hậu quả không đảo ngược được |
| 53 | (rỗng) | — | dòng trắng |
| 54 | `## 9. Bộ nhớ dài hạn` | GIỮ | tiêu đề mục |
| 55 | việc quan trọng → search mem0 | CHUYỂN | CHƯA có ở plugin TDQ; `mem0-memory` là skill user, không skill TDQ nào trỏ tới |
| 56 | project = tên repo, chốt xong `remember` | CHUYỂN | như trên |
| 57 | chi tiết: skill `mem0-memory` | GIỮ | dòng trỏ, đúng vai |

Cộng: XOÁ 10 · CHUYỂN 5 · GIỮ 21 · GIỮ (rút gọn) 12 · rỗng 9 = 57. Đếm bằng lệnh, không bằng mắt.

## 4. Chuyển đi đâu

Năm dòng CHUYỂN, mỗi dòng đúng một đích. Không đích nào chết — cả bốn file đều tồn tại.

| Dòng | Luật | Đích | Vì sao đích đó |
|---|---|---|---|
| 11 | không tự vào plan mode | `skills/tdq-conventions/references/approval.md` | file đang nói về cổng duyệt; "không tự vào plan mode" là luật cùng họ |
| 14 | chưa có git → được init; kiểm merge worktree | `skills/tdq-conventions/SKILL.md` §7 Git | §7 đã là chỗ của mọi luật git |
| 18 | ngoại lệ build TDQ bị chặn → tự commit | `skills/tdq-conventions/SKILL.md` §7 Git | phải nằm SÁT dòng 126 "never commit before the user asks", vì nó là ngoại lệ của đúng dòng đó |
| 55 | việc quan trọng → search mem0 trước khi kết luận | `skills/tdq-conventions/SKILL.md` §8 Research | mem0 là một lớp tra cứu, cùng họ với tavily ở §8 |
| 56 | project = tên repo; chốt xong `remember` | `skills/tdq-conventions/SKILL.md` §8 Research | như trên, viết chung một gạch đầu dòng với 55 |

Ba ràng buộc kiến trúc, soát từng cái:
- `docs/kien-truc.md:12` "luật thuộc `skills/`" — cả 5 đích đều nằm trong `skills/`, không đích
  nào rơi vào `scripts/`. KHÔNG phạm.
- `docs/kien-truc.md:15` "hook chỉ nhắc mã `[TDQ:*]` và chặn khi thiếu bằng chứng" — phương án
  này KHÔNG đề nghị thêm hook nào; 5 dòng đều đi vào skill. KHÔNG phạm.
- `docs/kien-truc.md:23` "`skills/` chỉ được nhắc TÊN lệnh của `scripts/`" — 5 dòng là luật
  hành xử, không dòng nào chép nội dung script. KHÔNG phạm.

## 5. Nhóm mồi khởi động — vì sao không xoá được

Đây là nhóm quan trọng nhất của báo cáo: các dòng **đã trùng với skill** nhưng vẫn phải ở lại,
vì có một cửa sổ mà không skill nào được nạp.

Cửa sổ đó có thật: `skills/tdq-intake/SKILL.md:12` định nghĩa **tầng `nhỏ`** — "answer or fix
on the spot, no request opened… No request, no `init` state, no plan, no QC". Ở tầng này
Claude trả lời thẳng, và nếu chính `tdq-intake` cũng chưa được nạp thì luật duy nhất còn hiệu
lực là CLAUDE.md.

| Dòng | Tình huống nó phải sống sót |
|---|---|
| 4 | user hỏi một câu kỹ thuật ngắn; không request nào mở, không skill nào nạp |
| 5, 6, 7 | phải hỏi lại một câu có option ngay trong lượt đầu, trước khi conventions kịp nạp |
| 10 | quyết định "có mở request không" xảy ra TRƯỚC khi intake được gọi |
| 22 | lệnh shell đầu tiên của lượt có thể đã chứa key nếu luật này vắng mặt |
| 26 | áp cho mọi câu trả lời, kể cả câu không liên quan TDQ |
| 36 | nhận nhầm một câu nói thành lời duyệt là hỏng cả request; hook chỉ cảnh báo, không chặn |
| 50, 51, 52 | quyết định gọi tool ngoài xảy ra ngay lượt đầu, hậu quả ra ngoài máy |

## 6. Bản CLAUDE.md đề xuất

29 dòng, giảm 49 %. Mọi luật bị bỏ đều nằm ở cột XOÁ (đã có hook chặn) hoặc cột CHUYỂN
(**phải viết vào skill TRƯỚC**, xem mục 8).

```markdown
# Quy tắc làm việc cho Claude

## 1. Quy trình chung
- Làm như chuyên gia kỹ tính: phân tích kỹ, research trước khi kết luận, không đoán.
- Yêu cầu chưa rõ → interview trước. Mọi câu hỏi có option phải ĐÁNH SỐ và mỗi option
  đúng 1 dòng, khuôn `- A (đề xuất): nội dung`.
  Luật đầy đủ: `skills/tdq-conventions/references/user-facing-block.md`.
- Đủ thông tin → plan → tự review → trình plan → **chờ user duyệt** mới làm. Mọi task.
  Không tự vào plan mode.

## 2. Trình bày & độ tin cậy
- Ngắn gọn nhất có thể, đi thẳng vào vấn đề chính.
- Không bao giờ đưa API key vào câu trả lời, log, lệnh shell hay prompt gửi model.
- Mọi kết luận phải có nguồn — không được bịa thông tin chưa xác định.

## 3. TDQ Workflow — mặc định tuyệt đối
- Chỉ NGƯỜI DÙNG duyệt, bằng chat thường. Câu chữ mơ hồ → HỎI lại, cấm tự suy diễn duyệt.
- Gộp gate: duyệt spec → viết plan ngay turn đó; duyệt plan → hỏi mode ngay turn đó.
  Câu duyệt đã nói sẵn mode → ghi cả hai, vào thẳng build, cấm hỏi lại.

## 4. Plugin ngoài
Mọi plugin đã bật sẵn ở user scope → không phải xin phép để dùng tool. Vẫn HỎI trước khi:
cài plugin/marketplace MỚI; chạy OAuth hay nhập credential; gọi tool GHI/XOÁ ra dịch vụ
ngoài (tạo page Notion, ghi DB, deploy, upload…).

## 5. Chi tiết ở đâu — đọc khi cần, KHÔNG chép lại vào đây
Quy ước chung (git, log, research, sub-agent, tick, graphify, QC): `skills/tdq-conventions/`.
Lane, tầng `nhỏ`, khuôn spec/plan, mode thực thi: các skill `tdq-*`.
Bộ nhớ dài hạn: skill `mem0-memory`.
```

Kiểm nhất quán: 10 dòng XOÁ biến mất vì hook/gate đã chặn cứng; 5 dòng CHUYỂN biến mất và có
đích ở mục 4; các dòng "GIỮ (rút gọn)" gộp vào mục 5 "Chi tiết ở đâu".

## 7. settings.json

Ba điểm, không in giá trị nào.

1. **Hai API key Tavily nằm dạng chữ thường trong khối `env`** (`TAVILY_API_KEY_PRIMARY`,
   `TAVILY_API_KEY_BACKUP`). File này không được mã hoá và hay bị chép theo khi backup hồ sơ
   `~/.claude/`. Đáng chuyển sang biến môi trường của shell (`~/.zshrc`) rồi để `settings.json`
   tham chiếu, hoặc để trống và nạp lúc chạy. Đây là quan sát, KHÔNG sửa theo phạm vi đã chốt.
2. `permissions.defaultMode = "bypassPermissions"` — mọi tool chạy không hỏi. Chính vì thế
   `hooks/scripts/bash_gate.py` mới là lớp chặn thật sự còn lại; luận điểm "xoá được vì có hook
   chặn" ở mục 3 đứng vững chính nhờ hook, không nhờ hộp thoại quyền.
3. `skipDangerousModePermissionPrompt = true` — bỏ luôn cả câu xác nhận của chế độ nguy hiểm.
   Cộng với điểm 2, nghĩa là hàng rào duy nhất giữa model và máy là hook của plugin. Điều này
   củng cố kết luận: **đầu tư vào hook đáng giá hơn đầu tư vào chữ trong instruction**.

## 8. Cái giá của phương án

- **Không được xoá trước khi chuyển.** 5 dòng CHUYỂN hiện CHƯA có ở plugin. Bỏ chúng khỏi
  CLAUDE.md ngay hôm nay là mất luật thật. Thứ tự bắt buộc: viết vào skill → kiểm → rồi mới cắt
  instruction. Đây là việc của request sau.
- **Sửa `skills/` là phải dựng lại 3 bundle portable.** `portable_claude`, `portable_codex`,
  `antigravity_portable` sinh từ `skills/`+`hooks/` (`docs/kien-truc.md:13`), nên request chuyển
  luật sẽ kèm `build_portable.py` + `tdq_checkportable.py check` cho cả ba.
- **Cửa sổ mất hiệu lực.** 10 dòng XOÁ chỉ an toàn khi hook còn chạy. Tắt plugin `tdq-workflow`,
  hoặc chạy ở môi trường không nạp hook (Codex CLI, Antigravity dùng bundle riêng), thì 10 luật
  đó biến mất theo. Ai chạy nhiều môi trường nên giữ mức thận trọng như bản đề xuất này.
- **Lợi ích đo được**: 57 → 29 dòng, giảm 49 % phần instruction nạp vào MỌI lượt của MỌI
  project. Phần cắt đi không biến mất — nó chuyển sang chỗ chỉ nạp khi cần.
