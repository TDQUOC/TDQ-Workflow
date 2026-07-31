# Report — 2026-07-31-failpath-demo (fallback tavily)

Engine agy trả `engine-failed` 2 lần liên tiếp (exit 3, preflight: model slug
`slug-khong-ton-tai` không có trên máy) → theo luật deep-search.md, DỪNG gọi agy
và chuyển Tavily trả lời brief.

## Kết quả (nguồn Tavily, 2026-07-31)

| Claim | Nguồn |
|---|---|
| Phiên bản Python 3 stable mới nhất là Python 3.14.6 | https://www.python.org/downloads/windows |

Evidence: "Latest Python 3 Release - Python 3.14.6" (python.org, trang Releases for Windows).

Ghi chú: **fallback tavily** — kết quả này KHÔNG qua search-runner/agy; bằng chứng
exit code 2 lần nằm ở QC mục Q6.
