#!/usr/bin/env python3
"""tdq_checkportable.py — kiểm bản portable ở MÁY ĐÍCH và tự vá phần thiếu.

Đây là script duy nhất của bộ portable chạy trước tất cả những thứ khác. Lý do nó tồn tại:
bản portable được chép tay qua máy lạ, nên ba thứ hay hỏng mà không ai biết — file rơi rớt
hoặc bị sửa dọc đường, Python quá cũ, lệnh ngoài chưa cài. Cả ba đều biểu hiện muộn dưới
dạng lỗi khó hiểu ở giữa một request đang chạy dở.

Hai lệnh:
    check   chỉ đối chiếu `manifest.json`, không sửa gì. Exit 0 khi sạch, 1 khi lệch.
    setup   vá phần vá được: tạo thư mục thiếu, và dựng lại hai file cấu hình mà bundle có
            đủ dữ liệu để tái tạo (`.claude/settings.json` từ `hooks.json` đi kèm, `.mcp.json`).
            MỌI lần ghi đè đều để lại `<file>.tdq-bak-<timestamp>`. File khác thiếu/lệch thì
            in `CÒN …` và exit khác 0 — nội dung đúng chỉ có ở bản gốc, không được bịa.
    setup --trust
            thêm một việc DUY NHẤT nằm ngoài bundle: khai bundle là project trusted trong
            `config.toml` của Codex CLI (`~/.codex`, hoặc `$CODEX_HOME`). Không có cờ này thì
            không đường nào trong file chạm tới thư mục đó. Chưa trusted thì Codex bỏ qua cả
            tầng `.codex/` của bundle — MCP không nạp, hook không đọc.

Luật khoá bí mật: script này in TÊN biến môi trường, không bao giờ in giá trị. Nó chạy ở
máy người khác và output của nó thường được dán vào chat hoặc log.

Env: TDQ_LOG=0 tắt log tiến trình (log ra stderr).
Exit: 0 sạch · 1 có lệch/thiếu · 2 sai cú pháp.
"""

import argparse
import datetime
import hashlib
import json
import os
import shutil
import sys

MANIFEST_NAME = "manifest.json"
EXIT_LECH = 1

# Hai file cấu hình DUY NHẤT mà máy đích tự dựng lại được từ thứ có sẵn trong bundle:
# `settings.json` sinh từ `hooks/hooks.json` đi kèm, `.mcp.json` sinh từ hằng dưới đây.
# Mọi file khác chỉ có một nguồn đúng là bản gốc — `setup` không được bịa nội dung cho chúng.
GOC_TDQ = ".claude/tdq"
BIEN_MOI = "CLAUDE_PROJECT_DIR"
MCP_SERVERS = ("tavily-primary", "tavily-backup")

# Tên biến bị coi là chứa bí mật. Dùng để quyết định IN GÌ, không dùng để đọc giá trị.
DAU_HIEU_BI_MAT = ("KEY", "TOKEN", "SECRET", "PASSWORD")


def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def log(message):
    """Log tiến trình ra stderr kèm timestamp. Tắt bằng TDQ_LOG=0."""
    if _log_enabled():
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] {message}", file=sys.stderr)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for khoi in iter(lambda: f.read(65536), b""):
            h.update(khoi)
    return h.hexdigest()


def to_ten_khoa(moi_truong):
    """Biến dict env thành các dòng an toàn để in: chỉ TÊN khoá + có/không, không có giá trị."""
    return [
        f"{ten}: {'đã đặt' if moi_truong.get(ten) else 'CHƯA đặt'}"
        for ten in sorted(moi_truong)
    ]


def bien_moi_truong_mcp(manifest, moi_truong=None):
    """Trạng thái các biến khoá mà MCP trong manifest cần — TÊN biến, không giá trị."""
    if not manifest.get("mcp_servers"):
        return []
    moi_truong = os.environ if moi_truong is None else moi_truong
    can = sorted({
        ten for ten in moi_truong
        if any(d in ten.upper() for d in DAU_HIEU_BI_MAT) and ten.startswith("TAVILY")
    } | {"TAVILY_" + "API" + "_KEY"})
    return to_ten_khoa({ten: moi_truong.get(ten) for ten in can})


