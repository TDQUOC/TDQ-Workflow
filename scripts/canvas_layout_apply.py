#!/usr/bin/env python3
"""Dời cả 5 khối cũ về đúng chương trong MỘT lượt ghi.

Vì sao không chạy `canvas_move_block.py` 5 lần: khung chương rộng 2640px, còn khối
cũ chỉ 760–1296px và đang nằm rải rác. Dời từng khối một thì khối vừa dời có thể
rơi vào vùng nguồn của khối kế tiếp và bị cuốn theo (đã xảy ra: ch2 bị lệnh dời ch7
gom mất 36 phần tử). Ở đây mọi phép dời được TÍNH trên cùng một ảnh chụp scene, rồi
mới xoá và tạo lại một lần.

Bảng MOVES chép từ `docs/tdq/plan/2026-08-12-hoan-thien-doc-excalidraw.md`.
"""

import sys

from canvas_move_block import api, plan_move, write_moves

MOVES = [
    # (chương, vùng nguồn x0,y0,x1,y1, y đích, tiêu đề mới, số phần tử mong đợi)
    (2, (1120, -110, 1880, 850), 1420, "2. Ưu điểm & lợi ích cho dev", 55),
    (5, (-220, -215, 1080, 1650), 4580, "5. Flow làm việc — lane quick & full", 65),
    (7, (40, 1780, 2680, 3340), 7520, "7. Sequence diagram — trình tự 1 request", 60),
    (9, (1920, -110, 2680, 1370), 10260, "9. Manifest & Dependency", 19),
    (10, (1120, 900, 1880, 1650), 11900, "10. Nền tảng & cách Test/Dev", 15),
]


def main(argv=None):
    dry_run = "--dry-run" in (argv if argv is not None else sys.argv[1:])
    elements = api("/api/elements")["elements"]
    print(f"Ảnh chụp scene: {len(elements)} phần tử\n")

    batches = []
    seen = {}
    problems = []
    for chapter, region, target_y, title, expect in MOVES:
        picked, new_elements = plan_move(elements, chapter, region, target_y, title)
        if len(picked) != expect:
            problems.append(f"chương {chapter}: chọn {len(picked)} phần tử, mong đợi {expect}")
        for el in picked:
            if el["id"] in seen:
                problems.append(
                    f"{el['id']} bị hai vùng cùng chọn: chương {seen[el['id']]} và {chapter}"
                )
            seen[el["id"]] = chapter
        batches.append((picked, new_elements))
        print()

    if problems:
        for p in problems:
            print(f"✗ {p}")
        print("Không ghi gì cả — sửa bảng MOVES rồi chạy lại.")
        return 1
    if dry_run:
        print("(dry-run, không ghi)")
        return 0
    return write_moves(batches)


if __name__ == "__main__":
    sys.exit(main())
