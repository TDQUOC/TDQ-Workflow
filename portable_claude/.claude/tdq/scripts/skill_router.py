#!/usr/bin/env python3
"""skill_router.py — NGUYÊN MẪU kho tra cứu skill: tìm đúng vài skill thay vì nạp cả 284.

**Đây là nguyên mẫu để ĐO, chưa lắp vào luồng nào.** Không hook nào gọi file này;
QC hạng mục Q18 kiểm đúng điều đó. Mục đích duy nhất của nó trong request này là
trả lời một câu hỏi bằng số: nếu giấu mô tả skill đi rồi tra khi cần, thì tra có
TRÚNG không. Trả lời sai câu đó thì tiết kiệm token xong hỏng việc — mất một skill
lẽ ra phải dùng mà không ai biết.

Vì sao BM25 chứ không phải vector DB: cả kho chỉ 284 mô tả, ~38.700 ký tự — nhỏ hơn
một file mã nguồn cỡ vừa. BM25 chạy tức thì, không cần model embedding, không cần
API key (ràng buộc user chốt ở câu 7b của brief). Nâng lên vector chỉ khi số đo cho
thấy từ khoá trượt, không nâng vì cảm giác.

Hai lệnh:
    python3 scripts/skill_router.py --dung-kho          # sinh lại docs/tdq/audit/skill-index.json
    python3 scripts/skill_router.py --tra "<câu>"       # tra top-k skill hợp nhất

Log service: timestamp ISO ra stderr, bật mặc định, tắt bằng `TDQ_LOG=0`.
Exit: 0 chạy xong · 2 sai cú pháp · 4 kho chưa dựng.
"""
import argparse
import json
import math
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_state  # noqa: E402 — dùng chung log service
import skill_tokens  # noqa: E402 — dùng chung bản đồ SKILL.md và mô tả đầy đủ
import skill_inventory  # noqa: E402 — dùng chung danh sách skill ĐANG BẬT

KHO = os.path.join(ROOT, "docs", "tdq", "audit", "skill-index.json")
TRUONG = ("ten", "mo_ta", "nguon", "duong_dan")
EXIT_THIEU_KHO = 4
TOP_K = 5

# Tham số BM25 chuẩn. k1 điều tiết mức thưởng khi một từ lặp nhiều lần, b điều tiết
# mức phạt tài liệu dài. Giữ giá trị chuẩn để số đo so được với tài liệu ngoài.
BM25_K1 = 1.5
BM25_B = 0.75


def _log(msg):
    if tdq_state.log_enabled():
        print(f"[{tdq_state.now_iso()}] {msg}", file=sys.stderr)


def bo_dau(chu):
    """Bỏ dấu tiếng Việt để 'thời gian' và 'thoi gian' tra ra cùng một chỗ."""
    tach = unicodedata.normalize("NFD", chu)
    return "".join(c for c in tach if unicodedata.category(c) != "Mn").replace("đ", "d")


TU_RE = re.compile(r"[a-z0-9]+")

# Từ chức năng — bỏ trước khi tính điểm. Đây KHÔNG phải tinh chỉnh cho đẹp số: kho
# skill gần như toàn tiếng Anh, chỉ 6 mô tả `tdq-*` viết tiếng Việt. Nên mỗi hư từ
# tiếng Việt ("cho", "này", "một") chỉ xuất hiện trong đúng 6 tài liệu đó → IDF cực
# cao → mọi câu hỏi tiếng Việt đều trả về tdq-*. Đo thật: "chạy quét sonarqube cho
# nhánh này" ra tdq-plan hạng 1, sonar-integrate hạng 3, chỉ vì "cho/này/chạy".
# Bỏ hư từ hai thứ tiếng là cách chuẩn của IR, không phải mẹo hợp bộ mẫu.
DUNG_TU = frozenset("""
a an and are as at be by for from has have how i in is it its of on or that the to
was what when where which who will with you your this these those do does can could
should would if then than there here it s
bi boi ca cac cai cho chua chuc co con cua cung da dang de den di do doi duoc dung
gi gia giup hay hoac khi khong la lai lam len luc mA ma moi mot muon nao nay nen ngay
nhu nhung no o phai qua ra rang rat roi sau se so ta thi tren tu tuy va vao ve vi voi
vua xong y toi ban minh chung ho no cai nhieu it hon nua lan cach kieu tren duoi
""".split())


def tach_tu(chu, bo_hu_tu=True):
    """Chuỗi → list từ đã chuẩn hoá. Cùng một hàm cho cả lúc dựng kho và lúc tra."""
    tu = TU_RE.findall(bo_dau(chu.lower()))
    return [t for t in tu if t not in DUNG_TU] if bo_hu_tu else tu


def dung_kho(project=ROOT):
    """Dựng kho từ skill ĐANG BẬT. Mỗi bản ghi đủ 4 trường của `TRUONG`."""
    hang = skill_inventory.inventory(project)
    ban_do = skill_tokens.ban_do_skill_md()
    ban_ghi = []
    for ten, mo_ta_ngan, nguon in hang:
        duong_dan = ""
        ds = ban_do.get(skill_tokens.khoa_tra(ten), [])
        if ds:
            duong_dan = os.path.relpath(ds[0], ROOT) if ds[0].startswith(ROOT) else ds[0]
        ban_ghi.append({
            "ten": ten,
            "mo_ta": skill_tokens._mo_ta_day_du(ten, mo_ta_ngan, ban_do),
            "nguon": nguon,
            "duong_dan": duong_dan,
        })
    thieu = [b["ten"] for b in ban_ghi if not b["duong_dan"]]
    _log(f"dựng kho: {len(ban_ghi)} bản ghi từ {len(hang)} skill đang bật")
    if thieu:
        # Không im lặng: đây là những skill mà router tìm ra cũng không chỉ được
        # file để đọc — tức tầng "off + đọc thẳng SKILL.md" không phục vụ được chúng.
        _log(f"cảnh báo: {len(thieu)} skill không dò ra SKILL.md (tên khai khác tên "
             f"thư mục), vd {thieu[:3]}")
    return ban_ghi


