# PLAN — Đề xuất nâng cấp TDQ Workflow từ ECC toàn diện hơn
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-17 · Bản: 1.0 · Lane: full
Spec: `docs/tdq/spec/2026-10-17-1621-de-xuat-ecc-toan-dien.md` (bản 1.0, ĐÃ DUYỆT)
Phê duyệt spec: nguyên văn “duyệt spec”, CLI ghi 2026-10-17T16:43:20+07:00.
SHA-256 nội dung spec: `334f59a02898505b64c248956ca7058f90c13919e1ba3f442ecd9586e3ded400`
Mode thực thi: main — người dùng đã chọn “1a” tại cổng mode, CLI ghi implement_mode=main; simulator trước đó: `Winner: main (gap 0.0 minutes)`. Ba task ghi artifact phụ thuộc tuần tự; khảo sát và QC nhiều subagent chỉ đọc theo hợp đồng T1.1/T3.1.
Trạng thái plan: HOÀN THÀNH THEO FALLBACK ĐÃ DUYỆT — người dùng “duyệt lệch”, CLI ghi cả #1/#2 lúc2026-10-17T17:27:04+07:00; không nghiệm thu ultra sạch hoàn toàn. Các ghi chú “chờ duyệt” trong task/DoD là lịch sử trước thời điểm này, giữ verdict FAIL nguyên bản. Phê duyệt plan gốc: nguyên văn “duyệt plan”, 2026-10-17T16:46:36+07:00; mode main theo “1a”.
Phân công main: leader giữ T1.1 vì `mcp`; T2.1 và T3.1 theo chuỗi phụ thuộc đã chọn, leader viết artifact và quản lý phản biện; không trao quyền ghi cho người kiểm.

## Mục lục

- Quy tắc thi hành
- P1 — Bằng chứng và đối chiếu hiện trạng
- P2 — Báo cáo hợp nhất và quyết định nâng cấp
- P3 — Phản biện đa chiều, test và QC cuối
- Cụm song song và luật file nóng
- Definition of Done
- Ước tính và mô phỏng

## Quy tắc thi hành

1. Chỉ tạo O1/O2/O3 và cập nhật hồ sơ workflow. Không sửa source/test/skill/hook/policy hoặc hồ sơ đã nghiệm thu của TDQ/ECC. Windows/PowerShell trước; macOS/Linux ghi xử lý sau, ngoài nghiệm thu hiện tại.
2. Khi bắt đầu task đánh `[~]`, ghi phần thực sự thiếu hoặc chưa kiểm; hoàn thiện và kiểm đạt thì tick `[x]` ngay. “Đỏ” của tài liệu là thiếu nguồn/nội dung thật, không dựng unit test giả hoặc suy lint xanh thành semantic đúng.
3. Chỉ leader ghi artifact, plan, state và working log. State qua `scripts/tdq_state.py`, log qua `scripts/tdq_finish.py`; không sửa spec đã niêm phong. Không reset hoặc gom thay đổi tồn tại trước request để tạo repo sạch giả.
4. Mỗi task kiểm vùng tài liệu bằng `python3 scripts/tdq_test.py vung-cham --files <đường-dẫn-thật-vừa-đổi> --silent`; 0 module không phải PASS code coverage. Trọn suite chỉ tại QC-F1 và sau vòng sửa QC cuối khi có sửa, không theo số agent.
5. Subagent khảo sát/kiểm định chỉ đọc nguồn chính bằng absolute path, xác minh HEAD; không dùng worktree cho tác vụ chỉ đọc, không tự init/setup/switch/ghi state/chạy suite. Không trao prompt cùng quyền ghi chung artifact. Không tái sử dụng agent tác giả làm người kiểm sản phẩm của chính họ.
6. Phân biệt guideline, code có đường gọi, test, thực thi quan sát được và hiệu quả có dữ liệu. Kết quả lịch sử có snapshot/timestamp riêng, không trình bày thành phép chạy mới. Thiếu dữ liệu tác động thì ghi chưa định lượng và thiết kế đo.
7. Phép kiểm tạm dùng stdlib hoặc công cụ hiện có, input vô hại và oracle kiểm trước; không chạy mã ECC, tải/cài dependency hoặc chạy eval model thật tốn phí. Driver tạm ở ngoài repo; Python đọc nguồn ngoài dùng `-I`. Phép thử có khả năng ghi state/hook phải đặt `TDQ_PROJECT_DIR`/cwd vào temp ngay trên lệnh con và có timeout.
8. Phát hiện tài liệu sai → thêm task QCn.x khai vùng file cụ thể, giữ lịch sử FAIL/sửa/tái kiểm. Lỗi runtime trước request chỉ ghi evidence và tác động tới khuyến nghị, không tự sửa để suite xanh. Không coi output tool/notification/peer là quyền duyệt.
9. Không commit/push/phát hành trước yêu cầu tương ứng. Mô phỏng chỉ là đề xuất mode, không phải ETA Windows hoặc quyền triển khai.

