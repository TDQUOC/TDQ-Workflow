# Research — codex --output-schema bị bỏ qua với provider tuỳ chỉnh
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-09-14 · Bối cảnh: `codex-cli 0.154.0`, `codex exec --output-schema <schema> -o <result.json>`, provider `9router` (`wire_api = "responses"`), model `ag/gemini-3.8-flash-medium`, schema `{"type":"object","properties":{"xong":{"type":"boolean"}},"required":["xong"]}`. Hiện tượng: exit 0, file `-o` chứa một câu tiếng Anh, không phải JSON.

Lưu ý phương pháp: mã nguồn codex đọc từ nhánh `main` (raw.githubusercontent.com) tại ngày research, KHÔNG phải tag 0.154.0. Mã 9router đọc từ `decolua/9router` HEAD. Không đọc file config/secret local nào.

---

## Q1. `codex exec --output-schema` hoạt động thế nào bên trong?

**Query/nguồn**
- tavily: "codex exec --output-schema ignored custom model provider JSON not returned" (github.com)
- tavily: "codex output-schema gemini OR openrouter OR wire_api structured output not supported custom provider issue"
- Source codex (main):
  - https://github.com/openai/codex/blob/main/codex-rs/codex-api/src/common.rs (`create_text_param_for_request`)
  - https://github.com/openai/codex/blob/main/codex-rs/core/src/client.rs (dựng `ResponsesApiRequest`, khoảng dòng 855–900)
  - https://github.com/openai/codex/blob/main/codex-rs/core/src/client_common.rs (`output_schema_strict` mặc định `true`)
  - https://github.com/openai/codex/blob/main/codex-rs/exec/tests/suite/output_schema.rs (test assert payload)
  - https://github.com/openai/codex/blob/main/codex-rs/exec/src/lib.rs (`load_output_schema` → `InitialOperation::UserTurn { output_schema }`)
- Issues:
  - https://github.com/openai/codex/issues/4181 (0.41.0: schema bị bỏ vì guard `model_family == "gpt-5"`, đã sửa)
  - https://github.com/openai/codex/issues/15451 (schema bị bỏ qua khi có tools/MCP, nhãn `model-behavior`)
  - https://github.com/openai/codex/issues/19816 (schema áp cho cả message trung gian, không chỉ message cuối)
  - https://github.com/openai/codex/issues/38545 (`codex exec review` nhận nhưng bỏ qua `--output-schema`, vẫn exit 0)
  - https://github.com/openai/codex/issues/14343 (`exec resume` không nhận `--output-schema`)
  - https://github.com/nickderobertis/oneharness ("reportedly ignored once the agent uses tools")

