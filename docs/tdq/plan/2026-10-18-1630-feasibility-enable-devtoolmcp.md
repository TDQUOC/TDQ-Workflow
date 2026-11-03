# PLAN — Tích Hợp Tùy Chọn Cấu Hình enable-devtoolmcp & Bộ Kỹ Năng Trình Duyệt Vào TDQ Workflow

Ngày: 2026-10-18 · Spec: ../spec/2026-10-18-1630-feasibility-enable-devtoolmcp.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — thực thi trực tiếp từng task, kiểm chứng logic auto-setup và auto-launch Chrome CDP trên máy (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: CHỜ DUYỆT

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Cấu hình Plugin Manifest & Tài liệu Guide
- P2 — Module Quản lý Chrome DevTools MCP & Auto-Launch
- P3 — Tích hợp SessionStart Hook & tdq_setup
- P4 — Bộ 2 Kỹ Năng tdq-browser-test (UI/UX 5 Lớp) & tdq-browser-research
- P5 — Kiểm thử Tự Động & QC Toàn Diện
- Dòng `Chạm:`
- Dòng `Cần:`
- Cụm song song
- Luật file nóng (một file, nhiều task chạm)
- Khuôn khối hợp đồng skill
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước kiểm tra: chạy test cụ thể của task đó; trọn bộ test suite chạy ở phase QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này, loop đến khi pass 100%.
6. Không commit/push cho đến khi user yêu cầu.
7. Tuân thủ 6 mã cấm cơ học (ANTI-1 Fake Red, ANTI-2 Blind Assertion, ANTI-3 Dirty State Git, ANTI-4 Late Tick, ANTI-5 Raw Dump, ANTI-6 Broad Area).

## P1 — Cấu hình Plugin Manifest & Tài liệu Guide
- [x] **T1.1** (e5m) Bổ sung trường `ENABLE_DEVTOOL_MCP` vào `.claude-plugin/plugin.json` — Test: `python3 -c "import json; data=json.load(open('.claude-plugin/plugin.json')); assert 'ENABLE_DEVTOOL_MCP' in data.get('userConfig', {})"`
- [x] **T1.2** (e5m) Sao chép cẩm nang hướng dẫn `CHROME_DEVTOOLS_MCP_GUIDE.md` sang `skills/tdq-setup/references/chrome-devtools-mcp-guide.md` — Test: `python3 -c "import os; assert os.path.exists('skills/tdq-setup/references/chrome-devtools-mcp-guide.md')"`

**Xong P1 khi**: File manifest plugin chứa cấu hình mới và tài liệu guide được lưu trữ an toàn trong repo.

## P2 — Module Quản lý Chrome DevTools MCP & Auto-Launch
- [x] **T2.1** (e15m) Xây dựng module `scripts/tdq_devtool_mcp.py` chứa các hàm cốt lõi: `is_enabled()`, `check_devtool_setup()`, `setup_devtool_mcp()`, `ensure_chrome_running()` — Test: `python3 -m unittest tests/test_devtool_mcp_integration.py`
  - Chạm: `scripts/tdq_devtool_mcp.py` → file mới, chưa node nào phụ thuộc
  - Dùng: `tdq-setup`
  - Để: Cung cấp logic setup và phát hiện trạng thái Chrome DevTools MCP
  - Ra: `scripts/tdq_devtool_mcp.py`
  - Kiểm: `python3 -c "import tdq_devtool_mcp; print(tdq_devtool_mcp.__file__)"`
  - Không dùng cho: Can thiệp mã nguồn server bên ngoài

**Xong P2 khi**: Module `tdq_devtool_mcp.py` hoàn tất, hỗ trợ kiểm tra port 9222 và cấu hình đa nền tảng.

## P3 — Tích hợp SessionStart Hook & tdq_setup
- [x] **T3.1** (e10m) Tích hợp kiểm tra `tdq_devtool_mcp.check_session_start()` vào `hooks/scripts/session_start.py` với cơ chế non-blocking (< 50ms) — Test: `python3 hooks/scripts/session_start.py < tests/fixtures/session_start_payload.json`
  - Chạm: `hooks/scripts/session_start.py` → `session_start.py`
  - Cần: T2.1
- [x] **T3.2** (e10m) Tích hợp hàm kiểm tra bậc cài đặt Chrome DevTools MCP vào `scripts/tdq_setup.py` — Test: `python3 scripts/tdq_setup.py`
  - Chạm: `scripts/tdq_setup.py` → `tdq_setup.py`
  - Cần: T2.1

**Xong P3 khi**: Hook `SessionStart` và lệnh `tdq_setup.py` nhận diện được trạng thái DevTools MCP mà không làm trễ phiên.

## P4 — Bộ 2 Kỹ Năng tdq-browser-test (UI/UX 5 Lớp) & tdq-browser-research
- [x] **T4.1** (e20m) Xây dựng kỹ năng `skills/tdq-browser-test/SKILL.md` chuyên sâu về kiểm thử UI/UX 5 lớp: Lớp 1 Tree DOM a11y, Lớp 2 Viewport Responsive Desktop/Mobile & Screenshot, Lớp 3 Element Interaction (hover, focus, state toggle), Lớp 4 Console & Network Error detection, Lớp 5 CSS cascade styling audit — Test: `python3 scripts/doc_lint.py skills/tdq-browser-test/SKILL.md`
- [x] **T4.2** (e15m) Xây dựng kỹ năng `skills/tdq-browser-research/SKILL.md` chuyên về crawl SPA, deep research, adaptive polling và timeout phòng vệ — Test: `python3 scripts/doc_lint.py skills/tdq-browser-research/SKILL.md`
  - Dùng: `tdq-build`
  - Để: Cung cấp chỉ dẫn chuẩn mực cho agent thực hiện E2E test và research
  - Ra: `skills/tdq-browser-test/SKILL.md`, `skills/tdq-browser-research/SKILL.md`
  - Kiểm: `python3 scripts/doc_lint.py skills/tdq-browser-test/SKILL.md skills/tdq-browser-research/SKILL.md`
  - Không dùng cho: Thay thế các rule code review khác

**Xong P4 khi**: Cả 2 kỹ năng được khởi tạo, vượt qua kiểm tra DocLint và chứa đầy đủ hướng dẫn kiểm thử UI/UX chuyên sâu chống bỏ sót lỗi.

## P5 — Kiểm thử Tự Động & QC Toàn Diện
- [x] **T5.1** (e15m) Soạn thảo test suite `tests/test_devtool_mcp_integration.py` bao phủ đầy đủ các kịch bản: `is_enabled`, `check_setup`, `auto_setup_mock`, `ensure_chrome_running`, kiểm tra 2 skill — Test: `python3 -m unittest tests/test_devtool_mcp_integration.py`
  - Chạm: `tests/test_devtool_mcp_integration.py` → file mới
  - Cần: T1.1, T2.1, T3.1, T4.1, T4.2
- [x] **T5.2** (e10m) Chạy smoke test thực tế gọi CDP endpoint và kiểm tra danh sách page — Test: `python3 -c "import urllib.request; assert 'Chrome' in urllib.request.urlopen('http://127.0.0.1:9222/json/version').read().decode()"`

**Xong P5 khi**: 100% test cases trong test suite đạt PASS và smoke test CDP trả lời thành công.

## Cụm song song
Một cụm tuần tự duy nhất vì các phase phụ thuộc nối tiếp nhau chặt chẽ: P1 (Config/Doc) → P2 (Core Manager) → P3 (Hooks/Setup) → P4 (Skills UI/UX chi tiết) → P5 (Test & QC).

## Luật file nóng (một file, nhiều task chạm)
Không có file nóng bị ghi đè chéo giữa các phase. `scripts/tdq_devtool_mcp.py` là trung tâm được tạo tại P2 và chỉ được import tại P3/P5.

## Definition of Done
- Cờ cấu hình `ENABLE_DEVTOOL_MCP` sẵn sàng trong plugin.json.
- Module `tdq_devtool_mcp.py` hoạt động chính xác, hỗ trợ auto-setup và auto-launch Chrome CDP cổng 9222.
- Kỹ năng `tdq-browser-test` hoàn thiện với chuẩn kiểm thử UI/UX 5 lớp chi tiết từng element, từng vùng layout.
- Kỹ năng `tdq-browser-research` hoàn thiện với cơ chế Adaptive Polling chống sót dữ liệu.
- Bộ test suite `tests/test_devtool_mcp_integration.py` đạt 100% PASS.
