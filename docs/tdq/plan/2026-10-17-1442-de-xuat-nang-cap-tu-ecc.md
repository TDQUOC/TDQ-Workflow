# PLAN — Đề xuất nâng cấp TDQ Workflow từ ECC và ước tính hiệu quả
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-17 · Bản: 1.0 · Lane: full
Spec: `docs/tdq/spec/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md` (bản 1.0, ĐÃ DUYỆT qua CLI)
Phê duyệt spec: nguyên văn “duyệt spec”, ghi nhận 2026-10-17T15:10:46+07:00.
SHA-256 spec: `8750ab433ba47c9723734fc73e6c52cd50ce6ff42c4040da9823a227d706c53a`
Mode thực thi: main — người dùng đã chọn “1a”; simulator đề xuất main, chênh lệch làm tròn 0.0 phút; ba task phụ thuộc tuần tự nên chưa có lợi ích chạy đội được chứng minh.
Trạng thái plan: HOÀN THÀNH — 3 task và QC1.1 đã xong; 9/9 DoD đạt theo O3. Phê duyệt gốc: “duyệt plan”; mode “1a”, implement_mode=main.
Phân công: leader giữ T1.1 (mcp); T2.1 và T3.1 thực hiện trực tiếp theo chuỗi phụ thuộc đã chọn, QC vẫn do agent độc lập kiểm.

## Mục lục

- Quy tắc thi hành
- P1 — Hồ sơ bằng chứng và đo nền
- P2 — Báo cáo đề xuất và roadmap
- P3 — Test và QC độc lập
- Cụm song song và luật file nóng
- Definition of Done
- Ước tính và đề xuất cách chạy

## Quy tắc thi hành

1. Chỉ tạo ba sản phẩm O1–O3 của spec; không sửa runtime, hook, state machine, dependency, source hoặc test của TDQ/ECC. Không tạo dashboard, hệ thống benchmark hoặc file mã nguồn mới trong repo.
2. Mỗi task đánh `[~]` lúc bắt đầu. Ghi tiêu chí thiếu/chưa kiểm trên artifact thật trước khi biên soạn; hoàn thiện, kiểm tra nội dung rồi tick `[x]` ngay. Với tài liệu, “đỏ” là thiếu bằng chứng/nội dung thật, không phải dựng test giả hay gọi lint thành bằng chứng semantic.
3. Phân biệt kết luận từ nguồn, phép đo và mô hình dự báo. Mọi số có nguồn hoặc giả định; không dùng confidence làm xác suất chất lượng. Có thể kết luận hoãn/không làm nhưng phải giải thích bằng chứng.
4. Kiểm vùng chạm theo từng task bằng `python3 scripts/tdq_test.py vung-cham --files <file-vừa-đổi> --silent` với đường dẫn thực tế của task. Kiểm toàn bộ chỉ tại QC-F1, chạy lại sau vòng sửa QC cuối nếu có sửa, không chạy lặp vì đổi người kiểm.
5. Phép thử state/hook/shell dùng thư mục tạm và đặt `TDQ_PROJECT_DIR` ngay trên lệnh thử; không cho phép thử ghi state thật. CLI cập nhật tiến độ request thật là ngoại lệ có chủ đích, chỉ qua `tdq_state.py`. Không chạy payload phá hoại; không thực thi mã tải về từ thư mục ECC.
6. Ghi môi trường, commit đầy đủ, trạng thái git ban đầu của cả hai repo và dữ liệu thô vào O1. Không đổi nhánh hoặc ghi vào ECC. Mã đo tạm nếu cần nằm ngoài repo/ECC, dùng thư viện chuẩn; Python đọc dữ liệu ngoài chạy với `-I`.
7. Ghi state qua CLI, working log qua `tdq_finish.py`; giữ nguyên thay đổi tồn tại trước request. Chỉ leader ghi plan/state/working log. Không sửa spec đã niêm phong.
8. QC FAIL → thêm task sửa tài liệu cụ thể, giữ phạm vi spec, kiểm lại phần ảnh hưởng; không tự sửa runtime để làm suite xanh. Lỗi môi trường hoặc lỗi trước request phải có bằng chứng, không được đổi nhãn thành PASS. Theo giới hạn vòng sửa của tdq-build; vượt giới hạn thì ghi lý do dừng đúng quy trình.
9. Không commit, push, triển khai nâng cấp hoặc phát hành trong plan này. Các mốc phiên bản là dự kiến. Không thực thi task trước khi plan và cách chạy được người dùng chốt.

## P1 — Hồ sơ bằng chứng và đo nền