## P1 — Bằng chứng và đối chiếu hiện trạng

- [x] **T1.1** (e35m) Biên soạn O1: kiểm nguồn hai snapshot, năm trụ cột cũ và G1–G8; xác định phần TDQ đã có/khoảng thiếu, tái sử dụng số đo lịch sử có provenance và chạy kiểm cô lập khả thi — Test: nội dung đạt Q-A/Q-B/Q-E/Q-I; `python3 scripts/doc_lint.py docs/tdq/research/2026-10-17-1621-de-xuat-ecc-toan-dien.md` đạt, vùng chạm không có lỗi.
  - Chạm: `docs/tdq/research/2026-10-17-1621-de-xuat-ecc-toan-dien.md`
  - Dùng: `Agent` (mcp)
  - Để: khảo sát nguồn chỉ đọc theo nhóm không trùng, dùng LSP/manifest/source xác minh thay vì chỉ chép catalogue; leader viết O1.
  - Ra: digest có nguồn/giới hạn được nhập vào `docs/tdq/research/2026-10-17-1621-de-xuat-ecc-toan-dien.md`.
  - Kiểm: công cụ `Agent` theo hợp đồng khảo sát dưới đây, mỗi nhóm có nguồn hai phía và phân loại chứng cứ; leader đối chiếu claim quyết định trước khi dùng.
  - Không dùng cho: ghi artifact/state, triển khai runtime, thực thi ECC, web/CVE/giá model hoặc eval trả phí.

### Hợp đồng khảo sát và kiểm cô lập

Nguồn TDQ chính: `C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow`; ECC: `C:/Users/admin/Documents/ECC`. HEAD khởi điểm theo spec; đọc lại Git status/HEAD để ghi sai khác. Bản đồ cũ dùng tìm điểm vào, không thay bằng chứng source.

Chia khảo sát chỉ đọc G1/G2/G6 (ngữ cảnh/bài học/skill) và G3/G4/G5/G7/G8 (eval/trace/risk/session/role) khi cần đọc nhiều file; không lặp cùng truy vấn cho nhiều agent. D01–D10 dùng evidence cũ nhưng leader kiểm lại nguồn quyết định ưu tiên, hành vi còn hiện hành và giới hạn. Không dùng digest ban đầu đã bị bác làm nguồn kết luận.

O1 cần có:
- Ma trận năm trụ cột và G1–G8: TDQ đã có, cơ chế ECC, nguồn file:line, entry point/caller/config/test, khoảng thiếu và trạng thái bằng chứng.
- Xác minh trực tiếp compact anchor, eval chạy lặp/scorer, trace audit, lane/QC, language-rule lazy load, host adapter và model/effort role config đã có; không nói TDQ chỉ hỗ trợ một host hoặc có lane Standard khi nguồn không chứng minh.
- Ranh giới an toàn memory, đề xuất lane/QC/model không thay quyền người dùng; phân biệt subprocess evaluator có thật với mô tả skill.
- Các phép kiểm cô lập khả thi: scorer trên fixture tổng hợp vô hại (đủ/thiếu trace, thứ tự đúng/sai); nhánh compact qua entry point/helper thật khi đã đọc side effect. Kiểm parser input rỗng/type không đúng hoặc phục hồi khi đường gọi liên quan cho phép, không mở thành audit bảo mật toàn repo.
- Driver/command đầy đủ, input/oracle, output, môi trường/timeout và dữ liệu thô. Không gọi formula hoặc fixture là đo chất lượng agent thật. Đường không kiểm được ghi lý do và tác động; không thay bằng assertion tự chấm.

