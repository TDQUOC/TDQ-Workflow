# Ranh giới luật: câu nào dịch được, câu nào phải giữ tiếng Việt

Ngày: 2026-08-19 · Request: 2026-08-19-1616-huong-a-dich-hybrid
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## 1. File này là gì

Lời khai cuối cùng cho từng mã `L###` của [luat-hien-co.md](luat-hien-co.md): dòng đó
thuộc phần LUẬT LÝ LUẬN (viết lại bằng tiếng Anh được) hay phần KHUÔN USER-FACING (phải
giữ nguyên tiếng Việt). Máy chỉ gợi ý — `scripts/luat_phan_loai.py` in bảng nháp — còn
bảng ở mục 5 là bản người soát đã chốt, và đó mới là thứ P3 phải tuân theo.

## 2. Tiêu chí phân loại

**user-facing** khi câu đó mang một chuỗi phải xuất hiện đúng từng chữ ở nơi user đọc:
khối duyệt in ra chat, option của câu hỏi, dòng khuôn chép vào spec/plan/report, tên mục
của artifact, hoặc câu khai báo ngôn ngữ đầu ra. **ly-luan** cho mọi câu còn lại — câu
dạy model cách nghĩ, cách quyết, cách kiểm.

Ba luật đi kèm, vì chúng quyết định vì sao con số ly-luan lớn đến vậy:

- Chuỗi nằm trong backtick (`[x]`, `Chạm:`, `DÙNG`, `➤ Duyệt:`) KHÔNG làm câu thành
  user-facing. Bản viết lại phải chép nguyên các chuỗi đó, nên chúng vẫn sống.
- Bảng tra dùng để model quyết (bảng phase, bảng lệch, bảng model/effort) là ly-luan,
  kể cả khi model tóm tắt nội dung bảng ra chat bằng tiếng Việt.
- Prompt giao cho agent con là agent-facing, không phải user-facing.

## 3. Số đo

| Nhãn | Số mã | Tỉ lệ |
|---|---|---|
| ly-luan | 291 | 88,4% |
| user-facing | 38 | 11,6% |
| **Tổng** | **329** | **100%** |

Máy gợi ý 80 mã user-facing; người soát hạ 43 mã và nâng 1 mã. Chỗ máy sai nhiều nhất là
luật "cả file là khuôn": `plan-template.md`, `spec-template.md`, `report-template.md` chứa
phần lớn là luật dạy cách viết tài liệu, chỉ vài dòng là khuôn thật.

## 4. Phát hiện phải nói thẳng

- **Câu khai báo ngôn ngữ gần như không nằm trong lưới.** Chỉ 3 mã (L031, L036, L311)
  chứa chữ "tiếng Việt". Câu "Mọi output cho user: tiếng Việt" ở đầu các skill không
  phải điểm neo, nên lưới không giữ nó. Hàng rào bù là luật R12 của `doc_lint.py` dựng ở
  P1: nó soi chính file sinh ra chứ không soi câu luật.
- **14 mã có số dòng đã lệch** so với file nguồn hiện tại, do các file đổi sau ngày kiểm
  kê (13 mã ở `context-budget.md`, 1 ở `team-mode.md`). Chữ neo thì vẫn còn nguyên trong
  file — bộ kiểm dò theo chữ nên vẫn xanh. Cột `file:dòng` chỉ còn giá trị tham khảo.
- **L096 lệch khoảng trắng**: bảng nén nhiều dấu cách thành một. Bộ kiểm chuẩn hoá khoảng
  trắng trước khi so nên không vỡ.

## 5. Bảng chốt

