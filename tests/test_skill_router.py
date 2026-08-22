"""Test cho scripts/skill_router.py — nguyên mẫu kho tra cứu skill.

Test quan trọng nhất ở đây là `TiLeTrungTest`: nó trả lời câu hỏi duy nhất khiến
cả hướng E đáng hay không đáng làm — **tra có TRÚNG không**. Router tra trượt còn
hại hơn tốn token, vì nó làm mất một skill lẽ ra phải dùng mà không ai biết.

Bộ prompt mẫu dưới đây cố ý KHÔNG toàn ca dễ. Ba nhóm:
  * `dễ`   — prompt nhắc thẳng tên công cụ ("unity shader", "mongodb").
  * `vừa`  — prompt nói việc, không nói tên công cụ.
  * `khó`  — prompt nói ý định bằng lời thường, không trùng từ khoá nào với mô tả.
Nhóm `khó` là nhóm phản ánh đúng cách người ta gõ prompt thật. Bỏ nó ra thì tỉ lệ
trúng đẹp lên nhưng con số hết nghĩa.
"""
import json
import os
import subprocess
import sys
import unittest

import helper  # noqa: F401  — chèn scripts/ vào sys.path
import skill_router

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "skill_router.py")

# (prompt, tuple skill CHẤP NHẬN ĐƯỢC, độ khó).
#
# Vì sao là TUPLE chứ không phải một tên: router phục vụ việc "lọc 284 skill xuống
# vài cái để đọc kỹ", nên tra trúng nghĩa là **một skill làm được việc đó** lọt vào
# top-k — không phải đúng cái tên tôi thích nhất. Vài prompt có hơn một skill làm
# được thật, chối điều đó thì con số bi quan sai lệch.
#
# Luật đặt đáp án, để tuple không thành cái cớ nới lỏng cho đẹp số:
#   1. Mọi tên trong tuple phải đọc mô tả của CHÍNH skill đó rồi mới đưa vào — mô tả
#      phải nói nó làm đúng việc prompt hỏi. Không đưa vào vì router trả ra nó.
#   2. Cấm nới tuple sau khi thấy kết quả trượt. Ba tuple hai tên dưới đây đều nới
#      vì mô tả nói thẳng, có trích trong comment ngay cạnh.
MAU = [
    ("sửa lỗi unity shader bị đen trên mobile", ("unity-shadergraph-design",), "dễ"),
    ("truy vấn mongodb aggregate cho báo cáo",
     ("mongodb-natural-language-querying",), "dễ"),
    ("crawl toàn bộ trang tài liệu về markdown", ("firecrawl-crawl",), "dễ"),
    ("lấy design token từ file figma", ("figma-generate-library",), "dễ"),
    ("viết spec cho request mới", ("tdq-spec",), "dễ"),
    ("viết plan có checkbox từng task", ("tdq-plan",), "dễ"),
    ("mở request mới và phân tích yêu cầu", ("tdq-intake",), "dễ"),
    ("chạy quét sonarqube cho nhánh này", ("sonar-analyze",), "dễ"),
    # skill-development mô tả: 'create a skill', 'add a skill to plugin' — đúng việc.
    ("tạo skill mới cho plugin của tôi", ("skill-creator", "skill-development"), "dễ"),
    # hook-development mô tả: 'create a hook', 'add a PreToolUse/PostToolUse/Stop hook'.
    ("dựng hook chặn hành vi lặp lại",
     ("writing-hookify-rules", "hook-development"), "dễ"),
    # Playwright chỉ có MCP tool, không có skill nào trong kho → đáp án đơn.
    ("tôi muốn tự động hoá thao tác trên trình duyệt", ("chrome-devtools",), "vừa"),
    ("kiểm tra chất lượng code trước khi merge", ("sonar-quality-gate",), "vừa"),
    ("ghi nhớ một quyết định kiến trúc cho lần sau", ("mem0-memory",), "vừa"),
    ("nghiên cứu sâu một chủ đề trên web rồi tổng hợp", ("tavily-research",), "vừa"),
    ("đóng gói bộ skill thành plugin cài được", ("plugin-structure",), "vừa"),
    ("làm ảnh bìa cho bài đăng mạng xã hội",
     ("canva-resize-for-social-media",), "vừa"),
    ("dữ liệu đang chậm, cần xếp lại bảng cho nhanh",
     ("mongodb-query-optimizer",), "khó"),
    ("nhân vật trong game đi xuyên tường", ("unity-patterns",), "khó"),
    ("tôi cần biết cái nút này bấm vào thì gọi hàm nào", ("graphify",), "khó"),
    ("mọi thứ trông lệch nhau, không thẳng hàng", ("frontend-design",), "khó"),
    ("giao việc cho nhiều trợ lý chạy song song",
     ("dispatching-parallel-agents",), "khó"),
    ("kiểm lại xem việc đã xong đúng chưa",
     ("verification-before-completion",), "khó"),
]


