# Kiểm chứng test và đề xuất tối ưu TDQ Workflow
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày kiểm tra: 27/10/2026 · Request: `2026-10-27-1246-do-dung-bao-toan-loi`  
HEAD: `d1b90b825596e84aba7136b02a545bc2fa06c21a` · Nhánh: `bugfix/do-dung-bao-toan-loi`

## 1. Kết luận để quyết định

**Chưa nên bật chạy song song mặc định.** Kiểm tra bổ sung phát hiện ba khoảng trống: thiếu 16 test trong bằng chứng cũ, cấu hình parallel làm mất fixture `tmp_path`, và sáu test tokenizer bị skip sai điều kiện trên Windows.

Đã chạy bổ sung 16 test: **15 pass, 1 skip có chủ đích**. Phạm vi chuẩn sau đối chiếu là **3.306 case, 13 skip**, tương ứng 3.293 case không skip trong các lượt đã ghi nhận. Tuy nhiên, smoke test riêng của parallel có **1 ERROR**, và chẩn đoán sáu assertion tokenizer có **5 pass, 1 FAIL**. Vì vậy không diễn giải con số coverage thành “tất cả chức năng đã đạt”.

Lượt này chỉ thêm bằng chứng và báo cáo; không sửa mã nguồn, test hay skill production. Giữ nguyên báo cáo cũ như ảnh chụp lịch sử; báo cáo bổ sung này thay thế kết luận “3290 đã đủ coverage” trong báo cáo trước.

## 2. Đã kiểm tra gì, kết quả thế nào

| Hạng mục | Cách kiểm | Kết quả | Thời gian tiến trình |
|---|---|---|---:|
| Bằng chứng Full gần nhất | Đối chiếu HEAD và hash 342 file nguồn với lượt Full trước | Còn khớp; không có thay đổi trong scripts/tests/hooks/skills | Kiểm tra phạm vi ban đầu 1,771 giây |
| Full unittest trước đó | 3.206 case trên cùng nguồn; tái sử dụng receipt, không chạy lại toàn bộ | PASS, 10 skip | 688,269 giây, số đo lịch sử cùng phiên |
| Pytest bổ sung trước đó | 84 case trong 6 module pytest | 82 pass, 2 skip | 6,845 giây, lịch sử cùng phiên |
| Collection mới | So sánh ID từng case của unittest và pytest | 3.306 case; phát hiện 16 ID thiếu ở module trộn hai kiểu test | 1,514 giây |
| Chạy đúng 16 ID thiếu | Pytest, HOME/USERPROFILE riêng, basetemp riêng | 15 pass, 1 skip | 1,047 giây |
| Smoke parallel giữ `no:tmpdir` | 1 test thật, 2 worker, các cờ liên quan giống runner | ERROR: fixture `tmp_path` not found | 0,953 giây |
| Smoke parallel giữ plugin tmpdir | Cùng test, 2 worker, thư mục tạm riêng | 1 pass | 0,959 giây |
| Kiểm tra thư viện tokenizer | Import bằng `.venv-tokens/Scripts/python.exe` | PASS | 0,082 giây |
| Sáu assertion tokenizer, HOME trống | Chỉ tháo skip decorator trong bộ nhớ, giữ nguyên assertion | 5 pass, 1 fail: 0 nhóm thay vì hơn 10 | 2,409 giây |
| Sáu assertion, HOME có registry plugin | HOME riêng, chép metadata plugin cần thiết; đọc skill thật | 5 pass, 1 fail: 2 nhóm thay vì hơn 10 | 2,847 giây |
| Đối chiếu cuối | Hợp ID bổ sung với discovery; kiểm nguồn và HEAD | 3.306 ID duy nhất, hash 342 file khớp | Không chạy lại suite |

**Giới hạn bằng chứng:** Full unittest cũ không có manifest ID từng case làm receipt riêng; phép đối chiếu dùng discovery mới, cùng số lượng và nguồn không đổi. Đây là lý do đề xuất lưu manifest case ngay lúc chạy. Các chẩn đoán mới cũng không thay thế một lượt Full trên Linux/macOS hoặc kiểm chứng mọi tổ hợp phiên bản dependency.

Collection chạy với plugin autoload tắt để thu thập ổn định; các test bổ sung và smoke chạy pytest thực tế. Lượt Full trước chạy quyền người dùng thường; smoke mới thuộc môi trường của agent. Không dùng smoke này để kết luận về quyền POSIX hay symlink.

