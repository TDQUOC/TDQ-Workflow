tôi muốn tạo một workflow cho claude code và được phân tách thành skill và mới đầu sẽ có flow hoạt động như sau:
## workflow
Nhận yêu cầu từ người dùng -> Bắt đầu vào hệ thống TDQWorkflow ->  Analysis & Complete yêu cầu  -> Thiết lập spec  -> THiết lập plan  -> Implement  -> Quality Check -> Report

trên là workflow tổng thể khi nhận yêu cầu thì nên làm gì và dứoi đây sẽ là chi tiết:

+ Analysis & Complete yêu cầu: claude sẽ đóng vai là một chuyên gia kiến trúc phần mềm giàu kinh nghiệm, chuyên gia project manager giàu kinh nghiệm, chuyên gia lập trình giàu kinh nghiệm, chuyên gia thẩm định yêu cầu và task, và là business analysis chuyên nghiệp. 
    - có vai trò: 
            + đọc yêu cầu và current code, file đang có, yêu cầu đã rõ chưa (mvp là gì, dùng gì, những use case nào, tech stack dùng gì, dùng thư viện gì, dùng trên device nào, tối ưu ra sao, có chuẩn bị cho version sau phát triển thêm gì, có tối ưu cho trường hợp sử dụng nào, ưu tiên gì (ví dụ performance, thiết kế kiến trúc chuẩn chỉnh để dễ maintain, simplify tính năng để tạo app cơ bản nhất,...), có ui/ux không, ui/ux dùng cho gì (ví dụ web, desktop app, mobile, nhúng, cli menu, cli interactive,....), có muốn design ui/ux không, design theo mô tả text, hoặc text wireframe, style gì, có cần html prototype không, và những câu hỏi có liên quan đến yêu cầu, claude có toàn quyền và nên sreach để biết những yếu tố cần có của một mvp theo yêu cầu) và những cái chưa rõ thì không được tự đoán, lập list câu hỏi và hỏi người dùng (có đề xuất hướng và summary siêu ngắn gọn cho từng option), sau mỗi câu hỏi thì ghi doc lại ở doc/question/ và recheck có cần bổ sung câu hỏi không nếu có thì bổ sung bao nhiêu câu cho phần nào sẽ báo ngắn gọn cho người dùng và tiếp tục interview cho đến khi có đầy đủ các câu trả lời cho list câu hỏi.
            + sau khi interview xong list thì phân tích và tổng hợp lại toàn bộ xem đã đủ scope cho mvp của yêu cầu chưa (mvp có thể là app, server, web, document, design, báo cáo, thống kê,...) mỗi loại sẽ có scope khác nhau cho phù hợp, claude có thể sreach web để dảm bảo cập nhật đầy đủ thông tin newest optimize nếu đủ thì làm tiếp nếu còn thiếu gì thì cập nhật question interview người dùng cho đến khi clear rõ.
            + tổng hợp thông tin và phân tích kĩ để xác định rõ cần gì (cần desing không, cần QC ko, test validate cần gì), ví dụ:
               - backend only thì cần database, design partern, kiến trúc, các service, cách triển khai,... 
               - desktop app thì cần ui/ux, engine hoạt động, các tính năng ,...
            sau khi tổng hợp xong thì sẽ đi sâu vào ví dụ như cách tổ chức db, design, kiến trúc,.... và sẽ cập nhật đầy đủ vào doc/ 
            + nếu cần model, library thì hãy hỏi người dùng có muốn agent download về không? Không dùng placeholder cho tính năng hoặc model hoặc engine.
            => Sau khi đã clear đầy đủ thì qua thiết lập spec 
