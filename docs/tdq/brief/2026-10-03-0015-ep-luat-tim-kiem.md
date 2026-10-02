# BRIEF — Buộc agent code tuân đúng luật tìm kiếm 4 tầng

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-03 · Slug: 2026-10-03-0015-ep-luat-tim-kiem · Lane: full · Nhánh: `feature/ep-luat-tim-kiem`

## Nguyên văn

> Tôi có gặp tình trạng này nên tôi muốn handle bộ workflow để agent codesex buộc phải tuân theo
> đúng luật

Kèm ảnh chụp một phiên Claude Code trong project excalidraw, agent tự nhận: (1) bỏ qua kiểm hiệu
ứng — chỉ chạy thang 8 bậc, "báo 8/8 ĐẠT nhưng chỉ kiểm công cụ có tồn tại hay không"; (2) dùng
grep cho câu hỏi khái niệm ("editor đăng ký font thế nào") lẽ ra phải dùng lumen; (3) khẳng định
trong spec vẫn đúng vì đã đọc tận nơi, nhưng cách tìm sai quy trình.

Chốt ở intake: `1a 2a` — lane `full`; áp cho **cả Claude Code lẫn Codex**.

## Hiểu & kiến thức

### Số đo 1 — phiên thật trong ảnh (`cdf604ee…jsonl`, 1,4 MB)

Dựng lại thứ tự mọi lần tìm của phiên, qua bốn request liên tiếp (phân tích, đóng gói, dựng app,
thêm font):

| Đoạn | Tìm bằng gì | Số lần |
|---|---|---|
| Lượt 2–36 (bốn request) | `grep` qua **Bash**, `sed -n`, `cat` | ~20 lần tìm, **0 lumen, 0 LSP** |
| Lượt 37 | user hỏi "rule tìm kiếm thế nào và lumen…" | — |
| Lượt 40–52 | lumen 1 lần, rồi LSP 11 lần | chỉ SAU khi user nhắc |

Ba điều số đo nói:

1. **Agent tìm qua Bash, không qua công cụ `Grep`.** Công cụ `Grep` chỉ được gọi 2 lần trong cả
   phiên. Một cổng chỉ cắm vào `Grep` bỏ sót 20/22 lần tìm.
2. **Câu hỏi khái niệm bị "đóng giả" thành grep.** Mẫu `static\|register\|export\|class `
   (lượt 34), `alias\|find:\|replacement\|woff2\|fonts\|…` (lượt 28), `http\|esm\|unpkg\|cdn\|apply\|name:`
   (lượt 29) là danh sách từ đoán mò nối bằng `\|` — hình dạng của một câu hỏi khái niệm, không
   phải của một tên đã biết. Ngược lại `fileHandle`, `saveFileToDisk`, `getFontFamilyString` là
   tên chính xác — grep chúng đúng luật.
3. **Không một lời nhắc nào về thứ tự tìm kiếm.** Mã hook xuất hiện trong phiên: `NEXT`, `APPROVE`,
   `GON`, `INTAKE`, `LOG`, `OUTPUT`. Luật 4 tầng chỉ nằm trong văn bản. Cùng kiểu hỏng với cổng đọc
   lại ở request trước: luật có trong file, không ai giữ nó ở đúng lúc agent chọn công cụ.

### Số đo 2 — Codex hiện KHÔNG thể tuân luật này, dù muốn

| Sự thật | Nguồn |
|---|---|
| `.codex-plugin/plugin.json` khai `"hooks": {}` — Codex dùng plugin TDQ **không có hook nào** | đọc file |
| `~/.codex/config.toml` chỉ khai MCP `cloudcli-browser` — **không có lumen, không có LSP** | đọc file |
| `.codex/hooks.json` ở gốc repo chỉ có cổng VÙNG FILE của mode `codex implement` | đọc file |
| `PreToolUse` của Codex **chỉ nhận `deny`**; `allow`/`additionalContext` bị từ chối ở runtime, và chỉ chắc chắn bắn với shell tool | `docs/tdq/research/2026-09-10-2247-mode-codex-implement.md` góc 2 |
| Hook project của Codex phải được **trust** mới chạy | cùng nguồn |

Hệ quả: với Codex, "nhắc" là không làm được — chỉ có chặn kèm lý do. Và chặn grep mà không cấp
lumen/LSP thì agent không có đường nào đúng để đi. Việc ĐẦU TIÊN cho Codex là đưa hai công cụ đó
vào tay nó.

### Số đo 3 — thang kiểm nói ĐẠT cho thứ đang chết

