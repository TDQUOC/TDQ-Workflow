# AUDIT — rà soát tối ưu workflow sau khi chuyển sang tiếng Anh

Ngày đo: 2026-08-22 · Request: `2026-08-22-1231-ra-soat-toi-uu-workflow` · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Phạm vi đo: `skills/**` + `agents/*.md` + `docs/claude-md-mau.md`

Hồ sơ này CHỈ đo và đề xuất. Không sửa một dòng luật nào. Mọi con số dưới đây đều kèm
lệnh sinh ra nó, chạy lại được.

Quy ước bộ đếm: chỗ nào ghi "bộ đếm thật" là dùng `anthropic-tokenizer` trong
`.venv-tokens` qua `scripts/skill_tokens.py`. Chỗ nào dùng `scripts/context_surface.py`
thì đó là ƯỚC LƯỢNG theo `BYTES_PER_TOKEN = 4` (dòng 40 của file ấy), và hồ sơ nói rõ
mỗi lần.

## Phát hiện chặn — bản chạy thật KHÔNG phải bản trong repo

Đây là câu trả lời trực tiếp cho câu hỏi "giữ đúng behavior không?". Trước khi bàn tối
ưu, phải biết cái đang chạy là cái nào.

| Chỉ số | Repo | Bản Claude Code nạp lúc chạy |
|---|---|---|
| Version | 0.28.0 | 0.19.0 |
| Ngày cập nhật | hôm nay | 2026-08-15 |
| Số file `.md` trong `skills/` | 44 | 39 |
| `tdq-build/SKILL.md` | tiếng Anh | tiếng Việt |

Nguồn: `cat ~/.claude/plugins/installed_plugins.json` · `find skills -name '*.md' | wc -l` ·
`find ~/.claude/plugins/cache/tdq-local/tdq-workflow/0.19.0/skills -name '*.md' | wc -l`

Năm file chỉ có ở repo, bản cache không có:
`skills/tdq-build/references/team-mode.md` · `skills/tdq-check-status/SKILL.md` ·
`skills/tdq-check-status/references/bang-lech.md` ·
`skills/tdq-check-status/references/report-template.md` ·
`skills/tdq-conventions/references/clean-code.md`

Hệ quả: toàn bộ đợt chuyển sang tiếng Anh chưa hề có mặt lúc chạy. Mọi số đo về
"behavior sau khi chuyển" chỉ đúng cho repo, chưa đúng cho phiên làm việc thật. Cách gỡ
nằm ngoài phạm vi hồ sơ này (không sửa file skill), nhưng phải làm trước khi áp bất kỳ
đề xuất nào: cài lại plugin từ marketplace `tdq-local` để cache bắt kịp 0.28.0.

## Mốc nền

Ba tầng nạp. Đây là số ƯỚC LƯỢNG theo 4 byte một token, không phải bộ đếm thật:

| Tầng | Token (ước lượng) | Nạp khi nào |
|---|---|---|
| Luôn nạp | 1.452 | mọi phiên, không tránh được |
| Nạp khi gọi skill | 10.785 | mỗi lần một skill `tdq-*` được kích hoạt |
| Đọc theo yêu cầu | 50.064 | chỉ khi skill trỏ vào file reference |

Nguồn: `python3 scripts/context_surface.py --quiet`

Trần một request lane full, đo bằng bộ đếm thật:

| Chỉ số | Giá trị |
|---|---|
| Trần token một request lane full | 59.486 |

Nguồn: `python3 scripts/skill_tokens.py --theo-phase`

Năm file nặng nhất trong vùng đo, xếp bằng bộ đếm thật (khác thứ hạng của
`context_surface.py`, vì bộ ước lượng 4 byte đếm chữ có dấu sai lệch):

