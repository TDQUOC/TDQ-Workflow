"""Khuôn khối nói với user (conventions §1 mục 6).

Ba bất biến dễ trôi:
1. File khuôn tồn tại và nêu đủ 5 thành phần + 7 chỗ phải dùng.
2. Khuôn cấm emoji — và bản thân file khuôn cũng không được chứa emoji.
3. Mọi skill có chỗ nói với user đều trỏ về file khuôn thay vì tự chế khuôn riêng.
"""
import os
import re
import sys
import unicodedata
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import scan_block_symbols as scan  # noqa: E402  (dùng chung máy quét của T0.1)
from scan_block_symbols import WHITELIST  # noqa: E402  (whitelist chốt ở T0.2)

SKILLS = os.path.join(ROOT, "skills")
PORTABLE = os.path.join(ROOT, "portable_codex", "workflow")
# Bản portable nay do `scripts/build_portable.py` SINH, không chép tay nữa. Vẫn kiểm
# nó: sinh sai đường dẫn hay sót file thì khuôn vẫn biến mất ở máy đích y như trôi tay.
BLOCK = os.path.join(SKILLS, "tdq-conventions", "references", "user-facing-block.md")
# Dải emoji hay gặp; `➤` (U+27A4) nằm ngoài các dải này nên vẫn hợp lệ.
# Thêm U+231B, U+23F3, U+2714 sau T0.2: `⏳` và `✔` từng lọt qua vì không nằm trong dải
# nào ở trên. `✓` (U+2713) KHÔNG bị cấm — nó là giao ước `✓ [TDQ:<MÃ>]` của workflow.
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-⛿✅❌⚠⌛⏳✔]")
# Skill nào có chỗ hỏi/trình cho user thì phải trỏ về khuôn chung.
POINTERS = (
    ("tdq-conventions", "SKILL.md"),
    ("tdq-spec", "SKILL.md"),
    ("tdq-plan", "SKILL.md"),
    # Khối hỏi commit của tdq-build nằm ở references/report-template.md từ Đ3
    # (thân SKILL.md chỉ còn dòng trỏ) — kiểm đúng chỗ đang giữ khuôn.
    ("tdq-build", "references", "report-template.md"),
    ("tdq-intake", "references", "lane-decision.md"),
    ("tdq-intake", "references", "interview.md"),
    ("tdq-intake", "references", "quick-lane.md"),
    # QC vòng 1: hai file dưới có chỗ nói với user nhưng chưa trỏ về khuôn.
    ("tdq-plan", "references", "mode-gate.md"),
    ("tdq-status", "SKILL.md"),
)


# Dòng luật trang trí: số thứ tự ở đầu dòng, dạng `1. ...`.
RULE = re.compile(r"^([1-8])\. ", re.M)
# Nhãn trường: `Mục tiêu: ...`. Luật 1 đòi cặp sao ôm cả dấu hai chấm.
# Loại luôn dấu kết câu khỏi phần tên: `Còn một câu cuối:` giữa một câu văn không phải nhãn.
# Tên nhãn chỉ gồm chữ và khoảng trắng: loại dấu kết câu, dấu nhấn `_`, ngoặc và nháy —
# `_Trả lời bằng chữ cái (vd: "A")_` là câu in nghiêng, không phải nhãn trường.
LABEL = re.compile(r"^(?P<mo>\*\*)?(?P<ten>[^:*`|.?!_()\"]{1,30}):(?P<dong>\*\*)?(?:\s|$)")
# Dạng sai duy nhất mà `LABEL` không thấy: dấu hai chấm bị đẩy ra NGOÀI cặp sao
# (`**Mục tiêu**: ...`). Phần tên khi đó chứa `*` nên `LABEL` bỏ qua dòng, và luật 1
# lọt lưới. Bắt riêng bằng regex dưới đây — nó không phụ thuộc tên nhãn viết bằng gì.
NHAN_SAI = re.compile(r"^\*\*[^*]{1,40}\*\*:")
DAN = "Xem đầy đủ tại: "
# Khối ví dụ đối chiếu (bản "Trước") cố tình sai khuôn — đánh dấu bằng chú thích ngay trên.
# Từ 2026-08-22 chú thích viết tiếng Anh; nhận cả hai để bản cũ và bản dịch cùng xanh.
BO_QUA = ("không phải mẫu để chép", "not a template to copy")
# Thứ khối mẫu không được chứa: gạch ngang giữa chữ, HTML, mã màu ANSI, ký tự kẻ khung.
CAM = ("~~", "<span", "\x1b[", "─", "│", "┌", "┬", "┐", "├", "└")
# 8 file skill chép khối mẫu, cộng file khuôn gốc.
MAU = (
    ("tdq-conventions", "references", "user-facing-block.md"),
    ("tdq-spec", "SKILL.md"),
    ("tdq-plan", "SKILL.md"),
    ("tdq-plan", "references", "mode-gate.md"),
    ("tdq-intake", "references", "lane-decision.md"),
    ("tdq-intake", "references", "quick-lane.md"),
    ("tdq-intake", "references", "interview.md"),
    ("tdq-build", "references", "report-template.md"),
    ("tdq-status", "SKILL.md"),
)

