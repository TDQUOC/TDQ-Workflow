# Rule TypeScript / JavaScript

Soul: chất lượng > runtime > context cost. Nạp sau `chung.md`, áp cho
`.ts .tsx .js .jsx .mjs .cjs`.

## Nguồn

- typescript-eslint Shared Configs — https://typescript-eslint.io/users/configs (2026) —
  ba tầng config: `recommended` (bắt lỗi đúng đắn, dùng ngay) → `strict` → `stylistic`.
- Danh mục rule typescript-eslint — https://typescript-eslint.io/rules — rule gắn dấu ✅
  thuộc bộ recommended: `no-explicit-any`, `no-floating-promises`, `await-thenable`,
  `ban-ts-comment`, `no-misused-promises`…
- Rule core JavaScript — https://eslint.org/docs/latest/rules (ESLint docs latest) —
  `no-unused-vars`, `no-shadow`, `no-redeclare`, `no-self-compare`…

## Khi nào áp dụng

- Viết hoặc sửa file TS/JS bất kỳ, gồm cả file config `.mjs/.cjs` và test.
- Trước khi nộp: chạy mục "Tự kiểm"; máy thiếu `eslint` thì ghi "chưa kiểm được".

## Luật Intentionality

1. **`any` là mất chủ đích kiểu**: `no-explicit-any` thuộc bộ recommended — thay bằng
   kiểu cụ thể, hoặc `unknown` rồi thu hẹp dần bằng kiểm tra kiểu.
2. **Promise bỏ lơ lửng là nuốt lỗi**: mọi Promise phải được `await`, `return`, hoặc
   đánh dấu bỏ có chủ đích (`no-floating-promises`, `no-misused-promises`,
   `await-thenable` đều ✅ recommended).
3. **Code chết và giấu lỗi kiểu**: biến không dùng (`no-unused-vars`) → xoá; directive
   `@ts-ignore`/`@ts-expect-error` trần bị `ban-ts-comment` chặn — phải kèm mô tả lý do.

## Ngưỡng đo được

- Cyclomatic ≤ 10, cognitive ≤ 15 mỗi hàm — theo `chung.md`. Rule `complexity` của
  ESLint mặc định 20 nên phải chỉnh về 10 trong config, không dùng default.
- Tầng config tối thiểu: `recommended` (core ESLint + typescript-eslint); dự án muốn
  lên `strict`/`stylistic` thì ghi vào spec của request.

## Làm gì

1. Extend đúng tầng config: `eslint` recommended cho JS, cộng `tseslint` recommended
   cho TS; đừng tự chọn rule lẻ khi chưa dùng hết bộ recommended.
2. Khai kiểu rõ ở biên (tham số, giá trị trả về của hàm export); cấm `any` trần.
3. Hàm async gọi ở đâu thì nơi đó quyết định rõ: `await`, `return`, hay bỏ có chủ đích —
  cấm gọi rồi lờ kết quả.
4. Directive `@ts-` nào cũng phải có mô tả lý do ngay sau directive.
5. Chạy `eslint <đường dẫn>` và sửa hết lỗi bộ recommended.

## Tự kiểm

- [ ] `eslint` sạch lỗi, hoặc đã ghi "chưa kiểm được" khi máy thiếu eslint
- [ ] Không `any` trần, không Promise lơ lửng, không `@ts-` thiếu mô tả
- [ ] Không biến/import thừa; hàm export có kiểu ở biên
- [ ] Trả lời được 3 câu hỏi Intentionality trong `chung.md`

## Ví dụ ĐÚNG/SAI

```ts
// SAI — any trần, promise lơ lửng, ts-ignore không lý do:
// @ts-ignore
function save(d: any) { fetch("/api", { body: d }); }
// ĐÚNG — kiểu ở biên, promise được xử lý:
async function luuBanGhi(banGhi: BanGhi): Promise<void> {
  const res = await fetch("/api", { method: "POST", body: JSON.stringify(banGhi) });
  if (!res.ok) throw new Error(`Lưu thất bại: HTTP ${res.status}`);
}
```