| File | Token |
|---|---|
| `skills/tdq-plan/references/plan-template.md` | 4.327 |
| `skills/tdq-intake/references/quick-lane.md` | 3.571 |
| `skills/tdq-spec/references/spec-template.md` | 3.394 |
| `skills/tdq-build/references/team-mode.md` | 3.175 |
| `skills/tdq-conventions/SKILL.md` | 2.948 |
| **Tổng cả vùng đo** | **68.937** |

Nguồn: `python3 -c "import sys,glob; sys.path.insert(0,'scripts'); import skill_tokens as st; f=sorted(glob.glob('skills/**/*.md',recursive=True))+sorted(glob.glob('agents/*.md'))+['docs/claude-md-mau.md']; t=st.dem_qua_venv([open(p).read() for p in f]); [print(x,p) for x,p in sorted(zip(t,f),reverse=True)[:5]]; print(sum(t))"`

## Mặt A — context cost

Ba khoản phình đo được, tất cả đều là chuyện CÁCH VIẾT, không đụng nội dung luật. Cột
token đo bằng bộ đếm thật trên đúng những dòng được đếm ở cột số lượng.

| Khoản | Số lượng | Token |
|---|---|---|
| Chú thích `i18n-allow` (tính cả 11 cái đã ở dạng trần) | 219 dòng | 3.105 |
| Khối mục lục trong file skill | 13 khối | 1.270 |
| Ghi chú "deliberate repetition" | 6 dòng | 124 |

Nguồn: `python3 -c "import sys,glob,re; sys.path.insert(0,'scripts'); import skill_tokens as st; f=sorted(glob.glob('skills/**/*.md',recursive=True))+sorted(glob.glob('agents/*.md'))+['docs/claude-md-mau.md']; L=[l for p in f for l in open(p).read().splitlines()]; a=[re.search('<!--.*?i18n-allow.*?-->',l).group(0) for l in L if 'i18n-allow' in l]; print(len(a), sum(st.dem_qua_venv(a)))"`

Chi tiết khoản nặng nhất: trong 219 chú thích, 208 cái viết kèm lý do dạng
`<!-- i18n-allow: canonical spec section names -->`, 11 cái đã ở dạng trần.
`scripts/i18n_check.py` dòng 121 kiểm `ALLOW_MARKER in stripped` và dòng 137 kiểm
`ALLOW_MARKER in text` — cả hai đều so khớp CHUỖI CON, nên marker trần
`<!-- i18n-allow -->` vẫn qua, không phải sửa một dòng công cụ nào.

Nguồn: `sed -n '32p;121p;137p' scripts/i18n_check.py`

Rút gọn cả 219 chú thích về marker trần: 3.105 → 1.533 token, tiết kiệm 1.572.
Đánh đổi: mất phần lý do dành cho người đọc. Giữ lý do ở chỗ khó đoán, rút gọn chỗ lặp
đi lặp lại (riêng cụm `canonical spec section names` lặp 11 lần trong một file).

Về mục lục: 13 khối, nhưng 2 khối nằm BÊN TRONG khối khuôn của `spec-template.md` (dòng
20) và `plan-template.md` (dòng 20) — chúng là nội dung sinh ra file spec/plan chứ không
phải mục lục của chính file skill, phải giữ. Mười một khối còn lại là mục lục thật của
file, xoá được, cộng lại 764 token. Không luật nào của `doc_lint.py` bắt buộc mục lục.

Nguồn: `grep -n 'Mục lục' scripts/doc_lint.py` (rỗng)

## Mặt B — trùng lặp và luật chồng luật

Đo bằng `scripts/doc_dup.py` viết trong request này: băm N dòng liên tiếp đã chuẩn hoá,
gộp các cửa sổ nối nhau thành một khối, đếm token bằng bộ đếm thật.

| Ngưỡng | Số khối trùng | Token |
|---|---|---|
| ≥ 3 dòng | 8 | 472 |
| ≥ 2 dòng | 59 | 1.378 |

