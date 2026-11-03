# Fix lỗi import webm alpha vào Unity 6.3 (Mac)

## Phạm vi
- In: encode lại `okay_vậy_hãy_tạo_video_với_hiệ_alpha.webm` bám sát đúng recipe
  ffmpeg mà Unity docs công bố là tương thích (`-vcodec vp8` +
  `-metadata:s:v:0 alpha_mode="1"` + thêm audio track Vorbis câm, thay vì không audio),
  vì research thấy nhiều case lỗi "VideoClip import error" giống hệt của user khi webm
  không có audio track hoặc muxer khác chuẩn Unity mong đợi.
- Cũng test song song bản tên file thuần ASCII để loại trừ nguyên nhân path có dấu.
- Out: không dùng AVPro hay Unity Transcode setting (đó là phương án dự phòng nếu bản
  fix vẫn lỗi).
- Không tự verify được trong Unity Editor thật (không có Unity MCP tool trong phiên
  này) → QC bằng Chrome như cũ, DoD cuối cùng cần **user tự import và xác nhận**.

## Task
- [x] Encode lại **1 pass thẳng từ mp4 gốc** (thư mục `frames/` PNG trung gian của
      request trước đã bị dọn, nên đổi cách: filter colorkey áp trực tiếp trên mp4,
      loại luôn khả năng PNG-roundtrip gây lỗi muxing) →
      `okay_vậy_hãy_tạo_video_với_hiệ_alpha_fix.webm` (video vp8 + audio Vorbis câm)
      và bản phụ `_fix_opus.webm` (audio gốc transcode Opus).
      Test: `ffprobe` cả 2 file ra `codec_name=vp8` (video) + audio track hợp lệ,
      1280x720, khớp thời lượng nguồn (~10s). ĐÃ PASS.
- [x] ~~Copy tên ASCII~~ — bỏ, vì lỗi Unity là generic import error (không phải lỗi
      đọc path), và bản gốc dùng tên có dấu vẫn import được vào Assets (chỉ lỗi lúc
      parse nội dung) → không cần thiết cô lập biến này trước.
- [~] QC bằng Chrome: **KHÔNG chạy được** — công cụ trình duyệt (claude-in-chrome) bị
      lỗi tầng browser/extension trong phiên này (tab crash ngay cả với trang tĩnh
      `example.com`, không liên quan file webm). Đã dừng theo nguyên tắc tránh rabbit
      hole, không phải lỗi của file/encode.
- [x] Cập nhật `README.md`: thêm mục "Bản fix cho Unity" — nguyên nhân nghi ngờ, lệnh
      encode mới, giải thích khác biệt bản `_fix` vs `_fix_opus`, checklist QC còn
      thiếu (Chrome + Unity thật).
- [x] User test vòng 1 (`_fix.webm` audio Vorbis, `_fix_opus.webm` audio Opus) →
      CẢ HAI vẫn lỗi. Opus bị Unity từ chối rõ ràng ("Unsupported codec 'OPUS'") —
      đúng docs, loại khỏi danh sách candidate. Vorbis vẫn lỗi generic
      `VideoClipImporter.cpp Line: 548` → audio không phải nguyên nhân chính.
- [x] Research thêm + encode vòng 2: nghi ffmpeg bỏ ghi alpha `BlockAdditional` ở
      P-frame (Chrome tự suy ra opaque khi thiếu block, Unity parser riêng có thể
      không có fallback này) → encode `-g 1 -lag-in-frames 0` ép mọi frame là
      keyframe. `muxing overhead` giảm 101%→92%, củng cố giả thuyết cấu trúc bất
      thường. Ra 2 file: `_v3_allintra_noaudio.webm` (ưu tiên),
      `_v4_allintra_audio.webm` (đối chứng, có audio Vorbis).
      Test: ffprobe cả 2 PASS (vp8 + alpha_mode=1).
- [x] User test vòng 2 → **PASS**: import Unity 6.3 thành công, hết lỗi
      `VideoClip import error`. Nguyên nhân đúng: thiếu `BlockAdditional` alpha ở
      P-frame; all-intra là fix đúng.
- [x] User báo vấn đề mới (không phải lỗi import): viền đen mờ quanh mép chi tiết
      mảnh khi chiếu trong Unity — artifact chromakey (pixel rìa bán trong suốt còn
      dính màu key đen, Unity compose straight-alpha nên lộ viền). User chọn hướng
      fix: **erode alpha 2px**. Encode `_v5_erode_noaudio.webm` (ưu tiên) +
      `_v6_erode_audio.webm` (đối chứng có audio).
      Test: ffprobe cả 2 PASS (vp8 + alpha_mode=1, khớp thời lượng).
- [ ] Chrome QC vòng 3: kết nối được browser (lỗi cũ là do 2 Chrome chưa chọn máy),
      nhưng chụp screenshot timeout liên tục với trang có video autoplay/loop — dừng
      sau nhiều lần thử, không rabbit-hole.
- [ ] User test `_v5_erode_noaudio.webm` trong Unity, báo còn viền đen không —
      **BLOCKED, chờ user**.

