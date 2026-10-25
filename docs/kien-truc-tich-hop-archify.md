# Hợp đồng tích hợp Archify — agent-first

Phiên bản hợp đồng: 1 · 2026-10-25 · Request: `2026-10-24-2348-hoan-thien-archify`.
Đây là thiết kế thực thi đã chốt, chưa phải báo cáo nghiệm thu. Thay thế các nhận định thiếu bằng chứng của bản trước.

## 1. Trách nhiệm

Agent hiện tại khảo sát bằng LSP/Grep/Graphify có kiểm freshness, viết BA và candidate. Archify 3.2.0 kiểm schema, bố cục và dựng HTML; không tự phân tích repo. TDQ giữ binding, snapshot và trạng thái publish. Không gọi endpoint AI riêng trong đợt này.

Một BA có actor, trigger, input, rules, happy path, exceptions, output và acceptance. View lựa chọn architecture/workflow/sequence/lifecycle/ERD theo câu hỏi, không bắt tất cả dạng cho mọi task.

## 2. Giao diện module đã khóa

Các module đều stdlib; hàm công khai dưới đây là contract cho triển khai. Tên chỉ đổi nếu đồng bộ caller/tests/docs cùng nhau.

### Delivery — scripts/archify_delivery.py

- `find_archify_root() -> str | None`: ARCHIFY_ROOT explicit sai không fallback; nếu không khai dùng home/Documents/archify và sibling dự án, chấp nhận root gói trực tiếp hoặc repo chứa archify/bin. Không hard-code admin.
- `get_archify_bin(root=None) -> Path | None`.
- `check_environment() -> dict`: node_ok, node_version, archify_root, ready; error giải thích nếu thiếu. Node từ 18.
- `build_finalize_command(diagram_type, candidate_path, output_path, quality='showcase', repo_root=None, archify_root=None) -> list[str]`.
- `run_finalize(diagram_type, candidate_path, output_path, quality='showcase', repo_root=None, archify_root=None, timeout=120) -> FinalizeResult`: dataclass `status: bool`, `receipt: dict`; optional get cho tương thích, không override tuple.
- `open_artifact(file_path) -> bool`: chỉ file HTML có thật, truyền file URI qua browser/platform API an toàn, không nội suy PowerShell.
- `atomic_delivery(target_path, content) -> Path`: ghi file tạm độc quyền cùng thư mục, fsync, replace, từ chối symlink. Không ghi nhiều artifact cùng PID vào một temp cố định.

run_finalize không publish Master hay bind doc. Nó tạo output trong staging của caller khi caller cần rollback toàn bộ. Thành công đòi exit 0, JSON object, ok=true, status=pass, gates validate/deliver/check=pass, native browser-check=pass; explainer chấp nhận not-run. Artifact path/hash/bytes khớp receipt, candidate hash trước/sau không đổi. Hash trong compact receipt phải kiểm thật. Timeout/malformed/stale output trả false có diagnostics. UTF-8 rõ ràng, stderr timestamp qua TDQ_LOG, stdout CLI chỉ JSON. CI offline đặt ARCHIFY_UPDATE_CHECK_DISABLED=1.

### Model — scripts/archify_model.py

- `graphify_to_archify(graph_json_path, focus_community=None, max_nodes=None, *, repository=None, evidence_kind='working-tree') -> dict`: trả **Archify IR thuần**, không có trường TDQ ngoài schema. Topology raw chỉ là candidate chưa publish.
- `graph_coverage(graph, selected_ids) -> dict`: total/selected/excluded/unknown inventory, directed flag, lý do lọc và quan hệ không đủ hướng.
- `validate_model(model) -> dict`: kiểm object envelope dưới đây, path tương đối an toàn, ID/view trùng, current cần revision đúng 40 hex và repository; view không vượt root. Trả model hợp lệ hoặc ValueError.

Sources dùng path/line/end_line đúng upstream; không bịa vai trò từ tên file; mặc định backend khi không khai loại nhưng ghi rõ là topology candidate. Graph không directed thì không vẽ cạnh như call có hướng; coverage giữ quan hệ unknown. Không gắn committed sources nếu evidence_kind planned/working-tree. repository có url/revision/link_mode và chỉ dẫn nguồn đúng snapshot; engine kiểm cuối bằng Git. Layout grid explicit để engine không phải đoán tọa độ thiếu.

