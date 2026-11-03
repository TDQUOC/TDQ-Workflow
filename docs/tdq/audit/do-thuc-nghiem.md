# Bốn phép đo thực nghiệm — bằng chứng chạy thật

Ngày: 2026-08-17 · Request: 2026-08-17-2121-toi-uu-context-workflow
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

File này giữ SỐ và BẰNG CHỨNG. Phần diễn giải và khuyến nghị nằm ở
[de-an-toi-uu-context.md](de-an-toi-uu-context.md) — tách ra để lúc số đổi thì biết
chính xác phải sửa chỗ nào.

## 1. Ba bản `skills/` lệch nhau tới đâu

Cách đo: băm md5 từng file `.md` của ba cây, rồi băm lại lần nữa sau khi chuẩn hoá
đường dẫn script: `${CLAUDE_PLUGIN_ROOT}/scripts/`, `${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/`,
`${CLAUDE_PROJECT_DIR}/.agents/tdq/scripts/`, và mọi chuỗi trong nháy kép kết thúc bằng
`/scripts/` — cùng quy về một ký hiệu. (Phải kể đủ cả bốn: QC độc lập thử tái lập theo
bản mô tả cũ chỉ nêu hai cái đầu và ra 15 file lệch thay vì 0.)

| cặp so | file chung | chỉ có ở bản portable | khác byte | khác NỘI DUNG thật |
|---|---|---|---|---|
| `skills/` vs `portable_claude/.claude/skills` | 44 | 1 (`tdq-checkportable`) | 15 | **0** |
| `skills/` vs `portable_codex/.agents/skills` | 44 | 1 (`tdq-checkportable`) | 15 | **0** |

**Kết luận: ba bản là MỘT bộ luật, khác nhau đúng một biến đường dẫn.** 16 file khác
byte, cả 16 đều về giống hệt sau khi chuẩn hoá đường dẫn; 0 file lệch nội dung.

Vì sao điều này quan trọng hơn nó tưởng: mọi lo ngại kiểu "tối ưu xong phải sửa ba
nơi, dễ lệch" là lo ngại SAI. Chi phí dịch/rút gọn là **×1**, cộng một bước thay
chuỗi. Ngược lại nó cũng nói rằng ba bản đang đồng bộ bằng quy trình chứ không bằng
máy — chưa có test nào khoá điều đó, và đó là rủi ro thật khi bắt đầu sửa hàng loạt.

## 2. Dịch sang tiếng Anh tiết kiệm bao nhiêu

Đo trên `skills/tdq-conventions/references/approval.md`, dịch tay sang tiếng Anh
trong thư mục tạm. File gốc **không đổi một byte**: md5 trước và sau đều là
`c890b7e70e33a3ef967a78421ce506d1`.

| bản | ký tự | token | ký tự/token |
|---|---|---|---|
| tiếng Việt (gốc) | 1.795 | 1.070 | 1,68 |
| tiếng Anh (dịch) | 1.985 | 668 | 2,97 |

**Hệ số EN/VI = 0,624 → tiết kiệm 37,6%.** Chú ý bản tiếng Anh DÀI hơn về ký tự
(1.985 > 1.795) mà vẫn ít token hơn hẳn — tiết kiệm đến từ hiệu suất token hoá, không
đến từ việc viết ngắn đi.

Vì sao 37,6% là **cận dưới**, không phải con số điển hình: file này đặc biệt nhiều
chuỗi tiếng Việt KHÔNG được phép dịch — `duyệt`, `chốt`, `đồng ý`, `cái này`,
`plan này duyệt chưa` — vì đó chính là chữ user gõ, dịch đi là hỏng luật. Một file
thuần văn xuôi sẽ tiết kiệm nhiều hơn. Muốn con số điển hình thì phải đo thêm 3–5
file nữa; request này chỉ đo một file theo đúng phạm vi spec.

## 3. Đề xuất `skillOverrides` tiết kiệm bao nhiêu

File sinh ra: [skill-overrides-de-xuat.json](skill-overrides-de-xuat.json) — 261 khoá.
Quy tắc đặt: nhóm `workflow` (23 skill) **giữ nguyên** vì đang dùng hằng ngày; nhóm
`game engine` và `design` (41 skill) đặt `off` vì chắc chắn lạc mục với một repo
Python/workflow; toàn bộ phần còn lại đặt `name-only` — thấy tên, không tốn mô tả.

| mức | số skill | token hiện | token sau |
|---|---|---|---|
| giữ nguyên | 23 | 1.210 | 1.210 |
| `name-only` | 220 | 22.954 | 2.451 |
| `off` | 41 | 5.624 | 0 |
| **tổng** | **284** | **29.788** | **3.661** |

**Tiết kiệm 26.127 token = 87,7%** của phần mô tả skill trong system prompt.

Cách đo: token mô tả + token tên + 6 token khung mỗi mục, giống hệt
`skill_tokens.py --mo-ta`. Dùng đúng một cách đo cho mọi kịch bản, vì đổi cách đo
giữa chừng là cách dễ nhất để bịa ra mức tiết kiệm không có thật.

Kiểm: 100% khoá có thật trong inventory · 100% giá trị thuộc 3 mức hợp lệ · md5 của
`~/.claude/settings.json` không đổi (`a6867f29f5a38c3dc51d048a0cd81471`) — file đề
xuất chỉ là đề xuất, chưa áp vào đâu.

## 4. Mức `name-only` có còn gọi được skill không — CHƯA đo được

Đây là hạng mục duy nhất của P4 **không chạy được** trong request này. Nói thẳng thay
vì đưa ra một câu suy đoán trông giống kết quả đo.

Hai lý do độc lập, mỗi lý do đủ để chặn:

1. Đặt một skill về `name-only` bắt buộc phải ghi vào file settings. Quy tắc 7 của
   plan cấm ghi vào mọi file settings, và QC Q14 khoá md5 của `~/.claude/settings.json`.
2. Kể cả nếu được phép ghi, `skillOverrides` chỉ được đọc lúc khởi tạo phiên. Phiên
   đang chạy sẽ không đổi hành vi, nên không có cách nào quan sát kết quả ngay trong
   turn này.

Bằng chứng gián tiếp đang có (đọc chuỗi trong binary Claude Code, ghi ở
`brief/2026-08-17-2121-toi-uu-context-workflow.md` vòng 3–4):

* Chuỗi báo lỗi khi gọi skill đã tắt: `" is disabled via skillOverrides. Remove the
  override from your settings to run it."` — tức có mức LÀM skill không gọi được.
* Chuỗi `(on/name-only locked by frontmatter disable-model-invocation)` gộp `on` và
  `name-only` vào cùng một vế đối lập với các mức bị khoá → hàm ý `name-only` vẫn
  thuộc nhóm model gọi được, chỉ giấu phần mô tả.

Hàm ý đó **mạnh nhưng chưa phải bằng chứng chạy**. Cách user tự xác nhận trong 1 phút:
thêm `"skillOverrides": {"<tên skill>": "name-only"}` vào `~/.claude/settings.json`,
mở phiên mới, bảo Claude dùng skill đó. Gọi được → kiến trúc 3 tầng ở đề án dùng được
nguyên trạng. Không gọi được → tầng giữa phải đổi từ `name-only` sang cơ chế khác, và
đề án đã ghi sẵn đường lui đó.