def chay(*args, env=None):
    proc = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True,
                          text=True, timeout=300,
                          env=dict(os.environ, TDQ_LOG="0", **(env or {})))
    return proc.returncode, proc.stdout, proc.stderr


class KhoTest(unittest.TestCase):
    """Kho phải khớp inventory, nếu không thì router đang tra trên tập skill sai."""

    def test_kho_da_dung_va_du_bon_truong(self):
        ban_ghi = skill_router.doc_kho()
        self.assertGreater(len(ban_ghi), 100)
        for b in ban_ghi[:50]:
            with self.subTest(ten=b.get("ten")):
                for t in skill_router.TRUONG:
                    self.assertIn(t, b)

    def test_so_ban_ghi_khop_skill_inventory(self):
        import skill_inventory
        self.assertEqual(len(skill_router.doc_kho()),
                         len(skill_inventory.inventory(ROOT)))

    def test_moi_ban_ghi_deu_co_duong_dan(self):
        """Spec §6 Q15 đòi "mọi duong_dan mở được" — bản ghi rỗng KHÔNG đạt.

        Bản đầu tra bảng bằng tên thư mục nên 10/284 skill không dò ra SKILL.md, vì
        tên khai khác tên thư mục (`canva-brand-check` ở thư mục `brand-check/`,
        `unity-mcp-orchestrator` ở `unity-mcp-skill/`) và một skill khai tên kèm dấu
        nháy kép. Cái giá không phải là thiếu một dòng log: mọi kiến trúc "giấu mô tả
        rồi đọc thẳng SKILL.md khi cần" đều mù với đúng 10 skill đó, im lặng.
        """
        rong = [b["ten"] for b in skill_router.doc_kho() if not b["duong_dan"]]
        self.assertEqual(rong, [], f"{len(rong)} bản ghi không có đường dẫn")

    def test_moi_duong_dan_khac_rong_deu_mo_duoc(self):
        for b in skill_router.doc_kho():
            if b["duong_dan"]:
                with self.subTest(ten=b["ten"]):
                    duong = b["duong_dan"]
                    if not os.path.isabs(duong):
                        duong = os.path.join(ROOT, duong)
                    self.assertTrue(os.path.exists(duong))

    def test_kho_thieu_thi_bao_loi_kem_lenh_dung_lai(self):
        rc, out, err = chay("--tra", "bất kỳ",
                            env={"TDQ_ROUTER_KHO": "/khong/he/co.json"})
        # Biến môi trường trên chưa được hỗ trợ; đường chắc chắn của ca này là gọi
        # thẳng `doc_kho` với đường dẫn không tồn tại trong tiến trình con.
        rc2 = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, %r); import skill_router;"
             "skill_router.doc_kho('/khong/he/co.json')" % os.path.join(ROOT, "scripts")],
            capture_output=True, text=True, timeout=120,
            env=dict(os.environ, TDQ_LOG="0"))
        self.assertEqual(rc2.returncode, skill_router.EXIT_THIEU_KHO)
        self.assertIn("--dung-kho", rc2.stderr)
        del rc, out, err