### Artifacts — scripts/archify_artifacts.py

- `document_digest(path) -> str`: SHA-256 UTF-8 bytes của doc sau loại đúng khối `<!-- tdq-archify-binding:start -->` đến `<!-- tdq-archify-binding:end -->`; chặn nhiều khối hoặc marker thiếu cặp.
- `source_fingerprint(project, paths=None) -> dict`: map path tương đối -> SHA-256, không theo symlink ra ngoài; exclude .git, node_modules, .venv, __pycache__, graphify-out, docs/architecture và docs/tdq, logs, docs/workinglog, output candidate/receipts. Khi explicit paths là nguồn, không tự mở rộng ngoài root.
- `build_manifest(project, document, candidate, artifact, receipt, *, evidence_kind='planned', revision=None, coverage=None, request=None, lane=None) -> dict`: schema_version=1; giữ file path khả chuyển, các hash document/candidate/artifact, source_files fingerprint, evidence_kind, revision, coverage, engine và receipt. Không ghi secret. Đầu vào receipt dict.
- `check_manifest(project, manifest) -> dict`: trả `{status: 'current'|'stale'|'invalid', reasons: [...]}`; kiểm hash nguồn, tài liệu/candidate/artifact, revision khi committed, không coi thiếu file như current.
- `bind_document(document, manifest_path) -> None`: chèn/đổi khối binding chứa đường dẫn manifest và hash manifest. document_digest không phụ thuộc khối này, không vòng tự băm.
- `check_binding(document, manifest_path) -> dict`: kiểm hash manifest trong binding cùng document_digest.
- `publish_bundle(staging, destination) -> Path`: directory bundle hợp lệ; lock độc quyền cạnh destination; không xóa lock tự ý nếu không biết owner sống/chết. Stage phải chứa index.html và manifest.json; caller đã validate. Hoán đổi snapshot bằng rename với backup/rollback, reject symlink và path nesting; cleanup chỉ file do mình tạo. Trả destination/index.html.
- `mark_stale(project) -> dict`: đọc docs/architecture/manifest.json nếu có, check freshness, ghi status.json riêng (không sửa manifest đã bind); absent -> skip, lỗi -> invalid.

Delivery không import artifacts/model. Model không import delivery. Artifacts không import CLI. CLI import ba module. Finish gọi mark_stale, không gọi AI/render.

## 3. CLI và envelope Master

Tất cả CLI chạy từ project đích; scripts nằm dưới plugin root, không giả target repo có scripts TDQ.

| Lệnh | Contract |
|---|---|
| check | Kiểm Node/engine, exit 0 khi ready |
| render | `--type TYPE --candidate PATH --out HTML [--quality standard|showcase] [--repo-root ROOT] [--document MD --request SLUG --lane full|quick]` |
| open | `HTML` |
| bridge | `--graph JSON --out JSON [--community ID] [--max-nodes N]` tạo candidate và coverage sidecar, không publish Master |
| sync-master | `--model JSON [--project ROOT] [--out DIR]` dựng mô hình agent-authored; mặc định out docs/architecture; graph raw không phải model |
| status | `[--project ROOT]` kiểm manifest Master và in freshness |
| verify | `--document MD --manifest JSON [--project ROOT]` kiểm binding/freshness, exit khác 0 khi stale |

render không document trả artifact_unbound rõ. Có document: sinh candidate/manifest cạnh output, bind trước cổng duyệt; không sửa doc đã duyệt âm thầm. Plan kiểm verify trước code. Đường CLI giữ receipt local được engine phát và không sửa bytes HTML sau finalize.

Master model (input agent viết, không phải schema Archify):

```json
{
  "schema_version": 1,
  "title": "Kiến trúc dự án",
  "evidence_kind": "committed",
  "revision": "40-hex-commit",
  "repository": {"url": "https://example.invalid/team/repo.git", "revision": "40-hex-commit", "link_mode": "local-only"},
  "source_paths": ["src/main.py"],
  "coverage": {"modules": [{"id": "app", "status": "verified"}], "unknown": [], "excluded": []},
  "views": [{"id": "overview", "type": "architecture", "candidate": "overview.json", "summary": "Bản đồ module"}]
}
```

