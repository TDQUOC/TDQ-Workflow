# Báo cáo — Hạn chế dừng giữa plan {#tong-quan}

@meta locale=vi

Stop hook và SessionStart trên Claude Code nay nêu task cần làm/kiểm lại. Không giám sát API/tool đang chạy và không bảo đảm tự hoàn tất mọi plan; `/goal` chỉ hướng dẫn tùy chọn, không tự bật.

## 1. Trước request: Stop nhắc chung {#truoc}

@workflow id=truoc-bao-cao title="Trước: dừng sớm khó biết làm tiếp gì"
| plan | Plan còn task | backend |
| stop | Stop chặn tối đa ba lượt | security |
| stuck | Lượt bốn hint chung | backend |
| resume | Resume thiếu task đầu chưa làm | frontend |
| plan > stop | chưa hoàn tất |
| stop > stuck | không tiến triển |
| stuck > resume | quay lại |

## 2. Sau request: nhắc đúng task {#sau}

@workflow id=sau-bao-cao title="Sau: có việc tiếp theo và lối thoát an toàn"
| plan2 | Task/DoD theo plan đã duyệt | backend |
| stop2 | Stop nhắc task và check | security |
| stuck2 | Ba lần không tiến triển: báo task | backend |
| resume2 | Resume phân biệt task mở/đã giao | frontend |
| goal2 | /goal do người dùng bật riêng | frontend |
| plan2 > stop2 |
| stop2 > stuck2 |
| stuck2 > resume2 |
| goal2 > plan2 |

Lệch nhỏ đối chiếu spec, dùng dự phòng, ghi `lech add` rồi tiếp tục; commit giữa chừng chỉ khi gỡ blocker. Bốn loại pause và cổng duyệt giữ nguyên. Không sửa Antigravity hoặc CI.

## 3. Đã test gì? {#da-test}

| Phép kiểm | Đầu ra thật |
|---|---|
| Stop hook | 116 passed, 23 subtests; 3 lần chặn và lần bốn hạ cấp |
| SessionStart/PromptContext | 94 passed, 146 subtests; resume/compact, task `[~]`, đầu `[ ]`, chờ `[>]` |
| Luật plan/spec/goal | 29 passed, 329 subtests; goal không tự bật |
| Full fresh | 4.187 case ID; chạy mới trên nguồn ổn định |

## 4. Kết quả test {#ket-qua}

Full fresh **4.180 passed, 7 skipped, 2.724 subtests passed** trong 793,74 giây pytest (runner 800,34 giây), `details_complete=true`, fingerprint trước/sau trùng. Subtests không cộng thêm vào số case ID. Vùng chạm Stop 379 passed; SessionStart 275 passed; luật cuối 593 passed/1 skipped. Một lượt vùng chạm Stop trước bị INCOMPLETE vì Ruff ghi `.ruff_cache` song song; không dùng làm verdict.

**Giới hạn:** `radius_complete=false`; `bo_sot=0` không chứng nhận đầy đủ bán kính. Eval chưa kích hoạt. Chưa thử `/goal` như một model trial; điều kiện `/goal 1a` đang bật do người dùng nhập không chứng minh plan hoàn thành. Hook không được gọi khi API/tool im bặt giữa lượt.