| Mã | Nhãn | Vì sao |
|---|---|---|
| L001 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L002 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L003 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L004 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L005 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L006 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L007 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L008 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L009 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L010 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L011 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L012 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L013 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L014 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L015 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L016 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L017 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L018 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L019 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L020 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L021 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L022 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L023 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L024 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L025 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L026 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L027 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L028 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L029 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L030 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L031 | user-facing | khai báo ngôn ngữ đầu ra của report |
| L032 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L033 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L034 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L035 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L036 | user-facing | khai báo ngôn ngữ đầu ra của report |
| L037 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L038 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L039 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L040 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L041 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L042 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L043 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L044 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L045 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L046 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L047 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L048 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L049 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L050 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L051 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L052 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L053 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L054 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L055 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L056 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L057 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L058 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L059 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L060 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L061 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L062 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L063 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L064 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L065 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L066 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L067 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L068 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L069 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L070 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L071 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L072 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L073 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L074 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L075 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L076 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L077 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L078 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L079 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L080 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L081 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L082 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L083 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L084 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L085 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L086 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L087 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L088 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L089 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L090 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L091 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L092 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L093 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L094 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L095 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L096 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L097 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L098 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L099 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L100 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L101 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L102 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L103 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L104 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L105 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L106 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L107 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L108 | user-facing | mang nguyên chữ `CẦN USER QUYẾT` in cho user |
| L109 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L110 | user-facing | mang nguyên câu hỏi in cho user |
| L111 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L112 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L113 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L114 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L115 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L116 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L117 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L118 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L119 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L120 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L121 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L122 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L123 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L124 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L125 | user-facing | đòi in lại nguyên văn khối user thấy |
| L126 | user-facing | nêu đúng thành phần của khối `➤ Duyệt:` |
| L127 | user-facing | cấm rút gọn option in cho user |
| L128 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L129 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L130 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L131 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L132 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L133 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L134 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L135 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L136 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L137 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L138 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L139 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L140 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L141 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L142 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L143 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L144 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L145 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L146 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L147 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L148 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L149 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L150 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L151 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L152 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L153 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L154 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L155 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L156 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L157 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L158 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L159 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L160 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L161 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L162 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L163 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L164 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L165 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L166 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L167 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L168 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L169 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L170 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L171 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L172 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L173 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L174 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L175 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L176 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L177 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L178 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L179 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L180 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L181 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L182 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L183 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L184 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L185 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L186 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L187 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L188 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L189 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L190 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L191 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L192 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L193 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L194 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L195 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L196 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L197 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L198 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L199 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L200 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L201 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L202 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L203 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L204 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L205 | user-facing | cả file `user-facing-block.md` là khuôn cho user |
| L206 | user-facing | cả file `user-facing-block.md` là khuôn cho user |
| L207 | user-facing | cả file `user-facing-block.md` là khuôn cho user |
| L208 | user-facing | cả file `user-facing-block.md` là khuôn cho user |
| L209 | user-facing | cả file `user-facing-block.md` là khuôn cho user |
| L210 | user-facing | cả file `user-facing-block.md` là khuôn cho user |
| L211 | user-facing | cả file `user-facing-block.md` là khuôn cho user |
| L212 | user-facing | cả file `user-facing-block.md` là khuôn cho user |
| L213 | user-facing | cả file `user-facing-block.md` là khuôn cho user |
| L214 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L215 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L216 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L217 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L218 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L219 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L220 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L221 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L222 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L223 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L224 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L225 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L226 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L227 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L228 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L229 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L230 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L231 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L232 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L233 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L234 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L235 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L236 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L237 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L238 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L239 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L240 | user-facing | dòng bảng so sánh 2 lane in cho user |
| L241 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L242 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L243 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L244 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L245 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L246 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L247 | user-facing | mang nguyên dòng `➤ Duyệt:` của chế độ nhanh |
| L248 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L249 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L250 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L251 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L252 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L253 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L254 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L255 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L256 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L257 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L258 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L259 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L260 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L261 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L262 | user-facing | ô option của vòng scope in cho user |
| L263 | user-facing | bắt in đúng một dòng cho user |
| L264 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L265 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L266 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L267 | user-facing | dòng bảng §3b chép vào spec |
| L268 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L269 | user-facing | dòng ví dụ của bảng §3b |
| L270 | user-facing | ô lý do đóng, chép nguyên vào spec |
| L271 | user-facing | ô lý do đóng, chép nguyên vào spec |
| L272 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L273 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L274 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L275 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L276 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L277 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L278 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L279 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L280 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L281 | user-facing | mang nguyên câu chú thích in cho user |
| L282 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L283 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L284 | user-facing | đòi khuôn hỏi mode nguyên văn |
| L285 | user-facing | mang nguyên tên đoạn `Vì sao đề xuất` |
| L286 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L287 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L288 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L289 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L290 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L291 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L292 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L293 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L294 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L295 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L296 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L297 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L298 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L299 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L300 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L301 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L302 | user-facing | dòng khuôn hợp đồng 5 trường, chép vào plan |
| L303 | user-facing | dòng khuôn hợp đồng 5 trường, chép vào plan |
| L304 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L305 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L306 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L307 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L308 | user-facing | khuôn task log service, chép vào plan |
| L309 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L310 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L311 | user-facing | khai báo ngôn ngữ đầu ra của spec |
| L312 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L313 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L314 | user-facing | mang nguyên tên mục `câu hỏi còn mở` của spec |
| L315 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L316 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L317 | user-facing | nối tiếp câu chú thích in cho user |
| L318 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L319 | ly-luan | không thấy dấu hiệu user-facing trong câu |
| L320 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L321 | user-facing | placeholder trong khuôn spec §2 |
| L322 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L323 | user-facing | dòng bảng §3b chép vào spec |
| L324 | user-facing | dòng DoD chép nguyên vào spec |
| L325 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L326 | user-facing | mang nguyên tên khối `Ràng buộc kiến trúc phải giữ` |
| L327 | user-facing | mang nguyên câu phải ghi vào spec |
| L328 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
| L329 | ly-luan | luật dạy cách viết, không phải chữ user đọc |