| Chỗ | Hỏng thế nào | Đo được |
|---|---|---|
| Bậc 3 (`tdq_lsp.py`) | chỉ kiểm binary language server có tồn tại | 2026-10-02: báo ĐẠT với `typescript@7` không có `tsserver`; `agent-lsp doctor` cùng lúc: **2 ok, 2 failed** |
| Smoke grep (`tdq_setup.smoke_grep`) | chỉ quét `*.py` | trên excalidraw (toàn TS) luôn TRƯỢT, dù `git grep` ra kết quả ngay |
| Lệnh hook in ra | `python3 scripts/tdq_state.py …` — đường TƯƠNG ĐỐI của repo plugin | ở project khác không có `scripts/`, lệnh fail ngay lượt đầu |
| lumen MCP với tham số `path` | lỗi `k value in knn query too large, provided 8192 and the limit is 4096` | gặp thật trong phase analyze này; bỏ `path` thì chạy |

Agent trong ảnh tin con số 8/8 và bỏ qua kiểm hiệu ứng — thang kiểm đã dạy nó rằng "có cài" là đủ.

### Ràng buộc kiến trúc phải giữ — và một chỗ phải đổi

`docs/kien-truc.md` 2026-07-29: hook **nhắc** và kiểm bằng hiệu ứng thật; điểm **chặn** duy nhất
là working log. Request trước (cổng đọc lại) user chọn "chỉ nhắc". Request này user nói rõ **"buộc
phải tuân theo"**, và Codex chỉ có `deny`. Nếu chọn chặn, đó là **điểm chặn thứ hai** của cả
workflow — phải ghi thành quyết định kiến trúc có ngày, không được lẳng lặng thêm.

### Hai câu hỏi một cổng theo-từng-lệnh KHÔNG trả lời được

Một lần grep đơn lẻ không cho biết agent đang hỏi khái niệm hay tên — `getFontFamilyString` vừa có
thể là tên đã biết, vừa có thể là tên đoán. Cái đo được bằng hiệu ứng là **thứ tự**: trong một
request, agent đã hỏi lumen/LSP/graphify lần nào TRƯỚC khi grep chưa. Vì vậy cổng nên kết hợp hai
tín hiệu: hình dạng mẫu (đoán mò) và trạng thái request (đã hỏi tầng khái niệm chưa).

### Trinh sát Codex (T1.1, chạy thật `codex-cli 0.155.1`, 2026-10-03)

| Câu hỏi | Phán quyết | Bằng chứng |
|---|---|---|
| (a) Plugin Codex khai `hooks` được không | **KHÔNG** | `codex features list` → `plugin_hooks  removed  false`; feature `hooks` thì `stable true`. Hook phải nằm ở `.codex/hooks.json` cấp project (hoặc user), không đi theo plugin |
| (b) `deny` có dừng lệnh và Codex có đọc lý do không | **CHƯA ĐO ĐƯỢC trên máy này** | `codex exec --dangerously-bypass-hook-trust` trong thư mục tạm có hook `PreToolUse` deny-grep → `401 Unauthorized … Missing bearer or basic authentication`: Codex chưa đăng nhập trên Windows (`~/.codex/` không có `auth.json`, không có `model_provider`). Hook không được gọi lần nào vì model chết trước lần gọi tool đầu. Mac (nơi đã đo mode codex 2026-09-10) đang mất kết nối (ssh timeout); Linux tắt |
| (c) Khai MCP rồi `codex mcp list` có thấy không | **CÓ** | trong `CODEX_HOME` tạm: `codex mcp add lumen -- <bin>/lumen stdio` và `codex mcp add lsp -- agent-lsp` → `codex mcp list` in cả hai, `enabled`; `config.toml` sinh ra đúng 2 bảng `[mcp_servers.*]` |

Hệ quả cho P3:

- T3.1 dùng `.codex/hooks.json` cấp project do `tdq-setup` ghi (đường lùi đã khai sẵn trong spec §5).
  Bỏ ý định khai trong `.codex-plugin/plugin.json`.
- T3.2 gọi CLI chính thức `codex mcp add` thay cho tự viết TOML — Codex tự lo cú pháp, ta chỉ lo
  backup và không ghi đè tên đã có. Lệnh thật: lumen là `<plugin lumen>/bin/lumen stdio` (đúng
  `args` mà plugin lumen khai cho Claude Code); `lsp` lấy NGUYÊN `command` + `args` của mục `lsp`
  trong `~/.claude.json`, để Codex khởi động đúng các language server Claude Code đang dùng.
- Q9 (Codex bị chặn trong một lượt thật) **bị chặn ngoài tầm**: cần user đăng nhập Codex trên
  Windows (`codex login`), hoặc Mac kết nối lại. Phần kiểm bằng unit test (khuôn `deny` mà Codex
  đọc, cùng khuôn `codex_edit_gate.py` đang dùng từ 2026-09-10) vẫn làm đủ.

## Hỏi đáp

