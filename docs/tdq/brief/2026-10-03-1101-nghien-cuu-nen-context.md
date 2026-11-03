# BRIEF — Nghiên cứu nén context và tối ưu thời gian chạy của workflow

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> Vậy bây giờ mở request research chi tiết giúp tôi tìm giải pháp có cách nào compress context và
> optimize bộ workflow này hơn ko để save context hơn và optimize working time hơn không và output
> request này là báo cáo và bảng đề xuất có ít nhất 3 hướng. Chưua thay đổi gì bộ workflow ở tuẻn
> này

**Đọc lần đầu**

- Mục tiêu: tìm cách giảm context mà workflow nạp vào phiên VÀ giảm thời gian chạy một request,
  mà không hạ chất lượng (soul: chất lượng > runtime > context cost).
- Đầu ra: một báo cáo nghiên cứu + bảng đề xuất **ít nhất 3 hướng**, mỗi hướng có số đo/ước lượng.
- Ràng buộc cứng: **không thay đổi bộ workflow trong request này** ("chưa thay đổi gì … ở turn
  này") — chỉ đo, đọc, nghiên cứu, viết báo cáo. Không sửa `skills/`, `hooks/`, `scripts/`.
- Mốc hiện tại (đo 2026-10-03, tokenizer thật, bản 0.56.0): lane full sàn 53.602 token, xấu nhất
  68.407; lane quick sàn 21.337, xấu nhất 36.142; luôn nạp 2.704/phiên.
- Thời gian gần nhất (request 2026-10-03-0732): implement 35 phút; plan 2h06 (gồm chờ duyệt);
  cột model time không đo được trên Windows.
- Chỗ chưa rõ (hỏi ở interview): "working time" là thời gian máy hay thời gian chờ user; phạm vi
  có gồm hook/token runtime trong phiên (lời nhắc, output lệnh) hay chỉ file luật; được thử
  nghiệm đo trên bản sao (không sửa workflow) hay chỉ phân tích giấy.

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Nguồn | Dùng? | Vì sao |
|---|---|---|---|
| Trợ lý `general-purpose` + WebSearch/WebFetch | built-in | ĐÃ DÙNG | tìm hiểu bên ngoài (tavily không có trong phiên này) |
| Tokenizer thật `.venv-tokens` | repo | ĐÃ DÙNG | mọi số token |
| `tdq_timing.py`, transcript JSONL | repo / máy | ĐÃ DÙNG | thời gian máy theo phase |
| `code-review`, `simplify` | built-in | KHÔNG | không có mã để soát — đầu ra là báo cáo |

### Đã biết (hai file nghiên cứu, 2026-10-03)

Chi tiết và phương pháp: `docs/tdq/research/2026-10-03-1101-nghien-cuu-nen-context.md` (bên
ngoài) và `docs/tdq/research/2026-10-03-1101-do-noi-bo.md` (đo nội bộ).

- **File luật KHÔNG phải nơi tốn nhất.** Sàn lane full 53,6K token, trong khi mỗi lần gọi API
  mang trung bình ~491K token (tối đa 966K) trên 2.624 lần gọi; ~90% là hội thoại tích luỹ.
- **Thời gian máy chỉ 14,9% đồng hồ** (69.300 / 464.820 s trên 11 request); còn lại là chờ user.
  Trong thời gian máy: model 59%; trọn bộ test 31% (59 lần chạy ≥ 200 s ở 8 request, ~7,4 lần
  mỗi request, nay ~363 s mỗi lần). Độ trễ trung vị tăng từ 3,9 s (< 100K context) lên 7,3 s
  (> 600K).
- **Cache bị ghi lại nguội:** 24 lần gọi ghi lại 11,7M token, 74% mọi lần ghi cache.
- Đầu ra lệnh shell ~456K token / 895 lệnh; mẩu `edited_text_file` ~204K token / 381 lần; hook
  SessionStart ~2,1K × 24 lần resume ≈ 50K ở phiên excalidraw; trợ lý mỗi lần khởi động 22–26K.
- Trong 100.858 token file luật: 16,7% khối code, 15,6% file khuôn mẫu, 6,1% chú thích HTML; chữ
  trùng y hệt chỉ ~1%.
- Bên ngoài: context càng dài chất lượng càng giảm (18/18 model); tuân luật giảm khi số luật
  đồng thời tăng; tỉa + tóm tắt hội thoại cắt token và thời gian rõ rệt; hook output trần 10.000
  ký tự; fork dùng chung cache của phiên cha, trợ lý thường thì không. **Một số con số bên ngoài
  chưa được kiểm chéo** (giá đọc cache 0,05×, hai bài arXiv 2605/2606, trần phía Codex) — QC
  phải xác minh trước khi đưa vào báo cáo.

### Đã chốt

- Đầu ra: một báo cáo + bảng đề xuất ≥ 3 hướng; mỗi hướng có số đo hoặc ước lượng có nguồn, cái
  giá về chất lượng/kiểm soát, áp được cho Codex không.
- Không sửa workflow. Thử nghiệm chỉ trên bản sao tạm ngoài repo.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | CÓ (đã chạy) | 4 góc, 1 file nghiên cứu |
| Đo nội bộ | CÓ (đã chạy) | transcript thật + tokenizer thật |
| Vòng phạm vi | BỎ | user đã chốt đầu ra và ràng buộc |
| Interview chi tiết | CÓ | 6 câu, hết câu hỏi |
| Spec → plan | CÓ | khung bất biến |
| Implement = thử nghiệm trên bản sao + viết báo cáo | CÓ | không đụng workflow |
| Soát lỗi `code-review` / rút gọn `simplify` | BỎ | không có mã |
| QC: kiểm chéo mọi con số và nguồn | CÓ | mức `full` |

Luồng: (1) kiểm chéo số bên ngoài · (2) thử nghiệm nén trên bản sao · (3) bảng đề xuất · (4) báo cáo.

## Hỏi đáp

Vòng phạm vi: BỎ — user đã chốt đầu ra (báo cáo + ≥ 3 hướng) và ràng buộc (không sửa workflow).

| # | Câu hỏi | Trả lời (2026-10-03) |
|---|---|---|
| 1 | "Thời gian làm việc" là gì? | **B** — chỉ thời gian MÁY chạy (agent làm, lệnh/test chạy), không tính thời gian chờ user |
| 2 | Được đo thử nghiệm? | **A** — có, trên bản sao tạm NGOÀI repo; workflow thật không đụng, bản sao xoá sau khi đo |
| 3 | Đề xuất giảm cổng duyệt? | **A** — được, nhưng ghi rõ cái giá về kiểm soát; user quyết khi đọc báo cáo |
| 4 | Phạm vi host? | **A** — Claude Code là chính, ghi chú hướng nào áp được cho Codex |
| 5 | Mức QC? | **A** — `full` |
| 6 | Bổ sung? | **A** — không |

Ghi chú: hai trợ lý nghiên cứu (tìm hiểu bên ngoài + đo nội bộ) khởi động ở phase này đã bị dừng
trước khi viết file; chưa có kết quả nào.
