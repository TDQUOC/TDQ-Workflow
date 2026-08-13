## Nguyên văn
> hiện tịa video outpout khi tôi import vào unity thì thấy báo lỗi hãy mở request check và fix

Mục tiêu: file `okay_vậy_hãy_tạo_video_với_hiệ_alpha.webm` (VP8 alpha, xuất ở request
trước [[2026-08-11-xoa-nen-video-webm]]) khi import vào Unity bị báo lỗi — cần xác
định lỗi cụ thể và fix.

Phạm vi đoán: lỗi có thể do (a) Unity không đọc được container/codec webm libvpx
build từ ffmpeg (thiếu track audio/muxer flag lạ), (b) tên file có dấu tiếng Việt +
khoảng trắng gây lỗi import path, (c) thiếu audio track làm Unity import warning chứ
không phải lỗi, (d) phiên bản Unity/platform không hỗ trợ VP8 software decode.

Chưa rõ — CẦN HỎI: nguyên văn thông báo lỗi Unity hiện ra khi import (chưa có, đây là
thông tin bắt buộc để chẩn đoán đúng, không đoán).

## Hiểu & kiến thức

## Hỏi đáp