Đây là minh họa cấu trúc, không là fixture evidence. Revision thực phải hợp lệ. `working-tree`/`planned` phải ghi nhãn, không xuất thành committed. Candidate relative to model parent, cấm path traversal/symlink escape; external repo root qua --project. Model agent authored phải cover inventory hoặc ghi unknown/excluded. Không có trần view im lặng. Master index là HTML cục bộ có thông tin revision/freshness/coverage và links tới từng view Archify; mỗi view tự chứa tài nguyên. Index dùng markup an toàn và escaped labels, không renderer sơ đồ tự viết. Không nhúng hơn giới hạn upstream vào explainer để vượt hợp đồng.

## 4. Lifecycle

Full: spec + candidate + HTML + manifest → binding vào spec → user duyệt → plan tham chiếu → verify trước code. Quick tương tự tại mini-plan. Binding không là gate mới.

Master được dựng từ model của snapshot xác định. Code đổi → finish mark_stale → agent đọc diff/evidence và sửa model → sync-master. Sau merge kiểm revision nhánh đích, không cho bản nhánh khác tự nhận current. HTML offline là snapshot: status CLI/finish là nơi phát hiện thay đổi, không hứa trang tĩnh theo dõi file.

Task preview planned được giữ làm lịch sử, không cập nhật bằng Master. Compare chỉ hiển thị diff, không merge mô hình. Nếu publish lỗi giữ bản đã xác minh, báo stale/invalid có nguyên nhân.

## 5. Agent-first và môi trường

ARCHIFY_ROOT là cấu hình active duy nhất cần thiết cho engine. Agent dùng context hiện tại vẫn có chi phí của host; không gọi là zero-cost. Endpoint OpenAI-compatible chỉ là hướng dự phòng nếu đường agent không dùng được, chưa có client trong đợt này. Không đọc key store của harness; không truyền env secrets vào HTML. User cho phép dữ liệu dự án khi thực sự cần endpoint đã cấu hình, không bao gồm dữ liệu ngoài dự án.

Engine ghim hợp đồng 3.2.0, Node >=18. Giữ native browser gate; explainer browser-check not-run không bằng visual review. Test offline tắt update check. Cấu hình fallback thiếu engine là thông báo rõ, không link tới file chưa có.

## 6. Tính khả chuyển và lỗi

Dùng sys.executable hoặc python theo môi trường, đường CLI absolute plugin root, output project root. Mở file qua URI, không shell interpolation. Temp file unique, concurrent lock, UTF-8 stdout/stderr và child decoding. Không sửa state trực tiếp.

Runtime bundle phải gồm module phụ thuộc thực tế; tests kiểm closure import, không chỉ đếm số file. Ràng buộc scripts không import hooks giữ nguyên. Không sửa luật workflow chỉ để vượt token budget; dùng reference một tầng và generator indices/lock.

## 7. Baseline và kiểm chứng

Baseline trước request mới: 5d6570d; nền trước tích hợp: a03d698. Log cũ bpzrsod7w: 2829 tests, 14 failures, 1 error, 9 skipped. Không coi mọi lỗi là baseline khi chưa đối chứng. Hai lỗi tái hiện ở phân tích: encoding adapter (150,266) và indices quick-lane/plan-template/spec-template. False-success finalize tái hiện bằng mocked process: exit 1/check fail/HTML cũ -> status true. Cú pháp skill positional -> argparse exit 2.

Kiểm đơn vị: delivery, model, artifacts, pipeline, distribution, finish, workflow-contract. Runtime: repo fixture có commit thật, native và explainer render bằng engine thật, Master cập nhật khi source đổi, doc/candidate mutation stale. Browser: đọc nhãn, focus, zoom, view links, console; mỗi smoke/runtime cap 120s. Không coi test mock xanh là schema/render đạt.

## 8. Tiêu chí bàn giao

Các mục Q1–Q8 trong spec mới là authority. Report tách unit/runtime/browser/reviewer/baseline, chờ hết tác vụ nền. Không có điều kiện tự tick thành công nếu thiếu Chrome hoặc thiếu renderer. Không commit/merge/push cho tới khi user yêu cầu. Mọi thiếu đầu ra phải báo, không lấp bằng config không có consumer hoặc lời hứa scanner.
