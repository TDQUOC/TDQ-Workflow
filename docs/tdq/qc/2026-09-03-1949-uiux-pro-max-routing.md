# QC — Ưu tiên tra ui-ux-pro-max cho các case UI/UX
Ngày: 2026-09-03 · Plan: ../plan/2026-09-03-1949-uiux-pro-max-routing.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

14 dòng DoD + 4 hạng mục cố định = 18 hạng mục.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Bảng routing có dòng UI/UX nêu đúng tên ui-ux-pro-max | `pytest -k routing_co_dong_uiux` | 1 passed | PASS |
| Q2 | Khối luật nêu đủ ba tầng | `pytest -k ba_tang` | 1 passed | PASS |
| Q3 | Nói rõ ui-ux-pro-max chỉ phủ tầng giữa | `pytest -k tang_giua` | 1 passed | PASS |
| Q4 | Dùng từ tra cứu, không có từ ra lệnh tuyệt đối | `pytest -k khong_menh_lenh` | 1 passed | PASS |
| Q5 | Mức ràng buộc bỏ qua được kèm một dòng lý do | `pytest -k muc_rang_buoc` | 1 passed | PASS |
| Q6 | Nêu đủ ba plugin ghép được | `pytest -k ghep_duoc` | 1 passed | PASS |
| Q7 | Có câu loại trừ Unity/game | `pytest -k loai_tru_unity` | 1 passed | PASS |
| Q8 | `skill_inventory.py --tat-ca` in ≥1 dòng plugin:ui-ux-pro-max | `skill_inventory.py --tat-ca \| grep -c` | 7 dòng | PASS |
| Q9 | Bản vá không đổi số dòng của các nguồn plugin khác | so md5 bảng đếm trước/sau bản vá | md5 trùng khít | PASS |
| Q10 | Bộ test riêng của request xanh toàn bộ | `pytest tests/test_uiux_routing.py -q` | 11 passed | PASS |
| Q11 | Suite toàn repo không vượt mốc đỏ có sẵn | `pytest -q` | 100 đỏ (đúng mốc), xanh 1548→1559 | PASS |
| Q12 | Ba bundle CLEAN | `tdq_checkportable.py check --root <3 bundle>` | CLEAN 93/143/86 | PASS |
| Q13 | doc_lint exit 0 trên brief, spec, plan, QC | `doc_lint.py <4 file>` | 0 violation | PASS |
| Q14 | Không file nào ngoài repo bị đụng | `git status --porcelain` | chỉ file trong repo | PASS |
| QC-F1 | Toàn bộ suite | `python3 -m pytest -q` | 100 failed, 1559 passed, 1 skipped | PASS |
| QC-F2 | Hồi quy vùng `Chạm:` | test của 3 module bị chạm | 24 + 81 + 11 passed | PASS |
| QC-F3 | Ràng buộc kiến trúc spec §5 (R1–R4) | kiểm từng dòng | R1–R4 giữ nguyên | PASS |
| QC-F4 | Clean code — 5 câu tự kiểm | đọc lại `_plugin_skill_dirs` | 5/5 "có" | PASS |

## Bằng chứng

### Q1–Q7 — bảy điều kiện văn bản luật
```
$ python3 -m pytest tests/test_uiux_routing.py -q -k "routing_co_dong_uiux or ba_tang or tang_giua or khong_menh_lenh or muc_rang_buoc or ghep_duoc or loai_tru_unity"
7 passed, 4 deselected in 0.01s
```

### Q8 — plugin đã hiện trong kiểm kê
```
$ python3 scripts/skill_inventory.py --tat-ca | grep -c "plugin:ui-ux-pro-max"
7
$ python3 scripts/skill_inventory.py --tat-ca | grep "plugin:ui-ux-pro-max" | cut -d'|' -f1
banner-design / brand / design-system / design / slides / ui-styling / ui-ux-pro-max
```
Trước bản vá con số này là 0 — đúng defect B3 của brief.

