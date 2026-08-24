# BRIEF — implement phải chạy hết plan, không dừng giữa chừng

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay bây giờ tôi muốn check là có tình trạng khi chạy thì claude code ko implement end to end
> plan mà xong vài phase rồi ngừng tôi muốn mở request để cho claude code đã implement plan thì
> sẽ implement end to end

**Đọc lần đầu**

- Mục tiêu: khi đã vào phase `implement`, workflow phải chạy hết mọi task của plan rồi mới trả
  lượt về cho user; không được làm xong vài phase/task rồi dừng như hiện nay.
- Phạm vi đoán: luật phase `implement` trong `skills/tdq-build/`, và cổng `Stop` ở
  `hooks/scripts/stop_gate.py`.
- Bằng chứng sơ bộ (chưa phải kết luận): `stop_gate.py` hiện chỉ chặn hai ca — `[TDQ:LOG]` khi
  repo đổi mà chưa ghi working log, và `[TDQ:TICK]` khi code đổi mà checkbox plan đứng yên.
  KHÔNG có cổng nào chặn việc kết thúc lượt trong lúc plan vẫn còn task chưa tick. Nghĩa là dừng
  giữa chừng hiện là hợp lệ với khung, nên đây có thể là lỗi THIẾU LUẬT chứ không phải lỗi code.
- Chỗ chưa rõ (sẽ hỏi ở vòng interview):
  - "dừng giữa chừng" tính từ mốc nào — hết mỗi phase P1/P2, hay hết mỗi task?
  - Có ca dừng CHÍNH ĐÁNG nào phải chừa không (hỏi duyệt, hết context, task bị chặn kỹ thuật)?
  - Muốn chặn cứng (Stop hook từ chối kết lượt) hay chỉ nhắc?

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Nguồn | Phán quyết |
|---|---|---|
| tdq-build | plugin:tdq-workflow | DÙNG — chứa luật "chạy hết plan trong một lượt" cần siết |
| tdq-conventions | plugin:tdq-workflow | DÙNG — `references/phases.md` ghi anti-pattern "Stopping midway" |
| tdq-diagram | plugin:tdq-workflow | DÙNG — lane full bắt buộc vẽ sơ đồ trước plan |
| tdq-plan / tdq-spec | plugin:tdq-workflow | DÙNG — khuôn spec và plan |
| tdq-lsp-setup | plugin:tdq-workflow | ĐÃ DÙNG — kiem 6/6 bậc ĐẠT |
| tdq-check-status | plugin:tdq-workflow | BỎ — không phải ca khôi phục phiên chết |
| tdq-status | plugin:tdq-workflow | BỎ — không phải câu hỏi tra trạng thái |
| WebFetch | built-in | ĐÃ DÙNG — tra tài liệu hook chính thức |
| superpowers:systematic-debugging | plugin ngoài | BỎ — nguyên nhân đã xác định, không cần vòng debug |

### Nguyên nhân gốc

Luật "implement chạy end-to-end trong một lượt" ĐÃ tồn tại ở hai chỗ:

- `skills/tdq-build/SKILL.md` mục Hard rules: "run end-to-end in ONE turn... do not stop
  halfway to ask".
- `skills/tdq-conventions/references/phases.md` dòng phase `implement`, cột anti-pattern ghi
  thẳng "Stopping midway".

Nhưng cả hai chỉ là chữ trong skill. Cơ chế DUY NHẤT có quyền từ chối kết lượt là `Stop` hook
`hooks/scripts/stop_gate.py`, và nó chỉ chặn hai ca `[TDQ:LOG]` và `[TDQ:TICK]`. Cả hai đều đòi
biến `culprit` khác rỗng, tức lượt đó phải có sửa file. Ca người dùng báo — làm vài task rồi kết
lượt, hoặc quay ra hỏi "có chạy tiếp không" — lọt qua sạch vì nhịp cuối thường không sửa file.

