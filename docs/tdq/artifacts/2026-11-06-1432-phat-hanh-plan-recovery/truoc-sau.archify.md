# Trước/Sau — Phát hành khôi phục plan {#tong-quan}

@meta locale=vi

Thiết kế planned: chuyển cải tiến Stop/resume đã nằm trên `dev` vào snapshot release `main` phiên bản 0.94.0 và push hai nhánh. Không đổi thuật toán đã kiểm. Git remote được đối chiếu trước/sau push.

## Luồng phát hành {#luong}

@workflow id=truoc-release title="Trước: bản 0.93.0 chưa mang cải tiến"
| dev | dev có cải tiến Stop/resume | backend |
| old | main đang ở bản 0.92.0 | security |
| remote | origin còn sau local | frontend |
| dev > old |
| old > remote |

@workflow id=sau-release title="Sau: bản 0.94.0 được xuất bản"
| bump | Bump hai plugin manifest | backend |
| changelog | Ghi Changelog và kiểm | backend |
| main | Sinh main sạch từ dev | security |
| push | Push dev và main | frontend |
| bump > changelog |
| changelog > main |
| main > push |

Nguồn: `README.md:213-218` nêu bump hai manifest, Changelog và `build_portable.py --sinh-main`. Đã kiểm local/remote hash qua Git; việc push và trạng thái cuối chỉ được khẳng định sau kiểm từ remote.