### Q9 — không phình bảng
Đếm số dòng theo từng nguồn plugin, bỏ riêng ui-ux-pro-max ra, so md5 giữa bản gốc
(`git stash`) và bản vá:
```
622d58132ab2f8563e8ad00765594dba   (trước bản vá, mọi nguồn)
622d58132ab2f8563e8ad00765594dba   (sau bản vá, trừ ui-ux-pro-max)
```
Tổng số dòng 217 → 226 (7 skill mới + 2 dòng khung). Cộng thêm hai ca test canh:
`khong_phinh_bang` (plugin không có thư mục skill → không sinh dòng) và
`uu_tien_thu_muc_skills_truoc` (có cả hai bố cục thì vẫn lấy `skills/`).

### Q10 — bộ test riêng
```
$ python3 -m pytest tests/test_uiux_routing.py -q
11 passed in 0.02s
```
11 ca: 7 ca văn bản luật, 3 ca hàm quét, 1 ca luật đã xuống bundle.

### Q11 / QC-F1 — suite toàn repo
```
$ python3 -m pytest -q
100 failed, 1559 passed, 1 skipped, 1482 subtests passed in 94.13s
```
Mốc đỏ có sẵn là 100 (báo cáo request 1733). Đã đối chứng riêng
`tests/test_skill_router.py`: `97 failed, 17 passed` giống hệt nhau trước và sau bản vá,
nên không có ca đỏ nào do lần sửa này gây ra.

### Q12 — ba bundle
```
CLEAN    93 file(s) match the manifest    (portable_claude)
CLEAN    143 file(s) match the manifest   (portable_codex)
CLEAN    86 file(s) match the manifest    (antigravity_portable)
```
Luật mới có mặt trong cả bốn bản sao `plugin-routing.md` của ba bundle
(portable_claude, portable_codex có hai bản, antigravity_portable).

### Q13 — doc_lint
```
$ python3 scripts/doc_lint.py <brief> <spec> <plan> <qc>
done — 0 violation(s) total, exit 0
```

### Q14 — không đụng file ngoài repo
`git status --porcelain` chỉ liệt kê file trong repo. Hai đường dẫn cấm
(`~/.claude/plugins/`, thư mục nguồn plugin) nằm ngoài repo nên không thể xuất hiện; plugin
chỉ được ĐỌC (`sed -n` trên `SKILL.md`) để lấy tên 7 skill.

### QC-F2 — hồi quy vùng Chạm
```
$ python3 -m pytest tests/test_skill_inventory.py -q          → 24 passed
$ python3 -m pytest tests/test_build_portable.py tests/test_checkportable.py -q → 81 passed
$ python3 -m pytest tests/test_uiux_routing.py -q             → 11 passed
```
`skills/tdq-conventions/references/plugin-routing.md` không có module test riêng ngoài bộ
test mới của request; `doc_lint` phủ phần khuôn dạng.

### QC-F3 — ràng buộc kiến trúc spec §5
- R1 — không file nào trong plugin hay trong bundle bị sửa tay; bundle chỉ đổi qua
  `build_portable.py`. Đối chiếu `git status`: mọi file bundle đổi đều là file sinh.
- R2 — dòng `figma` giữ nguyên; khối luật nói rõ figma là nguồn sự thật khi đã có file
  thiết kế, ui-ux-pro-max chỉ lấp chỗ trống → không mâu thuẫn.
- R3 — khối luật 28 dòng, không chép catalog: chỉ nêu số đo tổng (88 style, 192 bảng màu,
  74 cặp font, 119 nguyên tắc, 22 stack).
- R4 — `def _plugin_skill_dirs(home, project)` giữ nguyên chữ ký (dòng 162) và vẫn trả
  `[(tên plugin, thư mục skill)]`; định dạng bảng in ra không đổi.

### QC-F4 — clean code, 5 câu
- SRP: có — vòng lặp thêm vào chỉ làm một việc là chọn bố cục thư mục.
- OCP: có — thêm một bố cục mới chỉ cần thêm một phần tử vào tuple `(("skills",), (".claude", "skills"))`.
- LSP: có — hàm vẫn trả đúng một kiểu `list[tuple[str, str]]`, không thêm nhánh trả kiểu khác.
- ISP: có — không thêm tham số nào.
- DIP: có — vẫn đi qua đúng `_plugin_skill_dirs`, không dựng đường quét thứ hai song song.
Không câu nào "không", nên không phải sửa lại mã.

## Kết luận
PASS toàn bộ 18/18 hạng mục, vòng 1, không có task fix nào phải thêm vào plan.
