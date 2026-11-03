# BRIEF — Kiểm thử đa nền tảng trên macOS và Linux qua Tailscale

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

"vậy sau khi dev thì hoạt động tốt trên window, mac và linux không? hãy test lại với mac thì ở trong taiscale tdq 1772 và linux là máy rtxa5000 trong taiscale với admin pass là 1"

### Đọc hiểu lần đầu
- **Mục tiêu**: Kiểm thử thực tế toàn diện bộ mã nguồn TDQ-Workflow vừa phát triển trên các hệ điều hành mục tiêu: Windows (máy hiện tại), macOS (`macbook-air-ca-tdq` / `100.105.75.71`) và Linux (`dichthuat-rtxa5000` / `100.102.92.43`) thông qua mạng Tailscale và SSH.
- **Phạm vi dự kiến**:
  - Kết nối SSH vào macOS (`mbair`) và Linux (`superserver`).
  - Kiểm tra môi trường Python, git và chạy các bộ test trọng yếu (`tests/test_an_cua_so_windows.py`, `tests/test_auto_fix_python3_hook.py`, `tests/test_shim_python3.py`, `tests/test_claude_md_core.py`, v.v.).
  - Xác nhận tính tương thích đa nền tảng tuyệt đối (không bị lỗi cờ Windows `creationflags` trên POSIX, không lỗi đường dẫn PATH hay shell commands).

## Hiểu & kiến thức

### Thông số môi trường thực tế qua Tailscale
1. **Host macOS**:
   - Tên máy: `MacBook-Air-cua-tdq.local` (`100.105.75.71`, ssh alias: `mbair`, user `tdq`)
   - HĐH: Darwin 25.5.0 arm64 (macOS)
   - Python: 3.9.6
   - Kết nối: SSH key `id_ed25519_mbair_tdq`, xác thực tự động không cần nhập pass.

2. **Host Linux**:
   - Tên máy: `admin-superserver` (`100.102.92.43`, ssh alias: `superserver`, user `admin`)
   - HĐH: Ubuntu Linux 7.0.0-38-generic x86_64
   - Python: 3.14.4
   - Kết nối: SSH key `id_ed25519_superserver`, xác thực tự động không cần nhập pass.

3. **Kế hoạch kiểm thử chéo**:
   - Chạy các test suite trực tiếp qua SSH từ xa hoặc đồng bộ repo lên thư mục tạm `/tmp/tdq_test` của remote host để chạy trọn bộ kiểm thử:
     + `tests/test_an_cua_so_windows.py`: Xác nhận trên Linux và macOS, `tham_so_subprocess_an_cua_so()` trả về `{}` (rỗng), `chay_subprocess` chạy chuẩn không bị lỗi `ValueError: creationflags is only for Windows`.
     + `tests/test_auto_fix_python3_hook.py`: Xác nhận chuỗi fallback hook và logic setup tương thích.
     + `tests/test_shim_python3.py`: Xác nhận logic fixture POSIX và bỏ qua cài shim trên macOS/Linux.
     + `tests/test_claude_md_core.py`: Xác nhận render instruction.
     + Smoke test 3 tầng và các module cốt lõi.

## Hỏi đáp

- Người dùng đã chọn 1a: Express pipeline (quick lane).