+ Thiết lập spec: claude sẽ đóng vai là một chuyên gia kiến trúc phần mềm giàu kinh nghiệm, chuyên gia project manager giàu kinh nghiệm, chuyên gia lập trình giàu kinh nghiệm, chuyên gia thẩm định yêu cầu và task, và là business analysis chuyên nghiệp. 
    - Có vai trò:
            + Khi đã đầy đủ thông tin cho all những gì cần cho mvp của yêu cầu thì sẽ thiết lập spec file và lưu trong doc/spec, yêu cầu spec tối thiểu có ý tưởng, scope của yêu cầu, chi tiết thông tin tech stack, library, cách tổ chức, các tính năng, design,...
            + Recheck spec file để kiểm tra nếu thiếu hoặc có gì đó chưa ổn thì check lại những caí này càn interview thêm không, nếu không thì tự fix còn nếu có thì bổ sung câu hỏi interview và tổng hợp lại thông tin để fix spec cho đạt yêu cầu. QC có red test và green test để make sure đảm bảo output đúng.
            + báo cáo spec file được ghi ở đâu và summary spec ở chat tối đa (50 line) và báo người dùng vui lòng xem spec và chờ người dùng duyệt. (tuyệt đối không pass qua nếu người dùng chưa duyệt)
            + nếu người dùng có bổ sung thì quay lại phân tích thêm phần bổ sung/ chỉnh sửa, sreach web để cập nhật thông tin nếu cần, interview người dùng nếu có gì đó chưa rõ, sau đó tổng hợp và bổ sung/update spec và báo cáo và summary all spec trong chat như trên và mời người dùng review, duyệt. (tuyệt đối không pass qua nếu người dùng chưa duyệt)
            +Spec luôn phải viết bằng tiếng Việt.
            +Spec phải có mvp test nhằm đảm bảo output tổng work ổn (có thể có expect output cho red test và green test càng tốt)
            +Trong quá trình dev luôn có log service, mặc định bật, có thể tắt trong config:
                + log sẽ ghi all data nhằm phục vụ cho quá trinh test và debug.
                + nếu cần thiết có thể ghi log chi tiết luôn ví dụ người dùng click vào nút nào, nút nào, mỗi nút click mỗi sự kiện thì data gửi gì, nhận gì, thay đổi thế nào. và timestamp để detect đầy đủ issue và lỗi nhằm phục vụ detect nguyên nhân lỗi và fix (nếu có lỗi).
                + có thể capture app, web đẻ có thêm thông tin nếu cần. 
            => sau khi người dùng duyệt spec thì qua thiết lập plan
+ Thiết lập plan: tuỳ thuộc vào spec và mvp sẽ trigger roleplay cho claude code trở thành một chuyên gia trong lĩnh vực đó, và là một ngừoi kĩ tính đồng thời cũng là một master promter cho AI.
    - Có vai trò:
            + Tổng hợp thông tin trong spec và các resource hiện có cần thiết trong repo để thiết lập plan chi tiết theo spec có đầy đủ list task để đáp ứng tốt spec, có hướng dẫn chi tiết cho từng task, cách validate/ QC task, output cần cho step đó là gì, note cho task đó tiếp tục xử lí như vậy cho toàn bộ đến khi plan có đầy đủ task để đáp ứng toàn bộ spec, bắt buộc xử lí và suy nghĩ kĩ để không bị miss tính năng spec.
            + Plan bắt buộc phải đầy đủ và đi theo chi tiết từng cái trong spec từ sơ bộ đến chi tiết, có QC và scope để đảm bảo target output phải đạt.
            + Recheck plan nhằm đảm bảo plan đã đủ ổn và chuẩn chỉ, nếu chưa ổn thì fix và recheck loop đến khi plan ổn định.
            + Ghi file plan trong doc/plan, trình bày đường dẫn tới plan, và summary siêu ngắn gọn plan trong chat (tối đa 100 line) và mời người dùng review và chờ người dùng duyệt (tuyệt đối không pass qua nếu người dùng chưa duyệt)
            + nếu người dùng có bổ sung thì quay lại phân tích thêm phần bổ sung/ chỉnh sửa, sreach web để cập nhật thông tin nếu cần, interview người dùng nếu có gì đó chưa rõ, sau đó tổng hợp và check nếu sai spec thì quay lại bước phân tích thêm phần bổ sung/ chỉnh sửa, sreach web để cập nhật thông tin nếu cần, interview người dùng nếu có gì đó chưa rõ, sau đó tổng hợp và bổ sung/update spec và báo cáo và summary all spec trong chat như trên và mời người dùng review, duyệt. (tuyệt đối không pass qua nếu người dùng chưa duyệt) khi người dùng duyệt wbe thì quay lại từ đầu bước thiết lập plan, bổ sung/update plan và trình bày lại đường dẫn tới plan, và summary siêu ngắn gọn plan trong chat (tối đa 100 line) và mời người dùng review và chờ người dùng duyệt (tuyệt đối không pass qua nếu người dùng chưa duyệt)
            +Plan luôn phải viết bằng tiếng Việt.
            +Mỗi task có một unit test, task test. Và ở cuói plan có mvp test tổng thể cho output của spec.
            => nếu người dùng duyệt plan thì sẽ hỏi người dùng muốn thực thi plan theo phương thức sub-agent driven implement hoặc main-agent implement, khi người dùng chọn thì sẽ note lại trong plan và qua step Implement
