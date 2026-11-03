# Giảm timeout và thời gian chờ agent-lsp {#spec-ba}

**Cắt giảm thời gian chờ tối đa khi gọi MCP `lsp` từ 1.800 giây xuống 90 giây, kiểm soát phạm vi `blast_radius`, ngắt mạch tự động khi workspace lỗi và đo lường đầy đủ p50/p95 cùng độ phủ caller.**

- Luồng 1 (Chính sách & Hướng dẫn): Đồng bộ `uu-tien-tim-kiem.md` và `KHOI_HUONG_DAN` trong `tdq_setup.py`, ghi đè chỉ thị gọi `blast_radius` vô điều kiện từ MCP server `agent-lsp`.
- Luồng 2 (Giới hạn chờ 90 giây): Thiết lập `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT = "90000"` trong `~/.claude/settings.json` qua `tdq_setup.py`.
- Luồng 3 (Gate & Circuit Breaker): Mở rộng `lsp_gate.py` kiểm soát `blast_radius` (≤ 3 tệp, `scope="exported"`, `include_transitive=false`) và ngắt mạch khi workspace vừa timeout/lỗi.
- Luồng 4 (Telemetry & Caller Oracle): Ghi nhận `duration_ms`, `outcome` (`ok`, `empty`, `error`, `timeout`) tại `search_observe.py` (`PostToolUse` & `PostToolUseFailure`) và tổng hợp p50/p95, độ phủ caller trong `search_rules.py` & `search_replay.py`.

@answer scope="Thiết kế v1.0 · chờ duyệt · Mức QC ultra"
@meta locale=en style=editorial

## Luồng kiểm soát và quan sát 4 lớp {#flow}

@workflow id=lsp-timeout-flow title="Kiểm soát vòng đời truy vấn LSP và ngắt mạch tự động"
| setup | Setup 90s Idle | backend |
| gate | LSP Gate & Breaker | security |
| observe | Search Observe | backend |
| replay | Replay & Oracle | security |
| setup > gate | 90s cap |
| gate > observe | allow ≤3 files |
| observe > replay | duration & outcome | emphasis |

| Đầu ra | Thành phần chính | Tệp đích |
| --- | --- | --- |
| O1: Chính sách 3 tầng | Trung hòa chỉ thị upstream `blast_radius` | `uu-tien-tim-kiem.md`, `uu-tien-tim-kiem-chi-tiet.md` |
| O2: Trần chờ 90 giây | `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT = "90000"` | `scripts/tdq_setup.py` |
| O3: Gate & Mạch ngắt | Kiểm tra ≤ 3 tệp, `exported`, circuit breaker | `hooks/hooks.json`, `hooks/scripts/lsp_gate.py` |
| O4 & O5: Telemetry & Oracle | Đo `duration_ms`, `outcome`, p50/p95, caller coverage | `hooks/scripts/search_observe.py`, `scripts/search_rules.py`, `scripts/search_replay.py` |
