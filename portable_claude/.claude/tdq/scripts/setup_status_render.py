#!/usr/bin/env python3
"""setup_status_render.py — turn the collected setup data into one self-contained HTML page.

A pure function: dict in, HTML string out. Nothing here touches the machine, which is the
whole point — the rendering can be tested on a bare checkout with no agent-lsp, lumen, ollama
or graphify installed, while `setup_status.py` owns everything that must run for real.

Self-contained means literally that: the CSS is inline, there is no script tag, no font and
no image loaded from anywhere. The page has to be readable with the network unplugged,
because "is my setup working" is exactly the question asked when things are broken.

Log service: one ISO-timestamped line on **stderr**, on by default, muted with `TDQ_LOG=0`.
"""

import datetime
import html
import os
import sys

# Every block the page shows, in reading order: (anchor id, heading).
# The anchor is what `grep data-khoi=` counts, so the list is the single place a block is born.
THIEU = "không đọc được"

# Anyone who reruns `agent-lsp doctor` by hand sees these lines and reads them as failures.
# Measured: three consecutive runs named a different set of servers each time while the
# `Summary` line and the exit code did not move. Say so on the page, once.
GHI_CHU_DOCTOR = ("Dò sống bằng <code>agent-lsp doctor</code>. Các dòng "
                  "<code>[error] ... exited with error after 0s</code> trên stderr là nhiễu "
                  "lúc đóng tiến trình — mỗi lần chạy một tập khác nhau — nên "
                  "<b>không tính là chết</b>; cột trên lấy theo <code>Status:</code> của "
                  "từng server và đối chiếu với dòng <code>Summary:</code>.")

CSS = """
:root { --nen: #fbfbf9; --chu: #1d1d1b; --vien: #dcdcd4; --mo: #6b6b63;
        --dat: #1a7f4b; --thieu: #b3261e; --canh-bao: #a6690a; --o-nen: #ffffff; }
* { box-sizing: border-box; }
body { margin: 0; padding: 24px; background: var(--nen); color: var(--chu);
       font: 14px/1.55 -apple-system, "Segoe UI", system-ui, sans-serif; }
main { max-width: 1100px; margin: 0 auto; }
h1 { font-size: 22px; margin: 0 0 4px; }
h2 { font-size: 16px; margin: 32px 0 10px; padding-bottom: 6px;
     border-bottom: 1px solid var(--vien); }
h3 { font-size: 13px; margin: 20px 0 6px; color: var(--mo);
     text-transform: uppercase; letter-spacing: .04em; }
.meta { color: var(--mo); font-size: 12px; margin-bottom: 8px; }
.bao { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; background: var(--o-nen); }
th, td { border: 1px solid var(--vien); padding: 6px 9px; text-align: left;
         vertical-align: top; font-size: 13px; }
th { background: #f2f2ec; font-weight: 600; }
td.so { text-align: right; white-space: nowrap; }
code, .ma { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; }
.dat { color: var(--dat); font-weight: 600; }
.thieu { color: var(--thieu); font-weight: 600; }
.canh-bao { color: var(--canh-bao); font-weight: 600; }
.trong { color: var(--mo); font-style: italic; }
.ghi-chu { color: var(--mo); font-size: 12px; margin: 8px 0 0; }
.loi { color: var(--thieu); font-size: 12px; margin: 8px 0 0; }
@media (prefers-color-scheme: dark) {
  :root { --nen: #17171a; --chu: #ecece6; --vien: #37373d; --mo: #9a9a94;
          --o-nen: #1e1e22; --dat: #4cc38a; --thieu: #ff6b62; --canh-bao: #e0a33a; }
  th { background: #26262b; }
}
"""


def _log(message):
    """One ISO-timestamped line on stderr. Muted with TDQ_LOG=0 — the tdq_state contract."""
    if os.environ.get("TDQ_LOG", "1") != "0":
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] setup_status_render: {message}", file=sys.stderr)


def _e(gia_tri):
    """Escape anything coming from an external command before it becomes markup."""
    return html.escape("" if gia_tri is None else str(gia_tri))


def _dict(gia_tri):
    """A source that failed can hand back anything; only a real dict is treated as data."""
    return gia_tri if isinstance(gia_tri, dict) else {}


def _danh_sach(gia_tri):
    """Same fence for the row lists: a scalar is no data, not a one-row table."""
    return gia_tri if isinstance(gia_tri, list) else []


def _trong(ly_do=""):
    return f'<p class="trong">{THIEU}{" — " + _e(ly_do) if ly_do else ""}</p>'


