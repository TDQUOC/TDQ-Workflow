# Request: full claude export

## Nguyên văn
> hãy check claude export và tạo một bản full export ở document (replace bản export cũ)
> và với các repo local dependency thì hãy tạo bản full clone vào folder export, có
> manifest và đầy đủ để có thể setup đầy đủ ở máy khác nữa

## Hiểu ban đầu
- Kiểm tra tool `scripts/claude_export.py` (build/check) còn hoạt động đúng.
- Sinh lại bundle full tại `~/Documents/claude-code-export` (đè bản cũ — hiện lệch 6
  mục: CLAUDE.md, 3 file plugin config, repo TDQWorkflow lệch 11 commit, version
  0.7.0→0.8.0).
- Repo local dependency = marketplace `tdq-local` → `TDQWorkflow` (đã xác nhận là
  local-directory marketplace DUY NHẤT trong `known_marketplaces.json`; plugin còn lại
  đều nguồn GitHub). Tool đã clone full `.git` cho repo này (`clone_repo`) và rewrite
  path marketplace trỏ vào bundle — đúng yêu cầu "full clone + setup được ở máy khác".
- Chưa rõ: có cần archive bản cũ trước khi đè, hay đè thẳng (2 bản `.bak-20260805` đã
  có sẵn từ trước, không phải do turn này tạo).
