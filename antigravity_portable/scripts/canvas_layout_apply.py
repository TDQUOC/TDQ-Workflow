#!/usr/bin/env python3
"""Move all 5 old blocks to their right chapter in ONE write pass.

Why not run `canvas_move_block.py` 5 times: a chapter frame is 2640px wide while an old
block is only 760–1296px and they lie scattered. Moving them one at a time lets a block
just moved fall inside the source region of the next one and be dragged along (it happened:
the ch7 move swallowed 36 elements of ch2). Here every move is COMPUTED on one single scene
snapshot, and only then deleted and recreated in one go.

The MOVES table is copied from `docs/tdq/plan/2026-08-12-hoan-thien-doc-excalidraw.md`.
"""

import sys

from canvas_move_block import api, plan_move, write_moves

MOVES = [
    # (chapter, source region x0,y0,x1,y1, target y, new title, expected element count)
    (2, (1120, -110, 1880, 850), 1420, "2. Ưu điểm & lợi ích cho dev", 55),  # i18n-allow
    (5, (-220, -215, 1080, 1650), 4580, "5. Flow làm việc — chế độ nhanh & chuyên sâu", 65),  # i18n-allow
    (7, (40, 1780, 2680, 3340), 7520, "7. Sequence diagram — trình tự 1 request", 60),  # i18n-allow
    (9, (1920, -110, 2680, 1370), 10260, "9. Manifest & Dependency", 19),
    (10, (1120, 900, 1880, 1650), 11900, "10. Nền tảng & cách Test/Dev", 15),  # i18n-allow
]


def main(argv=None):
    dry_run = "--dry-run" in (argv if argv is not None else sys.argv[1:])
    elements = api("/api/elements")["elements"]
    print(f"Scene snapshot: {len(elements)} element(s)\n")

    batches = []
    seen = {}
    problems = []
    for chapter, region, target_y, title, expect in MOVES:
        picked, new_elements = plan_move(elements, chapter, region, target_y, title)
        if len(picked) != expect:
            problems.append(f"chapter {chapter}: picked {len(picked)} element(s), expected {expect}")
        for el in picked:
            if el["id"] in seen:
                problems.append(
                    f"{el['id']} picked by two regions: chapter {seen[el['id']]} and {chapter}"
                )
            seen[el["id"]] = chapter
        batches.append((picked, new_elements))
        print()

    if problems:
        for p in problems:
            print(f"✗ {p}")
        print("Nothing written — fix the MOVES table and run again.")
        return 1
    if dry_run:
        print("(dry-run, nothing written)")
        return 0
    return write_moves(batches)


if __name__ == "__main__":
    sys.exit(main())