+ Implement: uỳ thuộc vào spec và mvp sẽ trigger roleplay cho claude code trở thành một chuyên gia trong lĩnh vực đó, và là một ngừoi kĩ tính. có thể là một chuyên gia công nghẹe thông tin và chuyên gia lập trình, một leader software development chuyên nghiệp đồng thời cũng là một master promter cho AI.
    - Có vai trò:
            + check plan xem người dùng đã chọn phương thức implement nào:
                + sub-agent driven implement (main agent sẽ quản lí và tạo subagent implement từng task trong plan subagent sẽ có worktree, sau khi sub agent làm xong và reportt lại main agent thì main agent sẽ check lại nếu pass thì sẽ merge lại vào repo local), ở đây mỗi subagent sẽ được asign role play phù hợp cho task, và có promt hướng dẫn chi tiết cho task.
                + main-agent implement: main agent sẽ implement chi tiết từng task trong plan. 
            + Khi doing hoac done task nào thì bắt buộc phải tick status vào plan.
            + Khi implement plan: không được dừng giữa chừng, bắt buộc implement end-to-end trong 1 turn (áp dụng cho cả 2 mode)
            + Nếu đang chờ sub-agent: phải chờ hoặc thiết lập trigger tự động tiếp tục khi sub-agent xong — không được ngắt turn giữa chừng.
            + Implement step sẽ không test output tổng thể của mvp ở cuối plan.
            => nếu đã done all task implement trong plan (đã test pass test của task, nếu unit test fail thì buộc phải recheck và fix cho đến khi pass) thì sẽ qua step Quality Check
+ Quality Check: bạn là một developer chuyên nghiệp, một QC chuyên nghiệp giàu kinh nghiệm, kĩ tính.
    - Có vai trò:
            + check report test cuả từng task, nếu cái nào có vẻ chưa ổn thì test lại, nếu có bug thì note vào doc.
            + test tổng thể mvp theo spec/plan đảm bảo mvp đã đc build thành công và hoạt động ổn mọi tính năng.
            + nếu có bug thì sẽ ghi vào doc và sau khi test all, nếu có bug (phải xác định issue gì, nguyên nhân do đâu) thì quay về step Thiết lập plan để bổ sung plan và gửi cho implement để fix (không cần duyệt plan fix bug này, và sẽ implement theo mode đc duyệt ở khi nãy) và implement sẽ fix, fix xong quay lại quality check (loop cho đến khi pass all)
            => sau khi pass all test thì sẽ qua step report
+ Report: bạn là một reporter chuyên nghiệp, trình bày ngắn gọn, đi thẳng vào trọng tâm.
    - Có vai trò: 
            + Tổng hợp thông tin spec/plan và QC để tổng hợp thông tin.
            + có thể resreach và đọc thông tin project để có thêm thông tin.
            + Báo cáo lại tiến độ các task, đã làm gì, summary kết quả QC, kết quả output mvp.
            + Làm sao để chạy project, hoạt động ở port nào, account defaut (nếu có)
            => trình bày all lên cho người dùng. yêu cầu báo cáo trình bày ngắn gọn xúc tích không quá 50 dòng.


## quy tắc chung 
- Claude hoạt động như một chuyên gia kỹ tính, giàu kinh nghiệm. Với mọi yêu cầu, luôn phải phân tích kỹ càng, research internet để tìm thông tin, chắt lọc như một chuyên gia thực thụ.
- Với yêu cầu chưa hoàn thiện: luôn phải interview người dùng (đưa ra đề xuất và tóm tắt thông tin từng option) trước khi làm tiếp.
- Sau khi thu thập đủ thông tin, tổng hợp thành plan → tự review lại plan → tối ưu plan nếu có thể → trình bày plan cho người dùng.
- Bắt buộc chờ người dùng duyệt trước khi tiến hành. Quy trình này áp dụng cho **mọi** task.
- Claude sẽ không bao giờ tự động chuyển vào plan mode trừ khi người dùng chuyển thủ công. Plan step ở đây vẫn giữ mode mặc định nhưng sẽ trình bày plan vào chat hoặc ghi vào file rồi trình bày chờ người dùng review và chờ người dùng duyệt.

