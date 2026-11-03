# BRIEF — Nâng Cấp Khảo Sát Code 3 Chiều & Bảo Toàn Chủ Đích Refactor (`2026-10-20-1355-nang-cap-khao-sat-3-chieu-refactor`)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

"okay mở request update để xuất tổng hợp này cho tdqwworkflow giúp tôi nha"
(Áp dụng gói đề xuất tổng hợp 4 giải pháp:
 1. Chuyển search_gate từ chặn cứng lượt Grep sang kiểm tra điều kiện đủ 3 nguồn Grep + LSP + Graphify trước khi đóng phase analyze, cho phép quét rộng tự do.
 2. Chuẩn hóa quy trình Khảo sát Code 3 Chiều (Triangulation Code Exploration) trong intake/analyze và bảng đối chiếu vùng chạm.
 3. Nới lỏng Rung 1 và bổ sung ngoại lệ ưu tiên Clean Architecture / SOLID khi người dùng yêu cầu Refactor hoặc Mở rộng kiến trúc.
 4. Bổ sung khối xác thực chủ đích Trước vs Sau (Before / After Design Intent) vào brief và plan.)

## Hiểu & kiến thức

### 1. Phân tích nguyên nhân & Kiến trúc giải pháp
1. **Gỡ bỏ rào cản Hard Deny của Grep trong phase Khảo sát (`analyze` / `quick_analyze`)**:
   - Trong `hooks/scripts/search_gate.py`: Nhận diện phase hiện tại qua `tdq_state.load(cwd)`.
   - Nếu phase là `analyze`, `quick_analyze` (hoặc `no_state` / `idle`): Cho phép Grep tự do không bị giới hạn quota 10 lượt và không bị deny, giúp Agent thoải mái quét diện rộng (routes, configs, models, chuỗi UI, event buses).
   - Trong phase `implement`: Vẫn duy trì cơ chế 3 tầng chuẩn để ép buộc kỷ luật viết code.

2. **Cơ chế Tam Giác Khảo Sát (Triangulation Requirement) trước khi rời Phase Analyze**:
   - Trước khi đóng phase analyze để chuyển sang `spec` / `plan` (hoặc duyệt `quick_approved`):
   - Hook / logic kiểm tra sổ nhật ký `search_observe`: Với các request code (`feature`, `bugfix`), Agent bắt buộc phải có ít nhất 1 truy vấn cấu trúc LSP (`find_references` / `list_symbols` / `find_symbol`) hoặc Graphify (`affected` / `query`) để đối chiếu, tránh tình trạng chỉ grep qua loa rồi đoán mò.

3. **Bổ sung ngoại lệ Refactor & Clean Architecture vào Rung 1 (`chung.md`)**:
   - Trong mục `### Never simplify these away` của `skills/tdq-build/references/rules/chung.md`:
   - Bổ sung quy định: Khi người dùng yêu cầu Refactor, tái cấu trúc hoặc mở rộng kiến trúc, mục tiêu thiết kế sạch, tính module hóa và các nguyên lý SOLID đứng TRÊN luật phẫu thuật 1 dòng tối thiểu. Cấm Agent tự ý bẻ lái yêu cầu thành sửa tạm bợ.

4. **Chuẩn hóa Khối "Chủ đích Trước vs Sau" (Before / After Design Intent) trong Template**:
   - Cập nhật `skills/tdq-intake/references/analyze-full.md`, `skills/tdq-spec/references/spec-template.md` (§3) và `skills/tdq-plan/references/plan-template.md`: Bắt buộc nêu rõ kiến trúc hiện trạng (Trước) và kiến trúc mong muốn theo đúng chủ đích của người dùng (Sau).

### 2. Năng lực dùng được (Step B0)

Phân vân → DÙNG. Kiểm kê ngày 2026-10-20: 9 skill trên đĩa, cộng skill built-in trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-setup | plugin:tdq-workflow | NỀN | Cập nhật `KHOI_HUONG_DAN` ghim điều luật khảo sát 3 chiều vào `CLAUDE.md` |
| tdq-intake | plugin:tdq-workflow | NỀN | Chuẩn hóa quy trình khảo sát 3 chiều trong `analyze-full.md` |
| tdq-build | plugin:tdq-workflow | NỀN | Bổ sung ngoại lệ Refactor cho Rung 1 trong `chung.md` và thực thi TDD |
| tdq-spec | plugin:tdq-workflow | NỀN | Cập nhật khối Trước vs Sau trong `spec-template.md` |
| tdq-plan | plugin:tdq-workflow | NỀN | Cập nhật template plan bảng đối chiếu vùng chạm |
| Đã xét 20 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## Hỏi đáp
- Không có câu hỏi còn mở. Các giải pháp đã được thống nhất hoàn toàn.

### Lộ trình
- `spec` → `plan` → `implement` → `qc` → `report`
- Mức QC: `full` (Definition of Done 4 chiều: Grep tự do trong analyze, Kiểm tra tam giác 3 nguồn, Ngoại lệ Refactor cho Rung 1, Khối Trước vs Sau trong Spec/Plan).
