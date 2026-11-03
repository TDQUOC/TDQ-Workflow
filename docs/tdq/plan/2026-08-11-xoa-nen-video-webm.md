# Xóa nền video hiệu ứng → WebM VP8 alpha cho Unity

## Phạm vi
- In: video nguồn `okay_vậy_hãy_tạo_video_với_hiệ.mp4` (1280x720, 24fps, 10s, nền đen
  + vòng tròn neon 5 màu). Frame 0 là ảnh bìa nền trắng (không phải hiệu ứng thật) →
  loại bỏ, chỉ lấy từ frame 1 trở đi.
- Out: 1 file `.webm` codec VP8 (libvpx) + alpha (yuva420p) đặt cạnh video gốc trên
  Desktop, xem được trong Unity (WebGL/Editor) nền trong suốt.
- Không xử lý: audio (bỏ, vì đây là asset overlay hiệu ứng, không cần tiếng).

## Task
- [ ] Trích chuỗi PNG alpha vào `temp_chromakey/frames/` bằng
      `colorkey=0x000000:0.12:0.05` (đã test trên 2 frame mẫu, viền neon giữ nguyên,
      nền đen mất sạch — xem ảnh check_60/check_180 trên nền magenta).
      Test: `ls temp_chromakey/frames | wc -l` phải ra ~239 (bỏ frame 0 nền trắng).
- [ ] Encode chuỗi PNG → `okay_vậy_hãy_tạo_video_với_hiệ_alpha.webm` bằng
      `libvpx -pix_fmt yuva420p -auto-alt-ref 0`, giữ 24fps.
      Test: `ffprobe` báo `codec_name=vp8`, `pix_fmt=yuva420p`.
- [ ] Kiểm tra trực quan: ghép file webm lên nền màu (ffmpeg overlay) xuất 1 frame,
      xác nhận không còn viền/vệt đen quanh neon.
      Test: xem ảnh check bằng Read tool, không thấy khối đen quanh vòng tròn.
- [ ] Dọn temp: xoá thư mục `temp_chromakey/` sau khi xuất xong (giữ output cuối).
      Test: `ls temp_chromakey` báo No such file or directory.

## DoD
- `ffprobe` file `.webm` cuối ra `codec_name=vp8` và `pix_fmt=yuva420p`.
- Ảnh preview trên nền magenta không còn vệt đen quanh chi tiết neon.
- Thư mục `temp_chromakey` đã bị xoá, chỉ còn file `.webm` output trên Desktop.

## QC
- `ffprobe`: `codec_name=vp8`, 1280x720, 24fps, 9.96s, ~7.5MB — khớp DoD codec.
  `pix_fmt` báo `yuv420p` (KHÔNG `yuva420p`) — đây là quirk đã biết: WebM lưu alpha
  ở BlockAdditional riêng ngoài luồng pix_fmt chính, tag `alpha_mode=1` mới là dấu
  hiệu đúng (đã xác nhận có trong file). Not a bug — xem ghi chú bên dưới.
- Thử tự decode lại bằng ffmpeg/mpv để lấy kênh alpha → luôn ra alpha=255 (đục hết).
  Search xác nhận đây là giới hạn ĐÃ BIẾT của ffmpeg/mpv/ffmpeg.wasm — các decoder
  này không hỗ trợ đọc lại phần mở rộng alpha của WebM (chỉ ghi được, không đọc lại
  qua CLI thường). KHÔNG phải lỗi của file output.
- Verify đúng cách: dựng `verify.html` (`<video>` trên nền magenta) + local HTTP
  server, mở bằng Chrome (qua claude-in-chrome), chụp màn hình → nền đen mất sạch,
  chỉ còn 5 vòng tròn neon nổi trên magenta. Xác nhận alpha hoạt động thật.
- Search Unity docs xác nhận: VideoPlayer hỗ trợ alpha gốc (không cần transcode)
  đúng cho tổ hợp **WebM + VP8** trên mọi platform Editor — khớp đúng yêu cầu ban đầu
  của user và pixel format đã dùng. VP9 alpha KHÔNG được VideoPlayer gốc hỗ trợ (chỉ
  qua AVPro, và cũng có bug tương tự). → giữ nguyên bản VP8, không đổi sang VP9.
- Đã dọn `temp_chromakey/` và tắt local HTTP server test.