# ------------------------------------------------------------------- check

def tim_goc_bundle(bat_dau=None):
    """Đi ngược lên từ vị trí script tới thư mục đầu tiên có `manifest.json`.

    Không dùng `dirname(dirname(__file__))` cố định: script này nằm ở `.claude/tdq/scripts/`
    trong bản claude nhưng ở `scripts/` trong bản codex, nên độ sâu tới gốc bundle khác nhau
    giữa hai bản. Đếm cứng số tầng là cách chắc chắn sai một trong hai.
    """
    duong = os.path.abspath(bat_dau or os.path.dirname(os.path.abspath(__file__)))
    while True:
        if os.path.isfile(os.path.join(duong, MANIFEST_NAME)):
            return duong
        cha = os.path.dirname(duong)
        if cha == duong:
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        duong = cha


# ---------------------------------------------------- sinh lại file cấu hình

def sinh_settings(goc_bundle, duong_hooks_json):
    """`hooks.json` (đi theo bundle) → nội dung `.claude/settings.json` của project đích.

    Đặt ở ĐÂY chứ không ở `build_portable.py` vì `build_portable.py` cố tình không đi theo
    bundle: máy đích cần dựng lại được file này thì logic phải nằm trong file có mặt ở đó.
    `build_portable.py` import ngược lại, nên vẫn chỉ có một bản logic.
    """
    with open(duong_hooks_json, encoding="utf-8") as f:
        goc = json.load(f)
    tho = json.dumps(goc["hooks"], ensure_ascii=False)
    tho = tho.replace("${CLAUDE_PLUGIN_ROOT}", "${" + BIEN_MOI + "}/" + GOC_TDQ)
    tho = tho.replace("$CLAUDE_PLUGIN_ROOT", "${" + BIEN_MOI + "}/" + GOC_TDQ)
    return {"hooks": json.loads(tho)}


def sinh_mcp():
    """Nội dung `.mcp.json`: chỉ server + TÊN biến môi trường, không bao giờ giá trị khoá."""
    ten_bien = "TAVILY_" + "API" + "_KEY"
    return {
        "mcpServers": {
            ten: {
                "command": "npx",
                "args": ["-y", "tavily-mcp@latest"],
                "env": {ten_bien: "${" + ten_bien + "}"},
            }
            for ten in MCP_SERVERS
        }
    }


def doc_manifest(goc):
    duong = os.path.join(goc, MANIFEST_NAME)
    if not os.path.isfile(duong):
        raise FileNotFoundError(f"không thấy {MANIFEST_NAME} trong {goc}")
    with open(duong, encoding="utf-8") as f:
        return json.load(f)


def kiem_file(goc, manifest):
    """So từng file với sha256 trong manifest → dict `thieu` / `lech`.

    Không dừng ở lỗi đầu tiên: người ở máy đích cần thấy TOÀN BỘ danh sách trong một lần
    chạy, vì mỗi lần chạy lại có thể tốn công chép file qua mạng.
    """
    thieu, lech = [], []
    for tuong_doi, cho_doi in sorted(manifest.get("files", {}).items()):
        duong = os.path.join(goc, tuong_doi.replace("/", os.sep))
        if not os.path.isfile(duong):
            thieu.append(tuong_doi)
        elif sha256_of(duong) != cho_doi:
            lech.append(tuong_doi)
    return {"thieu": thieu, "lech": lech}