def _bang(cot, hang):
    """Render one table, or the "không đọc được" note when there is no row to show."""
    if not hang:
        return _trong()
    dau = "".join(f"<th>{_e(c)}</th>" for c in cot)
    than = []
    for dong in hang:
        o = "".join(f"<td>{c}</td>" for c in dong)
        than.append(f"<tr>{o}</tr>")
    return ('<div class="bao"><table><thead><tr>' + dau + "</tr></thead><tbody>"
            + "".join(than) + "</tbody></table></div>")


def _nhan_bac(nhan):
    lop = {"ĐẠT": "dat", "CẢNH BÁO": "canh-bao"}.get(nhan, "thieu")
    return f'<span class="{lop}">{_e(nhan)}</span>'


# ------------------------------------------------------------------ block 1

def _khoi_workflow(workflow):
    workflow = _dict(workflow)
    phan = []

    phan.append("<h3>Thang 7 bậc của agent-lsp</h3>")
    phan.append(_bang(["Bậc", "Tên", "Kết quả", "Chi tiết"],
                      [[f'<span class="so">{_e(b.get("so"))}</span>', _e(b.get("ten")),
                        _nhan_bac(b.get("nhan")), _e(b.get("chi_tiet")) or "—"]
                       for b in workflow.get("bac") or []]))

    phan.append("<h3>Skill có trên đĩa</h3>")
    phan.append(_bang(["Skill", "Nguồn", "Mô tả"],
                      [[f'<code>{_e(s.get("ten"))}</code>', _e(s.get("nguon")),
                        _e(s.get("mo_ta"))]
                       for s in workflow.get("skill") or []]))
    phan.append(f'<p class="ghi-chu">{_e(workflow.get("ghi_chu_builtin"))}</p>')

    phan.append("<h3>Hook: thời gian mỗi lượt (median)</h3>")
    phan.append(_bang(["Hook", "Tình huống", "Median", "Nhanh nhất", "Chậm nhất"],
                      [[f'<code>{_e(o)}</code>' if i == 0 else _e(o)
                        for i, o in enumerate(dong)]
                       for dong in workflow.get("do_hook") or []]))

    phan.append("<h3>Bề mặt tài liệu nạp vào ngữ cảnh</h3>")
    hang_hook = workflow.get("hook") or []
    phan.append(_bang(["File", "Tầng nạp", "Ký tự", "Token ước tính", "Tần suất"],
                      [[_e(o) for o in dong] for dong in hang_hook])
                if hang_hook else _trong())

    phan.append("<h3>State của request đang chạy</h3>")
    state = workflow.get("state") or {}
    quan_tam = ("active_request", "lane", "phase", "loai_request", "nhanh_request",
                "spec_approved", "plan_approved", "implement_mode")
    phan.append(_bang(["Khoá", "Giá trị"],
                      [[f'<code>{_e(k)}</code>', _e(state.get(k))]
                       for k in quan_tam if k in state]))

    for nguon, loi in (workflow.get("loi") or {}).items():
        phan.append(f'<p class="loi">Nguồn <code>{_e(nguon)}</code> lỗi: {_e(loi)}</p>')
    return "".join(phan)


# ------------------------------------------------------------------ block 2

def _khoi_dependency(dependency):
    dependency = _danh_sach(dependency)
    hang = []
    for muc in dependency or []:
        trang_thai = ('<span class="dat">đã cài</span>' if muc.get("co")
                      else '<span class="thieu">chưa cài</span>')
        # A missing tool is worth a command, not a restatement: the "chưa cài" column already
        # said it is absent, so the note carries the install hint instead.
        ghi_chu = (_e(muc.get("goi_y")) if not muc.get("co")
                   else _e(muc.get("chi_tiet"))) or "—"
        hang.append([f'<code>{_e(muc.get("ten"))}</code>', trang_thai,
                     _e(muc.get("ban")), f'<code>{_e(muc.get("duong_dan")) or "—"}</code>',
                     ghi_chu])
    return _bang(["Công cụ", "Có mặt", "Phiên bản", "Đường dẫn", "Ghi chú / lệnh cài"], hang)


# ------------------------------------------------------------------ block 3

