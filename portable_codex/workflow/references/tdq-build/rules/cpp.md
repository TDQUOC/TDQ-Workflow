# Rule C++

Soul: chất lượng > runtime > context cost. Nạp sau `chung.md`, áp cho
`.cpp .cc .cxx .hpp .h`.

## Nguồn

- C++ Core Guidelines (repo chính thức, Stroustrup & Sutter chủ biên) —
  https://github.com/isocpp/CppCoreGuidelines (commit gần nhất 2026-08-06, dự án sống) —
  trọng tâm: interface, resource/memory management, concurrency; theo được thì code
  type-safe tĩnh và không rò tài nguyên.
- Công bố gốc tại CppCon — https://isocpp.org/blog/2015/09/bjarne-stroustrup-announces-cpp-core-guidelines
  (2015) — guideline chủ đích viết để máy enforce được; kèm thư viện GSL (`not_null`…).
- LLVM Coding Standards — https://llvm.org/docs/CodingStandards.html — chuẩn style của
  hệ sinh thái clang/clang-tidy.

## Khi nào áp dụng

- Viết hoặc sửa file C++ bất kỳ; file `.h` dùng chung với C thì vẫn soát theo file này.
- Trước khi nộp: chạy mục "Tự kiểm"; máy thiếu `clang-tidy` thì ghi "chưa kiểm được".

## Luật Intentionality

1. **Interface phải nói rõ ý**: tham số con trỏ không được phép null → dùng kiểu như
   `gsl::not_null` thay vì ghi chú miệng; đơn vị và ràng buộc thể hiện bằng kiểu.
2. **Sở hữu tài nguyên mập mờ là nuốt lỗi**: `new`/`delete` trần rải rác không nói ai
   sở hữu → RAII và smart pointer; rò tài nguyên là lỗi Core Guidelines nhắm thẳng.
3. **Code chết**: biến không dùng, hàm không ai gọi, nhánh không thể tới —
   `clang-tidy` báo → xoá, không comment-out để dành.

## Ngưỡng đo được

- Cyclomatic ≤ 10 mỗi hàm — theo `chung.md`.
- Cognitive ≤ **25** mỗi hàm — C++ thuộc họ C (C, C++, Objective-C) nên dùng mức nới
  25 thay cho 15; vượt 25 vẫn phải tách hàm, không nới tiếp.
- Bộ check tối thiểu của clang-tidy: nhóm `cppcoreguidelines-*`.

## Làm gì

1. Quản lý tài nguyên bằng RAII: mở trong constructor, đóng trong destructor; quyền
   sở hữu thể hiện bằng smart pointer, không dùng `new`/`delete` trần.
2. Viết interface tự mô tả: kiểu nói được ràng buộc (`not_null`, tham chiếu thay con
   trỏ khi không có null hợp lệ).
3. Bật clang-tidy với nhóm check `cppcoreguidelines-*` trong config của repo.
4. Chạy `clang-tidy <đường dẫn>` và sửa hết cảnh báo nhóm đã bật.

## Tự kiểm

- [ ] `clang-tidy` sạch cảnh báo nhóm `cppcoreguidelines-*`, hoặc đã ghi
  "chưa kiểm được" khi máy thiếu clang-tidy
- [ ] Không `new`/`delete` trần; tài nguyên nào cũng có chủ sở hữu RAII rõ
- [ ] Không hàm nào vượt cyclomatic 10 hay cognitive 25
- [ ] Trả lời được 3 câu hỏi Intentionality trong `chung.md`

## Ví dụ ĐÚNG/SAI

```cpp
// SAI — new trần, ai delete không rõ, con trỏ có thể null không nói:
Widget* make(Config* c) { return new Widget(c->size); }
// ĐÚNG — sở hữu rõ bằng unique_ptr, ràng buộc null nói bằng kiểu:
std::unique_ptr<Widget> TaoWidget(gsl::not_null<const Config*> cauHinh) {
    return std::make_unique<Widget>(cauHinh->size);
}
```