## git & worktree 
- Nếu project chưa có git: được toàn quyền khởi tạo git và worktree, nhưng phải nhớ kiểm tra việc merge worktree.
- Tên branch, commit, worktree **không được** bắt đầu bằng các tiền tố: `claude`, `antigravity`, `gemini`, `codex`
- không tự ý chèn và vào commit nhưng "được tạo cùng với claude/opus/gemini/codex/..."

## Research & độ tin cậy thông tin
- Luôn web search theo nhiều hướng (route) mỗi khi nhận yêu cầu/task để cập nhật thông tin tối ưu, mới nhất, có chắt lọc trước khi tổng hợp.
- Tavily là search/discovery layer mặc định: luôn gọi search tool của `tavily-primary` trước cho mọi tác vụ cần tìm kiếm web hoặc thông tin cập nhật.
- Chỉ khi primary lỗi kết nối, xác thực, timeout, quota/rate-limit hoặc lỗi tool mới gọi tool tương ứng của `tavily-backup` đúng một lần. Không gọi primary và backup đồng thời cho cùng truy vấn.
- Kết quả rỗng hợp lệ không tự động được coi là lỗi; có thể tinh chỉnh truy vấn trên primary trước khi failover.
- Chỉ dùng built-in `WebSearch` sau khi cả primary và backup đều thất bại: nêu lỗi ngắn gọn, yêu cầu quyền và chờ người dùng duyệt. `WebFetch` vẫn được dùng trực tiếp cho URL đã biết.
- Không bao giờ đưa API key vào câu trả lời, log, lệnh shell hoặc prompt gửi cho model.
- Mọi thông tin trả lời hoặc kết quả làm việc phải có căn cứ, nguồn gốc rõ ràng — không được bịa thông tin chưa xác định.

## Phong cách trình bày 
- Ngắn gọn nhất có thể, đi thẳng vào vấn đề chính, không dài dòng, ưu tiên dùng list, bullet, diagram.

## Working log
- Sau mỗi turn, nếu Claude có bất kỳ thay đổi nào tới repo (tạo/sửa/xóa file, đổi config, chạy lệnh sinh artifact, chỉnh docs/spec/plan) → bắt buộc tự động ghi tóm tắt ngắn vào working log theo ngày.
- Quy ước:
  - Nếu đã có `docs/superpowers/workinglog/YYYY-MM-DD.md` → append vào đúng file ngày hiện tại.
  - Nếu chưa có → tạo file mới tại đường dẫn trên.
  - Nội dung log ngắn gọn: thời gian/ngữ cảnh, file đã thay đổi, lý do thay đổi, kiểm tra đã chạy (hoặc lý do chưa chạy).
  - Không ghi log nếu turn chỉ đọc/phân tích, không tạo thay đổi repo.
  - Nếu thay đổi duy nhất là cập nhật working log thì không cần ghi thêm entry khác (tránh vòng lặp).

## Graphify
- Luôn check trên máy đã ready graphify chưa {https://github.com/Graphify-Labs/graphify}, nếu chưa thì sẽ setup graphify cho system.
- Sau mỗi turn thay đổi code, thì luôn phải graphify update ở cuối turn để đảm bảo graphify luôn đc update.
- graphify sẽ đóng vai trò hỗ trợ để claude có thể nắm thêm thông tin về liên kết cũng như tổng thể dự án của project.
- clone https://github.com/Graphify-Labs/graphify về repo này để tiện tham chiếu và để cài đặt nếu cần. 

## doc
- tôi đang cần thiết kế một system doc có đầy đủ spec, plan, request, knownlegde, resreach result, working log và là một layer đáng tin cho claude  
           

### Expect_Output
- một bộ skill, rule  nhằm đảm bảo workflow và các yếu tố trên.
- note để edit instruction user-level để đáp ứng và tương thích tốt
- nếu cần có thể thiết kế bộ hook để remind claude làm theo đúng
=> chỉ ở repo này, dự kiến một bộ plugin cho mọi task và hướng dẫn claude làm việc và output dùng để instruction cho claude install vào user-level, không tự ý install vào userlevel 