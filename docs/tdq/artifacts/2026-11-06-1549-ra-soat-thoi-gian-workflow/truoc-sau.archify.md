# Trước/Sau — Rà soát tối ưu TDQ Workflow {#tong-quan}

@meta locale=vi

Bản planned cho báo cáo nghiên cứu, không phải thay đổi runtime. Ba subagent độc lập đã kiểm lại số liệu, policy optional và phép đo 50%. Báo cáo cuối phân tách CONFIRMED, UNCERTAIN và CONFLICT.

## Luồng kiểm chứng {#luong}

@workflow id=truoc-audit title="Trước: đề xuất nằm ở hai report riêng"
| report | Hai report Review | backend |
| claims | Số lịch sử và giả thuyết xen nhau | backend |
| optional | Có mục đề xuất optional sai luật | security |
| report > claims |
| claims > optional |

@workflow id=sau-audit title="Sau: claim gắn chứng cứ và guardrail"
| agents | Ba phản biện độc lập | frontend |
| source | Đối chiếu TDQ 0.94.0 | backend |
| verdict | Confirmed / uncertain / conflict | security |
| options | Bảng mandatory / conditional | backend |
| agents > source |
| source > verdict |
| verdict > options |

Quan trọng: timeout Graphify 300s không phải runtime 300s; LSP startup nhiều phút chưa tái kiểm được từ ledger còn lại. HTML report bắt buộc, không được tắt chỉ để nhanh. Không chạy benchmark hoặc sửa policy trong request này.
