# Nghiệm thu Express Report {#tong-quan}

@meta locale=en

Kết quả thực tế cho request `2026-11-03-0715-express-report`: Express dùng phase `report` hiện có; hai lane cùng contract Markdown + HTML Archify. Bằng chứng: 220 test PASS, 58 subtest; smoke 85 PASS, 18 subtest; eval 8 trial PASS gate. Preview thiết kế ban đầu stale sau thay đổi và không được dùng làm bằng chứng hiện hành.

## Luồng trước cập nhật {#truoc}

@workflow id=luong-truoc title="Trước: Express thiếu báo cáo nghiệm thu"
| analyze | quick_analyze | backend |
| quick | Implement + QC | backend |
| idle | idle | external |
| analyze > quick | duyệt nhanh một lần |
| quick > idle | đóng trực tiếp |

Baseline ở commit `e8b53a8`: Express không có report riêng; Deep có Markdown report nhưng chưa buộc HTML nghiệm thu.

## Luồng sau cập nhật {#sau}

@workflow id=luong-sau title="Sau: hai lane chung phase report"
| quick | Quick QC đạt | backend |
| deep | Deep QC đạt | backend |
| report | Phase report hiện có | backend |
| markdown | Markdown nghiệm thu | database |
| html | HTML Archify độc lập | cloud |
| idle | idle | external |
| quick > report | CLI chặn bỏ qua | emphasis |
| deep > report | luồng cũ được giữ |
| report > markdown | evidence Q1–Q5 |
| report > html | Before/After thực tế |
| markdown > idle | báo cáo xong |
| html > idle | verify current |

`phase_key()` hiển thị `quick_analyze → quick → report → idle`; CLI từ chối Quick `implement → idle`. Cổng duyệt Quick vẫn đúng một.

## Task và QC đã đo {#kiem-thu}

@workflow id=kiem-thu-flow title="Task, DoD và QC"
| tasks | 4 task đã hoàn tất | backend |
| dod | Q1–Q5 PASS | security |
| regression | 220 test + 58 subtest PASS | backend |
| smoke | 85 test + 18 subtest PASS | backend |
| eval | 8 A/B trial, gate PASS | cloud |
| tasks > dod | red-green |
| dod > regression | kiểm vùng chạm |
| regression > smoke | CLI/hook/Archify |
| smoke > eval | baseline 3/4, candidate 4/4 |

Phép thử: `python -m pytest tests/test_report_visual.py tests/test_state.py tests/test_phase_table.py tests/test_context_hooks.py tests/test_quick_qc.py tests/test_tdq_archify.py tests/test_archify_artifacts.py -q`. Bộ kiểm lint và token budget đều PASS.

## Đầu ra và giới hạn {#gioi-han}

@workflow id=outcome-flow title="Đầu ra thật và giới hạn"
| reportmd | reports/<slug>.md | database |
| reporthtml | reports/<slug>.html | cloud |
| limit | Worktree QC độc lập không thấy diff | external |
| preview | Preview thiết kế ban đầu stale | external |
| reportmd > reporthtml | cùng evidence |
| limit > reportmd | công khai |
| preview > reportmd | không dùng làm chứng cứ |

HTML này là nghiệm thu working-tree, không phải snapshot commit. QC độc lập cô lập thấy worktree rỗng nên verdict đó không kiểm được diff; các lệnh ở root đã kiểm lại. Nếu HTML stale hoặc engine lỗi, dùng fallback văn bản và không gắn link HTML thiếu.
