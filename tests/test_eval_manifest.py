#!/usr/bin/env python3
"""Tests for evaluation manifest identity, append-only rescore, and preflight mock (O11 / T3.3).

Covers:
1. Manifest base/candidate/corpus/scorer/permission identity validation and paired experiment invariant.
2. Rescore append-only: new versioned record pointing to raw trace, zero historical overwrite,
   deterministic identical verdicts on same trace + manifest.
3. Preflight mock: zero API/model/Keychain calls in offline mode, environment isolation verification,
   defensive platform checks without secret store scanning.
"""
import json
import os
import sys
import tempfile
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(GOC, "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import tdq_eval


class TestEvalManifestIdentity(unittest.TestCase):
    """Kiểm tra cấu trúc và tính toàn vẹn của Manifest evaluation (O11)."""

    def test_tao_manifest_hop_le(self):
        """Tạo manifest hợp lệ với đầy đủ các trường bắt buộc."""
        manifest = tdq_eval.tao_manifest_eval(
            base_commit="ea0cdbd",
            candidate_commit="f620094",
            corpus_version="tuan-thu-v1",
            check_set=["L001", "L002", "L003"],
            scorer_version="v2-temporal",
            permission_profile="offline-mock",
            is_offline=True,
        )
        self.assertEqual(manifest["phien_ban"], "v1")
        self.assertEqual(manifest["base_commit"], "ea0cdbd")
        self.assertEqual(manifest["candidate_commit"], "f620094")
        self.assertEqual(manifest["corpus_version"], "tuan-thu-v1")
        self.assertEqual(manifest["check_set"], ["L001", "L002", "L003"])
        self.assertEqual(manifest["scorer_version"], "v2-temporal")
        self.assertEqual(manifest["permission_profile"], "offline-mock")
        self.assertTrue(manifest["is_offline"])
        self.assertIn("tool_aliases", manifest)
        self.assertIn("shell", manifest["tool_aliases"])

    def test_xac_thuc_manifest_tu_choi_thieu_truong(self):
        """Từ chối manifest khi thiếu một trong các trường bắt buộc."""
        manifest = {
            "phien_ban": "v1",
            "base_commit": "ea0cdbd",
            # thiếu candidate_commit
            "corpus_version": "tuan-thu-v1",
            "check_set": ["L001"],
            "scorer_version": "v2-temporal",
            "permission_profile": "offline-mock",
            "is_offline": True,
        }
        hop_le, ly_do = tdq_eval.xac_thuc_manifest(manifest)
        self.assertFalse(hop_le)
        self.assertIn("candidate_commit", ly_do)

    def test_xac_thuc_manifest_tu_choi_sai_kieu(self):
        """Từ chối manifest khi các trường sai kiểu dữ liệu."""
        # check_set không phải list
        m1 = {
            "phien_ban": "v1",
            "base_commit": "ea0cdbd",
            "candidate_commit": "f620094",
            "corpus_version": "tuan-thu-v1",
            "check_set": "L001,L002",
            "scorer_version": "v2-temporal",
            "permission_profile": "offline-mock",
            "is_offline": True,
        }
        hop_le, ly_do = tdq_eval.xac_thuc_manifest(m1)
        self.assertFalse(hop_le)
        self.assertIn("check_set", ly_do)

        # base_commit rỗng
        m2 = dict(m1, check_set=["L001"], base_commit="   ")
        hop_le, ly_do = tdq_eval.xac_thuc_manifest(m2)
        self.assertFalse(hop_le)
        self.assertIn("base_commit", ly_do)

        # is_offline không phải bool
        m3 = dict(m1, check_set=["L001"], is_offline="true")
        hop_le, ly_do = tdq_eval.xac_thuc_manifest(m3)
        self.assertFalse(hop_le)
        self.assertIn("is_offline", ly_do)

    def test_xac_thuc_manifest_tu_choi_phien_ban_la(self):
        """Từ chối manifest có phiên bản không hỗ trợ (ví dụ v999)."""
        m = {
            "phien_ban": "v999",
            "base_commit": "ea0cdbd",
            "candidate_commit": "f620094",
            "corpus_version": "tuan-thu-v1",
            "check_set": ["L001"],
            "scorer_version": "v2-temporal",
            "permission_profile": "offline-mock",
            "is_offline": True,
        }
        hop_le, ly_do = tdq_eval.xac_thuc_manifest(m)
        self.assertFalse(hop_le)
        self.assertIn("Unsupported manifest version", ly_do)

    def test_manifest_offline_khong_gia_co_model_run(self):
        """Manifest offline từ chối khai báo model live (offline không giả có model run)."""
        m = {
            "phien_ban": "v1",
            "base_commit": "ea0cdbd",
            "candidate_commit": "f620094",
            "corpus_version": "tuan-thu-v1",
            "check_set": ["L001"],
            "scorer_version": "v2-temporal",
            "permission_profile": "offline-mock",
            "is_offline": True,
            "model": "claude-opus-5",  # không được phép khi offline
        }
        hop_le, ly_do = tdq_eval.xac_thuc_manifest(m)
        self.assertFalse(hop_le)
        self.assertIn("Offline manifest cannot declare live model", ly_do)

    def test_kiem_tra_paired_experiment_cung_corpus_va_check_set(self):
        """Base và candidate cùng corpus và check_set được chấp nhận là paired experiment."""
        m_base = tdq_eval.tao_manifest_eval(
            base_commit="ea0cdbd", candidate_commit="ea0cdbd",
            corpus_version="tuan-thu-v1", check_set=["L001", "L002"],
        )
        m_cand = tdq_eval.tao_manifest_eval(
            base_commit="f620094", candidate_commit="f620094",
            corpus_version="tuan-thu-v1", check_set=["L001", "L002"],
        )
        hop_le, ly_do = tdq_eval.kiem_tra_paired_experiment(m_base, m_cand)
        self.assertTrue(hop_le, f"Lẽ ra hợp lệ: {ly_do}")

    def test_kiem_tra_paired_experiment_khac_corpus_tu_choi(self):
        """Base và candidate khác corpus bị từ chối, không được gọi là paired experiment."""
        m_base = tdq_eval.tao_manifest_eval(
            base_commit="ea0cdbd", candidate_commit="ea0cdbd",
            corpus_version="corpus-cu", check_set=["L001"],
        )
        m_cand = tdq_eval.tao_manifest_eval(
            base_commit="f620094", candidate_commit="f620094",
            corpus_version="corpus-moi", check_set=["L001"],
        )
        hop_le, ly_do = tdq_eval.kiem_tra_paired_experiment(m_base, m_cand)
        self.assertFalse(hop_le)
        self.assertIn("Different corpus", ly_do)

    def test_kiem_tra_paired_experiment_khac_check_set_tu_choi(self):
        """Base và candidate khác check_set bị từ chối, không được coi là paired experiment."""
        m_base = tdq_eval.tao_manifest_eval(
            base_commit="ea0cdbd", candidate_commit="ea0cdbd",
            corpus_version="tuan-thu-v1", check_set=["L001"],
        )
        m_cand = tdq_eval.tao_manifest_eval(
            base_commit="f620094", candidate_commit="f620094",
            corpus_version="tuan-thu-v1", check_set=["L001", "L002"],
        )
        hop_le, ly_do = tdq_eval.kiem_tra_paired_experiment(m_base, m_cand)
        self.assertFalse(hop_le)
        self.assertIn("Different check_set", ly_do)


class TestRescoreAppendOnly(unittest.TestCase):
    """Kiểm tra cơ chế rescore append-only, zero overwrite và provenance (O11)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.thu_muc = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

        # Tạo transcript mẫu hợp lệ
        self.transcript_path = os.path.join(self.thu_muc, "transcript.jsonl")
        su_kien = [
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "bat dau"}]}},
            {"type": "user", "message": {"content": [{"type": "text", "text": "lenh user"}]}},
            {"type": "result", "result": "PASS", "total_cost_usd": 0.05, "num_turns": 3},
        ]
        with open(self.transcript_path, "w", encoding="utf-8") as f:
            for e in su_kien:
                f.write(json.dumps(e) + "\n")

        # Tạo bản ghi gốc ban đầu
        self.ban_ghi_goc = {
            "ca": "T01_brief_truoc",
            "nhanh": "viet",
            "lan": 1,
            "trang_thai": "xong",
            "transcript": self.transcript_path,
            "ma_thoat": 0,
            "chi_phi": 0.05,
            "so_luot": 3,
            "ket_qua": {"L001": "dat"},
            "kiem": ["L001"],
            "nhiem": [],
        }
        self.file_goc = os.path.join(self.thu_muc, "T01_brief_truoc__viet__1.json")
        with open(self.file_goc, "w", encoding="utf-8") as f:
            json.dump(self.ban_ghi_goc, f, ensure_ascii=False, indent=2)

    def test_rescore_append_only_tao_file_moi_va_khong_overwrite_file_cu(self):
        """Rescore append-only tạo file v2 mới, trỏ raw trace và giữ nguyên 100% file gốc."""
        # Lưu nội dung và mtime file gốc trước khi rescore
        with open(self.file_goc, "rb") as f:
            noi_dung_goc = f.read()

        manifest = tdq_eval.tao_manifest_eval(
            base_commit="ea0cdbd", candidate_commit="f620094",
            corpus_version="tuan-thu-v1", check_set=["L001"],
            scorer_version="v2-temporal",
        )

        xong, bo_qua = tdq_eval.rescore_append_only(
            self.thu_muc, phien_ban=2, manifest=manifest
        )
        self.assertEqual(len(xong), 1)
        self.assertEqual(len(bo_qua), 0)

        # 1. File gốc phải nguyên vẹn hoàn toàn
        with open(self.file_goc, "rb") as f:
            noi_dung_sau = f.read()
        self.assertEqual(noi_dung_goc, noi_dung_sau, "File bản ghi gốc bị sửa đổi!")

        # 2. File mới v2 phải tồn tại với tên T01_brief_truoc__viet__1__v2.json
        file_v2 = os.path.join(self.thu_muc, "T01_brief_truoc__viet__1__v2.json")
        self.assertTrue(os.path.exists(file_v2), "File rescore v2 không được tạo!")

        with open(file_v2, encoding="utf-8") as f:
            ban_ghi_v2 = json.load(f)

        # 3. Kiểm tra các trường provenance & identity của bản ghi mới
        self.assertEqual(ban_ghi_v2["rescore_version"], 2)
        self.assertEqual(ban_ghi_v2["ban_ghi_goc"], "T01_brief_truoc__viet__1.json")
        self.assertEqual(os.path.abspath(ban_ghi_v2["raw_trace"]), os.path.abspath(self.transcript_path))
        self.assertEqual(ban_ghi_v2["scorer_identity"], "v2-temporal")
        self.assertEqual(ban_ghi_v2["manifest_identity"], "v1")
        self.assertIn("thoi_gian_rescore", ban_ghi_v2)

        # 4. Các phép đo gốc (chi_phi, so_luot, ma_thoat) được bảo toàn
        self.assertEqual(ban_ghi_v2["chi_phi"], 0.05)
        self.assertEqual(ban_ghi_v2["so_luot"], 3)
        self.assertEqual(ban_ghi_v2["ma_thoat"], 0)

    def test_rescore_deterministic_cung_trace_cung_manifest(self):
        """Cùng raw trace và cùng manifest cho kết quả verdict giống hệt nhau (deterministic)."""
        manifest = tdq_eval.tao_manifest_eval(
            base_commit="ea0cdbd", candidate_commit="f620094",
            corpus_version="tuan-thu-v1", check_set=["L001"],
            scorer_version="v2-temporal",
        )

        tmp2 = tempfile.TemporaryDirectory()
        self.addCleanup(tmp2.cleanup)

        # Lần 1 vào self.thu_muc
        tdq_eval.rescore_append_only(self.thu_muc, phien_ban=2, manifest=manifest)
        # Lần 2 vào tmp2.name
        tdq_eval.rescore_append_only(self.thu_muc, thu_muc_dich=tmp2.name, phien_ban=3, manifest=manifest)

        f1 = os.path.join(self.thu_muc, "T01_brief_truoc__viet__1__v2.json")
        f2 = os.path.join(tmp2.name, "T01_brief_truoc__viet__1__v3.json")

        with open(f1, encoding="utf-8") as f:
            v1 = json.load(f)
        with open(f2, encoding="utf-8") as f:
            v2 = json.load(f)

        # Kết quả chấm điểm ket_qua phải giống nhau hoàn toàn
        self.assertEqual(v1["ket_qua"], v2["ket_qua"])

    def test_rescore_bo_qua_file_khong_hop_le_an_toan(self):
        """File json hỏng hoặc transcript không tồn tại được bỏ qua an toàn mà không crash."""
        file_hong = os.path.join(self.thu_muc, "T02__viet__1.json")
        with open(file_hong, "w", encoding="utf-8") as f:
            f.write("{ invalid json")

        file_thieu_tr = os.path.join(self.thu_muc, "T03__viet__1.json")
        with open(file_thieu_tr, "w", encoding="utf-8") as f:
            json.dump({
                "ca": "T01_brief_truoc", "nhanh": "viet", "lan": 1,
                "transcript": os.path.join(self.thu_muc, "khong_co.jsonl"),
            }, f)

        xong, bo_qua = tdq_eval.rescore_append_only(self.thu_muc, phien_ban=2)
        # 1 file gốc hợp lệ hoàn tất, 2 file lỗi bị bỏ qua
        self.assertEqual(len(xong), 1)
        self.assertEqual(len(bo_qua), 2)


class TestPreflightMockAndIsolation(unittest.TestCase):
    """Kiểm tra preflight mock, không đọc secret store, và xác thực cách ly môi trường (O11)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_preflight_offline_khong_goi_keychain_hay_api(self):
        """Chế độ offline không truy cập Keychain, API, hay model."""
        ket_qua = tdq_eval.kiem_tra_preflight(che_do="offline")
        self.assertTrue(ket_qua["san_sang"])
        self.assertEqual(ket_qua["che_do"], "offline")
        self.assertEqual(ket_qua["api_model"], "tat")
        self.assertIn("offline-mock", ket_qua["credential_source"])

    def test_preflight_xac_thuc_isolation_moi_truong(self):
        """Xác thực cách ly CLAUDE_CONFIG_DIR, CLAUDE_PLUGIN_ROOT, và HOME."""
        cfg_rieng = os.path.join(self.tmp.name, "custom_cfg")
        plugin_rieng = os.path.join(self.tmp.name, "custom_plugin")
        home_rieng = os.path.join(self.tmp.name, "custom_home")
        hop_rieng = os.path.join(self.tmp.name, "custom_sandbox")

        for d in (cfg_rieng, plugin_rieng, home_rieng, hop_rieng):
            os.makedirs(d, exist_ok=True)

        ket_qua = tdq_eval.kiem_tra_preflight(
            che_do="offline",
            cau_hinh=cfg_rieng,
            plugin_dir=plugin_rieng,
            nha=home_rieng,
            hop=hop_rieng,
        )
        self.assertTrue(ket_qua["isolation"]["cau_hinh_rieng"])
        self.assertTrue(ket_qua["isolation"]["plugin_rieng"])
        self.assertTrue(ket_qua["isolation"]["nha_rieng"])
        self.assertTrue(ket_qua["isolation"]["hop_rieng"])

    def test_preflight_live_tren_non_darwin_khong_token(self):
        """Ở chế độ live trên hệ điều hành không phải Darwin khi không có token thì báo không sẵn sàng."""
        ket_qua = tdq_eval.kiem_tra_preflight(che_do="live", token=None)
        if sys.platform != "darwin":
            self.assertFalse(ket_qua["san_sang"])
            self.assertIn("Credential source unavailable on this platform", ket_qua["ly_do"])

    def test_lay_token_phong_thu_non_darwin(self):
        """lay_token() từ chối trên non-Darwin với thông báo rõ ràng, không crash unhandled."""
        if sys.platform != "darwin":
            with self.assertRaises(tdq_eval.LoiThieuSo) as ctx:
                tdq_eval.lay_token()
            self.assertIn("non-macOS platform", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