**Xong P1 khi:** nguồn và giới hạn đủ để viết quyết định, mỗi nhóm có kết luận hoặc điều chưa xác minh cụ thể, không có claim hiệu quả ngoài evidence.

## P2 — Báo cáo hợp nhất và quyết định nâng cấp

- [x] **T2.1** (e35m) Biên soạn O2: hợp nhất D01–D10 với các khoảng thiếu có căn cứ trong G1–G8, phiếu nâng cấp, chi phí/lợi ích, dependency và roadmap Windows trước — Test: nội dung đạt Q-B–Q-F; `python3 scripts/doc_lint.py docs/tdq/reports/2026-10-17-1621-de-xuat-ecc-toan-dien.md` đạt, vùng chạm không có lỗi.
  - Chạm: `docs/tdq/reports/2026-10-17-1621-de-xuat-ecc-toan-dien.md`
  - Cần: T1.1

O2 phải đọc độc lập để ra quyết định, gồm:
- Tóm tắt dễ hiểu: vấn đề, ưu tiên, nên làm/thử/hoãn/không làm; nói rõ chưa triển khai.
- Bản đồ TDQ đã có/khoảng thiếu và ánh xạ từng D01–D10 sang giữ/sửa/gộp/hoãn/không làm, không bắt đủ mười tám đề xuất.
- Phiếu theo spec §3: nguồn, ví dụ trước/sau, điểm tích hợp dự kiến, tối thiểu thay đổi, phương án không làm, dependency, công sức thấp/cơ sở/cao có phân rã và duy trì, rủi ro/rollback, phép đo và go/no-go.
- Không cộng chồng lợi ích; tách giờ công/thời gian máy/token, assumptions và số đo. Không có corpus/đơn giá thì không sinh precision/recall/%/ROI tiền giả.
- Thiết kế đánh giá request sau: đối chứng cùng nhiệm vụ/quyền/chất lượng, tiêu chí oracle và yếu tố gây nhiễu; không chạy phiên model thật ở đây.
- Roadmap theo dependency và điều kiện vào/ra; Windows/PowerShell là mục tiêu hiện tại. Backlog **macOS và Linux xử lý sau**, kèm điều kiện quay lại và bằng chứng còn thiếu. Không cam kết release hoặc xây daemon khi chưa có nhu cầu.

**Xong P2 khi:** O2 truy ngược được O1, gói ưu tiên có điều kiện kiểm chứng, không đánh đồng guideline/source/test/hiệu quả đã đo.

## P3 — Phản biện đa chiều, test và QC cuối

Log: BỎ — chỉ tài liệu, không runtime mới; vẫn ghi working log và thời điểm kiểm.
Unit test runtime mới: BỎ — không sửa code; giữ lint, semantic review, kiểm cô lập và suite hiện có theo ultra.

- [x] **T3.1** (e35m) Đã hoàn thiện hồ sơ theo fallback lệch #1/#2 chờ duyệt, không đạt ultra nguyên bản hoàn toàn — Thực hiện phản biện đa chiều, QC ultra và hoàn thiện O3 với Q-A–Q-J cùng QC-F1–F4 — Test: phản biện và kiểm độc lập theo hợp đồng dưới đây, lint artifact đạt, suite QC-F1 đạt và mọi finding tài liệu được xử lý/tái kiểm.
  - Chạm: `docs/tdq/qc/2026-10-17-1621-de-xuat-ecc-toan-dien.md`
  - Cần: T1.1, T2.1
  - Dùng: `Agent`
  - Để: gọi các reviewer độc lập theo chiều và `tdq-workflow:tdq-qc-tester` kiểm cuối, leader xử lý finding và ghi O3.
  - Ra: verdict/evidence từng Q-A–Q-J, phản biện, sửa và tái kiểm tại `docs/tdq/qc/2026-10-17-1621-de-xuat-ecc-toan-dien.md`.
  - Kiểm: công cụ `Agent` theo hợp đồng QC đa chiều; đối chiếu từng verdict và command/output thật, không chỉ heading hoặc số lượng dòng.
  - Không dùng cho: sửa runtime/spec, tự duyệt, chạy suite theo mỗi reviewer hoặc coi nhiều đồng thuận là bằng chứng.

### Hợp đồng QC đa chiều