## DoD
- File `_fix.webm` có audio track + `alpha_mode=1` + vp8, verify Chrome không còn
  viền đen. → **1/2 đạt**: ffprobe pass, Chrome verify không chạy được (tool lỗi môi
  trường, đã ghi rõ trong README để làm lại sau).
- User xác nhận import Unity 6.3 không còn báo "VideoClip import error" (bắt buộc,
  vì đây là oracle duy nhất đáng tin cho lỗi Unity-side). → **ĐẠT** (vòng 2, file
  all-intra). Follow-up phát sinh: viền đen ở rìa (vòng 3, đang chờ user test
  `_v5_erode_noaudio.webm`).
- README cập nhật mục fix. → **Đã xong**.

## QC
- ffprobe 2 file fix: `codec_name=vp8` video 1280x720, audio (`vorbis`/`opus`) hợp
  lệ, `alpha_mode=1` trong metadata, thời lượng ~10s khớp nguồn.
- Chrome verify: KHÔNG chạy được — `mcp__claude-in-chrome__*` tab bị đóng ngay sau
  khi tạo, kể cả điều hướng tới `https://example.com` không liên quan file webm nào
  → xác nhận là lỗi công cụ/môi trường trong phiên, không phải lỗi file output. Đã
  dừng sau nhiều lần thử theo đúng nguyên tắc, không rabbit-hole.
- Chưa có xác nhận Unity Editor thật — không có Unity MCP tool trong phiên để tự
  test. Đây là phần DoD quan trọng nhất còn thiếu, cần user phản hồi.
- Dọn dẹp: xoá file test tạm (`verify_*.html`, bản copy ASCII test), xoá thư mục
  `docs/` thừa lẫn trong `temp_chromakey/` (state.json cũ từ lần init nhầm cwd).

## QC vòng 2 — kết quả user test vòng 1 + fix mới
- User import `_fix.webm` (Vorbis) + `_fix_opus.webm` (Opus) vào Unity 6.3 Mac →
  ẢNH CONSOLE xác nhận: Opus bị từ chối codec (`Unsupported codec 'OPUS'`, đúng docs
  Unity — chỉ hỗ trợ Vorbis cho webm audio); Vorbis vẫn lỗi generic
  `VideoClip import error ... VideoClipImporter.cpp Line: 548`.
- → Audio không phải nguyên nhân gốc. Chuyển hướng nghi vấn sang cấu trúc luồng
  video: ffmpeg/libvpx có thể bỏ ghi `BlockAdditional` (data alpha) ở một số
  P-frame để tối ưu — hành vi hợp lệ theo spec (thiếu block = giữ alpha frame
  trước) nhưng parser riêng của Unity có thể không implement fallback này.
- Verify gián tiếp: encode lại ép toàn bộ frame là keyframe (`-g 1
  -lag-in-frames 0`) → `muxing overhead` giảm từ ~101% xuống ~92%, cho thấy cấu
  trúc container đều/chuẩn hơn hẳn — củng cố giả thuyết (chưa phải bằng chứng
  100%, cần user xác nhận import Unity mới kết luận được).
- Trần vòng fix: đây là vòng 2/3. Nếu vòng 2 vẫn FAIL, cần `Editor.log` đầy đủ để
  soi log native chi tiết hơn dòng Console rút gọn, hoặc cân nhắc đề xuất chuyển
  sang phương án dự phòng (Unity Transcode/Keep Alpha từ 1 nguồn khác — ví dụ ProRes
  4444 — thay vì tự mux webm bằng ffmpeg).

## QC vòng 3 — import đã PASS, fix viền đen ở rìa
- User xác nhận vòng 2 **PASS**: import Unity 6.3 hết lỗi. Đóng mục lỗi import —
  DoD chính của request này đã đạt.
- Phát sinh vấn đề mới cùng file: viền đen mờ ở rìa các chi tiết mảnh khi chiếu.
  Nguyên nhân: alpha edge của `colorkey` là dải chuyển tiếp mượt, pixel trong dải
  còn dính màu key đen chưa decontaminate; Unity compose straight-alpha nên lộ viền.
  User chọn hướng fix trong 3 phương án đưa ra: **erode alpha 2px** (đơn giản, ít
  rủi ro, đổi lại rìa cứng hơn chút — chấp nhận được).
  Lệnh: filter `colorkey→split→alphaextract→erosion,erosion→alphamerge`, giữ
  nguyên toàn bộ tham số all-intra đã fix ở vòng 2.
  Ra 2 file: `_v5_erode_noaudio.webm` (ưu tiên), `_v6_erode_audio.webm` (đối chứng).
  ffprobe cả 2 PASS.
- Chrome QC: thử lại được (lỗi cũ hoá ra do có 2 Chrome kết nối chưa chọn máy nào —
  đã chọn Browser 1 macOS, connect thành công). Nhưng chụp screenshot bị timeout
  liên tục với trang có `<video autoplay loop>` — nghi script injection bị chặn bởi
  vòng lặp render video, khác lỗi cũ (không phải file webm sai). Dừng sau nhiều lần
  thử, dọn tab + tắt local server.
- Đây là bug mới (chất lượng hình ảnh), không tính vào trần 3 vòng của lỗi import
  (lỗi import đã đóng ở PASS). Đang chờ user test `_v5_erode_noaudio.webm` trong
  Unity.
