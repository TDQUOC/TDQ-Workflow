"""Unit tests for scripts/tdq_vision_diff.py (Vision Test Loop CLI and image diff engine)."""
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import tdq_vision_diff  # noqa: E402


def _make_solid_image(width: int, height: int, color: tuple[int, int, int, int]) -> Image.Image:
    """Create a solid RGBA image for testing."""
    return Image.new("RGBA", (width, height), color)


class VisionDiffUnitTests(unittest.TestCase):
    """Test suite covering canvas normalization, masking, bounding boxes, reports, Figma, and logging."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_normalize_canvas_no_distortion(self) -> None:
        """Two images with different dimensions are padded onto a shared canvas without stretching pixels."""
        src = _make_solid_image(100, 80, (20, 40, 60, 255))
        src.putpixel((99, 79), (250, 10, 10, 255))
        dist = _make_solid_image(140, 120, (20, 40, 60, 255))

        src_norm, dist_norm = tdq_vision_diff.normalize_canvas(src, dist, fill_color=(0, 0, 0, 0))

        self.assertEqual(src_norm.size, (140, 120))
        self.assertEqual(dist_norm.size, (140, 120))
        # Original pixel at (99, 79) must remain at (99, 79), proving no resize distortion occurred.
        self.assertEqual(src_norm.getpixel((99, 79)), (250, 10, 10, 255))
        # Padded region outside original (100, 80) must equal fill_color.
        self.assertEqual(src_norm.getpixel((100, 80)), (0, 0, 0, 0))
        self.assertEqual(src_norm.getpixel((139, 119)), (0, 0, 0, 0))

    def test_ignore_boxes_masking(self) -> None:
        """Dynamic regions listed in --ignore-boxes are masked out so mismatch_rate becomes 0.0."""
        src = _make_solid_image(120, 100, (240, 240, 240, 255))
        dist = src.copy()
        draw = ImageDraw.Draw(dist)
        # Simulate a dynamic clock widget at (10, 15) with size 30x20.
        draw.rectangle([10, 15, 39, 34], fill=(10, 20, 200, 255))

        ignore_boxes = tdq_vision_diff.parse_ignore_boxes("10,15,30,20")
        self.assertEqual(ignore_boxes, [(10, 15, 30, 20)])

        diff_mask, mismatch_pixels, total_pixels = tdq_vision_diff.compute_diff_mask(
            src, dist, color_tolerance=12, ignore_boxes=ignore_boxes
        )
        self.assertEqual(mismatch_pixels, 0)
        self.assertEqual(total_pixels, 120 * 100 - 30 * 20)
        self.assertIsNone(diff_mask.getbbox())

    def test_bounding_boxes_and_highlight(self) -> None:
        """Two separated diff clusters are detected as [1] and [2] and rendered onto diff_highlight.png."""
        src = _make_solid_image(200, 160, (255, 255, 255, 255))
        dist = src.copy()
        draw = ImageDraw.Draw(dist)
        # Box 1 near top-left: x=10..29 (w=20), y=12..27 (h=16)
        draw.rectangle([10, 12, 29, 27], fill=(220, 20, 20, 255))
        # Box 2 near bottom-right: x=140..169 (w=30), y=110..134 (h=25)
        draw.rectangle([140, 110, 169, 134], fill=(20, 20, 220, 255))

        diff_mask, mismatch_pixels, _ = tdq_vision_diff.compute_diff_mask(
            src, dist, color_tolerance=10
        )
        self.assertEqual(mismatch_pixels, (20 * 16) + (30 * 25))

        boxes = tdq_vision_diff.find_bounding_boxes(diff_mask, grid_size=16, min_area=16)
        self.assertEqual(len(boxes), 2)
        self.assertEqual(boxes[0]["id"], 1)
        self.assertEqual((boxes[0]["x"], boxes[0]["y"], boxes[0]["w"], boxes[0]["h"]), (10, 12, 20, 16))
        self.assertEqual(boxes[1]["id"], 2)
        self.assertEqual((boxes[1]["x"], boxes[1]["y"], boxes[1]["w"], boxes[1]["h"]), (140, 110, 30, 25))

        highlight = tdq_vision_diff.render_highlight_image(dist, diff_mask, boxes)
        self.assertEqual(highlight.size, (200, 160))
        # Border at top-left corner of box 1 must be bright red.
        self.assertEqual(highlight.getpixel((10, 12)), (255, 32, 32, 255))

    def test_reports_relative_and_base64(self) -> None:
        """CLI generates metrics.json, <slug>.md, and <slug>.html in both relative and --embed-base64 modes."""
        src_path = self.work_dir / "source.png"
        dist_path = self.work_dir / "dist.png"
        out_rel = self.work_dir / "out_rel"
        out_b64 = self.work_dir / "out_b64"

        src = _make_solid_image(160, 120, (250, 250, 250, 255))
        dist = src.copy()
        draw = ImageDraw.Draw(dist)
        draw.rectangle([20, 20, 49, 49], fill=(30, 30, 30, 255))
        src.save(src_path)
        dist.save(dist_path)

        # Relative mode (mismatch exceeds 1% threshold -> exit code 1, but all reports written)
        rc_rel = tdq_vision_diff.main([
            "--source", str(src_path),
            "--dist", str(dist_path),
            "--out-dir", str(out_rel),
            "--slug", "sample-ui",
            "--threshold", "0.01",
            "--round", "1",
        ])
        self.assertEqual(rc_rel, 1)
        self.assertTrue((out_rel / "diff_highlight.png").is_file())
        self.assertTrue((out_rel / "metrics.json").is_file())
        self.assertTrue((out_rel / "sample-ui.md").is_file())
        self.assertTrue((out_rel / "sample-ui.html").is_file())

        metrics = json.loads((out_rel / "metrics.json").read_text(encoding="utf-8"))
        self.assertFalse(metrics["passed"])
        self.assertEqual(metrics["canvas_size"], [160, 120])
        self.assertEqual(len(metrics["bounding_boxes"]), 1)

        md_text = (out_rel / "sample-ui.md").read_text(encoding="utf-8")
        self.assertIn("FAIL", md_text)
        self.assertIn("[1]", md_text)

        html_rel = (out_rel / "sample-ui.html").read_text(encoding="utf-8")
        self.assertNotIn("data:image/png;base64,", html_rel)
        self.assertIn("diff_highlight.png", html_rel)
        # All 4 interactive features must be present in the HTML report:
        self.assertIn("Before/After Split Slider", html_rel)
        self.assertIn("Overlay Onion-Skin", html_rel)
        self.assertIn("Blink 2Hz", html_rel)
        self.assertIn("Interactive Bounding Box Explorer", html_rel)
        self.assertIn("Multi-round Progress Timeline", html_rel)

        # Base64 mode with relaxed threshold -> exit code 0
        rc_b64 = tdq_vision_diff.main([
            "--source", str(src_path),
            "--dist", str(dist_path),
            "--out-dir", str(out_b64),
            "--slug", "sample-ui",
            "--threshold", "0.10",
            "--embed-base64",
            "--round", "2",
        ])
        self.assertEqual(rc_b64, 0)
        html_b64 = (out_b64 / "sample-ui.html").read_text(encoding="utf-8")
        self.assertIn("data:image/png;base64,", html_b64)

    def test_figma_url_missing_token_returns_exit_3(self) -> None:
        """Calling CLI with --figma-url when FIGMA_TOKEN is missing returns exit code 3 and logs pause hint."""
        dist_path = self.work_dir / "dist.png"
        _make_solid_image(80, 80, (255, 255, 255, 255)).save(dist_path)
        out_dir = self.work_dir / "out_figma"

        stderr_buf = io.StringIO()
        with mock.patch.dict(os.environ, {"FIGMA_TOKEN": "", "TDQ_LOG": "1"}, clear=False):
            with mock.patch("sys.stderr", stderr_buf):
                rc = tdq_vision_diff.main([
                    "--figma-url", "https://www.figma.com/design/AbCdEf123/MyDesign?node-id=12-34",
                    "--dist", str(dist_path),
                    "--out-dir", str(out_dir),
                ])
        self.assertEqual(rc, 3)
        self.assertIn("pause --loai dau-vao-user", stderr_buf.getvalue())

    def test_figma_url_with_mock_opener(self) -> None:
        """fetch_figma_source parses file_key and node_id and downloads the PNG via custom opener."""
        file_key, node_id = tdq_vision_diff.parse_figma_url(
            "https://www.figma.com/design/KeyXYZ987/Landing-Page?node-id=45-67"
        )
        self.assertEqual(file_key, "KeyXYZ987")
        self.assertEqual(node_id, "45:67")

        png_buf = io.BytesIO()
        _make_solid_image(64, 64, (100, 150, 200, 255)).save(png_buf, format="PNG")
        png_bytes = png_buf.getvalue()

        def fake_opener(req, timeout=30):
            url = req.full_url if hasattr(req, "full_url") else str(req)
            resp = mock.MagicMock()
            resp.__enter__.return_value = resp
            if "api.figma.com" in url:
                payload = {"images": {"45:67": "https://figma-alpha-api.s3.us-west-2.amazonaws.com/img/test.png"}}
                resp.read.return_value = json.dumps(payload).encode("utf-8")
            else:
                resp.read.return_value = png_bytes
            return resp

        out_png = self.work_dir / "fetched_figma.png"
        result_path = tdq_vision_diff.fetch_figma_source(
            "https://www.figma.com/design/KeyXYZ987/Landing-Page?node-id=45-67",
            out_png,
            token="figd_test_token_123",
            opener=fake_opener,
        )
        self.assertEqual(result_path, out_png)
        self.assertTrue(out_png.is_file())
        with Image.open(out_png) as fetched_img:
            self.assertEqual(fetched_img.size, (64, 64))

    def test_log_service_default_and_disabled(self) -> None:
        """log_event prints ISO timestamped line to stderr by default and stays silent when TDQ_LOG=0."""
        buf_on = io.StringIO()
        with mock.patch.dict(os.environ, {"TDQ_LOG": "1"}, clear=False):
            with mock.patch("sys.stderr", buf_on):
                tdq_vision_diff.log_event("vision check started")
        output_on = buf_on.getvalue()
        self.assertRegex(
            output_on,
            r"^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\] tdq_vision_diff: vision check started\n$",
        )

        buf_off = io.StringIO()
        with mock.patch.dict(os.environ, {"TDQ_LOG": "0"}, clear=False):
            with mock.patch("sys.stderr", buf_off):
                tdq_vision_diff.log_event("should not appear")
        self.assertEqual(buf_off.getvalue(), "")

    def test_cli_missing_input_returns_exit_2(self) -> None:
        """Missing source/dist files or invalid arguments return exit code 2."""
        out_dir = self.work_dir / "out_err"
        rc = tdq_vision_diff.main([
            "--source", str(self.work_dir / "nonexistent.png"),
            "--dist", str(self.work_dir / "nonexistent_dist.png"),
            "--out-dir", str(out_dir),
        ])
        self.assertEqual(rc, 2)

    def test_multi_round_timeline_history(self) -> None:
        """Running multiple rounds appends to rounds_history.json and renders timeline entries."""
        src_path = self.work_dir / "source.png"
        dist_v1 = self.work_dir / "dist_v1.png"
        dist_v2 = self.work_dir / "dist_v2.png"
        out_dir = self.work_dir / "out_rounds"

        src = _make_solid_image(100, 100, (255, 255, 255, 255))
        d1 = src.copy()
        ImageDraw.Draw(d1).rectangle([10, 10, 49, 49], fill=(0, 0, 0, 255))
        d2 = src.copy()
        src.save(src_path)
        d1.save(dist_v1)
        d2.save(dist_v2)

        rc1 = tdq_vision_diff.main([
            "--source", str(src_path),
            "--dist", str(dist_v1),
            "--out-dir", str(out_dir),
            "--slug", "timeline-ui",
            "--threshold", "0.01",
            "--round", "1",
        ])
        self.assertEqual(rc1, 1)

        rc2 = tdq_vision_diff.main([
            "--source", str(src_path),
            "--dist", str(dist_v2),
            "--out-dir", str(out_dir),
            "--slug", "timeline-ui",
            "--threshold", "0.01",
            "--round", "2",
        ])
        self.assertEqual(rc2, 0)

        history = json.loads((out_dir / "rounds_history.json").read_text(encoding="utf-8"))
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["round"], 1)
        self.assertEqual(history[1]["round"], 2)
        html_text = (out_dir / "timeline-ui.html").read_text(encoding="utf-8")
        self.assertIn("Round 1", html_text)
        self.assertIn("Round 2", html_text)


if __name__ == "__main__":
    unittest.main()