Các harness mới kiểm hash `~/.claude/CLAUDE.md` trước/sau và đều ghi nhận không thay đổi. Đây là kiểm tra file cấu hình này, không phải chứng minh toàn bộ filesystem bất biến.

## 3. Những phát hiện cần xử lý

### 3.1. Đủ module không có nghĩa đủ test

`tests/test_team_chong_conflict.py` chứa cả unittest và các hàm pytest. Unittest đã thu thập module này, nhưng bỏ qua 16 hàm/biến thể pytest. Cách bổ sung “chỉ chạy những module chưa xuất hiện” không phát hiện được chúng.

**Cần làm:** collection manifest ở cấp node ID; so sánh tập dự kiến, đã thực thi, pass/fail/error/skip. Module chỉ dùng để tóm tắt. ID thiếu, collection lỗi hoặc trùng ID phải làm kết quả INCOMPLETE/ERROR, không được PASS.

Pytest hỗ trợ thu thập cả hàm test lẫn unittest.TestCase; dùng `--collect-only -q` để kiểm danh mục. Nguồn: [pytest good practices](https://www.pytest.org/en/latest/explanation/goodpractices.html), [pytest usage](https://pytest.org/en/stable/how-to/usage.html).

### 3.2. Parallel backend hiện làm hỏng fixture

`scripts/tdq_test.py::_run_pytest` truyền `-p no:tmpdir`. Plugin đó cung cấp `tmp_path`, trong khi test thật đang dùng fixture này.

Đã tái hiện bằng `tests/test_archify_artifacts.py::test_document_digest_basic`: giữ cờ gây ERROR; giữ plugin và cấp basetemp riêng thì pass. Đây là smoke có kiểm soát, không phải một lượt Full parallel. Lệnh chẩn đoán dùng 2 worker thay cho auto để giới hạn tải; chưa sửa runner.

Ngoài ra, `subprocess.run` của backend không truyền timeout dù có nhánh bắt TimeoutExpired. Đây là phát hiện từ đọc mã, chưa phải thử nghiệm treo tiến trình. Cần timeout cấu hình được và dọn cả cây worker trên Windows; timeout không được biến thành PASS.

### 3.3. Tokenizer đang skip sai và test phụ thuộc máy

Production đã chọn `Scripts/python.exe` trên Windows, nhưng điều kiện skip trong `tests/test_skill_tokens.py` vẫn kiểm `.venv-tokens/bin/python`. Thư viện thực tế import được.

Khi chạy sáu assertion bị che bởi skip, năm assertion pass. Assertion còn lại đòi hơn 10 dòng nhóm nguồn plugin; môi trường riêng trống có 0, registry plugin hiện tại có 2. Test đo bảng bị gắn với số plugin cài trên một máy, nên không portable.

**Cần làm:** nhận diện venv theo platform và tạo fixture inventory xác định. Giữ kiểm tra token tên nhỏ hơn mô tả và kiểm tra dữ liệu không rỗng bằng fixture có số lượng dự kiến. Không xóa assertion chất lượng, không cài thêm plugin chỉ để thỏa ngưỡng 10. Năm pass chẩn đoán không xóa sáu skip trong số liệu chuẩn; standard runner chưa được sửa.

### 3.4. Phân loại 13 skip

| Nhóm | Số case | Cách xử lý đề xuất |
|---|---:|---|
| Quyền POSIX không tương đương Windows | 3 | Có job Linux/macOS phù hợp |
| Symlink không tạo được trong lượt quyền thường | 3 | Job có capability; giữ lý do skip rõ |
| Tokenizer kiểm sai đường dẫn venv | 6 | Sửa điều kiện và fixture; cần chạy thật |
| Help của tdq_state.py không dùng argparse | 1 | Skip có chủ đích, line 95–96 của test_team_chong_conflict.py |

Không coi mọi skip là lỗi, cũng không coi mọi skip đều hợp lệ lâu dài. Một bộ test giảm số skip bằng cách bỏ test sẽ không đạt DoD.

## 4. Vì sao runtime tốn thời gian

1. **Full suite đắt:** lượt thành công gần nhất mất khoảng 11 phút 28 giây. Ba lượt Full trong quá trình sửa lỗi trước đó cộng 1.951,093 giây, khoảng 32,5 phút tiến trình. Hai lượt đầu đã phát hiện lỗi; không được xem toàn bộ thời gian này là lãng phí.
2. **Bằng chứng thiếu làm phát sinh lượt kiểm tra bổ sung:** inventory ở cấp module đã bỏ sót 16 case. Chạy nhanh nhưng báo thiếu khiến vòng QC kéo dài.
3. **Thiếu cách tái sử dụng kết quả có điều kiện:** một bước report/finish có thể muốn chạy lại test dù nguồn không đổi. Cần chứng minh fingerprint đầy đủ, không dựa riêng vào HEAD.
4. **Chạy song song hiện chưa sẵn sàng:** lỗi fixture và phụ thuộc cấu hình máy có thể làm tăng số vòng sửa/retry. Nhiều worker cũng có chi phí khởi động và collection riêng.
5. **Transcript có chi phí đọc toàn kho:** read_transcripts đi qua các file ứng viên trong kho session, rồi mới xử lý phạm vi liên quan. Đây là cơ hội lập chỉ mục metadata và cache parse; chưa đo được mức giảm ở phiên bản hiện tại.
6. **Tool round trip và kiểm tra môi trường lặp:** nên gộp các đọc độc lập, lưu readiness theo fingerprint. Không bỏ cổng duyệt spec/plan mà người dùng cần.

Theo [tài liệu pytest-xdist](https://pytest-xdist.readthedocs.io/en/stable/how-it-works.html), mỗi worker thực hiện collection; session fixture cũng chạy theo worker, không tự đảm bảo chỉ một lần toàn suite ([fixture guidance](https://pytest-xdist.readthedocs.io/en/stable/how-to.html)). Vì vậy tăng worker phải đi cùng isolation và phép đo.

## 5. Đề xuất theo thứ tự thực hiện

| Ưu tiên | Hiện tại | Dự định làm | Kỳ vọng | DoD |
|---|---|---|---|---|
| P0 — coverage và skip | So module; bỏ sót pytest trong module hỗn hợp; tokenizer skip sai | Manifest từng case, phân loại skip, fixture tokenizer xác định | Báo cáo test đúng và ổn định giữa máy | 3.306 ID tại HEAD này được giải trình; thêm test ở module hỗn hợp phải phát hiện; thiếu ID/collection error không PASS; 6 tokenizer assertion chạy được với fixture |
| P0 — runner và isolation | Tắt tmpdir; timeout chưa truyền; một số test dựa HOME thật | Giữ fixture, HOME/basetemp riêng, timeout và dọn worker | Không lỗi ngay setup, không chạm cấu hình thật, không treo vô hạn | Smoke fixture pass; timeout→ERROR/INCOMPLETE; hash cấu hình người dùng không đổi; regression chứng minh không có worker mồ côi |
| P1 — tái sử dụng bằng chứng | Nguồn không đổi vẫn có thể lặp kiểm chứng | Receipt gắn fingerprint và manifest; nhiều yêu cầu cùng key dùng chung một job | Tránh một lượt Full dư khoảng 688 giây trong tình huống tương đương | Key gồm source/test/config/deps/Python/OS/quyền/runner/flags/selection/schema; thay từng thành phần phải invalid; FAIL/ERROR/INCOMPLETE không reuse thành PASS |
| P1 — readiness và batch | Có bước kiểm tra môi trường/đọc lặp | Cache readiness theo project và môi trường; batch thao tác độc lập | Giảm round trip và setup lặp | MCP disconnect, đổi config hoặc dependency phải kiểm lại; không gộp mutation phụ thuộc; giữ mọi approval cần thiết |
| P2 — 2 worker trước | Auto workers chưa được kiểm chứng toàn bộ | Sau P0, A/B serial và 2 worker, cân nhắc loadfile | Giảm thời gian thực thi khi isolation đủ tốt | Ít nhất 3 cặp A/B đảo thứ tự, cùng nguồn/env và node IDs; kết quả/skip bằng nhau; median giảm tối thiểu 20%, không flake/race; nếu không đạt thì giữ serial |
| P2 — transcript incremental | Đọc/parse nhiều file cũ | Index metadata + cache parse có fingerprint | Giảm thời gian đọc log khi chỉ vài session đổi | Cache lạnh/nóng trả cùng span/quality; append/truncate/replace/delete đều invalid; malformed và file đang ghi không bị báo complete sai |

Ngưỡng 20% là tiêu chí đề xuất để quyết định có bật 2 worker, **không phải số đã đo được**. Không thay mặc định `-n auto` chỉ từ smoke một case.

Đối với reuse, HEAD một mình không đủ vì có thể có thay đổi chưa commit hoặc môi trường khác. Cần cả dependency/fixture/config và ranh giới freshness. Một receipt PASS có các skip không hợp lệ cũng không đủ để đóng DoD chức năng.

## 6. Expect runtime: cái gì đã đo, cái gì chưa

| Thông tin | Loại bằng chứng | Cách hiểu đúng |
|---|---|---|
| Full 688,269 giây | Đã đo, cùng HEAD | Chi phí một lượt Full trước đó; không phải mọi lần sẽ giống |
| Đối chiếu phạm vi 1,771 giây; collection 1,514 giây; bổ sung 1,047 giây | Đã đo trong lượt review | Có thể kiểm freshness/phạm vi nhanh; chưa phải implementation cache hoàn chỉnh |
| Loại một Full trùng có thể tránh khoảng 11,5 phút | Ước lượng từ receipt trên | Chỉ khi cùng fingerprint và bằng chứng đầy đủ; còn overhead xác minh |
| Benchmark cũ serial 71,470 giây → 2 worker 37,677 giây | Lịch sử từ audit trước, một cặp, 389 test + 32 subtest | Giảm 47,3% ở mẫu cũ; không ngoại suy cho 3.306 case hiện tại |
| Transcript/cache readiness giảm bao nhiêu | Chưa đo ở implementation đề xuất | Phải benchmark sau khi có bản thử nghiệm |
| Tổng workflow giảm bao nhiêu phần trăm | Chưa đủ dữ liệu | Không cộng resource time của job chồng nhau thành wall time |

**Đề xuất đợt tiếp theo:** gom hai mục P0 thành một request ổn định runner và chất lượng bằng chứng; sau đó làm P1 reuse. Parallel toàn suite và index transcript triển khai sau khi có baseline đáng tin. Chưa triển khai các đề xuất này trong lượt review.

## 7. Kiểm chứng còn cần trước khi áp dụng đề xuất

- Với coverage: fixture có module trộn unittest/pytest, parametrization, case mới/thừa/thiếu, collection lỗi, skip theo capability; manifest lưu ngay trong chính lượt chạy.
- Với reuse: thử sửa từng thành phần fingerprint; kết quả cũ/lỗi/truncated receipt phải bị từ chối; hai caller đồng thời chỉ khởi chạy một job; job đang chạy không được coi là pass.
- Với parallel: smoke fixture đã chỉ ra lỗi; sau khi sửa cần suite đủ case, isolation, timeout/cancel, Windows quyền thường và POSIX phù hợp. Chưa chạy Full parallel hiện tại vì đã tái hiện lỗi nền tảng bằng một case.
- Với tokenizer: fixture inventory cố định phải kiểm số dòng, tổng skill, quan hệ token; một job CLI dùng tokenizer thật. Không dùng skip để che fixture sai.
- Với transcript: so output cache lạnh/nóng với parser hiện tại trên log append, mất dòng, thay file và session chồng nhau; giữ unknown/partial trung thực.
- Với báo cáo: phải tách case inventory, assertion chạy thật, skip và lỗi chẩn đoán. Không viết “all green” khi vẫn có phát hiện mở.

## 8. Bằng chứng có thể mở lại

Các file dưới đây là receipt hoặc log thực tế; không chứa nội dung transcript riêng tư.

- [Đối chiếu cuối: ID, nguồn, HEAD](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/review-final-proof.json).
- [Collection 3.306 ID và 16 ID thiếu](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/review-collection.json).
- [Receipt 16 test bổ sung](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/review-missing.json), [stdout](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/review-missing.stdout.txt), [JUnit](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/review-missing.xml).
- [Receipt chẩn đoán parallel/tokenizer](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/review-diagnostics.json).
- [Parallel lỗi fixture](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/review-parallel-no-tmpdir.stdout.txt), [parallel cùng test thành công](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/review-parallel-with-tmpdir.stdout.txt).
- [Tokenizer với registry riêng](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/review-tokenizer-populated.json), [log 5 pass / 1 fail](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/review-tokenizer-populated.stderr.txt).
- [Full cùng HEAD trước đó](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-F1-after-QC2.json), [84 pytest bổ sung trước đó](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-F2-pytest-isolated.json).
- [Báo cáo triển khai đợt 1 trước review](./2026-10-27-1246-do-dung-bao-toan-loi.html).
- Audit gốc: `C:\Users\admin\Documents\TDQ-Reports\2026-10-27-runtime-cost\bao-cao.html`.

Phạm vi kết luận: đủ để xác định khoảng trống và xếp thứ tự tối ưu. Chưa chứng minh backend parallel toàn suite đạt, chưa sửa các vấn đề vừa phát hiện, chưa commit/merge/push.