class TachTuTest(unittest.TestCase):
    """Chuẩn hoá từ — cùng một hàm cho lúc dựng kho và lúc tra, nếu không thì lệch."""

    def test_bo_dau_tieng_viet(self):
        self.assertEqual(skill_router.tach_tu("Thời Gian"), ["thoi", "gian"])

    def test_chu_d_gach_ngang_ve_d_thuong(self):
        self.assertIn("dong", skill_router.tach_tu("đóng"))

    def test_bo_dau_cau_va_giu_so(self):
        self.assertEqual(skill_router.tach_tu("unity-3d, shader!"),
                         ["unity", "3d", "shader"])


class TraTest(unittest.TestCase):
    """Hành vi tra: offline, có thứ tự điểm, không văng khi không khớp gì."""

    def test_tra_chay_duoc_khi_khong_co_bien_api_key(self):
        sach = {k: "" for k in os.environ
                if "API_KEY" in k.upper() or "TOKEN" in k.upper()}
        rc, out, _err = chay("--tra", "sửa lỗi unity shader", env=sach)
        self.assertEqual(rc, 0)
        self.assertIn("unity", out)

    def test_diem_giam_dan(self):
        kho = skill_router.KhoBM25(skill_router.doc_kho())
        diem = [d for d, _ in kho.tra("viết spec cho request mới", 5)]
        self.assertEqual(diem, sorted(diem, reverse=True))

    def test_cau_khong_khop_gi_thi_bao_khong_co_chu_khong_van(self):
        rc, out, _err = chay("--tra", "zzzqqqxxx")
        self.assertEqual(rc, 0)
        self.assertIn("No skill matches", out)

    def test_hai_co_cung_luc_bi_tu_choi(self):
        rc, _out, err = chay("--dung-kho", "--tra", "x")
        self.assertEqual(rc, 2)
        self.assertIn("--dung-kho", err)