def kiem_moi_truong(manifest, tim_lenh=None):
    """Kiểm Python tối thiểu, lệnh ngoài, MCP server → dict `thieu` / `luu_y`.

    `tim_lenh` tiêm được để test không phụ thuộc máy đang chạy. Mọi thứ vắng mặt đều trả
    về dưới dạng dữ liệu, không ném exception: script này chạy ở máy lạ, và một traceback
    ở đây nghĩa là người dùng mất luôn đường tự vá.
    """
    tim_lenh = tim_lenh or shutil.which
    thieu, luu_y = [], []

    toi_thieu = str(manifest.get("python_min") or "3.8")
    can = tuple(int(p) for p in toi_thieu.split("."))
    if sys.version_info[:len(can)] < can:
        dang_co = ".".join(str(p) for p in sys.version_info[:3])
        thieu.append(f"Python >= {toi_thieu} (đang có {dang_co})")

    for lenh in manifest.get("external_commands", []):
        if tim_lenh(lenh) is None:
            thieu.append(f"lệnh ngoài `{lenh}` chưa có trong PATH")

    for may_chu in manifest.get("mcp_servers", []):
        # MCP chỉ người dùng duyệt được trong giao diện harness — máy không tự bật thay được.
        luu_y.append(f"MCP `{may_chu}` cần bạn duyệt thủ công một lần")

    return {"thieu": thieu, "luu_y": luu_y}


# ------------------------------------------------------------------- setup

def ghi_de_co_backup(duong, noi_dung_moi):
    """Ghi đè file nhưng luôn để lại `<file>.tdq-bak-<timestamp>`. Trả đường dẫn bản sao lưu.

    Không có tuỳ chọn tắt backup: file bị ghi đè có thể mang thứ người dùng tự thêm (khối
    `env` chẳng hạn), nên khả năng hoàn tác là thứ duy nhất giữ cho việc tự vá còn an toàn.
    """
    sao_luu = None
    if os.path.isfile(duong):
        dau = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        sao_luu = f"{duong}.tdq-bak-{dau}"
        shutil.copy2(duong, sao_luu)
        log(f"sao lưu {os.path.basename(duong)} → {os.path.basename(sao_luu)}")
    with open(duong, "w", encoding="utf-8") as f:
        f.write(noi_dung_moi)
    return sao_luu