Các lời gọi dưới đây là **công cụ Agent**, không giả định một CLI semantic-review tồn tại. Người kiểm khác người tạo digest khảo sát tương ứng và khác tác giả artifact. Dùng absolute repo chính, kiểm HEAD, chỉ đọc; không `isolation=worktree`.

Gọi các reviewer trong cùng một lượt để chạy song song, tối đa một người cho mỗi chiều:

| Nhãn | Công cụ/vai trò | Phạm vi và output bắt buộc |
|---|---|---|
| `qc-nguon-khoang-thieu` | Agent `general-purpose`, kế thừa model, chỉ đọc | Kiểm nguồn/caller/config và TDQ đã có, G1–G8, D01–D10; trả Q-A/Q-B/Q-C cùng source cụ thể, lỗi và giới hạn |
| `qc-thiet-ke-an-toan` | Agent `general-purpose`, kế thừa model, chỉ đọc | Kiểm phiếu §3, quyền duyệt/memory/trace, phương án tối thiểu/không làm, dependency/rollback và Windows scope; trả Q-D/Q-F/Q-J |
| `qc-dinh-luong-roadmap` | Agent `general-purpose`, kế thừa model, chỉ đọc | Tính lại số từ dữ liệu gốc, kiểm assumptions, lợi ích giao nhau, công sức/duy trì, go/no-go và thiết kế đối chứng; trả Q-E/Q-F/Q-I |

Prompt mỗi reviewer: đọc spec/plan/O1/O2, chỉ kiểm chiều được giao, dùng nguồn và phép tính độc lập, trả finding có severity/file:line/scenario/evidence, cùng PASS/FAIL/chưa xác minh theo mã. Không sửa, chạy suite hoặc triển khai; không tự đọc transcript cá nhân/call API. Khi cần driver cô lập, chỉ stdlib, temp và timeout theo quy tắc thi hành; cung cấp lệnh/input/output thật. Không làm lại toàn bộ chiều khác.

Leader xác minh từng finding. Finding thật → thêm QCn.x khai O1/O2/O3 đúng vùng, sửa nhỏ nhất và tái kiểm người phát hiện; không che lịch sử FAIL. Reviewer mâu thuẫn → đối chiếu nguồn/oracle, giữ chưa xác minh nếu chưa phân xử được. Không đổi spec ngoài quyền.

Sau xử lý phản biện, gọi **một** `tdq-workflow:tdq-qc-tester` độc lập kiểm cuối Q-A–Q-J, đọc findings/fix và evidence CLI; không phải reviewer tự nghiệm thu kết quả của mình. Prompt yêu cầu đọc artifact thật, kiểm các claim quyết định và tính toán, tái lập phép kiểm cô lập trọng yếu, không chỉ kiểm hình thức; trả từng mã, verdict, nguồn/command/output và giới hạn. Dùng log/ledger suite của leader nếu cùng snapshot, không chạy trùng suite.

### Lệnh kiểm hiện có và người chạy

Leader chạy tại QC-F1:

```text
python3 scripts/tdq_test.py tron-bo --silent
python3 scripts/tdq_test.py so
python3 scripts/doc_lint.py docs/tdq/research/2026-10-17-1621-de-xuat-ecc-toan-dien.md docs/tdq/reports/2026-10-17-1621-de-xuat-ecc-toan-dien.md docs/tdq/qc/2026-10-17-1621-de-xuat-ecc-toan-dien.md
```

Có vòng sửa QC → sau vòng sửa cuối chạy lại suite và ghi ledger, không thêm lần chạy thứ ba chỉ vì chép output hoặc đổi người kiểm. Test failed/skipped và lỗi có từ trước phải ghi thật. Smoke vô hại mỗi tiến trình có trần 120 giây theo ultra; không tự nâng trần. Runtime mới và UI KHÔNG ÁP DỤNG, không dựng daemon hoặc phiên agent trả phí để lấp bảng.

QC-F2: chạy vùng chạm ba tài liệu, ghi rõ 0 module không là PASS unit coverage; semantic có reviewer kiểm. QC-F3: đối chiếu từng ràng buộc spec §5, diff/CLI thật. QC-F4: KHÔNG ÁP DỤNG — không sửa file code.

## Cụm song song và luật file nóng