class TiLeTrungTest(unittest.TestCase):
    """Con số quyết định hướng E có đáng làm hay không."""

    @classmethod
    def setUpClass(cls):
        cls.kho = skill_router.KhoBM25(skill_router.doc_kho())
        cls.co_that = {b["ten"] for b in cls.kho.ban_ghi}

    def _ket_qua(self, k):
        trung = []
        for prompt, dung, do_kho in MAU:
            ten = [b["ten"] for _d, b in self.kho.tra(prompt, k)]
            trung.append((prompt, dung, do_kho, any(d in ten for d in dung), ten))
        return trung

    def test_moi_skill_dung_trong_bo_mau_deu_co_that_trong_kho(self):
        """Đặt đáp án là skill không tồn tại thì tỉ lệ trúng tự động đẹp lên vì
        chẳng bao giờ so được — phải chặn ngay từ đây."""
        for _prompt, dung, _do_kho in MAU:
            for d in dung:
                with self.subTest(skill=d):
                    self.assertIn(d, self.co_that)

    def test_khong_prompt_nao_duoc_nhieu_hon_hai_dap_an(self):
        """Chặn đường nới tuple cho tới khi trúng: nới rộng là lách, không phải đo."""
        for prompt, dung, _do_kho in MAU:
            with self.subTest(prompt=prompt):
                self.assertLessEqual(len(dung), 2)

    def test_bo_mau_du_20_prompt_va_du_ba_do_kho(self):
        self.assertGreaterEqual(len(MAU), 20)
        for muc in ("dễ", "vừa", "khó"):
            self.assertGreaterEqual(sum(1 for m in MAU if m[2] == muc), 3)

    def test_in_ti_le_trung_top_1_va_top_5(self):
        """Test này LUÔN xanh — nó công bố số, không phán quyết. Ngưỡng nằm ở
        `test_bao_cao_phai_khuyen_nghi_dung_neu_top5_duoi_90`."""
        top1 = self._ket_qua(1)
        top5 = self._ket_qua(5)
        t1 = sum(1 for r in top1 if r[3]) / len(top1) * 100
        t5 = sum(1 for r in top5 if r[3]) / len(top5) * 100
        theo_kho = {}
        for _p, _d, do_kho, ok, _ten in top5:
            o = theo_kho.setdefault(do_kho, [0, 0])
            o[0] += int(ok)
            o[1] += 1
        print(f"\nTỈ LỆ TRÚNG trên {len(MAU)} prompt mẫu: "
              f"top-1 = {t1:.1f}% · top-5 = {t5:.1f}%")
        for muc in ("dễ", "vừa", "khó"):
            if muc in theo_kho:
                dung, tong = theo_kho[muc]
                print(f"  top-5 nhóm {muc}: {dung}/{tong} = {dung / tong * 100:.1f}%")
        truot = [r[0] for r in top5 if not r[3]]
        if truot:
            print(f"  TRƯỢT top-5 ({len(truot)}): " + " · ".join(truot))
        self.assertGreaterEqual(t5, t1, "top-5 không thể tệ hơn top-1")

    def test_hoi_tieng_anh_trung_han_hoi_tieng_viet_cung_mot_y(self):
        """Bằng chứng cho nguyên nhân gốc, không phải để router đẹp lên.

        Cùng MỘT ý định, hỏi hai thứ tiếng. Kho mô tả gần như toàn tiếng Anh, nên
        nếu tiếng Anh trúng mà tiếng Việt trượt thì cái hỏng KHÔNG phải BM25 — là
        khoảng cách ngôn ngữ giữa câu hỏi và mô tả. Số này quyết định câu khuyến
        nghị ở đề án: router từ khoá không phục vụ được user gõ tiếng Việt.
        """
        cap = [
            ("mọi thứ trông lệch nhau, không thẳng hàng",
             "elements are misaligned, fix the visual layout", "frontend-design"),
            ("nhân vật trong game đi xuyên tường",
             "game character passes through walls, collision bug", "unity-patterns"),
            ("kiểm tra chất lượng code trước khi merge",
             "check code quality gate before merging", "sonar-quality-gate"),
            ("nghiên cứu sâu một chủ đề trên web rồi tổng hợp",
             "deep research a topic on the web and synthesize", "tavily-research"),
        ]
        viet = anh = 0
        for cau_viet, cau_anh, dung in cap:
            tv = dung in [b["ten"] for _d, b in self.kho.tra(cau_viet, 5)]
            ta = dung in [b["ten"] for _d, b in self.kho.tra(cau_anh, 5)]
            viet += tv
            anh += ta
            print(f"  {dung}: VI={'trúng' if tv else 'TRƯỢT'} · "
                  f"EN={'trúng' if ta else 'TRƯỢT'}")
        print(f"CÙNG Ý ĐỊNH, {len(cap)} cặp — top-5 tiếng Việt {viet}/{len(cap)} · "
              f"tiếng Anh {anh}/{len(cap)}")
        self.assertGreater(anh, viet,
                           "nếu hai thứ tiếng ngang nhau thì nguyên nhân gốc là thứ "
                           "khác, phải đi tìm lại chứ không được kết luận vội")

    def test_nhom_de_phai_gan_nhu_trung_het(self):
        """Prompt nhắc thẳng tên công cụ mà còn trượt thì BM25 hỏng, không phải khó."""
        de = [r for r in self._ket_qua(5) if r[2] == "dễ"]
        ti_le = sum(1 for r in de if r[3]) / len(de) * 100
        self.assertGreaterEqual(ti_le, 80.0,
                                f"nhóm dễ chỉ trúng {ti_le:.1f}% — chỉ mục có vấn đề")


if __name__ == "__main__":
    unittest.main()