**Năm câu chốt ở cuối phase analyze, cộng một yêu cầu bổ sung** (nguyên văn user: `1a 2a 3a 4a 5a
và bổ sung thêm là ở đầu project nếu agent mcp chưa init thì mặc định auto init và set rule sreach
và vận hành trước`).

| # | Câu hỏi | Chốt | Hệ quả |
|---|---|---|---|
| 1 | Mức cưỡng chế trên Claude Code | **Chặn có điều kiện**: deny khi request chưa hỏi tầng khái niệm lần nào VÀ mẫu có hình đoán mò; grep tên chính xác không bao giờ bị chặn | **Điểm chặn thứ hai** của workflow — phải ghi thành quyết định có ngày trong `kien-truc.md`, sửa câu 2026-07-29 cho khớp |
| 2 | Codex | **Cùng cổng, dạng `deny`**; `tdq-setup` khai MCP lumen + LSP cho Codex | Không cấp công cụ thì không bắt tuân luật được |
| 3 | Kiểm hiệu ứng | **Bậc 3 khởi động thật** language server theo ngôn ngữ project; smoke grep theo ngôn ngữ thật; **gộp thang + smoke thành một lệnh** | Không còn đường "chỉ chạy thang" — 8/8 chỉ khi công cụ trả lời được |
| 4 | Đường dẫn `scripts/…` tương đối | **Sửa luôn**: hook in đường dẫn tuyệt đối của plugin | Plugin chạy được ở project khác ngay lượt đầu |
| 5 | Mức QC | **`full`** + phép đo phát lại phiên excalidraw | Đã ghi `muc_qc=full` |
| + | Bổ sung | **Tự khởi tạo bộ tìm kiếm ở đầu project**: MCP chưa sẵn sàng → mặc định tự init, đặt luật tìm kiếm, vận hành trước khi làm việc | Xem vướng kỹ thuật bên dưới |

### Sửa spec 1.0 → 1.1 (2026-10-03)

User hỏi: `Vậy khi nào dùng lumen lsp khi mới vào đã dùng grep r`. Phát lại phiên excalidraw qua
quy tắc của spec 1.0: lượt 7 (`fileHandle`, tên agent tự đoán) và lượt 9 (`^export`) LỌT, lần
chặn đầu tiên mới ở lượt 10. User chốt `A`: thêm **luật mở đầu** (lần tìm code đầu tiên của
request phải qua tầng khái niệm, trừ tên có nguyên văn trong prompt) và **mở khoá có hạn**
(một lần gọi tầng khái niệm chỉ mở N lần tìm kế tiếp).

Một khẳng định của bản nháp 1.1 sai và đã sửa trước khi trình: `docs/tdq/.tdq-prompt-last.json`
chỉ lưu mã băm của prompt, không lưu chữ — cổng phải tự ghi token định danh của prompt.

### Vướng kỹ thuật của yêu cầu bổ sung, và cách giải

**Index lumen có thể mất 11 phút** (đo 2026-10-02 trên excalidraw: 843 file, 29.796 chunk,
11m5s). Một hook `SessionStart` chờ chừng đó là treo phiên. Cách giải: hook chỉ làm phần RẺ và
đồng bộ (dò trạng thái bằng file mốc, không gọi tiến trình đo), còn phần ĐẮT — cài phụ thuộc đã
khai, dựng đồ thị, index — chạy NỀN trong một tiến trình tách rời, có khoá pid để không chạy
chồng. Trong lúc index chưa xong, cổng tìm kiếm KHÔNG chặn (chặn mà không có đường đúng để đi là
kẹt), nó chỉ nói rõ tầng nào đang dựng.

**Cài phụ thuộc tự động ở MỌI project** đi theo đúng danh sách phụ thuộc đã khai của `tdq-setup`
(quyết định 2026-09-28). Thứ nằm ngoài danh sách thì ghi nợ và nhắc, không tự chạy.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| analyze | **CÓ** (đang chạy) | đã soi phiên thật + cấu hình Codex + thang kiểm |
| research web | **BỎ — đổi thành trinh sát chạy thật ở P1 của plan** | câu hỏi "plugin Codex có khai hook được không, `PreToolUse` còn chỉ-deny không" chỉ chạy thật `codex-cli 0.155.1` trên máy mới trả lời chắc; nguồn web hiện có là 2026-09-10 |
| vòng hỏi phạm vi | **CÓ** | 5 câu thiết kế, câu 1 đổi luật kiến trúc |
| spec · plan · implement · qc · report | **CÓ** | chạm tầng hook của hai host |
| đo lại trên phiên thật | **CÓ — bắt buộc** | chạy lại 22 lần tìm của phiên excalidraw qua cổng mới: bao nhiêu lần bị bắt, bao nhiêu lần bắt oan |