- Task ghi artifact tuần tự: `T1.1 → T2.1 → T3.1`. O1/O2/O3 mỗi file một chủ ghi, không có task triển khai độc lập để giao cùng wave.
- Khảo sát chỉ đọc trong T1.1 có thể chia nhóm không trùng như hợp đồng; phản biện trong T3.1 chạy song song theo ba chiều, sau đó kiểm cuối. Đây là hỗ trợ khảo sát/QC, không quyết định mode thực thi tài liệu thay người dùng.
- Plan/state/log do leader sở hữu. Nếu QC yêu cầu sửa O1/O2, leader thêm task fix khai đúng file và dependency; không cho reviewer ghi đè tác giả.
- `Chạm:` cho tài liệu được khai để simulator biết quyền ghi; không symbol runtime thay đổi, không thêm caller source/test vào quyền ghi. Quan hệ source ở spec §2b và O1 là bằng chứng khảo sát, không phải blast radius sửa code.
- Không tạo thêm file evidence theo từng agent chỉ để tăng song song; dùng digest trả về, leader tổng hợp vào O1/O3.

## QC vòng 1 — fix

- [x] **QC1.1** Ghi minh bạch sai isolation/model ở research/reviewer, kiểm absolute-source/diff/worktree và ghi lệch Q10 ánh xạ Q-J; không sửa quá khứ thành tuân thủ — Test: reviewer thiết kế tái kiểm O1/O3, `git worktree list`, source/ECC diff và `tdq_state.py lech list` có #1 chờ người dùng.
  - Chạm: `docs/tdq/research/2026-10-17-1621-de-xuat-ecc-toan-dien.md`, `docs/tdq/reports/2026-10-17-1621-de-xuat-ecc-toan-dien.md`, `docs/tdq/qc/2026-10-17-1621-de-xuat-ecc-toan-dien.md`
  - Cần: T1.1, T2.1

- [x] **QC1.2** Sửa phân rã P0 theo tổng từng phiếu thành 3.5h thiết kế +5.5h triển khai +7h kiểm; giữ 16h tổng — Test: reviewer định lượng tính lại độc lập và lint/vùng chạm đạt.
  - Chạm: `docs/tdq/reports/2026-10-17-1621-de-xuat-ecc-toan-dien.md`, `docs/tdq/qc/2026-10-17-1621-de-xuat-ecc-toan-dien.md`
  - Cần: T2.1

- [x] **QC1.3** Bổ sung gap auth macOS của eval real-run trên Windows và làm chính xác citation descriptor/store enforcement, PreCompact summary — Test: reviewer nguồn tái kiểm Q-A/B, lint/vùng chạm đạt; không đọc credential hoặc chạy live eval.
  - Chạm: `docs/tdq/research/2026-10-17-1621-de-xuat-ecc-toan-dien.md`, `docs/tdq/reports/2026-10-17-1621-de-xuat-ecc-toan-dien.md`, `docs/tdq/qc/2026-10-17-1621-de-xuat-ecc-toan-dien.md`
  - Cần: T1.1, T2.1

## Definition of Done

Ánh xạ nguyên vẹn spec §6: **10 dòng Q-A–Q-J**. Các điều kiện semantic dùng **một lời gọi Agent kiểm cuối chung** tại T3.1 sau phản biện phân chiều, không gọi lại một agent cho mỗi dòng. Lệnh suite/lint không thay semantic, semantic không thay command đã chạy.