Nguồn: `python3 scripts/doc_dup.py --vung skills --vung agents --vung docs/claude-md-mau.md --quiet --top 15`
và cùng lệnh đó thêm `--min-dong 2`

Cặp nặng nhất: `skills/tdq-conventions/references/user-facing-block.md:129` ↔
`skills/tdq-spec/SKILL.md:48`, 6 dòng, 140 token. Đây là khối chat mẫu chép hai nơi.

Phần chênh giữa hai ngưỡng — 51 khối, 906 token — phần lớn là khuôn hai dòng lặp lại
(dòng `Soul:`, dòng `Xong khi:`/`Bước kế tiếp:`). Nhóm này rủi ro cao hơn khi gộp: một
số khuôn lặp là CỐ Ý, để agent đọc lẻ một file vẫn thấy đủ luật.

Sáu chỗ đã tự khai "deliberate repetition" chính là nhóm cố ý ấy. Chúng cần giữ nội
dung, chỉ rút gọn được cách ghi chú.

## Mặt C — runtime

Đo trên ba phiên đã đóng, chép ra thư mục tạm để không tính phiên đang chạy. Ba phiên
đó là `d64f9bf9` · `a08c5f39` · `67f134a1`.

| Chỉ số | Giá trị |
|---|---|
| Tổng số bước | 1.555 |
| Tool call trên mỗi turn | 1,04 |
| Lần đọc lại file đã đọc | 30 |
| Thời gian mỗi bước, trung vị | 4,6 giây |
| Thời gian mỗi bước, p90 | 16,1 giây |

Nguồn: chép ba file `d64f9bf9*.jsonl`, `a08c5f39*.jsonl`, `67f134a1*.jsonl` từ
`~/.claude/projects/-Users-truongdinhquoc-Documents-TDQWorkflow/` vào một thư mục tạm,
rồi `python3 scripts/step_audit.py --transcript-dir <thư mục tạm> --sessions 3`

Con số 1,04 là phát hiện đáng kể nhất của mặt này. Luật gom nhiều tool call độc lập vào
một turn gần như KHÔNG bao giờ được áp: trung bình mỗi turn chỉ có một tool call. Ba mươi
lần đọc lại file đã đọc là hệ quả cùng gốc.

Luật gom hiện không nằm trong bất kỳ SKILL.md nào của `tdq-*` — nó đến từ prompt hệ thống
của harness. Vì vậy đề xuất ở mặt này là ĐƯA luật ấy vào chỗ agent chắc chắn đọc, không
phải sửa luật.

Vị trí luật cứng trong file, đối chiếu với kết quả research (luật cứng đặt giữa file mất
30–50% mức tuân thủ, nguồn `docs/tdq/research/2026-08-22-1231-ra-soat-toi-uu-workflow.md`).
Định nghĩa dùng để đếm: một dòng là "luật cứng" khi nó chứa một trong tám từ khoá
`MUST` · `NEVER` · `ALWAYS` · `BANNED` · `is banned` · `are banned` · `BẮT BUỘC` · `CẤM`;
"nằm giữa" là dòng có số thứ tự trong khoảng 20%–80% độ dài file.

| Chỉ số | Giá trị |
|---|---|
| Dòng luật cứng trong 7 file `skills/tdq-*/SKILL.md` | 22 |
| Nằm ở 60% giữa file | 11 (50%) |
| File tệ nhất: `tdq-spec/SKILL.md` | 3/3 nằm giữa |
| File tệ nhì: `tdq-conventions/SKILL.md` | 2/3 nằm giữa |

Nguồn tổng: `grep -chE 'MUST|NEVER|ALWAYS|BANNED|is banned|are banned|BẮT BUỘC|CẤM' skills/tdq-*/SKILL.md | paste -sd+ - | bc`
Nguồn vị trí: chạy đoạn sau, in ra `22 11`:

