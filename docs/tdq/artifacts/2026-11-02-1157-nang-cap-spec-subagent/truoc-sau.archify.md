# Spec và subagent đổi gì? {#tong-quan}

@meta locale=en

Sau update, spec và mini-plan mở bằng một trang sơ đồ Trước/Sau, và subagent không sửa được project trước phase implement.

- Spec: thêm sơ đồ hiện trạng cạnh sơ đồ thiết kế mới.
- Pipeline nhanh: cùng luật, bỏ ngưỡng hai module.
- Subagent: mở ở mọi phase, trước implement chỉ ghi docs.
- Không thêm script; chỉ một nhánh chặn trong edit_gate.

## Luồng viết spec hôm nay {#spec-truoc}

@workflow id=spec-truoc-flow title="Trước: spec chỉ vẽ thiết kế mới"
| brief | Brief + khảo sát | backend |
| text | Bảng Trước/Sau bằng chữ | backend |
| one | Vẽ 1 sơ đồ thiết kế mới | backend |
| gate | User duyệt spec | external |
| brief > text | |
| text > one | |
| one > gate | |

Dev phải tự hình dung hiện trạng từ bảng chữ; HTML chỉ cho thấy thiết kế mới.

## Luồng viết spec sau update {#spec-sau}

@workflow id=spec-sau-flow title="Sau: sơ đồ Trước và Sau trong một trang"
| brief | Brief + khảo sát | backend |
| before | Vẽ sơ đồ hiện trạng | backend |
| after | Vẽ sơ đồ sau update | backend |
| page | Render 1 HTML + bind | backend |
| gate | User duyệt spec | external |
| brief > before | evidence |
| before > after | |
| after > page | explainer | emphasis |
| page > gate | link HTML |

Feature dựng mới hoàn toàn: sơ đồ hiện trạng ghi "chưa có". Chữ trong spec chỉ giải thích sơ đồ.

## Subagent ghi file hôm nay {#sub-truoc}

@workflow id=sub-truoc-flow title="Trước: chỉ chặn khi lệch vùng plan"
| sub | Subagent gọi Edit | external |
| docs | File trong docs? | backend |
| zone | Ngoài vùng Chạm? | backend |
| ok | Ghi được | backend |
| deny | Chặn TDQ:TEAM | security |
| sub > docs | |
| docs > ok | có |
| docs > zone | không |
| zone > deny | có | security |
| zone > ok | không |

Trước implement chưa có vùng `Chạm:` nào, nên subagent ghi được mọi file ngoài docs.

## Subagent ghi file sau update {#sub-sau}

@workflow id=sub-sau-flow title="Sau: thêm chặn theo phase"
| sub | Subagent gọi Edit | external |
| docs | File trong docs? | backend |
| phase | Đã tới implement? | backend |
| zone | Ngoài vùng Chạm? | backend |
| ok | Ghi được | backend |
| deny | Chặn TDQ:TEAM | security |
| sub > docs | |
| docs > ok | có |
| docs > phase | không |
| phase > deny | chưa | security |
| phase > zone | rồi |
| zone > deny | có | security |
| zone > ok | không |

Hook nhận ra subagent nhờ trường `agent_id` Claude Code gắn vào input. Main agent không có trường này nên không bị nhánh mới chặn.