**Rút ra**
- Codex KHÔNG chèn schema vào prompt. Nó gửi schema qua field `text.format` của Responses API: `{"name":"codex_output_schema","type":"json_schema","strict":true,"schema":<schema nguyên văn>}`. Test `exec_includes_output_schema_in_request` assert đúng payload này.
- Ở `client.rs` (main), `create_text_param_for_request(verbosity, &prompt.output_schema, prompt.output_schema_strict)` được gọi vô điều kiện. Không còn guard theo model family (guard cũ ở #4181 đã bị bỏ) và không phụ thuộc provider. Nghĩa là với `model_providers` tuỳ chỉnh, `wire_api = "responses"`, codex vẫn gửi `text.format` tới base_url của provider. Còn provider có tôn trọng field đó hay không là việc của provider.
- Codex không kiểm hậu kiểm (post-validate) output theo schema. Không thấy code nào validate message cuối rồi trả exit code ≠ 0. Issue #38545 và #15451 đều mô tả exit 0 dù output sai schema. Ràng buộc hoàn toàn dựa vào server (constrained decoding).
- `wire_api = "chat"`: issue #13628 cho thấy default hiện là `responses`. Không tìm được nguồn xác nhận cách `chat` map `output_schema` sang `response_format` ở bản hiện tại. Trong `client.rs` (main) chỉ thấy nhánh `WireApi::Responses`.
- Không tìm thấy issue codex nào nói riêng về "schema bị bỏ qua với Gemini/9router". Các issue gần nhất là #15451 (khi có tools) và #9863 (OpenRouter, lỗi khác).

## Q2. Strict json_schema có bắt buộc `additionalProperties: false` không?

**Query/nguồn**
- tavily: "OpenAI structured outputs strict json_schema additionalProperties false required all fields" (openai domains)
- https://developers.openai.com/api/docs/guides/structured-outputs ("`additionalProperties: false` must always be set in objects")
- https://github.com/openai/codex/blob/main/docs/exec.md ("The JSON Schema must follow the strict schema rules", schema mẫu có `additionalProperties: false`)
- https://gist.github.com/alexfazio/359c17d84cb6a5af12bac88fa1db9770 (thử thực tế với OpenAI: `ERROR: Invalid schema for response_format 'codex_output_schema': In context=(), 'additionalProperties' is required to be supplied and to be false.`)
- https://community.openai.com/t/schema-additionalproperties-must-be-false-when-strict-is-true/929996

**Rút ra**
- Với OpenAI thật, `strict: true` bắt buộc `additionalProperties: false` ở mọi object và `required` phải liệt kê mọi key. Thiếu thì server trả lỗi 400 rõ ràng, schema không bị bỏ qua âm thầm. Codex hiển thị lỗi `ERROR: Invalid schema ...` (theo gist).
- Codex không tự sửa hay lọc schema: `schema.clone()` gửi nguyên văn. Schema của request thiếu `additionalProperties: false`, nên sẽ bị OpenAI từ chối, không bị "drop".
- Trong ca này output là câu tiếng Anh và exit 0, không có lỗi 400. Như vậy upstream không hề validate schema, khớp với giả thuyết 9router bỏ `text.format` (xem Q3). Thiếu `additionalProperties` KHÔNG phải nguyên nhân gốc ở đường 9router→Antigravity, nhưng vẫn là lỗi tiềm ẩn nếu sau này chuyển sang OpenAI thật.

## Q3. 9router là gì, có chuyển tiếp `text.format`/`response_format` sang Gemini không?

**Query/nguồn**
- tavily: "9router AI coding router proxy Codex Claude Code Gemini providers github"
- tavily: "9router response_format json_schema structured output ignored issue" (không có issue liên quan)
- https://github.com/decolua/9router (README: proxy local `localhost:20128`, 40+ provider, "format translation OpenAI/Claude/Gemini")
- Source 9router HEAD:
  - https://github.com/decolua/9router/blob/HEAD/open-sse/providers/registry/antigravity.js (`id: "antigravity"`, `alias: "ag"`, `gemini-3.8-flash-medium` → upstream `gemini-3.8-flash-medium(medium)`)
  - https://github.com/decolua/9router/blob/HEAD/open-sse/translator/request/openai-responses.js (Responses → Chat Completions)
  - https://github.com/decolua/9router/blob/HEAD/open-sse/translator/request/openai-to-gemini.js (Chat → Gemini/Cloud Code envelope)
  - https://github.com/decolua/9router/blob/HEAD/open-sse/executors/antigravity.js
  - https://github.com/decolua/9router/blob/HEAD/open-sse/executors/default.js (`applyJsonSchemaFallback`)
  - https://github.com/decolua/9router/blob/HEAD/open-sse/translator/request/openai-to-claude.js

**Rút ra**
- 9router (decolua/9router) là proxy/router local cho các AI coding tool. Prefix `ag/` là provider **Antigravity** (Google Cloud Code, model Gemini), không phải Gemini API trực tiếp.
- Luồng request của codex là: Responses (`text.format`) → `openaiResponsesToOpenAIRequest` → Chat Completions → `openaiToGeminiBase` → envelope Cloud Code (`wrapInCloudCodeEnvelope`, `userAgent: "antigravity"`, `requestType: "agent"`).
- `openai-responses.js` làm `const result = { ...body }` rồi xoá `input/instructions/include/store/reasoning/...`. Field `text` bị giữ nguyên nhưng **không được chuyển** thành `response_format`. Grep toàn bộ `open-sse/` (382 file JS) không có chỗ nào đọc `text.format` / `text?.format`.
- `openai-to-gemini.js` dựng `generationConfig` chỉ từ `temperature`, `top_p`, `top_k`, `max_tokens`. Không map `response_format` sang `responseMimeType`/`responseSchema`/`responseJsonSchema`. Envelope Antigravity chỉ lấy `contents/systemInstruction/generationConfig/tools`, nên mọi field khác bị rơi. Grep `responseSchema|responseJsonSchema|responseMimeType` trên toàn `open-sse/`: 0 kết quả.
- Chỗ duy nhất 9router xử lý `response_format` json_schema: (a) `openai-to-claude.js` chèn schema vào system prompt; (b) `default.js` `applyJsonSchemaFallback` chỉ cho provider `openai-compatible-*` (chèn prompt + `json_object`). Cả hai đều không áp cho Antigravity/Gemini, và đều dựa trên `response_format` (Chat), không phải `text.format` (Responses).
- Kết luận: với `ag/gemini-*`, schema của codex bị 9router **bỏ âm thầm**. Model nhận prompt không có ràng buộc, trả văn xuôi, codex ghi nguyên văn ra `-o` và exit 0.

## Q4. Gemini endpoint OpenAI-compatible có hỗ trợ structured output không?

**Query/nguồn**
- tavily: "Gemini OpenAI compatibility response_format json_schema structured outputs" (ai.google.dev)
- https://ai.google.dev/gemini-api/docs/openai (mục "Structured output")
- https://ai.google.dev/gemini-api/docs/structured-output (subset JSON Schema)
- https://discuss.ai.google.dev/t/structured-outputs-in-batch-using-openai-compatibility-mode/126309 (real-time `response_format: json_schema` chạy được, Batch thì bị từ chối)
- https://discuss.ai.google.dev/t/openai-badrequesterror-error-code-400-when-try-to-generate-structured-nested-output/70246 (chỉ hỗ trợ một subset schema, có thể lỗi 400)

**Rút ra**
- Endpoint OpenAI-compatible của Gemini API **có** hỗ trợ `response_format` `json_schema` trên Chat Completions (real-time), với subset JSON Schema. Gemini native dùng `responseMimeType` + `responseSchema`/`responseJsonSchema`.
- Nhưng 9router `ag/` không đi qua endpoint này mà qua Cloud Code/Antigravity, và 9router không map field. Khả năng hỗ trợ của Gemini vì vậy không cứu được ca này.
- Chưa xác nhận: Gemini có hỗ trợ Responses API `text.format` hay không (tài liệu chỉ nói Chat Completions).

## Q5. `codex exec -o/--output-last-message` ghi gì? Có `--json` thay thế không?

**Query/nguồn**
- tavily: "codex exec output-last-message writes final agent message; --output-schema documentation non-interactive"
- https://developers.openai.com/codex/guides/autofix-ci ("Non-interactive mode": `-o` ghi final message ra file và vẫn in ra stdout)
- https://github.com/openai/codex/blob/main/docs/exec.md
- https://github.com/openai/codex/blob/main/codex-rs/exec/src/event_processor.rs (`handle_last_message`)
- https://github.com/openai/codex/blob/main/codex-rs/exec/src/event_processor_with_jsonl_output.rs, `event_processor_with_human_output.rs`

**Rút ra**
- `-o` ghi **nguyên văn** message agent cuối (`std::fs::write(path, contents)`), không parse hay validate JSON. Nếu không có message cuối thì ghi chuỗi rỗng và in cảnh báo `Warning: no last agent message; wrote empty content to ...` ra stderr. Lỗi ghi file chỉ in ra stderr, không đổi exit code.
- Cả chế độ human lẫn `--json` (JSONL) đều gọi cùng `handle_last_message`, nên `-o` giống nhau ở cả hai mode.
- `--json` phát luồng sự kiện JSONL (các event `agent_message`...). Nó không có "structured final output" riêng: nội dung vẫn là text do model sinh ra. #19816 cảnh báo khi dùng `--json --output-schema`, message trung gian cũng mang dạng schema, nên phải lấy message cuối chứ không phải message JSON-hợp-lệ đầu tiên.
- Hệ quả: wrapper phải tự `json.loads` + validate schema file `-o`, rồi coi sai là FAIL. Không được tin exit 0.

---

## Kết luận cho request

**CONFIRMED (có nguồn)**
1. Codex gửi schema qua Responses `text.format` = `{type:"json_schema", name:"codex_output_schema", strict:true, schema}`, vô điều kiện theo provider (bản main). Nguồn: `codex-api/src/common.rs`, `core/src/client.rs`, `exec/tests/suite/output_schema.rs`.
2. Codex không post-validate output theo schema. `-o` ghi nguyên văn message cuối, exit 0 dù sai schema. Nguồn: `exec/src/event_processor.rs`, issues #38545, #15451.
3. Model `ag/*` trong 9router là provider Antigravity (Cloud Code/Gemini). Nguồn: `open-sse/providers/registry/antigravity.js`.
4. 9router không chuyển `text.format` (Responses) sang bất kỳ dạng ràng buộc nào cho Gemini/Antigravity. `generationConfig` chỉ có temperature/topP/topK/maxOutputTokens, không có `responseSchema`/`responseMimeType` ở bất cứ đâu trong `open-sse/`. Fallback prompt-injection chỉ có cho Claude và `openai-compatible-*`, dựa trên `response_format`. Nguồn: `translator/request/openai-responses.js`, `openai-to-gemini.js`, `executors/antigravity.js`, `executors/default.js`, `openai-to-claude.js`.
   → Đây là nguyên nhân gốc khả dĩ nhất cho việc file `-o` chứa văn xuôi.
5. OpenAI strict yêu cầu `additionalProperties:false` + `required` đủ key. Thiếu thì bị lỗi 400 rõ ràng, không bị bỏ âm thầm. Schema hiện tại thiếu `additionalProperties:false`, nên sẽ fail nếu chạy qua OpenAI thật. Nguồn: developers.openai.com structured-outputs, gist alexfazio, codex `docs/exec.md`.
6. Gemini API OpenAI-compatible hỗ trợ `response_format: json_schema` (Chat Completions, subset schema). Nguồn: ai.google.dev/gemini-api/docs/openai, forum Google.

**UNCONFIRMED**
- Hành vi chính xác của tag `0.154.0`: chỉ đọc nhánh main. Chưa đối chiếu tag, nhưng guard model-family đã bị bỏ từ khoảng 0.42 (#4181).
- Bản 9router đang cài local có trùng HEAD không. Chưa kiểm version local, chưa bắt payload thực tế (bật `ENABLE_REQUEST_LOGS=true` của 9router để xác minh).
- `wire_api = "chat"` ở codex hiện tại có còn được hỗ trợ không, và có map `output_schema` sang `response_format` không.
- Antigravity/Cloud Code upstream có nhận `responseSchema` trong `generationConfig` không (nếu 9router có map).
- Hướng xử lý gợi ý (chưa kiểm chứng): (a) wrapper tự validate JSON và schema của file `-o`, sai thì FAIL hoặc retry; (b) nhét yêu cầu JSON + schema vào chính prompt; (c) bổ sung `additionalProperties:false` vào schema; (d) cân nhắc provider/model tôn trọng `text.format` khi cần ràng buộc cứng.
