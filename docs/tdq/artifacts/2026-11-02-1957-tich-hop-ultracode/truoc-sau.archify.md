# Ultracode thay đổi TDQ thế nào? {#tong-quan}

@meta locale=en

Sau cập nhật, `_ultracode` là modifier thực thi trên hai lane TDQ hiện có. Workflow tăng lực khảo sát và kiểm chứng; TDQ vẫn giữ state, approval, Git và worktree.

- Không thêm lane/state/phase mới.
- Không đặt token ceiling; route hữu hạn thay cho loop theo budget.
- Express tự route; Deep cho chọn thêm review/implement.
- Workflow agent chỉ đọc source, ghi report path riêng hoặc trả structured output.

## Intake trước update {#intake-truoc}

@workflow id=intake-truoc-flow title="Trước: chỉ có express và deep"
| user | User chọn lane | external |
| normalize | Chuẩn hóa quick/full | backend |
| init | tdq_state init | backend |
| pipeline | Chạy pipeline hiện hữu | backend |
| user > normalize | express/deep |
| normalize > init | quick/full |
| init > pipeline | |

Ultracode hiện chỉ được gọi thủ công ngoài contract lane; mini-plan/brief chưa ghi policy nhất quán.

## Intake sau update {#intake-sau}

@workflow id=intake-sau-flow title="Sau: _ultracode là modifier"
| user | User chọn lane + suffix | external |
| parse | Bóc _ultracode | backend |
| init | Init quick/full | backend |
| route | Ghi policy + route hữu hạn | backend |
| workflow | Workflow khi cần | cloud |
| gate | Gate TDQ hiện hữu | security |
| user > parse | express_ultracode |
| parse > init | canonical lane |
| init > route | |
| route > workflow | policy bật | emphasis |
| workflow > gate | structured result |

State vẫn chỉ biết `quick|full`; modifier nằm trong brief/mini-plan/spec.

## Điều phối trước update {#owner-truoc}

@workflow id=owner-truoc-flow title="Trước: Agent gọi rời rạc"
| leader | Main agent | backend |
| reader | Research agent | cloud |
| state | TDQ state | database |
| team | TDQ team worktree | backend |
| leader > reader | giao một việc |
| reader > leader | digest |
| leader > state | phase/gate |
| leader > team | implement |

Batch Agent đã hỗ trợ nghiên cứu, nhưng chưa có completion accounting đa lane hay contract Workflow chung.

## Điều phối sau update {#owner-sau}

@workflow id=owner-sau-flow title="Sau: TDQ leader giữ control plane"
| user | User | external |
| leader | TDQ leader | backend |
| engine | Workflow engine | cloud |
| readers | Reader/reviewer agents | cloud |
| reports | docs reports / structured output | database |
| state | tdq_state | database |
| team | tdq_team | backend |
| user > leader | chọn route |
| leader > engine | lane hữu hạn |
| engine > readers | inherited subtasks |
| readers > reports | evidence | emphasis |
| reports > leader | accounting |
| leader > state | phase + approval | security |
| leader > team | implement worktrees |

Workflow không gọi state/Git. Khi plugin khác chặn docs write, agent trả structured output để leader ghi.