def ten_theo_duoi(duoi):
    """Tên file bản codex mang số thứ tự đọc do build sinh ra: thêm một skill là số dịch
    hết. Dò theo đuôi tên để test khoá vào ĐÚNG file, không khoá vào con số."""
    for ten in sorted(os.listdir(PORTABLE)):
        if re.match(r"\d\d-", ten) and ten.endswith(duoi):
            return ten
    raise AssertionError(f"bản portable thiếu file …{duoi}")


PORTABLE_SPEC = ten_theo_duoi("-spec.md")
PORTABLE_PLAN = ten_theo_duoi("-plan.md")


# Số khối mẫu ĐANG có trong từng file, chốt bằng số đếm thật lúc viết test.
# Có mặt để phép kiểm khối không im lặng chạy rỗng: xoá mất một khối thì con số lệch
# và test đỏ. Hai file mang số 0 là có thật — `interview.md` và `tdq-status/SKILL.md`
# hướng dẫn bằng văn xuôi, dòng `➤` của chúng nằm ngoài khối ```.
SO_KHOI = {
    "tdq-conventions/references/user-facing-block.md": 1,
    "tdq-spec/SKILL.md": 1,
    "tdq-plan/SKILL.md": 1,
    "tdq-plan/references/mode-gate.md": 1,
    "tdq-intake/references/lane-decision.md": 1,
    # 2026-08-22: 1 → 2. Bước 4 của chín bước trước đây nhét dòng `➤` vào giữa câu văn
    # bằng nháy ngược; bản dịch tách nó ra khối ``` riêng để cụm `i18n-allow` miễn đúng
    # dòng mẫu đó. Khối mới là khối thật, chịu luật 1/3/7 như mọi khối khác.
    "tdq-intake/references/quick-lane.md": 2,
    "tdq-intake/references/interview.md": 0,
    "tdq-build/references/report-template.md": 1,
    "tdq-status/SKILL.md": 0,
    "portable/" + PORTABLE_SPEC: 1,
    "portable/" + PORTABLE_PLAN: 1,  # bản sinh chép từ tdq-plan/SKILL.md (khối mode-gate ở file riêng)
    "portable/references/user-facing-block.md": 1,
}


# 12 file phạm vi kiểm: 9 file khuôn/khối mẫu bên `skills/` cộng 3 file bản portable.
FILE_PHAM_VI = tuple(
    (os.path.join(SKILLS, *p), "skills/" + "/".join(p)) for p in MAU
) + tuple(
    (os.path.join(PORTABLE, *p), "portable/workflow/" + "/".join(p))
    for p in ((PORTABLE_SPEC,), (PORTABLE_PLAN,),
              ("references", "tdq-conventions", "user-facing-block.md"))
)


