"""Luật "luôn ưu tiên sub-agent chạy song song" — đo trên plan THẬT, không trên fixture.

Vì sao cần file riêng: các test khác khoá HÌNH DẠNG của luật (có mục gì, có dòng gì).
File này khoá HIỆU QUẢ — số đợt của lịch trình mới không được tệ hơn bản cũ trên chính
những plan đã viết trong repo. Luật chia đợt trôi về cũ mà vẫn xanh thì bộ luật vô nghĩa.
"""
import os
import unittest

from helper import ROOT
import tdq_team

PLAN_DIR = os.path.join(ROOT, "docs", "tdq", "plan")


# Bốn plan làm mẫu đo, GHIM theo tên chứ không lấy "mới nhất": lấy động thì mỗi
# request sau lại đổi tập đo, test đỏ dù code không hỏng. Đổi tập này là việc có ý
# thức — sửa tên ở đây rồi đo lại, đừng để thời gian tự sửa hộ.
PLAN_MAU = (
    "2026-08-17-1828-subagent-team-implement.md",
    "2026-08-17-2001-smoke-test-main-vs-doi.md",
    "2026-08-17-2121-toi-uu-context-workflow.md",
    "2026-08-18-1744-uu-tien-subagent-song-song.md",
)


def _plan_that():
    """Đường dẫn 4 plan mẫu. Thiếu file nào là lỗi thật, không im lặng bỏ qua."""
    duong = [os.path.join(PLAN_DIR, ten) for ten in PLAN_MAU]
    thieu = [d for d in duong if not os.path.isfile(d)]
    assert not thieu, f"thiếu plan mẫu: {thieu}"
    return duong


def _so_dot(dot_theo_task):
    return max(dot_theo_task.values()) if dot_theo_task else 0


TEAM_MODE = os.path.join(ROOT, "skills", "tdq-build", "references", "team-mode.md")


def _team_mode():
    with open(TEAM_MODE, encoding="utf-8") as f:
        return f.read()


class LyDoBangTest(unittest.TestCase):
    """T4.3 — bảng lý do giữ task trong file luật phải khớp tập đóng trong code."""

    def test_ly_do_bang_du_moi_nhom_cua_code(self):
        noi_dung = _team_mode()
        for ma in tdq_team.LY_DO_GIU:
            with self.subTest(nhom=ma):
                self.assertIn(f"`{ma}`", noi_dung, f"bảng thiếu nhóm {ma}")

    def test_ly_do_bang_dung_so_dong(self):
        dong = [d for d in _team_mode().splitlines() if d.strip().startswith("| `")]
        self.assertEqual(len(dong), len(tdq_team.LY_DO_GIU))

    def test_ly_do_bang_hop_dong_co_vi_du_dung_va_sai(self):
        khoi = _team_mode().split("Hợp đồng dùng chung")
        self.assertGreater(len(khoi), 1, "thiếu ví dụ cho nhóm hop-dong")
        than = khoi[1].split("\n\n")[0] + khoi[1].split("\n\n")[1]
        self.assertIn("ĐÚNG", than)
        self.assertIn("SAI", than)


class RanhGioiTest(unittest.TestCase):
    """T4.4 — khuôn prompt giao việc: 9 trường, có ranh giới ba tầng và lệnh tự kiểm."""

    def test_ranh_gioi_khuon_du_chin_truong(self):
        noi_dung = _team_mode()
        for truong in ("TASK:", "CỤM:", "BASE:", "WORKTREE:", "VÙNG FILE:", "TEST:",
                       "TRẢ VỀ:", "RANH GIỚI:", "TỰ KIỂM:"):
            with self.subTest(truong=truong):
                self.assertIn(truong, noi_dung, f"khuôn prompt thiếu trường {truong}")

    def test_ranh_gioi_du_ba_tang(self):
        than = _team_mode().split("RANH GIỚI:")[1].split("TỰ KIỂM:")[0]
        for tang in ("luôn được làm", "hỏi trước", "cấm"):
            with self.subTest(tang=tang):
                self.assertIn(tang, than.lower(), f"ranh giới thiếu tầng \"{tang}\"")

    def test_ranh_gioi_tu_kiem_la_mot_lenh(self):
        dong = _team_mode().split("TỰ KIỂM:")[1].split("\n")[0]
        self.assertTrue(dong.strip(), "trường TỰ KIỂM rỗng")


