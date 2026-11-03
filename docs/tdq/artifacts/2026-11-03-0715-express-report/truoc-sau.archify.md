# Báo cáo trực quan cho hai lane TDQ {#tong-quan}

@meta locale=en

Express thêm phase `report` sau QC; cả Express và Deep dùng cùng bộ Markdown nghiệm thu và HTML Archify kết quả thực tế. Sơ đồ trước/sau ở đây là thiết kế dự kiến, không phải chứng cứ nghiệm thu.

## Express trước cập nhật {#express-truoc}

@workflow id=express-truoc-flow title="Trước: Express đóng ngay sau QC"
| input | Yêu cầu Express | external |
| analyze | quick_analyze | backend |
| gate | Duyệt mini-plan | security |
| implement | Implement + QC + fix | backend |
| idle | Đóng request, hỏi commit | external |
| input > analyze | khảo sát |
| analyze > gate | mini-plan |
| gate > implement | một lần duyệt |
| implement > idle | QC xong, không report riêng |

Trước: `phase_key()` chỉ hiển thị `quick_analyze` và `quick`, sau duyệt chuyển thẳng `idle`; không có báo cáo HTML nghiệm thu.

## Express sau cập nhật {#express-sau}

@workflow id=express-sau-flow title="Sau: Express có phase report"
| input | Yêu cầu Express | external |
| analyze | quick_analyze | backend |
| gate | Duyệt mini-plan | security |
| implement | Implement + QC + fix | backend |
| report | Report Markdown + HTML Archify | cloud |
| idle | Đóng request, hỏi commit | external |
| input > analyze | khảo sát |
| analyze > gate | mini-plan |
| gate > implement | một lần duyệt |
| implement > report | QC xanh | emphasis |
| report > idle | report hoàn tất |

Sau: phase `report` có dòng riêng trong state, không thêm cổng duyệt. Nếu Archify không khả dụng, report ghi fallback trung thực, không link output thiếu.

## Báo cáo hai lane trước cập nhật {#report-truoc}

@workflow id=report-truoc-flow title="Trước: Deep có Markdown, Express không có report"
| deep | Deep QC | backend |
| deepmd | Markdown report Deep | database |
| express | Express QC | backend |
| close | Đóng Express | external |
| deep > deepmd | phase report |
| express > close | không report |

Cả hai lane có thể có Archify preview thiết kế trước implement, nhưng preview không phải bằng chứng kết quả thực tế.

## Báo cáo hai lane sau cập nhật {#report-sau}

@workflow id=report-sau-flow title="Sau: một contract report thực tế"
| deep | Deep QC xanh | backend |
| express | Express QC xanh | backend |
| phase | Phase report chung | backend |
| md | Markdown nghiệm thu | database |
| html | HTML Archify độc lập | cloud |
| truth | Task, DoD, QC, kết quả, giới hạn | security |
| deep > phase | vào report |
| express > phase | vào report |
| phase > truth | chứng cứ thực tế |
| truth > md | số đo và giới hạn |
| truth > html | Before/After + luồng kết quả | emphasis |

HTML report độc lập với HTML preview thiết kế đã duyệt; hai đầu ra dùng cùng số đo và fallback công khai.
