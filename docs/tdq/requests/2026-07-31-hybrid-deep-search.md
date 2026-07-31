# Request — 2026-07-31-hybrid-deep-search

## Nguyên văn yêu cầu (user, 15:53 +07)
> okay vậy tôi muốn cập nhật lại là deep sreach sẽ ưu tiên dùng agy và chạy
> default ở 3.6 flash medium, nhưng claude + tavily sẽ đi bao quát bên ngoài
> để nắm hướng (gom hết vào 1 lần chỉ spam tối đa 3agent claude) và điều phối
> agy sreach agent đi sreach chi tiết bên trong để agy và claude có thể làm
> việc colapse với nhau, hãy check xem có khả thi không và có tối ưu không?

## Cách hiểu đầu tiên
- Nâng cấp deep search 0.5.0 thành flow hybrid 2 tầng:
  1. **Scout (Claude + Tavily)**: 1 đợt duy nhất, ≤3 agent Claude, đi rộng để
     nắm hướng — output là bản đồ hướng (route, vendor/keyword, seed URL).
  2. **Detail (agy)**: orchestrator dùng output scout để chia route chi tiết,
     giao các agent search-runner (agy) đào sâu; merge kết quả cuối.
- Đổi model default của `search_task.py`: `gemini-3.6-flash-low` →
  `gemini-3.6-flash-medium` (đã xác nhận slug có thật qua
  `external_models.py list agy`).
- Mục tiêu: kết hợp độ phủ của Claude (benchmark Run B: 16 findings, không sót
  vendor) với chi phí token Claude thấp của agy (Run A: 93k vs 189k).

## Bổ sung (user, 15:59 +07)
> ngoài việc cho agy chỉ đi search sâu thì vẫn cho nó search tổng quát +
> search sâu theo điều hướng của claude — nếu agy có thêm thông tin thì có
> thể bổ sung để claude có lớp thông tin bao quát hơn.
→ Hiểu: agy có thêm vai trò "tổng quát" (lớp phủ độc lập thứ 2, song song
với scout Claude), không chỉ đào sâu theo điều hướng.

## Chốt thêm (user, 16:01 +07)
> phase 1 sẽ chỉ 1 agent claude đi song song với 1 agent agy đi rộng
→ Phase 1 cố định: 1 Claude scout ∥ 1 agy tổng quát (không phải 3+1).
Phase 2: các agent agy đào sâu theo route tổng hợp từ phase 1.
(Cap ≤3 agent Claude của user áp cho toàn flow — phase 1 chỉ dùng 1.)

## Chỗ chưa rõ (sẽ interview nếu lane full)
- Escalation chain mới khi đổi default (medium → high? còn dùng low?).
- Scout có được tính là findings cuối (merge chung) hay chỉ làm bản đồ route?
- Khi nào được phép bỏ tầng scout (câu hỏi hẹp/rõ route)?
- Cap tổng: 3 scout + 3 agy = 6 agent/run có chấp nhận không (thời gian ~2 phase).
- Format bàn giao scout → agy (routes + seed hints ghi vào brief hay file riêng).