- [x] **T1.1** (e35m) Hoàn thiện O1: đối chiếu cả năm trụ cột giữa hai snapshot, xác minh khoảng thiếu của TDQ và thu phép đo nền vô hại — Test: mọi trụ cột có nguồn TDQ/ECC, quan hệ thực tế, trạng thái chứng cứ; phép đo có dữ liệu thô và cách tính lại; `python3 scripts/doc_lint.py docs/tdq/research/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md` đạt.
  - Chạm: `docs/tdq/research/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md`
  - Dùng: `Agent` (mcp)
  - Để: giao khảo sát chỉ đọc cho agent có LSP khi cần đối chiếu nhiều file; leader tổng hợp, không trao quyền ghi chung tài liệu.
  - Ra: kết luận kèm nguồn và giới hạn được nhập vào `docs/tdq/research/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md`.
  - Kiểm: `python3 scripts/doc_lint.py docs/tdq/research/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md` và đối chiếu từng kết luận về nguồn thực tế; lint không thay kiểm chứng nội dung.
  - Không dùng cho: triển khai tính năng, sửa source/state, benchmark phá hoại, hoặc giao lại cùng một truy vấn cho nhiều agent.

**Phạm vi khảo sát và bằng chứng phải xuất hiện trong O1:**

| Trụ cột | Điểm vào nguồn TDQ | Kỹ thuật ECC cần đối chiếu | Kiểm thực tế và giới hạn |
|---|---|---|---|
| Hooks & Latency | `hooks/hooks.json`, entry point hook mà matcher thực sự gọi | Dispatcher, denial dampening, trivial-edit bypass | Đếm matcher/process theo sự kiện; đo startup và hook hiện có với input vô hại, tách đường găng và tổng thời gian; dispatcher chưa có chỉ được mô hình hóa |
| Multi-Agent & Worktree | `scripts/tdq_team.py`, helper registry và dependency thực của entry point | TCAS/proximity, lifecycle và cache lockfile | Xác nhận fingerprint đã có; kiểm ví dụ DAG/cùng file/phụ thuộc bằng entry point hiện có trong môi trường tạm; đánh giá cô lập cache, không tự cài dependency nặng |
| Quality & Review | `scripts/tdq_state.py`, `scripts/doc_lint.py`, quy tắc QC và test artifact liên quan | `orch-review`, phản biện độc lập, evidence | Phân biệt lint/fixture xanh với artifact được kiểm thật; kiểm luồng thiếu artifact và thông báo nền, không tự mở rộng thành bugfix |
| Shell Safety | Matcher Bash/PowerShell và implementation được gọi thật | `scanShell`, ngân sách parser, quoting/nesting/encoding | Chuỗi thử chỉ làm dữ liệu; chỉ chạy entry point phân tích an toàn đã kiểm side effect; ghi rõ đường không được bảo vệ |
| Cross-Platform Stability | Chọn shell, đường dẫn, helper subprocess/import đã tìm bằng LSP và grep | WSL stub, hardening đường dẫn/Windows | Đối chiếu điều kiện kích hoạt thật; test thư mục tạm Unicode/khoảng trắng khi khả thi; không suy luận CVE từ tên bản vá |

- Nguồn ECC: `C:/Users/admin/Documents/ECC`; dùng báo cáo request `2026-10-17-1208-deep-research-kien-truc-ecc` làm chỉ mục rồi xác minh trực tiếp nguồn. Không coi đường dẫn dự kiến là file đã xác minh.
- LSP trước tra quan hệ; không có server phù hợp hoặc import không phân giải thì ghi giới hạn và đối chiếu nguồn/manifest. Graph cũ không được dùng để kết luận không có dependency.
- Với phép đo hook khả thi: ghi lần gọi đầu riêng; warm-up không gộp vào mẫu chính; thu một tập lặp và công khai số mẫu, mọi giá trị, median/p95 và cách tính. Không gọi lần chạy đầu là cold OS cache nếu không kiểm soát cache hệ điều hành. Không đặt SLA từ tập mẫu nhỏ.
- Đầu vào thật chưa đủ cho QC precision/recall, tỷ lệ xung đột, tiết kiệm token hoặc cache: ghi “chưa định lượng”, lý do, dữ liệu còn thiếu và thiết kế đo lần sau. Không bỏ phép đo startup khả thi chỉ để dùng nhãn này cho mọi chỉ số.
- Dữ liệu nền và lệnh tái lập đặt trong O1, không thêm sản phẩm ngoài §2 spec. Các lệnh được ghi chính xác sau khi xác minh CLI/entry point, trước khi chốt task.