def _ghi_json_co_backup(duong, du_lieu):
    noi_dung = json.dumps(du_lieu, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if _doc(duong) == noi_dung:
        return None
    ghi_de_co_backup(duong, noi_dung)
    return duong


def _doc(duong):
    try:
        with open(duong, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def chay_setup(goc, manifest):
    """Tự vá phần vá được, trả `(việc đã làm, việc KHÔNG tự vá được)`.

    Ranh giới cố ý hẹp: chỉ hai file cấu hình dựng lại được từ dữ liệu có sẵn trong bundle.
    Mọi file khác lệch nội dung thì nguồn đúng duy nhất nằm ở bản gốc — bịa nội dung cho
    chúng còn nguy hiểm hơn để nguyên, vì `check` sau đó sẽ báo sạch trên một bundle sai.
    """
    da_lam, chiu = [], []

    for tuong_doi in kiem_file(goc, manifest)["thieu"]:
        thu_muc = os.path.dirname(os.path.join(goc, tuong_doi.replace("/", os.sep)))
        if thu_muc and not os.path.isdir(thu_muc):
            os.makedirs(thu_muc, exist_ok=True)
            da_lam.append(f"tạo thư mục {os.path.relpath(thu_muc, goc)}")

    # Chỉ vá thứ manifest thật sự đòi: bản codex không có `.mcp.json`, thêm vào đó là làm
    # bẩn bundle — lần `check` sau sẽ thấy một file lạ không ai giải thích được.
    trong_manifest = set(manifest.get("files", {}))
    if ".mcp.json" in trong_manifest:
        if _ghi_json_co_backup(os.path.join(goc, ".mcp.json"), sinh_mcp()):
            da_lam.append("sinh lại .mcp.json")

    duong_hooks = os.path.join(goc, GOC_TDQ.replace("/", os.sep), "hooks", "hooks.json")
    duong_settings = os.path.join(goc, ".claude", "settings.json")
    if ".claude/settings.json" in trong_manifest and os.path.isfile(duong_hooks):
        cai_dat = sinh_settings(goc, duong_hooks)
        cu = _doc(duong_settings)
        if cu:  # giữ lại khối `env` người dùng đã có — chỉ dựng lại phần hook
            try:
                cai_dat.setdefault("env", json.loads(cu).get("env", {}))
            except ValueError:
                pass
        mat_trang = cu is None
        if _ghi_json_co_backup(duong_settings, cai_dat):
            da_lam.append(
                "sinh lại .claude/settings.json (phần hook; khối `env` không tái tạo được"
                " — chép lại từ bản gốc nếu bạn từng thêm biến ở đó)"
                if mat_trang else "sinh lại .claude/settings.json")

    con = kiem_file(goc, manifest)
    chiu = [f"{t} (chép lại từ bản gốc)" for t in con["thieu"] + con["lech"]]
    return da_lam, chiu


# -------------------------------------------------- tin cậy project cho Codex CLI

# Thư mục cấu hình của Codex. `CODEX_HOME` là biến chính Codex đọc, nên tôn trọng nó cũng là
# cách để test chạy được mà không bao giờ chạm `~/.codex` thật.
THU_MUC_CODEX_MAC_DINH = "~/.codex"


def duong_config_codex(moi_truong=None):
    """Đường dẫn `config.toml` của Codex CLI ở máy này (chưa chắc tồn tại)."""
    moi_truong = os.environ if moi_truong is None else moi_truong
    goc = moi_truong.get("CODEX_HOME") or os.path.expanduser(THU_MUC_CODEX_MAC_DINH)
    return os.path.join(goc, "config.toml")


def _khoa_project(goc_bundle):
    """Khoá TOML của một project — Codex khớp theo đường dẫn tuyệt đối đã giải symlink."""
    return f'[projects."{os.path.realpath(goc_bundle)}"]'


def da_trusted(goc_bundle, moi_truong=None):
    """Project đã được khai `trust_level = "trusted"` chưa. Thiếu file/thiếu quyền → False.

    Không ném với bất kỳ input nào: hàm này chạy trong đường `check`, và `check` mà crash ở
    máy lạ nghĩa là người dùng mất luôn đường chẩn đoán.
    """
    noi_dung = _doc(duong_config_codex(moi_truong))
    if not noi_dung:
        return False
    khoa = _khoa_project(goc_bundle)
    vi_tri = noi_dung.find(khoa)
    if vi_tri < 0:
        return False
    # Chỉ đọc tới đầu block kế tiếp: `trust_level` của một project KHÁC không tính.
    con_lai = noi_dung[vi_tri + len(khoa):]
    ket = con_lai.find("\n[")
    return 'trust_level = "trusted"' in (con_lai if ket < 0 else con_lai[:ket])


def bat_trusted(goc_bundle, moi_truong=None):
    """Ghi block `[projects."<bundle>"] trust_level = "trusted"` vào config của Codex.

    Đây là đường DUY NHẤT trong toàn bộ file này ghi ra ngoài cây bundle, nên nó bị bó bằng
    ba luật cứng: chỉ chạy khi có cờ `--trust`, luôn để lại `<file>.tdq-bak-<timestamp>`
    trước khi sửa file có sẵn, và không bao giờ ghi chồng block của project đã khai.

    Vì sao vẫn cần: project chưa trusted thì Codex bỏ qua TOÀN BỘ tầng `.codex/` của nó —
    MCP không nạp, hook không đọc. Bundle sẽ trông như không có gì, đúng câu hỏi đã sinh ra
    request này.

    Trả `(đã ghi?, đường dẫn config, lý do bỏ qua)`.
    """
    duong = duong_config_codex(moi_truong)
    if da_trusted(goc_bundle, moi_truong):
        return False, duong, "project đã được khai trusted từ trước"
    cu = _doc(duong)
    khoi = f'\n{_khoa_project(goc_bundle)}\ntrust_level = "trusted"\n'
    if cu is None:
        os.makedirs(os.path.dirname(duong), exist_ok=True)
        with open(duong, "w", encoding="utf-8") as f:
            f.write("# TDQ Workflow thêm block dưới đây bằng `setup --trust`.\n" + khoi)
        log(f"tạo mới {duong} và khai project trusted")
        return True, duong, ""
    moi = cu if cu.endswith("\n") else cu + "\n"
    ghi_de_co_backup(duong, moi + khoi)
    log(f"ghi {duong}: thêm block projects cho {os.path.realpath(goc_bundle)}")
    return True, duong, ""


# ---------------------------------------------------------------------- CLI

def _in_ket_qua(goc, manifest):
    file_ = kiem_file(goc, manifest)
    moi_truong = kiem_moi_truong(manifest)
    for tuong_doi in file_["thieu"]:
        print(f"THIẾU  {tuong_doi}")
    for tuong_doi in file_["lech"]:
        print(f"LỆCH   {tuong_doi}")
    for dong in moi_truong["thieu"]:
        print(f"THIẾU  {dong}")
    for dong in moi_truong["luu_y"]:
        print(f"LƯU Ý  {dong}")
    for dong in bien_moi_truong_mcp(manifest):
        print(f"LƯU Ý  biến {dong}")
    # Chỉ bản codex mới có tầng `.codex/`, và chỉ tầng đó mới phụ thuộc trạng thái trusted.
    if ".codex/config.toml" in manifest.get("files", {}):
        if da_trusted(goc):
            print(f"LƯU Ý  project đã trusted trong {duong_config_codex()}")
        else:
            print("LƯU Ý  project chưa trusted — Codex bỏ qua TOÀN BỘ .codex/ (MCP + hook)"
                  " cho tới khi bạn chạy `setup --trust` hoặc bấm đồng ý trong Codex")
    # Manifest không liệt kê file nào thì nó không chứng minh được gì. Báo "sạch 0 file" ở
    # đây là biến một manifest hỏng thành giấy chứng nhận an toàn.
    if not manifest.get("files"):
        print("LỖI   manifest không liệt kê file nào — bản portable hỏng, chép lại từ gốc")
        return False
    sach = not (file_["thieu"] or file_["lech"] or moi_truong["thieu"])
    if sach:
        print(f"SẠCH   {len(manifest.get('files', {}))} file khớp manifest")
    return sach


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="tdq_checkportable.py",
        description="Kiểm bản portable theo manifest và tự vá phần thiếu.")
    parser.add_argument("lenh", choices=("check", "setup"))
    parser.add_argument("--root", help="gốc bản portable, mặc định suy từ vị trí script")
    parser.add_argument(
        "--trust", action="store_true",
        help="chỉ dùng với `setup`: khai bundle này là project trusted trong config.toml của "
             "Codex CLI (mặc định ~/.codex, hoặc $CODEX_HOME). Đây là đường DUY NHẤT ghi ra "
             "ngoài bundle; luôn để lại bản sao lưu .tdq-bak-<timestamp>.")
    args = parser.parse_args(argv)

    goc = args.root or tim_goc_bundle()
    try:
        manifest = doc_manifest(goc)
    except (FileNotFoundError, ValueError) as loi:
        print(f"LỖI    {loi}")
        return EXIT_LECH

    log(f"{args.lenh} · root={goc}")
    if args.lenh == "setup":
        try:
            da_lam, chiu = chay_setup(goc, manifest)
        except OSError as loi:
            # Bundle giải nén sai quyền hoặc nằm trên mount chỉ đọc là ca thường gặp ở máy
            # lạ. Traceback ở đây chỉ làm người dùng tưởng script hỏng.
            print(f"LỖI   không ghi được vào bundle: {loi}")
            print("      sửa quyền thư mục (chmod -R u+w) rồi chạy lại `setup`")
            return EXIT_LECH
        if args.trust:
            try:
                da_ghi, duong, ly_do = bat_trusted(goc)
            except OSError as loi:
                print(f"LỖI   không ghi được cấu hình Codex: {loi}")
                return EXIT_LECH
            da_lam.append(f"khai project trusted trong {duong}" if da_ghi
                          else f"bỏ qua --trust: {ly_do}")
        for viec in da_lam:
            print(f"ĐÃ LÀM {viec}")
        if not da_lam:
            print("ĐÃ LÀM (không có gì cần vá)")
        for viec in chiu:
            print(f"CÒN    {viec}")
        sach = _in_ket_qua(goc, manifest)
        # Vá xong mà bundle vẫn hỏng thì exit 0 là báo láo — người dùng sẽ đi tiếp và
        # gặp lỗi thật ở giữa một request đang chạy dở.
        return 0 if sach else EXIT_LECH

    return 0 if _in_ket_qua(goc, manifest) else EXIT_LECH


if __name__ == "__main__":
    sys.exit(main())