```
python3 -c "
import glob,re
p=re.compile(r'MUST|NEVER|ALWAYS|BANNED|is banned|are banned|BẮT BUỘC|CẤM')
t=m=0
for f in glob.glob('skills/tdq-*/SKILL.md'):
    L=open(f).read().splitlines(); n=len(L)
    for i,l in enumerate(L,1):
        if p.search(l):
            t+=1; m+= 0.2*n<=i<=0.8*n
print(t,m)
"
```

## Mặt D — chất lượng bản dịch tiếng Anh

Đợt chuyển giữ đúng ranh giới ba tầng: luật trong `skills/**` và `agents/*.md` sang
tiếng Anh, tài liệu và hội thoại giữ `doc_lang`. Kiểm máy sạch.

| Kiểm | Kết quả |
|---|---|
| `i18n_check.py --kind comment` | 0 vi phạm |
| `i18n_check.py --kind string` | 0 vi phạm |
| `i18n_check.py --kind body` | 0 vi phạm |

Nguồn: `for k in comment string body; do python3 scripts/i18n_check.py --kind $k scripts hooks skills agents; done`

Phạm vi kiểm là bốn thư mục luật. `docs/claude-md-mau.md` nằm ngoài: nó là TÀI LIỆU nên
viết bằng `doc_lang`, và kiểm `--kind body` trên nó báo 42 dòng tiếng Việt đúng như thiết
kế, không phải vi phạm.

Ba điểm bản dịch còn nặng hơn bản gốc, đo được bằng token:

Thứ nhất, 219 chú thích `i18n-allow` là chi phí SINH RA bởi đợt chuyển — bản tiếng Việt
trước đây không có dòng nào. Đây là 3.105 token mới hoàn toàn.

Thứ hai, tên mục vẫn giữ tiếng Việt trong câu tiếng Anh (`Lộ trình`, `Ranh giới module`,
`Chạm:`, `Mode thực thi`), mỗi lần dùng kéo theo một chú thích `i18n-allow`. Đây là lựa
chọn ĐÚNG — tên mục là định danh máy đọc, dịch đi là vỡ. Cái tối ưu được là chú thích,
không phải cái tên.

Thứ ba, câu tiếng Anh trong SKILL.md dài hơn bản Việt cùng nghĩa. Ví dụ đo được ở
`skills/tdq-plan/SKILL.md` bước 1 (dòng 15–30): bản hiện tại dùng 16 dòng cho một ý.
Rút gọn được mà không mất một luật nào, vì phần thừa là câu nối chứ không phải điều kiện.

## Top 10 đề xuất

Xếp theo token tiết kiệm giảm dần. Mọi đề xuất ở đây chỉ đụng CÁCH VIẾT. Đề xuất nào
động tới nội dung một luật đã bị loại khỏi bảng trước khi xếp hạng.