def read(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as f:
        return f.read()


def sections(text):
    """{tên mục `## ...` (bỏ phần trong ngoặc): thân mục} — để kiểm đúng phạm vi.

    Cần thiết vì cả mục thành phần lẫn mục luật đều dùng danh sách đánh số; đếm
    trên cả file sẽ trộn hai mục vào nhau.
    """
    ra, ten = {}, None
    for line in text.split("\n"):
        if line.startswith("## "):
            ten = line[3:].split("(")[0].strip()
            ra[ten] = []
        elif ten is not None:
            ra[ten].append(line)
    return {k: "\n".join(v) for k, v in ra.items()}


def khoi_mau(text):
    """Các khối ``` có dòng `➤` — tức khối thật sự in ra cho user.

    Khối nằm trong danh sách đánh số thì bị thụt lề theo danh sách; bỏ đúng phần
    thụt của dấu mở khối để so luật trên nội dung thật.
    """
    ra, dang, trong, le, truoc = [], [], False, 0, ""
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            if (trong and any(d.startswith("➤") for d in dang)
                    and not any(b in truoc for b in BO_QUA)):
                ra.append(dang)
            dang, trong, le = [], not trong, len(line) - len(line.lstrip())
            continue
        if trong:
            dang.append(line[le:] if line[:le].strip() == "" else line)
        elif line.strip():
            truoc = line
    return ra


class UserFacingBlockTest(unittest.TestCase):
    def test_block_file_exists(self):
        self.assertTrue(os.path.isfile(BLOCK), "thiếu references/user-facing-block.md")

    def test_lists_six_components(self):
        text = read(BLOCK)
        for token in (("Opening line", "Câu dẫn"), ("Body", "Nội dung"),
                      ("File path", "Đường dẫn file"), ("Separator rule", "Đường kẻ ngăn"),
                      ("Answer block", "Khối trả lời"),
                      # 2026-09-03: thành phần 6, đường kẻ kết lượt.
                      ("Closing rule of the turn", "Đường kẻ kết lượt")):
            with self.subTest(component=token[0]):
                self.assertTrue(any(t in text for t in token),
                                f"khuôn thiếu thành phần: {token[0]}")

    def test_lists_seven_touchpoints(self):
        text = read(BLOCK)
        for token in (("pipeline",), ("interview",), ("spec",), ("plan",), ("mode",),
                      ("express", "chế độ nhanh"), ("commit",)):
            with self.subTest(touchpoint=token[0]):
                self.assertTrue(any(t in text for t in token),
                                f"khuôn thiếu chỗ giao tiếp: {token[0]}")

    def test_bans_emoji_and_has_no_emoji_itself(self):
        text = read(BLOCK)
        self.assertTrue("No emoji" in text or "Không emoji" in text,
                        "khuôn không nêu luật cấm emoji")
        # Quét cả 12 file phạm vi, không riêng file khuôn: `⏳` từng lọt vào
        # tdq-status/SKILL.md đúng vì phép quét cũ chỉ nhìn mỗi file khuôn.
        for path, ten in FILE_PHAM_VI:
            with self.subTest(file=ten):
                found = EMOJI.search(read(path))
                self.assertIsNone(found,
                                  f"file dạy Claude in emoji cho user: {found and found.group(0)!r}")

    def test_rules_table_and_seven_rules(self):
        """Khuôn phải dạy CÁCH trình bày, không chỉ liệt kê thành phần.

        Ba thứ dễ trôi nhất: bảng ánh xạ thành phần -> cấu trúc dùng, đủ bảy luật
        trang trí đánh số, và một cặp ví dụ trước/sau để người sửa tự đối chiếu.
        """
        text = read(BLOCK)
        muc = sections(text)

        # 2026-09-03: thêm "The six components". Yêu cầu gate-chat cộng thành phần 6
        # (đường kẻ cuối lượt) nên tiêu đề mục đổi từ five sang six; giữ cả hai tên cũ
        # để bản portable chưa dựng lại không đỏ oan.
        bang = [d for d in (muc.get("The six components")
                            or muc.get("The five components")
                            or muc.get("Sáu thành phần")
                            or muc.get("Năm thành phần", "")).split("\n")
                if d.lstrip().startswith("|")]
        self.assertGreaterEqual(
            len(bang), 6,
            f"mục Năm thành phần thiếu bảng cấu trúc trình bày (có {len(bang)} dòng bảng)")

        luat = RULE.findall(muc.get("The eight decoration rules")
                            or muc.get("The seven decoration rules")
                            or muc.get("Bảy luật trang trí", ""))
        self.assertEqual(
            [str(i) for i in range(1, 9)], luat,
            f"mục luật trang trí phải có đúng 8 luật đánh số 1-8, đang là {luat}")

        for tieu_de in (("### Before", "### Trước"), ("### After", "### Sau")):
            with self.subTest(vidu=tieu_de[0]):
                self.assertTrue(any(t in text for t in tieu_de),
                                f"khuôn thiếu ví dụ đối chiếu {tieu_de[0]}")

    def test_hard_rules_giu_buoc_tu_soat(self):
        """Mục "Hard rules" phải giữ bước tự-soát trước khi gửi khối câu hỏi.

        Luật 8 (đánh số câu hỏi) từng bị vi phạm trong lúc bản thân luật đã có
        sẵn trong file con — cái thiếu là bước ĐỌC LẠI bản nháp trước khi gửi.
        Xoá bước đó đi thì luật lại trôi y như cũ, nên khoá nó bằng test.
        """
        muc = sections(read(BLOCK))
        cung = muc.get("Hard rules") or muc.get("Luật cứng", "")
        self.assertIn(
            "self-check before sending", cung.lower(),
            'mục "Hard rules" mất bước tự-soát trước khi gửi')
        # 3 câu soát nằm THỤT vào trong bullet, nên không dùng `RULE` (neo đầu dòng).
        hoi = re.findall(r"^\s+([1-9])\. ", cung, re.M)
        self.assertEqual(
            ["1", "2", "3"], hoi,
            f"bước tự-soát phải có đúng 3 câu hỏi đánh số 1-3, đang là {hoi}")

    def test_sample_blocks_follow_rules(self):
        """Mọi khối mẫu chép trong skill phải theo đúng luật 1, 3, 7 của khuôn.

        Khối mẫu là thứ Claude chép lại nguyên văn khi nói với user, nên khối lệch
        khuôn nghĩa là user thấy khối lệch khuôn.
        """
        for parts in MAU:
            self.kiem_khoi_mau(os.path.join(SKILLS, *parts), "/".join(parts))

    def kiem_khoi_mau(self, path, ten):
        """Luật 1, 3, 7 cộng danh sách cấm — dùng chung cho skill và bản portable."""
        with open(path, encoding="utf-8") as f:
            text = f.read()
        khoi_list = khoi_mau(text)
        self.assertEqual(
            SO_KHOI[ten], len(khoi_list),
            f"{ten}: số khối mẫu đổi từ {SO_KHOI[ten]} thành {len(khoi_list)} — "
            "khối bị xoá thì phép kiểm dưới đây chạy rỗng mà vẫn xanh")
        for i, khoi in enumerate(khoi_list):
            with self.subTest(file=ten, khoi=i):
                con = [d for d in khoi if d.strip()]
                # 2026-09-03: thành phần 6 cho phép đúng MỘT dòng `---` nằm dưới dòng `➤`,
                # là đường kẻ kết lượt. Bỏ nó ra rồi mới xét luật 7, để luật 7 vẫn bắt được
                # mọi thứ khác lọt xuống dưới khối trả lời.
                if con[-1].strip() == "---":
                    con = con[:-1]
                self.assertTrue(con[-1].startswith("➤"),
                                f"luật 7: dòng cuối khối phải là dòng `➤`, đang là {con[-1]!r}")
                self.assertEqual(1, sum(1 for d in con if d.startswith("➤")),
                                 "luật 7: mỗi khối đúng một dòng `➤`")
                for dong in con:
                    if dong.startswith(DAN):
                        duong = dong[len(DAN):].strip()
                        self.assertTrue(
                            duong.startswith("`") and duong.endswith("`"),
                            f"luật 3: đường dẫn phải bọc nháy ngược, đang là {duong!r}")
                        continue
                    if dong.startswith(("➤", "- ", "|")) or dong.strip() == "---":
                        continue
                    self.assertIsNone(
                        NHAN_SAI.match(dong),
                        f"luật 1: dấu hai chấm phải nằm TRONG cặp sao — {dong!r}")
                    m = LABEL.match(dong)
                    if m:
                        self.assertTrue(
                            m.group("mo") and m.group("dong"),
                            f"luật 1: nhãn trường phải in đậm cả dấu hai chấm — {dong!r}")
                than = "\n".join(khoi)
                for xau in CAM:
                    self.assertNotIn(xau, than, f"khối mẫu chứa thứ bị cấm: {xau!r}")
                for dong in khoi:
                    self.assertIsNone(re.match(r"#{1,6} ", dong),
                                      f"khối mẫu dùng tiêu đề `#` — không dựng được: {dong!r}")

    def test_code_generated_blocks_conform(self):
        """Dòng gợi ý do mã sinh cũng là dòng `➤` in cho user — cùng luật với khối mẫu.

        Ba chuỗi máy đang bắt được kiểm kèm ở đây: sửa trang trí mà làm lệch một byte
        của chúng là làm hỏng hook và test khác.
        """
        sys.path.insert(0, os.path.join(ROOT, "hooks", "scripts"))
        import _common

        for target, mode in (("spec", None), ("plan", None), ("quick", None),
                             ("mode", "main"), ("mode", "subagent")):
            dong = _common.approve_hint(target, mode)
            with self.subTest(target=target, mode=mode):
                self.assertTrue(dong.startswith("➤ "), f"luật 7: phải mở bằng `➤ ` — {dong!r}")
                self.assertEqual(1, dong.count("\n") + 1, "dòng gợi ý phải nằm trên một dòng")
                self.assertIn(" · Feedback: just say it", dong)
                la = [c for c in dong if ord(c) > 127 and unicodedata.category(c)[0] in "PS"
                      and c not in WHITELIST]
                self.assertEqual([], la, f"ký tự ngoài whitelist trong chuỗi mã sinh: {la}")

        self.assertIn("the plan proposes {mode}", _common.APPROVE_HINTS["mode"],
                      "chuỗi `the plan proposes {mode}` là thứ tests/test_context_hooks.py bắt")
        self.assertEqual('➤ Approve: say "approve spec" or type "A" · Feedback: just say it',
                         _common.approve_hint("spec"), "chuỗi cổng duyệt spec đổi byte")

    def test_portable_matches_source(self):
        """Bản portable do máy sinh — kiểm để chắc bộ sinh mang đủ khuôn sang.

        Nó phải mang đủ bảy luật và đúng whitelist của khuôn gốc; hai file spec/plan
        của nó chép khối mẫu nên chịu chung luật 1, 3, 7.
        """
        khuon = read(PORTABLE, "references", "tdq-conventions", "user-facing-block.md")
        # Từ 2026-08-22 khuôn gốc viết tiếng Anh; bản portable sinh từ nó nên đọc tên
        # mục tiếng Anh trước, tên cũ giữ lại để bản portable cũ vẫn kiểm được.
        luat = RULE.findall(sections(khuon).get("The eight decoration rules")
                            or sections(khuon).get("The seven decoration rules")
                            or sections(khuon).get("Bảy luật trang trí", ""))
        self.assertEqual([str(i) for i in range(1, 9)], luat,
                         f"bản portable thiếu tám luật trang trí, đang là {luat}")
        for ch in WHITELIST:
            with self.subTest(ky_tu=ch):
                muc_ky_hieu = (sections(khuon).get("The symbols allowed")
                               or sections(khuon).get("Ký hiệu được phép", ""))
                self.assertIn(ch, muc_ky_hieu,
                              f"bản portable thiếu ký tự whitelist {ch!r}")

        for ten in (PORTABLE_SPEC, PORTABLE_PLAN):
            self.kiem_khoi_mau(os.path.join(PORTABLE, ten), f"portable/{ten}")

    def test_symbol_whitelist(self):
        """Nội dung khối in cho user chỉ được chứa sáu ký hiệu đã chốt.

        Phạm vi là nội dung khối ``` chứ không phải cả file: văn xuôi hướng dẫn quanh
        khối không tới mắt user, siết nó sẽ buộc sửa chữ trong câu.
        """
        tong, theo_file = scan.quet(scan.SCOPE, chi_khoi=True)
        la = {ch: dict(theo_file[ch]) for ch in tong if ch not in WHITELIST}
        self.assertEqual({}, la, f"ký tự ngoài whitelist trong khối mẫu: {la}")

    def test_every_user_facing_skill_points_here(self):
        for parts in POINTERS:
            with self.subTest(file="/".join(parts)):
                self.assertIn("user-facing-block", read(SKILLS, *parts),
                              "file này nói với user nhưng không trỏ về khuôn chung")
        # Bản portable có khuôn riêng đặt cạnh nó, hai file kia phải trỏ về đúng bản đó.
        for ten in (PORTABLE_SPEC, PORTABLE_PLAN):
            with self.subTest(file=f"portable/{ten}"):
                self.assertIn("user-facing-block", read(PORTABLE, ten),
                              "file portable này nói với user nhưng không trỏ về khuôn")


if __name__ == "__main__":
    unittest.main()