class LuatKhopTest(unittest.TestCase):
    """QC1.3 — luật nằm rải ở nhiều file thì phải khớp nhau, không được đá nhau.

    Model đọc `tdq-build/SKILL.md` trước `references/team-mode.md`; hai chỗ nói khác
    nhau thì luật ở file được đọc trước thắng, và bản vá coi như không tồn tại.
    """

    FILE_NHAC_NHOM = (
        os.path.join(ROOT, "skills", "tdq-build", "SKILL.md"),
        os.path.join(ROOT, "skills", "tdq-plan", "references", "mode-gate.md"),
        os.path.join(ROOT, "skills", "tdq-build", "references", "team-mode.md"),
        os.path.join(ROOT, "hooks", "scripts", "edit_gate.py"),
    )

    def _doc(self, path):
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_luat_khop_khong_con_con_so_4_nhom(self):
        for path in self.FILE_NHAC_NHOM:
            with self.subTest(file=os.path.basename(path)):
                noi_dung = self._doc(path)
                for cam in ("4 nhóm", "bốn nhóm", "lý do thứ năm"):
                    self.assertNotIn(cam, noi_dung,
                                     f"{path} còn chốt cứng số nhóm cũ: {cam}")

    def test_luat_khop_mode_gate_liet_ke_du_nhom(self):
        noi_dung = self._doc(os.path.join(ROOT, "skills", "tdq-plan", "references",
                                          "mode-gate.md"))
        for ma in tdq_team.LY_DO_GIU:
            with self.subTest(nhom=ma):
                self.assertIn(f"`{ma}`", noi_dung)

    def test_luat_khop_khuon_prompt_dung_so_truong(self):
        for path in self.FILE_NHAC_NHOM[:3]:
            with self.subTest(file=os.path.basename(path)):
                self.assertNotIn("7 trường", self._doc(path),
                                 f"{path} còn nói khuôn prompt 7 trường")

    def test_luat_khop_mode_main_cung_nap_doctrine(self):
        """Đầu ra §2-10: doctrine leader áp cả mode `main`, không chỉ nhánh subagent."""
        than = self._doc(os.path.join(ROOT, "skills", "tdq-build", "SKILL.md"))
        nhanh_main = than.split("`main`")[1].split("`subagent`")[0]
        self.assertIn("team-mode.md", nhanh_main,
                      "nhánh mode `main` không trỏ tới doctrine leader")


class SoDotTest(unittest.TestCase):
    """T3.7 — số đợt sau khi sửa phải nhỏ hơn hoặc bằng bản cũ, trên 4 plan thật."""

    def test_so_dot_khong_tang_tren_plan_that(self):
        for duong in _plan_that():
            with self.subTest(plan=os.path.basename(duong)):
                tasks = tdq_team.doc_plan(duong)
                self.assertTrue(tasks, "plan không đọc ra task nào")
                cu = _so_dot(tdq_team._chia_dot_theo_phase(tasks))
                quyet = {t.ma: tdq_team.quyet_dinh_task(t, tasks) for t in tasks}
                moi = _so_dot(tdq_team.chia_dot(tasks, quyet))
                self.assertLessEqual(moi, cu, f"số đợt tăng: cũ {cu} → mới {moi}")

    def test_so_dot_giam_that_o_it_nhat_mot_plan(self):
        """Không đủ: "không tệ hơn" cũng đúng khi lịch trình mới chẳng làm gì cả."""
        giam = []
        for duong in _plan_that():
            tasks = tdq_team.doc_plan(duong)
            cu = _so_dot(tdq_team._chia_dot_theo_phase(tasks))
            quyet = {t.ma: tdq_team.quyet_dinh_task(t, tasks) for t in tasks}
            moi = _so_dot(tdq_team.chia_dot(tasks, quyet))
            if moi < cu:
                giam.append(f"{os.path.basename(duong)}: {cu} → {moi}")
        self.assertTrue(giam, "không plan nào giảm số đợt — lịch trình mới không ăn gì")

    def test_so_dot_moi_task_deu_co_dot(self):
        for duong in _plan_that():
            with self.subTest(plan=os.path.basename(duong)):
                tasks = tdq_team.doc_plan(duong)
                quyet = {t.ma: tdq_team.quyet_dinh_task(t, tasks) for t in tasks}
                dot = tdq_team.chia_dot(tasks, quyet)
                self.assertEqual(set(dot), {t.ma for t in tasks})


if __name__ == "__main__":
    unittest.main()