| # | Đề xuất | Token tiết kiệm | Luật gốc bị chạm | Phép kiểm bắt được nếu vỡ | Rủi ro |
|---|---|---|---|---|---|
| 1 | Rút 219 chú thích `i18n-allow` còn marker trần `<!-- i18n-allow -->` | 1.572 | luật ngôn ngữ ba tầng (`skills/tdq-build/references/rules/`) | `for k in comment string body; do python3 scripts/i18n_check.py --kind $k scripts hooks skills agents; done` ra 0 vi phạm cả ba lần | thấp |
| 2 | Rút câu nối thừa trong thân bảy `skills/tdq-*/SKILL.md`, giữ nguyên mọi điều kiện | 850 | không — chỉ cắt câu nối, không cắt điều kiện | `python3 scripts/tdq_eval.py chay --nhanh ca-hai` giữ nguyên điểm tuân thủ | trung bình |
| 3 | Dời phần ít dùng của `skills/tdq-conventions/SKILL.md` xuống `references/`, để lại con trỏ | 800 | luật nạp conventions đầu mọi skill (`skills/tdq-conventions/SKILL.md`) | `python3 scripts/context_surface.py --quiet` tầng nạp-khi-gọi-skill giảm, tầng đọc-theo-yêu-cầu tăng đúng bằng đó | trung bình |
| 4 | Xoá 11 khối mục lục thật trong file skill, giữ 2 khối nằm trong khuôn spec/plan | 764 | không — `doc_lint.py` không có luật mục lục | `python3 scripts/doc_lint.py` trên một spec và một plan mẫu vẫn thoát 0 | thấp |
| 5 | Cắt ví dụ dài trùng khuôn trong `skills/tdq-intake/references/quick-lane.md` | 400 | chín bước thi hành lane quick (`quick-lane.md`) | chạy một request lane quick đầu-cuối, đủ chín bước | trung bình |
| 6 | Gộp 8 khối trùng nguyên văn ≥3 dòng về một nơi, chỗ còn lại để link | 330 | khối chat 5 thành phần (`user-facing-block.md`) | `python3 scripts/doc_dup.py --vung skills --vung agents --vung docs/claude-md-mau.md` còn 0 khối ≥3 dòng | trung bình |
| 7 | Gộp nhóm khuôn `Xong khi:`/`Bước kế tiếp:` trùng 2 dòng, chừa các chỗ lặp cố ý | 300 | luật mỗi skill khai `Xong khi:` và `Bước kế tiếp:` (`skills/tdq-conventions/SKILL.md`) | `python3 scripts/doc_lint.py --pair <spec> <plan>` thoát 0, và mỗi SKILL.md còn đủ hai dòng | cao |
| 8 | Rút 6 ghi chú "deliberate repetition" thành ký hiệu ngắn `(rep: <file>)` | 82 | luật lặp có chủ ý (`skills/tdq-conventions/SKILL.md`) | `grep -rc 'rep:' skills` còn đúng 6 chỗ đánh dấu, không mất chỗ nào | thấp |
| 9 | Dời 11 dòng luật cứng đang nằm giữa file lên đầu hoặc cuối bảy SKILL.md | 0 | không — chỉ đổi vị trí, giữ nguyên chữ | `python3 scripts/tdq_eval.py chay --nhanh ca-hai --lan 3` điểm tuân thủ không giảm | trung bình |
| 10 | Đưa luật gom tool call độc lập vào một turn lên đầu `skills/tdq-build/SKILL.md` | 0 (ghi thêm ~40) | không — luật mới đến từ harness, không sửa luật cũ | `python3 scripts/step_audit.py` số tool call mỗi turn tăng trên 1,04 | thấp |

Tổng token tiết kiệm ước tính: **5.098**, bằng **8,6%** của trần 59.486 token một request
lane full. Riêng dòng 3 là chuyển tầng chứ không xoá chữ: nó bớt 800 token ở tầng nạp mỗi
lần gọi skill, và cộng đúng 800 vào tầng đọc theo yêu cầu.

### Đối chiếu soul

Luật gốc: `skills/tdq-conventions/references/soul.md` — chất lượng > runtime > context cost.

Không đề xuất nào trong mười dòng trên chạm `soul.md`. Cả mười đều nằm ở nhánh context
cost và runtime, tức hai bậc dưới của thang, và không dòng nào đánh đổi chất lượng lấy
token: mỗi dòng đều kèm một phép kiểm chứng minh hành vi giữ nguyên.

Hai dòng cần user duyệt trước khi làm dù không chạm soul, vì chúng đổi cấu trúc file mà
nhiều skill khác trỏ vào: dòng 3 (dời nội dung `tdq-conventions/SKILL.md`) và dòng 7
(gộp khuôn `Xong khi:`/`Bước kế tiếp:`, hạng rủi ro cao).

Việc gỡ bản plugin cũ 0.19.0 ở mục đầu hồ sơ đứng NGOÀI bảng: nó không tiết kiệm token,
nhưng phải làm trước, vì áp mười đề xuất lên repo trong khi runtime vẫn nạp 0.19.0 thì
không đo lại được gì.