**Xong P1 khi:** O1 đọc được độc lập, từng trụ cột có bằng chứng hoặc giới hạn cụ thể; số đo và giả định tách riêng; trạng thái nguồn TDQ/ECC không bị sửa bởi khảo sát.

## P2 — Báo cáo đề xuất và roadmap

- [x] **T2.1** (e25m) Viết O2 từ O1: phiếu đề xuất, ma trận ưu tiên/chi phí/lợi ích và roadmap dự kiến — Test: bao phủ Q-C–Q-F, mỗi đề xuất truy ngược được ID bằng chứng; mọi phép tính đồng nhất đơn vị; `python3 scripts/doc_lint.py docs/tdq/reports/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md` đạt.
  - Chạm: `docs/tdq/reports/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md`
  - Cần: T1.1

**Cấu trúc bắt buộc của O2:**

- Tóm tắt quyết định: nên làm, điều chỉnh, hoãn hoặc không làm; ưu tiên vì vấn đề đã xác minh, không vì ECC có tính năng.
- Mỗi trụ cột có hiện trạng TDQ, cơ chế ECC, điểm TDQ đã có và phần thiếu; mô tả giải thuật/giả mã chỉ khi giải thích được khác biệt hoặc trade-off.
- Mỗi phiếu đề xuất: ID, vấn đề, nguồn hai phía, cơ chế, thay đổi tối thiểu/điểm tích hợp, phương án không làm, dependency, công sức triển khai/duy trì, rủi ro, rollback, phép đo và go/no-go.
- Ma trận thấp/cơ sở/cao khi có dữ liệu/giả định công khai; kiểm lợi ích giao nhau, tách giờ người/thời gian máy/token. Không tính ROI tiền nếu chưa có đơn giá; thiếu dữ liệu thì nêu cách quyết định tạm thời.
- Roadmap `v0.72.0–v0.75.0` là dự kiến: thứ tự theo dependency và bằng chứng, điều kiện vào/ra từng giai đoạn; kỹ thuật không có lợi ích được loại thay vì cố lấp đủ phiên bản.
- Giới hạn và điều kiện mở request triển khai riêng; O2 chính là report kết thúc, không sinh report lặp lại.

**Xong P2 khi:** người đọc chọn được đề xuất và điều kiện kiểm chứng, không hiểu dự báo là số đo triển khai; không có phần trăm chất lượng từ confidence tự chấm.

## P3 — Test và QC độc lập

Log: BỎ — chỉ biên soạn tài liệu, không có runtime mới; working log và timestamp phép đo vẫn bắt buộc.
Unit test runtime mới: BỎ — không sửa mã nguồn; giữ kiểm tài liệu, kiểm ngữ nghĩa, phép đo tái lập và suite hiện có.

- [x] **T3.1** (e20m) Thực hiện QC ultra và hoàn thiện O3 với kết quả Q-A–Q-I — Test: `python3 scripts/tdq_test.py tron-bo --silent` tại QC-F1, lint ba artifact, kiểm độc lập theo hợp đồng bên dưới; chỉ hoàn tất khi mọi điều kiện DoD có bằng chứng và không còn lỗi chưa xử lý.
  - Chạm: `docs/tdq/qc/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md`
  - Cần: T1.1, T2.1
  - Dùng: `Agent`
  - Để: gọi `tdq-workflow:tdq-qc-tester` kiểm độc lập spec/plan và O1/O2, tái lập phép đo an toàn, kiểm nguồn/tính toán và mọi Q-A–Q-I; không giao QC cho agent đã viết đề xuất.
  - Ra: kết quả độc lập và bằng chứng được leader ghi vào `docs/tdq/qc/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md`.
  - Kiểm: một lần gọi công cụ `Agent` theo hợp đồng kiểm định dưới đây, trả từng mã Q-A–Q-I cùng PASS/FAIL/giới hạn, bằng chứng nguồn/lệnh/output và phát hiện cần xử lý.
  - Không dùng cho: tự sửa spec, sửa runtime, tự hạ QC, ghi state, hoặc tính thông báo tác vụ nền là phê duyệt.

### Hợp đồng lệnh kiểm định độc lập

“Lệnh kiểm” ngữ nghĩa bên dưới là **lời gọi công cụ Agent**, không phải một CLI được giả định tồn tại. Gọi một lần, không gọi lại cho từng dòng DoD:

- `subagent_type`: `tdq-workflow:tdq-qc-tester`.
- `description`: theo model thực tế và effort của vai trò, hậu tố `qc-de-xuat-ecc`.
- `prompt`: đọc spec, plan, research và reports cùng slug `2026-10-17-1442-de-xuat-nang-cap-tu-ecc` tại repo hiện hành; kiểm Q-A–Q-I, trả từng mã, verdict, vị trí bằng chứng và lỗi. Không chỉ kiểm tồn tại chuỗi/heading. Kiểm đầy đủ nguồn cho kết luận quyết định ưu tiên, tính lại bảng định lượng từ dữ liệu thô, tái lập phép đo khả thi trong thư mục tạm. Chạy suite QC-F1 và lint nếu leader chưa chạy; nếu đã chạy trên cùng nội dung, dùng output đầy đủ có provenance để tránh chạy trùng. Không sửa file/state hoặc duyệt gate.
- Bằng chứng đầu vào kèm theo prompt: nội dung snapshot/môi trường từ O1, kết quả kiểm đã chạy, git status/diff trước và sau, mọi giới hạn môi trường đã biết.
- Agent kiểm nguồn/tính toán bằng chính công cụ đọc và thực thi, không chỉ phê chuẩn nhận định của người viết. Leader đối chiếu từng phát hiện, áp dụng sửa tài liệu rồi kiểm lại; nếu lỗi không thuộc phạm vi, nêu rõ và xử lý theo quy tắc dừng chứ không tự sửa code.

**Lệnh lint artifact:**

```text
python3 scripts/doc_lint.py docs/tdq/research/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md docs/tdq/reports/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md docs/tdq/qc/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md
```

**Kịch bản QC phải kiểm nội dung thật:**

- Luồng chính: lần từ ưu tiên trong O2 đến vấn đề, nguồn hai repo, phép đo/giả định và điều kiện triển khai.
- Biên thiếu dữ liệu: QC/scheduling không có corpus/lịch sử → ghi chưa định lượng và cách bổ sung, không tự sinh tỷ lệ.
- Biên không có lợi ích: dependency nhẹ hoặc kỹ thuật đã có → có lý do giữ nguyên/hoãn; không ép áp dụng.
- Thất bại/phục hồi: nguồn hoặc phép đo không tái lập → ghi FAIL, sửa/rút kết luận rồi kiểm lại. Không sửa input để đạt số mong muốn.

## Cụm song song và luật file nóng

- Chuỗi bắt buộc: `T1.1 → T2.1 → T3.1`. Ba cụm ghi file, mỗi cụm một chủ ghi; không có hai task triển khai độc lập để chạy đồng thời. Mỗi task sở hữu một đường dẫn O1/O2/O3, không khai wildcard.
- Trong T1.1 có thể gọi agent **chỉ đọc** theo nhóm hooks/shell/Windows; team/worktree; QC/state/evidence. Kết quả trả về để leader tổng hợp O1, không tạo thêm sản phẩm. Đây là hỗ trợ khảo sát, không tự chọn mode triển khai đội.
- Agent QC độc lập bắt buộc kể cả khi người dùng chọn `main`; mode triển khai không loại bỏ QC ultra.
- Dòng `Chạm:` của plan này chỉ khai tài liệu để simulator thấy quyền ghi và chuỗi phụ thuộc; không có symbol runtime bị đổi nên không phát sinh caller cần sửa. Căn cứ quan hệ nguồn đã có ở spec §2b; khi khảo sát vẫn xác minh lại bằng LSP/manifest.
- Không có file sản phẩm nào chung giữa các task. Plan/state/log do leader quản lý. QC yêu cầu sửa O1/O2 → leader thêm task sửa tương ứng, khai đường dẫn và dependency; không để QC agent ghi đè tài liệu của tác giả.

## Definition of Done

Ánh xạ nguyên vẹn §6 spec. Có **9 dòng DoD**. Các dòng ngữ nghĩa dùng chung **một** lệnh công cụ Agent tại T3.1, đọc đúng verdict theo mã; không chạy bảy/tám agent lặp lại và không coi kiểm hình thức là kiểm nội dung. Lệnh suite tại Q-H chạy một lần ở QC-F1; các kết quả lint bổ trợ được lưu trong O3.

