#!/usr/bin/env python3
"""Harness 50 bài test kiểm toán toàn diện hiệu năng và độ chính xác của Graphify trên dự án Photoboth360."""
import json
import os
import subprocess
import sys
import time

GRAPH_PATH = r"C:\Users\admin\Documents\Photoboth360\graphify-out\graph.json"
REPORT_PATH = r"C:\Users\admin\Documents\Photoboth360\graphify-out\GRAPH_REPORT.md"
TARGET_DIR = r"C:\Users\admin\Documents\Photoboth360"
LOG_FILE = r"C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow\evals\photoboth360_audit_logs.jsonl"
SUMMARY_FILE = r"C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow\evals\photoboth360_audit_summary.md"

def load_graph():
    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def run_cli_cmd(args, timeout=15):
    t0 = time.perf_counter()
    try:
        res = subprocess.run(
            ["graphify"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=TARGET_DIR,
            creationflags=0x08000000 if sys.platform.startswith("win") else 0
        )
        elapsed = (time.perf_counter() - t0) * 1000
        return res.returncode, res.stdout, res.stderr, elapsed
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        return -1, "", str(e), elapsed

def main():
    print(f"Loading graph from {GRAPH_PATH}...")
    t0 = time.perf_counter()
    graph = load_graph()
    load_time = (time.perf_counter() - t0) * 1000
    nodes = graph.get("nodes", [])
    # Graphify uses 'links' in NetworkX JSON format
    edges = graph.get("links", graph.get("edges", []))

    print(f"Graph loaded: {len(nodes)} nodes, {len(edges)} edges in {load_time:.2f}ms")

    tests = []

    def record_test(tid, cat, name, passed, details, latency_ms):
        result = {
            "test_id": tid,
            "category": cat,
            "name": name,
            "status": "PASS" if passed else "FAIL",
            "latency_ms": round(latency_ms, 2),
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        tests.append(result)
        print(f"[{result['status']}] {tid}: {name} ({result['latency_ms']}ms)")

    # -------------------------------------------------------------
    # Nhóm 1 (T01 - T10): Entity Coverage (Kiểm tra Node tồn tại đúng file & location)
    # -------------------------------------------------------------
    def test_entity(tid, label_or_sub, file_sub, desc):
        t_start = time.perf_counter()
        matches = [n for n in nodes if (label_or_sub in (n.get("label") or "")) and (file_sub in (n.get("source_file") or ""))]
        lat = (time.perf_counter() - t_start) * 1000
        passed = len(matches) > 0
        details = f"Found {len(matches)} matching node(s)"
        if matches:
            m = matches[0]
            details += f": id={m.get('id')} label={m.get('label')} file={m.get('source_file')} loc={m.get('source_location')}"
        record_test(tid, "Entity Coverage", desc, passed, details, lat)

    test_entity("T01", "app.js", "nodeserver/app.js", "Node app.js tồn tại trong đồ thị")
    test_entity("T02", "config.js", "nodeserver/config.js", "Node config.js tồn tại trong đồ thị")
    test_entity("T03", "data.js", "nodeserver/app/controller/data.js", "Controller data.js tồn tại")
    test_entity("T04", "file.js", "nodeserver/app/controller/file.js", "Controller file.js tồn tại")
    test_entity("T05", "data.js", "nodeserver/app/models/data.js", "Model data.js tồn tại")
    test_entity("T06", "file.js", "nodeserver/app/models/file.js", "Model file.js tồn tại")
    test_entity("T07", "socket.js", "nodeserver/app/socket/socket.js", "Socket module socket.js tồn tại")
    test_entity("T08", "ffmpeg.js", "nodeserver/app/utils/ffmpeg.js", "Utils ffmpeg.js tồn tại")
    test_entity("T09", "AsyncTestHubSample", "AsyncTestHubSample.cs", "C# Class AsyncTestHubSample tồn tại")
    test_entity("T10", "HTTPProtocolFactory", "HTTPProtocolFactory.cs", "C# Class HTTPProtocolFactory tồn tại")

    # -------------------------------------------------------------
    # Nhóm 2 (T11 - T20): Dependency & Imports Accuracy (Kiểm tra Edge quan hệ phụ thuộc)
    # -------------------------------------------------------------
    def test_edge(tid, src_sub, tgt_sub, rel_type, desc):
        t_start = time.perf_counter()
        matches = []
        for e in edges:
            if rel_type and e.get("relation") != rel_type:
                continue
            s = e.get("source", "")
            t = e.get("target", "")
            sf = e.get("source_file", "")
            if (src_sub.lower() in s.lower() or src_sub.lower() in sf.lower()) and (tgt_sub.lower() in t.lower()):
                matches.append(e)
        lat = (time.perf_counter() - t_start) * 1000
        passed = len(matches) > 0
        details = f"Found {len(matches)} edge(s) matching ({src_sub} --{rel_type or '*'}--> {tgt_sub})"
        if matches:
            m = matches[0]
            details += f": {m.get('source')} --{m.get('relation')}--> {m.get('target')} at {m.get('source_location')}"
        record_test(tid, "Dependency Accuracy", desc, passed, details, lat)

    test_edge("T11", "app.js", "express", None, "app.js phụ thuộc express")
    test_edge("T12", "app.js", "mongoose", None, "app.js phụ thuộc mongoose")
    test_edge("T13", "app.js", "cors", None, "app.js kết nối cors middleware")
    test_edge("T14", "app.js", "path", None, "app.js phụ thuộc path module")
    test_edge("T15", "app.js", "config", None, "app.js phụ thuộc config module")
    test_edge("T16", "routes.js", "controller", None, "routes kết nối controller")
    test_edge("T17", "data.js", "ffmpeg", None, "controller data.js kết nối utils ffmpeg")
    test_edge("T18", "AsyncTestHubSample", "HubConnection", None, "AsyncTestHubSample phụ thuộc HubConnection")
    test_edge("T19", "HTTPProtocolFactory", "HTTP", None, "HTTPProtocolFactory phụ thuộc HTTP protocol")
    test_edge("T20", "ffmpeg.js", "fluent_ffmpeg", None, "ffmpeg module import fluent-ffmpeg")

    # -------------------------------------------------------------
    # Nhóm 3 (T21 - T30): Method & Structural Call Flow
    # -------------------------------------------------------------
    def test_call_or_member(tid, owner_sub, target_sub, rel_types, desc):
        t_start = time.perf_counter()
        matches = []
        for e in edges:
            rel = e.get("relation", "")
            if rel_types and rel not in rel_types:
                continue
            s = e.get("source", "")
            t = e.get("target", "")
            sf = e.get("source_file", "")
            if (owner_sub.lower() in s.lower() or owner_sub.lower() in sf.lower()) and (target_sub.lower() in t.lower()):
                matches.append(e)
        lat = (time.perf_counter() - t_start) * 1000
        passed = len(matches) > 0
        details = f"Found {len(matches)} structural call/member edge(s)"
        if matches:
            details += f": {matches[0].get('source')} --{matches[0].get('relation')}--> {matches[0].get('target')}"
        record_test(tid, "Structural & Call Flow", desc, passed, details, lat)

    test_call_or_member("T21", "app.js", "connectMongoDB", ("defines", "contains", "calls"), "app.js định nghĩa hàm connectMongoDB")
    test_call_or_member("T22", "app.js", "startServer", ("defines", "contains", "calls"), "app.js định nghĩa hàm startServer")
    test_call_or_member("T23", "data.js", "all", ("defines", "contains", "method", "references"), "controller data.js định nghĩa all")
    test_call_or_member("T24", "file.js", "upload", ("defines", "contains", "method", "references"), "controller file.js xử lý upload")
    test_call_or_member("T25", "ffmpeg.js", "thumbnail", ("defines", "contains", "method", "references"), "ffmpeg utils định nghĩa hàm thumbnail")
    test_call_or_member("T26", "AsyncTestHubSample", "Start", ("method", "defines", "contains"), "AsyncTestHubSample có method Start")
    test_call_or_member("T27", "AsyncTestHubSample", "OnConnectButton", ("method", "defines", "contains"), "AsyncTestHubSample có OnConnectButton")
    test_call_or_member("T28", "HTTPProtocolFactory", "GetProtocolFromUri", ("method", "defines", "contains"), "HTTPProtocolFactory có GetProtocolFromUri")
    test_call_or_member("T29", "file.js", "delete", ("defines", "contains", "method", "references"), "controller file.js định nghĩa delete")
    test_call_or_member("T30", "data.js", "upload", ("defines", "contains", "method", "references"), "controller data.js định nghĩa upload")

    # -------------------------------------------------------------
    # Nhóm 4 (T31 - T40): Semantic Query Performance & Precision
    # -------------------------------------------------------------
    def test_query(tid, query_str, expected_kw, desc):
        rc, out, err, lat = run_cli_cmd(["query", query_str, "--budget", "1500", "--graph", GRAPH_PATH], timeout=15)
        passed = (rc == 0) and any(kw.lower() in out.lower() for kw in expected_kw)
        details = f"Query rc={rc}, output_len={len(out)}, expected={expected_kw}"
        if not passed:
            details += f" | err={err[:100]}"
        record_test(tid, "Semantic Query", desc, passed, details, lat)

    test_query("T31", "express server startup and port listening", ["app.js", "listen", "express"], "Tìm luồng khởi động server express")
    test_query("T32", "realtime websocket socket.io communication", ["socket", "io", "connection"], "Tìm luồng kết nối websocket socket.io")
    test_query("T33", "database configuration or settings", ["config", "db", "port"], "Tìm cấu hình hệ thống / database")
    test_query("T34", "file upload and media storage controller", ["file", "upload", "multer"], "Tìm chức năng upload tệp tin")
    test_query("T35", "video conversion or ffmpeg rendering", ["ffmpeg", "exec", "video"], "Tìm xử lý video ffmpeg")
    test_query("T36", "signalr hub connection and messagepack protocol", ["signalr", "hub", "messagepack"], "Tìm kết nối SignalR Hub")
    test_query("T37", "http request dispatching and routes", ["routes", "router", "express"], "Tìm định tuyến routes")
    test_query("T38", "cryptography and security certificate validation", ["certificate", "crypto", "x509", "tls"], "Tìm module mã hóa và chứng chỉ")
    test_query("T39", "tls client authentication protocol", ["tls", "client", "handshake"], "Tìm giao thức xác thực TLS")
    test_query("T40", "elliptic curve key generation", ["curve", "ec", "key"], "Tìm thuật toán Elliptic Curve")

    # -------------------------------------------------------------
    # Nhóm 5 (T41 - T50): Architectural Map & Blast-Radius
    # -------------------------------------------------------------
    def test_affected(tid, node_name, expected_aff, desc):
        rc, out, err, lat = run_cli_cmd(["affected", node_name, "--depth", "2", "--graph", GRAPH_PATH], timeout=15)
        passed = (rc == 0) and any(exp.lower() in out.lower() for kw in expected_aff for exp in [kw])
        details = f"Affected rc={rc}, expected {expected_aff} in output: {passed}"
        if not passed:
            details += f" | err={err[:100]}"
        record_test(tid, "Architectural Impact", desc, passed, details, lat)

    test_affected("T41", "nodeserver_config", ["app.js", "routes", "socket", "controller", "ffmpeg"], "Vết lan truyền khi đổi nodeserver config")
    test_affected("T42", "nodeserver_app_models_data", ["controller", "data", "routes"], "Vết lan truyền khi đổi data model")
    test_affected("T43", "nodeserver_app_models_file", ["controller", "file", "upload"], "Vết lan truyền khi đổi file model")
    test_affected("T44", "nodeserver_app_utils_ffmpeg", ["file", "video", "controller"], "Vết lan truyền khi đổi ffmpeg utils")

    # God nodes CLI
    rc_gn, out_gn, _, lat_gn = run_cli_cmd(["god-nodes", "--top", "10", "--graph", GRAPH_PATH], timeout=15)
    passed_gn = (rc_gn == 0) and ("God nodes" in out_gn)
    record_test("T45", "Architectural Impact", "Truy vấn danh sách God nodes kiến trúc", passed_gn, f"God nodes identified in {lat_gn:.1f}ms", lat_gn)

    # Community verification from REPORT
    def test_community(tid, comm_name, desc):
        t_start = time.perf_counter()
        passed = False
        details = ""
        if os.path.exists(REPORT_PATH):
            with open(REPORT_PATH, "r", encoding="utf-8") as f:
                content = f.read()
                passed = comm_name.lower() in content.lower()
                details = f"Found '{comm_name}' in GRAPH_REPORT.md: {passed}"
        lat = (time.perf_counter() - t_start) * 1000
        record_test(tid, "Architectural Impact", desc, passed, details, lat)

    test_community("T46", "Cryptography", "Xác thực cụm kiến trúc Cryptography")
    test_community("T47", "TLS", "Xác thực cụm kiến trúc TLS Protocol")
    test_community("T48", "BestHTTP", "Xác thực cụm kiến trúc BestHTTP Core")
    test_community("T49", "Certificate", "Xác thực cụm kiến trúc Certificate Management")

    # Explain
    rc_exp, out_exp, _, lat_exp = run_cli_cmd(["explain", "nodeserver_app_js", "--graph", GRAPH_PATH], timeout=15)
    passed_exp = (rc_exp == 0) and len(out_exp) > 30
    record_test("T50", "Architectural Impact", "Giải thích ngữ cảnh kiến trúc nút app.js (explain)", passed_exp, f"Explain output length={len(out_exp)} chars", lat_exp)

    # -------------------------------------------------------------
    # Xuất log chi tiết ra JSONL
    # -------------------------------------------------------------
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        for t in tests:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    # Thống kê tổng hợp
    total_tests = len(tests)
    passed_count = sum(1 for t in tests if t["status"] == "PASS")
    failed_count = total_tests - passed_count
    accuracy = (passed_count / total_tests) * 100
    avg_latency = sum(t["latency_ms"] for t in tests) / total_tests

    cat_stats = {}
    for t in tests:
        c = t["category"]
        if c not in cat_stats:
            cat_stats[c] = {"total": 0, "passed": 0, "latencies": []}
        cat_stats[c]["total"] += 1
        if t["status"] == "PASS":
            cat_stats[c]["passed"] += 1
        cat_stats[c]["latencies"].append(t["latency_ms"])

    summary_md = f"""# Báo Cáo Kiểm Toán & Đánh Giá Graphify Full Trên Dự Án Photoboth360

- **Thời gian thực hiện**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Dự án mục tiêu**: `{TARGET_DIR}`
- **Quy mô đồ thị**: {len(nodes):,} nodes · {len(edges):,} edges · 535 communities
- **Tổng số bài test**: {total_tests} bài
- **Kết quả**: {passed_count}/{total_tests} PASS ({accuracy:.1f}%) · {failed_count} FAIL
- **Độ trễ trung bình**: {avg_latency:.2f} ms / test

## Thống Kê Chi Tiết Theo Phân Nhóm

| Nhóm Kiểm Thử | Số Bài Test | Đạt (PASS) | Tỷ Lệ Đạt (%) | Độ Trễ TB (ms) |
|---|---|---|---|---|
"""
    for c, s in cat_stats.items():
        rate = (s["passed"] / s["total"]) * 100
        avg_l = sum(s["latencies"]) / len(s["latencies"])
        summary_md += f"| **{c}** | {s['total']} | {s['passed']} | {rate:.1f}% | {avg_l:.2f} ms |\n"

    summary_md += "\n## Chi Tiết 50 Bài Test\n\n"
    for t in tests:
        summary_md += f"- **{t['test_id']}** [{t['status']}] `{t['category']}` — {t['name']} ({t['latency_ms']} ms)\n  - *Chi tiết*: {t['details']}\n"

    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write(summary_md)

    print("\n" + "="*60)
    print(f"AUDIT COMPLETE: {passed_count}/{total_tests} PASS ({accuracy:.1f}%)")
    print(f"Detailed logs: {LOG_FILE}")
    print(f"Summary report: {SUMMARY_FILE}")
    print("="*60)

if __name__ == "__main__":
    main()
