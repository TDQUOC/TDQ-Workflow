# Checkpoint source sau QC3 — 2026-10-31
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Request `2026-10-27-1846-kiem-chung-tang-toc`, nhánh `bugfix/kiem-chung-tang-toc`, lane full, mode subagent, QC ultra, phase implement. Tiến độ **21/26 task**; T5.3 còn `[~]`, D1–D8 PASS, D9–D12 chưa chứng nhận. Người dùng đã yêu cầu tiếp tục và xác nhận tắt nguồn ghi; source được sửa, review và kiểm chứng như dưới đây.

## QC3.1 đã đóng

Phát hiện từ cặp Full thật: hai sample đều runner PASS nhưng metadata parity FAIL ở293case/2790parameter. Pytest9 saferepr ở context và khi dựng lại qua xdist; recorder cũ thêm repr nữa. Diagnostic trong RAM, không sửa raw/verifier, khoanh còn2fixture nondeterministic.

- `scripts/tdq_test_manifest.py`: giữ context canonical trước transport; wrapper tryfirst ghi outcome/reason sau các hook; worker chỉ gắn metadata, controller ghi sidecar. Không đổi verifier, schema fields, guard hoặc package.
- `tests/test_tdq_test_manifest.py`: regression process serial/2worker với quote/backslash/int/list/dict và các outcome, đối chiếu toàn evidence trừ duration.
- `tests/test_bao_cao_gitflow.py`: sorted(set(...)) giữ nguyên15subtest/assertion.
- `tests/test_subagent_start.py`: bốn label ổn định empty/cwd-only/session-only/null-values, giữ nguyên payload thật và assertionrc0.
- Author: producer116test+73subtest PASS; fixtures22test+66subtest PASS; crossseed17vs91 giữ đủ19subtest và metadata khớp. Các lượt RED/GREEN chưa đạt được giữ nguyên trong `QC3.1-author/runs`.
- Reviewer độc lập không có finding4file; tích hợp theo SHA, backup bytes cũ ở `QC3.1-root-backup`; [hash integration](QC3.1-integration.json).
- Root vung-cham7module:235casePASS90.08s, [receipt](runs/QC3.1-parent-radius-62d6e58500b6450fb7205429fac2d097/receipt.json). Hai consumer bổ sung:40test+6subtestPASS144.72s, [receipt](runs/QC3.1-parent-consumers-921c0b511b9643c0a6bde50ed78a5bc8/receipt.json). Mọi guard/cleanup PASS. LSP0diagnostic4file, gitdiffcheck sạch; Ruff chưa cài. Master và graph đã refresh trước Full cuối.

## Bằng chứng trên source cuối

Source SHA-256 của harness: `81c1946345d8495ef32dbb3924de801020c957c5599918b9c3d4317c5f3278ad`.

- **Full fresh PASS3594, skip8, fail/error0;3602case**, baseline3306 đủ, không remap. Wall1117.6745854s, execute1112.4460645s. Child/harness exit0, config/source/dependency guard và cleanup PASS. [Receipt](runs/QC-F1-final-after-QC3-20261031-6add68337dd44ca9b785b1603918f786/receipt.json).
- [D1–D8 semantic PASS](dod-checks-final-QC3.json), [evidence-index v2](evidence-index.json). Skip đều có reason/capability, POSIX limitation giữ rõ.
- **Runtime6/6PASS**, từng scenario dưới120s, verifier khớp nguồn Full. [Runtime](runtime-final.json), [receipt](runs/runtime-final-after-QC3-ed06898fbca3436baf4a965c036e004a/receipt.json).
- [QC sơ bộ độc lập](qc-preliminary-20261031.md): PRELIMINARY/INCOMPLETE, không có codefinding mới được xác nhận. Đây không là D11finalPASS; thiếu benchmark/cache/browser/report.

## Lượt benchmark cuối bị config drift

Đã khớp source identity với Full trước khi bắt đầu đủ3cặp1–2/2–1/1–2. Không có agent/test khác do leader chạy đồng thời.

- Sample1, workers1: **PASS1159.9919125s**, raw integrity không lỗi. Sample2, workers2 đang chạy thì quan sát digest phát hiện `.codex/config.toml` đổi. Chưa đủ cặp để chứng nhận parity hoặc tốc độ trên source cuối.
- File config có LastWriteTime **21:58:38.1385815+07**. Dừng đúng owned child40992,parent8904 sau xác minh command/parent; harness còn sống để seal receipt và cleanup.
- [Receipt FAIL](runs/benchmark-full-final-after-QC3-9e893fa657584476a8a85ee20c8110ae/receipt.json): child/harness-1 do dừng chủ động, config_guard mismatch; **source/dependency không đổi, cleanup complete**. Chỉ `.codex/config.toml` đổi; ledger vẫn ổn định. Không gọi đây là lỗi correctness hoặc timeout.
- [Diagnostic](config-drift-QC3-20261031.json), [partial report lưu riêng](benchmark-full.config-drift-QC3-20261031.json), [sampleJSONL](benchmark-full.config-drift-QC3-20261031.samples.jsonl). Giữ cả các archive trước sửa và lượt cấu hình lỗi; không sửa raw hoặc dùng số này vào median cuối.

## Khoanh vùng nguồn ghi: chưa quy tác giả

Quan sát agent-lsp10984 mở21:58:11, parent24648 thuộc Codex desktop17540, cwdColoring_System; TypeScript server được mở cùng lúc. Có chat **Check request** của Coloring_System đang active. Đã đọc metadata/lịch sử liên quan nhưng không thấy lệnh trực tiếp ghi config. VSCode local history có file config cũ, không có snapshot khớp before của lượt đo. Không có Sysmon/handle utility sẵn dùng. Những dữ liệu này **không đủ chứng minh tiến trình/chat nào đã ghi file**.

Không dừng phiên người dùng, sửa/khóa/hoàn nguyên cấu hình hoặc nới guard. Không gửi tin nhắn sang chat khác. [Dự thảo phối hợp](coordination-message-draft-20261031.md) đang chờ quyền gửi rõ ràng nếu người dùng chọn cách phối hợp liên chat.

## Điều kiện và bước tiếp tục

State đã pause mat-truy-cap. Cần cửa sổ khoảng2giờ không có nguồn ghi cấu hình user-level trong thời gian Full/benchmark; các tác vụ setup/MCP/plugin/model có thể làm thay đổi đầu vào này. Khoảng yên tĩnh ngắn không chứng minh nguồn ghi đã dừng, không chạy lại mù để tìm PASS.

Sau khi điều kiện được đáp ứng: kiểm source và source_identity với Full trước đo. Finish cuối lượt sẽ thay workinglog31; projection hiện chỉ loại ngày mở request27 nên có thể cần Full mới theo hợp đồng, không chỉ xét code hash. Làm mới runtime nếu nguồn đối chiếu đổi. Sau đó đủ6sample Full mới, cache-pairs3cặp mỗi đường (log thật tách fixture), QC độc lập cuối, D9–D12 và report MD/HTML desktop/mobile. Không commit/push khi chưa có yêu cầu.

Đã dùng đủ3vòng QC; nếu QC sau còn lỗi correctness mới, tuân thủ cap và hỏi người dùng thay vì tự mở vòng4. Config drift là điều kiện môi trường, không được hạ thành ngưỡng hiệu năng/fallback giả.