Kết luận: đây là lỗi THIẾU CỔNG, không phải lỗi code sai. Sửa = thêm một điểm chặn thứ ba.

### Kiến thức ngoài đã tra

Tài liệu hook chính thức (code.claude.com/docs/en/hooks): `Stop` hook trả `decision: "block"`
kèm `reason` sẽ ép model chạy tiếp. Claude Code set `stop_hook_active: true` ở lần `Stop` kế
tiếp để chống lặp vô hạn; muốn chặn tiếp phải chủ động trả `stop_hook_active: false`.
Đây là câu trả lời do model tóm tắt trang tài liệu, phải kiểm bằng chạy thật ở phase implement
trước khi tin — `stop_gate.py` hiện đang `return` ngay khi thấy cờ đó.

### Quyết định đã chốt

- Chặn CỨNG: phase `implement` mà plan còn task chưa `[x]` thì `Stop` bị từ chối, KHÔNG đòi
  điều kiện có sửa file. (câu 1a)
- Chặn LẶP: trả `stop_hook_active: false` để mỗi nhịp định kết lượt sớm đều bị đẩy tiếp cho tới
  khi mọi task `[x]`. (câu 2a)
- Chừa đủ ba ca dừng chính đáng: đang chờ user duyệt/trả lời · sub-agent còn chạy · task bị chặn
  kỹ thuật đã ghi lý do. (câu 3a)
- Có lối thoát tường minh: ghi dấu tạm hoãn kèm lý do qua `tdq_state.py`. (câu 4a)
- **Ngoại lệ "lỗi không tự fix được" và lối thoát câu 4 dùng CHUNG một cơ chế.** Hook không thể
  tự biết một lỗi có tự fix được hay không, nên bên muốn dừng phải KHAI BÁO: ghi lý do vào
  state, hook thấy dấu đó mới cho dừng, và chính dòng lý do đó là thứ in ra cho user. Không có
  đường dừng im lặng.

### Phương án loại bỏ

- Chặn ở `PreToolUse`: sai tầng — kết lượt không phải một tool call, không bắt được.
- Đếm task chưa xong rồi chỉ in hint: user đã bác ở câu 1, nhắc suông chính là hiện trạng.
- Bắt model tự hứa trong skill: hiện trạng đã có luật đó rồi mà vẫn hỏng.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research thêm | BỎ | Nguyên nhân đã xác định trong code, kiến thức ngoài đã tra đủ |
| spec | CÓ | Khung bất biến |
| diagram | CÓ | Bắt buộc ở lane full — một luồng: nhánh quyết định của `Stop` hook |
| plan | CÓ | Khung bất biến |
| implement | CÓ | Khung bất biến |
| QC độc lập bằng agent | BỎ | Chạm đúng một file hook, QC leader tự chạy đủ |
| Chia sub-agent | CÓ | Chốt ở gate mode sau khi duyệt plan |
| report | CÓ | Khung bất biến |

## Hỏi đáp

Vòng scope: BỎ — yêu cầu trỏ đúng một hành vi (kết lượt khi plan chưa xong), mọi mặt còn lại
suy được từ `stop_gate.py` và `phases.md`.

- **Chặn ở mức nào?** → 1a: chặn cứng, không đòi điều kiện có sửa file. Kèm yêu cầu thêm: nếu
  ngưng vì lỗi không tự fix được thì được ngưng, nhưng PHẢI báo cho người dùng.
- **Chặn lặp hay một nhịp?** → 2a: chặn lặp tới khi mọi task xong.
- **Ca dừng chính đáng nào được chừa?** → 3a: đủ ba ca (chờ user · sub-agent đang chạy · task bị
  chặn kỹ thuật đã ghi lý do).
- **Lối thoát khi user chủ động muốn dừng?** → 4a: dấu tạm hoãn tường minh ghi qua
  `tdq_state.py`.