- [x] **Q-A** O1 xác minh nguồn/commit và quan hệ thực tế — Lệnh kiểm: công cụ `Agent` theo hợp đồng T3.1; PASS mục Q-A khi kết luận quan trọng đối chiếu khớp nguồn hai repo và provenance rõ ràng.
- [x] **Q-B** O1 tái lập phép đo, có dữ liệu thô/môi trường/cách tính và giới hạn — Lệnh kiểm: công cụ `Agent` theo hợp đồng T3.1; PASS mục Q-B khi tính lại được kết quả và phép đo không chạy được được nêu trung thực.
- [x] **Q-C** O2 phủ từng trụ cột cùng hiện trạng/khoảng thiếu/kết luận — Lệnh kiểm: công cụ `Agent` theo hợp đồng T3.1; PASS mục Q-C từ nội dung từng trụ cột, không từ việc chỉ tồn tại heading.
- [x] **Q-D** O2 có đủ trường của mọi đề xuất, kể cả không làm/rollback/go-no-go — Lệnh kiểm: công cụ `Agent` theo hợp đồng T3.1; PASS mục Q-D khi từng trường có nội dung thực chứng hoặc giả định được ghi rõ.
- [x] **Q-E** O2 tách đo/dự báo, không trộn đơn vị hoặc cộng chồng, thiếu dữ liệu ghi rõ — Lệnh kiểm: công cụ `Agent` theo hợp đồng T3.1; PASS mục Q-E sau khi tính lại bảng và đối chiếu giả định.
- [x] **Q-F** O2 có roadmap phụ thuộc và điều kiện chuyển, không cam kết phát hành — Lệnh kiểm: công cụ `Agent` theo hợp đồng T3.1; PASS mục Q-F khi thứ tự roadmap không mâu thuẫn dependency và scope đã duyệt.
- [x] **Q-G** O3 có QC độc lập và xử lý phát hiện, không báo PASS thiếu kiểm — Lệnh kiểm: công cụ `Agent` theo hợp đồng T3.1; đối chiếu kết quả độc lập thực tế với bảng Q-A–Q-I được leader ghi, giữ nguyên mọi giới hạn/verdict.
- [x] **Q-H** Tài liệu qua lint và suite hiện có đạt, lỗi không bị che giấu — Lệnh kiểm: `python3 scripts/tdq_test.py tron-bo --silent`; kết quả lint ba artifact theo lệnh tại T3.1 là bằng chứng bổ trợ bắt buộc. Không tick nếu lint hoặc suite còn lỗi chưa xử lý.
- [x] **Q-I** Không sửa runtime/ECC, không nới gate/phát hành; state qua CLI, thay đổi trước request được giữ — Lệnh kiểm: công cụ `Agent` theo hợp đồng T3.1; đối chiếu git status/diff/snapshot hai repo và lịch sử CLI, không chỉ dựa vào tuyên bố người viết.

## Ước tính và đề xuất cách chạy

Tổng dự toán tác nghiệp: **80 phút** = T1.1 35 + T2.1 25 + T3.1 20. Không gồm chờ duyệt; đây là dự toán, không cam kết thời gian. Nếu thiếu dữ liệu ngoài môi trường hiện có, áp dụng cách ghi giới hạn trong spec, không tự mở rộng công việc.

Lệnh mô phỏng bắt buộc trên plan:

```text
python3 scripts/tdq_bench.py simulate --plan docs/tdq/plan/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md --thuc-do docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json --he-so-agent 1.5
```

Kết quả chạy ngày 2026-10-17: simulator đọc 3 task, giao được 2 task, leader giữ 1 task, chia 2 wave; hệ số agent 1.5. Dòng kết luận nguyên văn: `Winner: main (gap 0.0 minutes)`. Mô hình trả main 6.1 phút và team 6.1 phút sau làm tròn; không có bằng chứng từ mô phỏng này rằng main nhanh hơn đáng kể.

Đây không phải benchmark Windows hoặc ETA thực. Bộ hằng số cũ và mô hình công cụ không thay dự toán tác nghiệp 80 phút; chỉ dùng đề xuất chế độ theo quy trình. Chuỗi phụ thuộc và một file mỗi đầu ra là lý do không ưu tiên overhead điều phối đội. Chế độ khả dụng đọc từ CLI ngày 2026-10-17: `main`, `subagent`; `codex` chưa được người dùng cấp quyền cho workflow gọi và bộ hằng số không có số đo Codex. Không chạy calibration hoặc xin quyền Codex trong bước này. Kết quả trên được ghi trước cổng chọn mode; sau đó người dùng trả lời “1a” và CLI đã đặt `implement_mode=main`.

## QC vòng 1 — fix

- [x] **QC1.1** Sửa provenance ECC của E-T2/D06 từ hai dẫn nguồn sai số dòng sang nguồn carrier thật, giữ ranh giới giữa nguyên tắc ECC và projection đề xuất cho TDQ — Test: đọc `scripts/lib/context-carriers.js:146-170` tại ECC đúng snapshot; QC độc lập xác nhận Q-A, lint O1/O2 và vùng chạm đạt.
  - Chạm: `docs/tdq/research/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md`, `docs/tdq/reports/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md`
  - Cần: T1.1, T2.1