def ghi_kho(ban_ghi, path=KHO):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ban_ghi, f, ensure_ascii=False, indent=2)
        f.write("\n")
    _log(f"ghi kho → {os.path.relpath(path, ROOT)}")


def doc_kho(path=KHO):
    """Đọc kho. Chưa dựng → thoát mã 4 kèm đúng lệnh phải chạy, không tra bừa."""
    try:
        with open(path, encoding="utf-8") as f:
            ban_ghi = json.load(f)
    except OSError:
        print(f"skill_router.py: chưa có kho {os.path.relpath(path, ROOT)}.\n"
              "Dựng bằng: python3 scripts/skill_router.py --dung-kho", file=sys.stderr)
        sys.exit(EXIT_THIEU_KHO)
    thieu = [b.get("ten", "?") for b in ban_ghi
             if any(t not in b for t in TRUONG)]
    if thieu:
        print(f"skill_router.py: {len(thieu)} bản ghi thiếu trường bắt buộc "
              f"(vd {thieu[0]}). Dựng lại bằng: "
              "python3 scripts/skill_router.py --dung-kho", file=sys.stderr)
        sys.exit(EXIT_THIEU_KHO)
    return ban_ghi


class KhoBM25:
    """Chỉ mục BM25 trên kho skill. Dựng một lần, tra nhiều lần."""

    def __init__(self, ban_ghi):
        self.ban_ghi = ban_ghi
        self.tai_lieu = [tach_tu(f"{b['ten']} {b['ten']} {b['mo_ta']}") for b in ban_ghi]
        # Tên skill đếm hai lần: người gõ prompt hay nhắc đúng tên công cụ, và tên
        # là tín hiệu mạnh hơn một từ bất kỳ trong mô tả dài.
        self.do_dai = [len(d) for d in self.tai_lieu]
        self.dai_tb = sum(self.do_dai) / len(self.do_dai) if self.do_dai else 0
        self.df = {}
        for doc in self.tai_lieu:
            for tu in set(doc):
                self.df[tu] = self.df.get(tu, 0) + 1
        self.tf = [{} for _ in self.tai_lieu]
        for i, doc in enumerate(self.tai_lieu):
            for tu in doc:
                self.tf[i][tu] = self.tf[i].get(tu, 0) + 1

    def _idf(self, tu):
        n = len(self.tai_lieu)
        df = self.df.get(tu, 0)
        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def diem(self, cau_hoi, i):
        tong = 0.0
        for tu in tach_tu(cau_hoi):
            f = self.tf[i].get(tu, 0)
            if not f:
                continue
            chuan = 1 - BM25_B + BM25_B * (self.do_dai[i] / self.dai_tb or 1)
            tong += self._idf(tu) * f * (BM25_K1 + 1) / (f + BM25_K1 * chuan)
        return tong

    def tra(self, cau_hoi, k=TOP_K):
        """Top-k bản ghi hợp nhất. Trả list (điểm, bản ghi), điểm 0 bị loại."""
        cham = [(self.diem(cau_hoi, i), b) for i, b in enumerate(self.ban_ghi)]
        cham = [c for c in cham if c[0] > 0]
        cham.sort(key=lambda c: (-c[0], c[1]["ten"]))
        return cham[:k]


def lenh_dung_kho(args):
    ghi_kho(dung_kho(args.project))
    print(f"Đã dựng kho: {os.path.relpath(KHO, ROOT)}")
    return 0


def lenh_tra(args):
    kho = KhoBM25(doc_kho())
    ket_qua = kho.tra(args.tra, args.k)
    if not ket_qua:
        print(f"Không skill nào khớp {args.tra!r}.")
        return 0
    print(f"| # | skill | điểm | nguồn |")
    print("|---|---|---|---|")
    for thu_tu, (diem, b) in enumerate(ket_qua, 1):
        print(f"| {thu_tu} | {b['ten']} | {diem:.2f} | {b['nguon']} |")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="skill_router.py",
        description="Nguyên mẫu kho tra cứu skill (BM25, offline). CHƯA lắp vào luồng.")
    parser.add_argument("--dung-kho", action="store_true", dest="dung_kho",
                        help="sinh lại docs/tdq/audit/skill-index.json")
    parser.add_argument("--tra", metavar="CÂU",
                        help="tra top-k skill hợp với câu này")
    parser.add_argument("-k", type=int, default=TOP_K, help=f"số kết quả (mặc định {TOP_K})")
    parser.add_argument("--project", default=ROOT, help="thư mục project để kiểm kê skill")
    args = parser.parse_args(argv)

    if bool(args.dung_kho) == bool(args.tra):
        parser.error("chọn đúng một trong hai: --dung-kho hoặc --tra \"<câu>\"")
    _log(f"skill_router · {'--dung-kho' if args.dung_kho else '--tra'}")
    return lenh_dung_kho(args) if args.dung_kho else lenh_tra(args)


if __name__ == "__main__":
    sys.exit(main())
