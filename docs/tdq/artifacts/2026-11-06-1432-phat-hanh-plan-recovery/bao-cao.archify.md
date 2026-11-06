# Báo cáo phát hành TDQ Workflow 0.94.0 {#tong-quan}

@meta locale=vi

Phiên bản `0.94.0` đóng gói cải tiến Stop/resume đã có trong `dev`. `main` là snapshot plugin tinh gọn từ `dev`; hai nhánh đã push lên origin và hash remote trùng local. Không tạo tag/GitHub release object.

## 1. Trước phát hành {#truoc}

@workflow id=truoc-publish title="Trước: bản 0.93.0 trên manifest"
| dev | dev có Stop/resume mới | backend |
| manifest | Manifest 0.93.0 | backend |
| main | main snapshot cũ | security |
| origin | origin còn sau local | frontend |
| dev > manifest |
| manifest > main |
| main > origin |

## 2. Sau phát hành {#sau}

@workflow id=sau-publish title="Sau: main 0.94.0 đã push"
| bump | Hai manifest 0.94.0 | backend |
| log | Changelog mới | backend |
| snap | main tinh gọn từ dev | security |
| push | dev/main cùng origin | frontend |
| bump > log |
| log > snap |
| snap > push |

## 3. Đã test gì? {#da-test}

| Kiểm | Bằng chứng |
|---|---|
| Manifest + Changelog | Cùng version 0.94.0, doc_lint 0 vi phạm |
| Đóng gói + adapter | 51 passed, 9 subtests passed trong 7,26s |
| Snapshot | `build_portable.py --sinh-main`: kept=175, dropped=5374; main chứa version 0.94.0 |
| Remote | `git ls-remote --heads origin dev main` khớp hash local sau push |

## 4. Kết quả test {#ket-qua}

**Release PASS.** `dev@9f09eef0`, `main@825b1929`; `git push origin dev main` thành công. Full fresh 4.180 passed/7 skipped là chứng cứ của request cải tiến Stop/resume trước bump; release chỉ chạy targeted 51 passed, không báo full fresh mới. Eval vẫn chưa kích hoạt; không tự suy hiệu quả với model nhỏ từ test.
