# Trước/Sau — Eval chỉ chạy khi người dùng đồng ý {#tong-quan}

@meta locale=vi

Thiết kế planned: hai gate eval (`implement`, `report`) mặc định tắt. Chỉ khi người dùng yêu cầu và đồng ý, lệnh `eval-enable` ghi lời đồng ý vào state, gate mới chạy như cũ. Lệnh `eval-waive` bị bỏ vì mặc định đã không chặn.

## Gate eval trước và sau {#luong-gate}

@workflow id=truoc-gate title="Trước: eval tự chặn khi đổi skill/hook"
| chinh | Plan có Chạm skill/hook/plugin | backend |
| gate | set phase=implement/report | security |
| thieu | Thiếu eval_plan_file hoặc chứng cứ | backend |
| waive | Phải gọi eval-waive để đi tiếp | backend |
| chinh > gate | tự động |
| gate > thieu | chặn |
| thieu > waive | bắt buộc miễn |

@workflow id=sau-gate title="Sau: eval chỉ chạy khi bật"
| nguoi | Người dùng yêu cầu eval | frontend |
| bat | eval-enable --by lời người dùng | backend |
| gate2 | Gate implement/report kiểm như cũ | security |
| tat | Chưa bật: gate bỏ qua | backend |
| nguoi > bat | đồng ý |
| bat > gate2 | eval_enabled có giá trị |
| tat > gate2 | không có cờ thì bỏ qua |

Hiện trạng có nguồn: `scripts/tdq_state.py:2258-2350` hai gate, `:2353-2376` `eval-waive`, `:2803-2814` gọi trong `cli()`. Thiết kế sau là đề xuất, không phải kết quả runtime.
