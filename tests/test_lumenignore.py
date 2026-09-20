""".lumenignore — keep the generated bundle copies out of the semantic index.

Why it is worth a test rather than just a file: the three portable bundles are generated copies
of `scripts/`, `hooks/`, `skills/` and `agents/`, so every chunk of real source exists three or
four times on disk. Measured before this file existed, a search for the code that stamps the
approval time could not put `scripts/tdq_state.py` in the top 8 — duplicates held the slots.
With the bundles excluded the same query ranks it 1st.

The failure mode this guards is silent: someone adds a fourth bundle, or renames one, and
search quality decays with nothing going red. So the list is checked against the directories
that actually exist, not against a hard-coded copy of itself.
"""
import io
import os
import unittest

from helper import ROOT

LUMENIGNORE = os.path.join(ROOT, ".lumenignore")
# A generated tree is one that `build_portable.py` writes. Its marker: it holds a copy of
# `scripts/tdq_state.py`, the file every bundle carries.
DAU_HIEU_BUNDLE = os.path.join("scripts", "tdq_state.py")


def dong_hieu_luc():
    """The ignore patterns, without comments and blank lines."""
    with io.open(LUMENIGNORE, encoding="utf-8") as f:
        return [d.strip() for d in f
                if d.strip() and not d.lstrip().startswith("#")]


def thu_muc_ban_sao():
    """Every top-level directory holding its own copy of scripts/tdq_state.py."""
    ra = []
    for ten in sorted(os.listdir(ROOT)):
        duong = os.path.join(ROOT, ten)
        if not os.path.isdir(duong) or ten.startswith("."):
            continue
        if os.path.exists(os.path.join(duong, DAU_HIEU_BUNDLE)):
            ra.append(ten)
        # antigravity_portable keeps its copy one level down.
        elif any(os.path.exists(os.path.join(duong, con, DAU_HIEU_BUNDLE))
                 for con in os.listdir(duong)
                 if os.path.isdir(os.path.join(duong, con))):
            ra.append(ten)
    return ra


class LumenIgnoreTest(unittest.TestCase):
    def test_file_ton_tai(self):
        self.assertTrue(os.path.exists(LUMENIGNORE),
                        ".lumenignore is missing — every lumen search goes back to seeing "
                        "each source file three or four times")

    def test_moi_bundle_sinh_ra_deu_bi_loai(self):
        """The real invariant: a new bundle must not silently start polluting the index."""
        bo_qua = {d.rstrip("/") for d in dong_hieu_luc()}
        thieu = [t for t in thu_muc_ban_sao() if t not in bo_qua]
        self.assertEqual(thieu, [],
                         f"these generated copies are still indexed: {thieu}")

    def test_co_du_ba_bundle_hien_tai(self):
        bo_qua = {d.rstrip("/") for d in dong_hieu_luc()}
        for ten in ("portable_claude", "portable_codex", "antigravity_portable"):
            with self.subTest(ten=ten):
                self.assertIn(ten, bo_qua)

    def test_khong_loai_nham_thu_muc_nguon(self):
        """Excluding the source itself would turn the whole layer off."""
        bo_qua = {d.rstrip("/") for d in dong_hieu_luc()}
        for ten in ("scripts", "hooks", "skills", "agents", "tests", "docs"):
            with self.subTest(ten=ten):
                self.assertNotIn(ten, bo_qua)


if __name__ == "__main__":
    unittest.main()
