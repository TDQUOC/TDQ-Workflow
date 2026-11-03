# Đổi rule ưu tiên tìm kiếm: LSP + lumen cùng hạng, ưu tiên index sẵn

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay tôi muốn giữ nguyên và update lại rule là lsp -> lumen -> grep thfi bây giừo tôi muốn
> lsp và lumen đều được ưu tiên để sreach và ưu tiên index project để có data sreach thì có
> ổn không?

Ý hiểu ban đầu: (1) giữ nguyên model lumen = `qwen3-embedding:0.6b` (không revert) — đã xong ở
request trước, không cần làm gì thêm; (2) đổi luật gốc trong `uu-tien-tim-kiem.md` từ
"LSP trước, lumen chỉ khi LSP rỗng" sang "LSP và lumen đều được ưu tiên ngang nhau"; (3) muốn
project được index sẵn (chủ động) thay vì chỉ đánh thức Ollama theo nhu cầu như luật cũ.

Phạm vi đoán: sửa `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md` (nguồn luật) + 4 điểm
hook (`tdq-intake`, `tdq-spec`, `tdq-plan`, `tdq-build`) + test chống lệch
(`tests/test_tdq_lsp_skill.py`) + có thể đổi cơ chế lifecycle Ollama (mục 3 của file, hiện là
"wake on demand, release right after" — mâu thuẫn với "ưu tiên index sẵn").

Điểm CHƯA RÕ, cần hỏi trước khi viết plan (xem `## Hỏi đáp`).

## Hiểu & kiến thức

- File nguồn `uu-tien-tim-kiem.md` là single source, có test tự động (`test_tdq_lsp_skill.py`)
  so khớp 4 file hook — sửa rule bắt buộc sửa đồng bộ cả 5 chỗ, không thể sửa 1 nơi.
- Luật hiện tại có lý do rõ trong file: LSP chính xác cho câu hỏi có tên symbol (định nghĩa, ai
  gọi, kiểu, rename), lumen mạnh cho câu hỏi khái niệm không có tên. Test thực nghiệm vừa chạy
  (`docs/tdq/plan/2026-08-26-0015-*.md`) xác nhận đúng: LSP thắng tuyệt đối khi có tên symbol,
  lumen (bản qwen3 mới) thắng khi câu hỏi là khái niệm tiếng Việt.
- "Đều được ưu tiên" có ít nhất 2 cách hiểu khác hẳn nhau về chi phí — cần hỏi (xem Hỏi đáp Q2).
- "Ưu tiên index sẵn" mâu thuẫn trực tiếp với mục 3 hiện tại của file
  (`Ollama's lifecycle — on demand, released right after`) — đổi nghĩa là bỏ hẳn triết lý
  "chỉ đánh thức khi cần" sang "giữ index/model sẵn sàng liên tục". Có phí thật: Ollama phải
  chạy thường trực (RAM), và lumen cần được `index` lại mỗi khi code đổi để data không cũ.
- Rủi ro nếu làm mà không hỏi: đổi rule sai ý user → phải sửa lại 5 file + test lần nữa; hoặc
  bật Ollama thường trực tốn RAM ngoài ý muốn user.

## Hỏi đáp

1. Bạn muốn "LSP và lumen đều ưu tiên" theo nghĩa nào?
   - A (đề xuất): Gọi CẢ HAI song song cho mọi câu hỏi tìm kiếm, gộp kết quả 2 nguồn trước
     khi đọc — không còn thứ tự trước/sau, tốn thêm lệnh gọi mỗi lần nhưng không bỏ sót loại
     câu hỏi nào (LSP mạnh symbol, lumen mạnh khái niệm).
   - B: Bỏ quy tắc "lumen CHỈ chạy khi LSP rỗng" — vẫn gọi LSP trước, nhưng cho phép gọi lumen
     NGAY sau đó luôn (không cần chờ LSP rỗng), agent tự quyết theo loại câu hỏi.
   - C: Khác — bạn mô tả cụ thể cách phối hợp bạn muốn.

2. "Ưu tiên index project để có data search" — bạn muốn ở mức nào?
   - A (đề xuất): Tự động index lại lumen mỗi khi có code đổi trong turn (gắn vào bước
     `tdq_finish.py`/graphify hiện có cuối mỗi turn đổi code) — index luôn mới, Ollama chỉ bật
     lúc index/search rồi tắt như cũ, không tốn RAM thường trực.
   - B: Giữ Ollama + model chạy thường trực suốt session (bỏ hẳn cơ chế "đánh thức rồi tắt")
     để search nhanh hơn, đổi lại tốn RAM liên tục trên máy.
   - C: Chỉ index lại thủ công khi bạn yêu cầu, không tự động.

3. Việc đổi lifecycle Ollama (nếu chọn 2B) có ảnh hưởng project khác trên máy dùng chung lumen
   không — bạn có muốn giới hạn thay đổi này CHỈ cho project TDQWorkflow không?
   - A (đề xuất): Chỉ áp dụng trong ngữ cảnh dùng lumen cho TDQWorkflow (ghi rõ trong rule,
     không đổi hành vi mặc định của lumen cho project khác).
   - B: Áp dụng chung cho mọi lần dùng lumen trên máy.

### Trả lời (user, nguyên văn "1a 2a 3a")
- Lane: **quick**.
- Câu 2 → **A**: gọi CẢ LSP và lumen song song cho MỌI câu hỏi tìm kiếm, gộp kết quả trước khi
  đọc — bỏ hẳn thứ tự trước/sau.
- Câu 3 → **A**: tự động reindex lumen cuối mỗi turn có đổi code, gắn vào `tdq_finish.py`
  (đã xác nhận qua research: lumen incremental theo Merkle root hash, không quét lại toàn bộ
  project mỗi lần — chi phí thấp). Ollama vẫn chỉ đánh thức lúc index/search rồi tắt, KHÔNG bật
  thường trực → câu 4 (phạm vi Ollama thường trực) không còn áp dụng.
