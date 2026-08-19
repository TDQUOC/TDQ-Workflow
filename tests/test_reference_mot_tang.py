"""Khoá cấu trúc nạp của bộ skill: mọi reference phải tới được trong ĐÚNG MỘT tầng.

Vì sao cần lưới này. Hướng dẫn chính thức của Anthropic về Agent Skills nói giữ reference
đúng một tầng từ `SKILL.md`, vì model "có thể chỉ đọc một phần" file được trỏ tới từ một
file đã là reference. Luật nằm ở tầng 2 trở xuống vì thế có nguy cơ được đọc nửa vời —
mà đọc nửa vời một luật thì tệ hơn không có luật, vì không ai thấy chỗ thiếu.

Lưới này khoá ba thứ, mỗi thứ một lớp:
  - mọi file `references/**/*.md` được ít nhất một `SKILL.md` trỏ THẲNG tới;
  - mọi link `.md` trong `skills/` trỏ tới file có thật (sửa link không được tạo link hư);
  - file reference dài hơn `TRAN_DONG` dòng phải có mục lục, để model đọc chọn lọc.

Cách đo: dựng đồ thị link markdown, giải cả link tương đối cùng thư mục. Không dùng số
dòng hay thứ tự file — chèn một dòng không được làm đỏ oan.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")

# Bắt link markdown `(duong/dan.md)` và đường dẫn trong dấu nháy ngược `` `duong/dan.md` ``.
# Nháy ngược cũng tính vì bộ skill dùng cả hai kiểu để trỏ file, và model đọc cả hai như
# nhau — chỉ tính kiểu link markdown sẽ bỏ sót đường trỏ có thật.
LINK_RE = re.compile(r"[(`]([A-Za-z0-9_./-]+\.md)[)`]")

# Chỉ link markdown thật `](duong/dan.md)`. Dùng riêng cho test link chết: đường dẫn trong
# nháy ngược phần lớn là NHẮC TÊN trong câu văn ("nạp `chung.md` trước"), không phải link —
# bắt chúng phải giải được sẽ đỏ oan hàng loạt và người ta sẽ tắt test.
MD_LINK_RE = re.compile(r"\]\(([A-Za-z0-9_./-]+\.md)\)")

# Ngưỡng dòng bắt buộc có mục lục. Lấy đúng con số hướng dẫn chính thức khuyên (100).
TRAN_DONG = 100

# NGOẠI LỆ DUY NHẤT của luật một tầng: nhóm điều phối theo ngôn ngữ.
# `references/rules/` có 10 file, mỗi file một ngôn ngữ, và một request chỉ mở ĐÚNG MỘT
# trong số đó. Bắt `SKILL.md` trỏ thẳng cả 10 file sẽ nhồi 10 dòng vào thân skill — thứ
# nạp trong MỌI request — để phục vụ thứ chỉ dùng một. Nên nhóm này được phép có đúng
# MỘT bước điều phối: `SKILL.md` → `rules/index.md` → file ngôn ngữ. Đổi lại, ngoại lệ bị
# khoá chặt hơn phần còn lại: cửa vào phải ở tầng 1, và index phải trỏ đủ MỌI file anh em
# — thiếu một file là có luật ngôn ngữ không đường nào tới.
DIEU_PHOI = {os.path.join("tdq-build", "references", "rules"): "index.md"}


def _duyet(thu_muc, duoi=".md"):
    for goc, _, ten_files in os.walk(thu_muc):
        for ten in sorted(ten_files):
            if ten.endswith(duoi):
                yield os.path.join(goc, ten)


def cac_skill_md():
    """Mọi `skills/<ten>/SKILL.md` — cửa vào tầng 1 của mỗi skill."""
    return sorted(
        os.path.join(SKILLS, d, "SKILL.md")
        for d in os.listdir(SKILLS)
        if os.path.isfile(os.path.join(SKILLS, d, "SKILL.md")))


def cac_reference():
    """Mọi file reference, kể cả trong thư mục con (`references/rules/…`)."""
    ra = []
    for d in sorted(os.listdir(SKILLS)):
        thu_muc = os.path.join(SKILLS, d, "references")
        if os.path.isdir(thu_muc):
            ra += sorted(_duyet(thu_muc))
    return ra


def _giai(path, duong_dan):
    """Giải một đường dẫn `.md` trong văn bản về file có thật, thử ba gốc.

    Ba gốc vì bộ skill dùng cả ba kiểu viết, và model đọc cả ba như nhau:
    tương đối với chính file (`references/x.md`), tương đối với gốc repo
    (`skills/tdq-plan/SKILL.md`, `docs/kien-truc.md`), và tương đối với `skills/`
    (`tdq-build/references/team-mode.md`). Trả None khi không gốc nào ra file có thật.
    """
    for goc in (os.path.dirname(path), ROOT, SKILLS):
        thu = os.path.normpath(os.path.join(goc, duong_dan))
        if os.path.isfile(thu):
            return thu
    return None


def duong_dan_trong(path, chi_link_md=False):
    """Mọi đường dẫn `.md` xuất hiện trong `path`, chưa giải."""
    with open(path, encoding="utf-8") as f:
        noi_dung = f.read()
    return (MD_LINK_RE if chi_link_md else LINK_RE).findall(noi_dung)


def link_trong(path):
    """Tập file THẬT nằm trong `skills/` mà `path` trỏ tới."""
    ra = set()
    for m in duong_dan_trong(path):
        dich = _giai(path, m)
        if dich and dich.startswith(SKILLS + os.sep):
            ra.add(dich)
    return ra


def _ten_ngan(path):
    return os.path.relpath(path, SKILLS)


def _thuoc_dieu_phoi(path):
    """File có nằm trong một nhóm điều phối không (và không phải chính cửa vào)."""
    thu_muc = os.path.dirname(os.path.relpath(path, SKILLS))
    cua_vao = DIEU_PHOI.get(thu_muc)
    return cua_vao is not None and os.path.basename(path) != cua_vao


class MotTang(unittest.TestCase):
    """Mọi reference phải được một `SKILL.md` trỏ thẳng — không có luật nào ở tầng 2."""

    def test_moi_reference_duoc_skill_md_tro_thang(self):
        tu_skill = set()
        for s in cac_skill_md():
            tu_skill |= link_trong(s)
        tang_hai = [_ten_ngan(f) for f in cac_reference()
                    if f not in tu_skill and not _thuoc_dieu_phoi(f)]
        self.assertEqual(
            [], tang_hai,
            "Các file reference sau KHÔNG được `SKILL.md` nào trỏ thẳng, tức nằm ở tầng 2 "
            "trở xuống và có nguy cơ bị đọc nửa vời — thêm một dòng trỏ ở thân skill "
            f"tương ứng: {tang_hai}")

    def test_nhom_dieu_phoi_co_cua_vao_o_tang_mot_va_tro_du_anh_em(self):
        tu_skill = set()
        for s in cac_skill_md():
            tu_skill |= link_trong(s)
        for thu_muc, ten_cua_vao in DIEU_PHOI.items():
            cua_vao = os.path.join(SKILLS, thu_muc, ten_cua_vao)
            self.assertIn(
                cua_vao, tu_skill,
                f"Cửa vào của nhóm điều phối `{thu_muc}` phải được một `SKILL.md` trỏ "
                f"thẳng, nếu không cả nhóm nằm ở tầng 3 trở xuống: {ten_cua_vao}")
            duoc_tro = link_trong(cua_vao)
            thieu = [_ten_ngan(f) for f in sorted(_duyet(os.path.join(SKILLS, thu_muc)))
                     if f != cua_vao and f not in duoc_tro]
            self.assertEqual(
                [], thieu,
                f"`{thu_muc}/{ten_cua_vao}` là đường DUY NHẤT tới các file này mà lại "
                f"không trỏ tới chúng — luật ngôn ngữ đó không có đường nào tới: {thieu}")


class KhongLinkChet(unittest.TestCase):
    """Mọi link `.md` trong `skills/` phải trỏ tới file có thật.

    Lưới hồi quy cho chính việc phẳng hoá: thêm/sửa dòng trỏ mà gõ sai đường dẫn thì luật
    không những vẫn ở tầng sâu, mà còn mất luôn đường tới — hỏng nặng hơn lúc chưa sửa.
    """

    def test_khong_link_nao_tro_vao_hu_khong(self):
        hong = []
        for path in cac_skill_md() + cac_reference():
            for duong_dan in duong_dan_trong(path, chi_link_md=True):
                if _giai(path, duong_dan) is None:
                    hong.append(f"{_ten_ngan(path)} -> {duong_dan}")
        self.assertEqual([], hong, f"Link trỏ tới file không tồn tại: {hong}")


class MucLuc(unittest.TestCase):
    """File reference dài phải có mục lục khớp tiêu đề của chính nó.

    Hướng dẫn chính thức khuyên mục lục cho file reference dài hơn 100 dòng, để model đọc
    đúng phần cần thay vì nuốt cả file. Mục lục lệch khỏi tiêu đề thật còn hại hơn không
    có, nên test khoá luôn phần khớp — không chỉ khoá phần "có tồn tại một cái mục lục".
    """

    @staticmethod
    def _tieu_de(noi_dung):
        """Danh sách tiêu đề `##` (bỏ `###` trở xuống và bỏ chính mục lục)."""
        ra = []
        for dong in noi_dung.splitlines():
            if dong.startswith("## ") and not dong.startswith("## Mục lục"):
                ra.append(dong[3:].strip())
        return ra

    def test_file_dai_co_muc_luc_khop_tieu_de(self):
        thieu, lech = [], []
        for path in cac_reference():
            with open(path, encoding="utf-8") as f:
                noi_dung = f.read()
            if len(noi_dung.splitlines()) <= TRAN_DONG:
                continue
            if "## Mục lục" not in noi_dung:
                thieu.append(_ten_ngan(path))
                continue
            khoi = noi_dung.split("## Mục lục", 1)[1].split("\n## ", 1)[0]
            for tieu_de in self._tieu_de(noi_dung):
                if tieu_de not in khoi:
                    lech.append(f"{_ten_ngan(path)}: thiếu mục `{tieu_de}`")
        self.assertEqual(
            [], thieu,
            f"File reference dài hơn {TRAN_DONG} dòng mà chưa có `## Mục lục`: {thieu}")
        self.assertEqual([], lech, f"Mục lục không khớp tiêu đề thật: {lech}")