- [x] **Q-A** O1 nguồn/provenance được xác minh, không đánh đồng guideline/code/test/thực thi/hiệu quả — Lệnh kiểm: công cụ `Agent`, `tdq-workflow:tdq-qc-tester`, theo hợp đồng T3.1; PASS mục Q-A với nguồn thật và xử lý claim cũ sai.
- [x] **Q-B** O1/O2 phủ các nhóm/trụ cột, TDQ đã có và khoảng thiếu — Lệnh kiểm: cùng lời gọi công cụ `Agent` kiểm cuối T3.1; đọc verdict Q-B từ nội dung, không đếm heading.
- [x] **Q-C** O2 ánh xạ từng D01–D10 và gộp đề xuất có lý do — Lệnh kiểm: cùng lời gọi công cụ `Agent` kiểm cuối T3.1; đọc verdict Q-C.
- [x] **Q-D** O2 phiếu đề xuất đủ trường §3, ví dụ, không làm/rollback/go-no-go — Lệnh kiểm: cùng lời gọi công cụ `Agent` kiểm cuối T3.1; đọc verdict Q-D từng phiếu.
- [x] **Q-E** O1/O2 tách dữ liệu/mô hình, tính lại khớp, không cộng chồng hay chạy eval model thật — Lệnh kiểm: cùng lời gọi công cụ `Agent` kiểm cuối T3.1; đọc verdict Q-E cùng dữ liệu/command tính lại.
- [x] **Q-F** O2 roadmap đúng dependency, Windows trước, macOS/Linux sau — Lệnh kiểm: cùng lời gọi công cụ `Agent` kiểm cuối T3.1; đọc verdict Q-F và kiểm backlog không nằm nghiệm thu.
- [x] **Q-G** O3 có phản biện đa chiều, kiểm cuối và lịch sử xử lý finding — Lệnh kiểm: cùng lời gọi công cụ `Agent` kiểm cuối T3.1; leader đối chiếu verdict Q-G với lời gọi/kết quả thực rồi ghi O3.
- [x] **Q-H** PASS evidence leader cập nhật sau notification suite2 (134module, failed0,434.79s,exit0; ledger2/2); verdict kiểm cuối trước đó CHỜ được giữ trong O3 — O3 lint/suite đạt, giữ skip/provenance, không gọi vùng 0 module là coverage — Lệnh kiểm: `python3 scripts/tdq_test.py tron-bo --silent` tại QC-F1 và lint ba artifact theo T3.1; kiểm cuối xác nhận evidence, không chạy lại lệnh theo dòng DoD.
- [x] **Q-I** PASS (lệch #2 Q9, chờ duyệt; kiểm cuối FAIL tiêu chí tái lập nguyên bản) — O1/O3 phép kiểm cô lập có input/oracle/output, biên/giới hạn rõ, không runtime giả — Lệnh kiểm: cùng lời gọi công cụ `Agent` kiểm cuối T3.1; tái lập driver vô hại trong O1, đọc verdict Q-I.
- [x] **Q-J** PASS (lệch #1 Q10, chờ duyệt; kiểm cuối FAIL nguyên bản, Git độc lập bị chặn) — Không sửa source/ECC/hồ sơ cũ hoặc vượt quyền; state/log đúng CLI, giữ thay đổi có trước — Lệnh kiểm: cùng lời gọi công cụ `Agent` kiểm cuối T3.1, đối chiếu `git diff --check`, `git status --short`, `git diff --stat`, `git -C C:/Users/admin/Documents/ECC status --short` và lịch sử CLI; đọc verdict Q-J.

QC tổng gồm 10 DoD và QC-F1–F4, không thêm tiêu chí sản phẩm ngoài spec. Nghiệm thu sau khi mọi mục có quyết định/evidence, không còn finding tài liệu mở; chưa định lượng có phương pháp không đồng nghĩa hiệu quả đã chứng minh.

## Ước tính và mô phỏng

Tổng dự toán tác nghiệp: **105 phút** = T1.1 35 + T2.1 35 + T3.1 35. Đây là thời gian dự kiến làm việc, không gồm chờ duyệt, không là cam kết và không phải công sức triển khai các nâng cấp được đề xuất. Không cộng thời gian reviewer song song thành wall-clock leader.

Lệnh simulator bắt buộc trên plan:

```text
python3 scripts/tdq_bench.py simulate --plan docs/tdq/plan/2026-10-17-1621-de-xuat-ecc-toan-dien.md --thuc-do docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json --he-so-agent 1.5
```

Kết quả thật lúc 2026-10-17T16:45:40: 3 task, giao được 2, leader giữ 1, 2 wave; `Winner: main (gap 0.0 minutes)`. Mô hình trả main/team cùng 6.1 phút sau làm tròn. Bộ hằng số lịch sử không phản ánh độ sâu đọc nguồn hoặc QC đa chiều của request này; không phải ETA Windows và không thay dự toán tác nghiệp 105 phút. Không suy main nhanh hơn đáng kể từ gap 0.0. Không đặt `implement_mode` trong state ở bước lập plan. Các mode khả dụng kiểm qua CLI: main và subagent; Codex chưa được người dùng cấp quyền, không xin quyền hoặc chạy calibration trong request này.