def _khoi_chi_tiet(chi_tiet):
    chi_tiet = _dict(chi_tiet)
    lumen = _dict(chi_tiet.get("lumen"))
    lsp = _dict(chi_tiet.get("lsp"))
    phan = ["<h3>lumen — model embedding đang dùng</h3>"]
    hang = []
    if lumen.get("model"):
        hang.append(["Model", f'<code>{_e(lumen["model"])}</code>'])
    if lumen.get("config"):
        hang.append(["File cấu hình", f'<code>{_e(lumen["config"])}</code>'])
    for i, host in enumerate(lumen.get("endpoint") or []):
        nhan = "Endpoint chính" if i == 0 else f"Endpoint dự phòng {i}"
        hang.append([nhan, f'<code>{_e(host)}</code>'])
    phan.append(_bang(["Mục", "Giá trị"], hang))
    if lumen.get("chi_tiet"):
        phan.append(f'<p class="loi">{_e(lumen["chi_tiet"])}</p>')

    khai, song = lsp.get("so_khai_bao") or 0, lsp.get("so_song") or 0
    phan.append("<h3>agent-lsp — khai báo so với thực nhận</h3>")
    if khai:
        lop = "dat" if song == khai else "thieu"
        phan.append(f'<p>Khai báo <b>{khai}</b> language server · '
                    f'khởi động được <span class="{lop}">{song}</span>.</p>')
        chet = lsp.get("chet") or []
        if chet:
            ten = ", ".join(f'<code>{_e(c.get("lang"))}</code> ({_e(c.get("binary"))})'
                            for c in chet)
            phan.append(f'<p class="loi">Không nhận được: {ten}</p>')
    phan.append(_bang(["Ngôn ngữ", "Binary khai báo", "Thực nhận"],
                      [[f'<code>{_e(m.get("lang"))}</code>',
                        f'<code>{_e(m.get("binary"))}</code>',
                        (f'<span class="dat">ok</span>' if m.get("trang_thai") == "ok"
                         else f'<span class="thieu">{_e(m.get("trang_thai"))}</span>')]
                       for m in lsp.get("may") or []]))
    if khai:
        phan.append(f'<p class="ghi-chu">{GHI_CHU_DOCTOR}</p>')
    if lsp.get("chi_tiet"):
        phan.append(f'<p class="loi">{_e(lsp["chi_tiet"])}</p>')
    return "".join(phan)


# ------------------------------------------------------------------ block 4

def _khoi_mcp(mcp):
    mcp = _dict(mcp)
    hang = []
    for may in _danh_sach(mcp.get("server")):
        trang_thai = ('<span class="dat">' if may.get("noi_duoc") else '<span class="thieu">')
        hang.append([_e(may.get("ten")), f'<code>{_e(may.get("dich"))}</code>',
                     trang_thai + _e(may.get("trang_thai")) + "</span>"])
    phan = [_bang(["Server", "Địa chỉ / lệnh (đã che khoá)", "Trạng thái"], hang)]
    if mcp.get("chi_tiet"):
        phan.append(f'<p class="loi">{_e(mcp["chi_tiet"])}</p>')
    return "".join(phan)


# ------------------------------------------------------------------- the page

# One row per block: HTML id, heading, the key it reads out of the collected dict, and the
# function that builds its body. Adding a block to the page is adding a row here — `render()`
# below never learns their names.
KHOI = (
    ("workflow", "1 · TDQ-Workflow: skill, hook, state", "workflow", _khoi_workflow),
    ("dependency", "2 · Dependency và thư viện liên quan", "dependency", _khoi_dependency),
    ("chi-tiet", "3 · Chi tiết: lumen và agent-lsp", "chi_tiet", _khoi_chi_tiet),
    ("mcp", "4 · MCP mà Claude Code thực sự nhận", "mcp", _khoi_mcp),
)


def render(du_lieu):
    """Build the whole page. Pure: no file is read, no command is run, nothing is cached."""
    goc = du_lieu if isinstance(du_lieu, dict) else {}
    meta = goc.get("meta")
    meta = meta if isinstance(meta, dict) else {}
    # One section per line on purpose: the page is meant to be greppable from a terminal as
    # well as readable in a browser, and `grep -c data-khoi=` is one of its DoD checks.
    muc = "\n".join(
        f'<section data-khoi="{ma}"><h2>{_e(tieu_de)}</h2>\n{dung(goc.get(khoa))}</section>'
        for ma, tieu_de, khoa, dung in KHOI)
    _log(f"rendered {len(KHOI)} block(s)")
    return (
        "<!doctype html>\n"
        '<html lang="vi"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>Trạng thái setup TDQ-Workflow</title>"
        f"<style>{CSS}</style></head>\n<body><main>\n"
        "<h1>Trạng thái setup TDQ-Workflow</h1>\n"
        f'<p class="meta">Sinh lúc {_e(meta.get("sinh_luc"))} · dự án '
        f'<code>{_e(meta.get("project"))}</code> · Python {_e(meta.get("python"))}</p>\n'
        f"{muc}\n</main></body></html>\n")
