# Báo Cáo Kiểm Toán & Đánh Giá Graphify Full Trên Dự Án Photoboth360

- **Thời gian thực hiện**: 2026-10-19 18:16:44
- **Dự án mục tiêu**: `C:\Users\admin\Documents\Photoboth360`
- **Quy mô đồ thị**: 21,585 nodes · 52,741 edges · 535 communities
- **Tổng số bài test**: 50 bài
- **Kết quả**: 50/50 PASS (100.0%) · 0 FAIL
- **Độ trễ trung bình**: 691.14 ms / test

## Thống Kê Chi Tiết Theo Phân Nhóm

| Nhóm Kiểm Thử | Số Bài Test | Đạt (PASS) | Tỷ Lệ Đạt (%) | Độ Trễ TB (ms) |
|---|---|---|---|---|
| **Entity Coverage** | 10 | 10 | 100.0% | 2.19 ms |
| **Dependency Accuracy** | 10 | 10 | 100.0% | 29.53 ms |
| **Structural & Call Flow** | 10 | 10 | 100.0% | 19.00 ms |
| **Semantic Query** | 10 | 10 | 100.0% | 2698.47 ms |
| **Architectural Impact** | 10 | 10 | 100.0% | 706.49 ms |

## Chi Tiết 50 Bài Test

- **T01** [PASS] `Entity Coverage` — Node app.js tồn tại trong đồ thị (2.78 ms)
  - *Chi tiết*: Found 1 matching node(s): id=nodeserver_app label=app.js file=nodeserver/app.js loc=L1
- **T02** [PASS] `Entity Coverage` — Node config.js tồn tại trong đồ thị (2.36 ms)
  - *Chi tiết*: Found 1 matching node(s): id=nodeserver_config label=config.js file=nodeserver/config.js loc=L1
- **T03** [PASS] `Entity Coverage` — Controller data.js tồn tại (2.25 ms)
  - *Chi tiết*: Found 1 matching node(s): id=nodeserver_app_controller_data label=controller/data.js file=nodeserver/app/controller/data.js loc=L1
- **T04** [PASS] `Entity Coverage` — Controller file.js tồn tại (3.13 ms)
  - *Chi tiết*: Found 1 matching node(s): id=nodeserver_app_controller_file label=controller/file.js file=nodeserver/app/controller/file.js loc=L1
- **T05** [PASS] `Entity Coverage` — Model data.js tồn tại (2.4 ms)
  - *Chi tiết*: Found 1 matching node(s): id=nodeserver_app_models_data label=models/data.js file=nodeserver/app/models/data.js loc=L1
- **T06** [PASS] `Entity Coverage` — Model file.js tồn tại (1.93 ms)
  - *Chi tiết*: Found 1 matching node(s): id=nodeserver_app_models_file label=models/file.js file=nodeserver/app/models/file.js loc=L1
- **T07** [PASS] `Entity Coverage` — Socket module socket.js tồn tại (1.8 ms)
  - *Chi tiết*: Found 1 matching node(s): id=nodeserver_app_socket_socket label=socket.js file=nodeserver/app/socket/socket.js loc=L1
- **T08** [PASS] `Entity Coverage` — Utils ffmpeg.js tồn tại (1.81 ms)
  - *Chi tiết*: Found 1 matching node(s): id=nodeserver_app_utils_ffmpeg label=ffmpeg.js file=nodeserver/app/utils/ffmpeg.js loc=L1
- **T09** [PASS] `Entity Coverage` — C# Class AsyncTestHubSample tồn tại (1.84 ms)
  - *Chi tiết*: Found 2 matching node(s): id=photobooth_360_hardware_assets_best_http_examples_signalrcore_asynctesthubsample_besthttp_examples_asynctesthubsample label=AsyncTestHubSample file=photobooth-360-hardware/Assets/Best HTTP/Examples/SignalRCore/AsyncTestHubSample.cs loc=L17
- **T10** [PASS] `Entity Coverage` — C# Class HTTPProtocolFactory tồn tại (1.65 ms)
  - *Chi tiết*: Found 2 matching node(s): id=photobooth_360_hardware_assets_best_http_source_connections_httpprotocolfactory_besthttp_connections_httpprotocolfactory label=HTTPProtocolFactory file=photobooth-360-hardware/Assets/Best HTTP/Source/Connections/HTTPProtocolFactory.cs loc=L20
- **T11** [PASS] `Dependency Accuracy` — app.js phụ thuộc express (29.12 ms)
  - *Chi tiết*: Found 2 edge(s) matching (app.js --*--> express): nodeserver_app --imports_from--> ref_express at L3
- **T12** [PASS] `Dependency Accuracy` — app.js phụ thuộc mongoose (29.18 ms)
  - *Chi tiết*: Found 2 edge(s) matching (app.js --*--> mongoose): nodeserver_app --imports_from--> ref_mongoose at L4
- **T13** [PASS] `Dependency Accuracy` — app.js kết nối cors middleware (29.2 ms)
  - *Chi tiết*: Found 2 edge(s) matching (app.js --*--> cors): nodeserver_app --imports_from--> ref_cors at L6
- **T14** [PASS] `Dependency Accuracy` — app.js phụ thuộc path module (29.31 ms)
  - *Chi tiết*: Found 1 edge(s) matching (app.js --*--> path): nodeserver_app --imports_from--> ref_path at L2
- **T15** [PASS] `Dependency Accuracy` — app.js phụ thuộc config module (29.14 ms)
  - *Chi tiết*: Found 2 edge(s) matching (app.js --*--> config): nodeserver_app --imports_from--> nodeserver_config at L5
- **T16** [PASS] `Dependency Accuracy` — routes kết nối controller (30.95 ms)
  - *Chi tiết*: Found 2 edge(s) matching (routes.js --*--> controller): nodeserver_app_routes_routes --imports_from--> nodeserver_app_controller_file at L3
- **T17** [PASS] `Dependency Accuracy` — controller data.js kết nối utils ffmpeg (29.05 ms)
  - *Chi tiết*: Found 2 edge(s) matching (data.js --*--> ffmpeg): nodeserver_app_controller_data --imports_from--> nodeserver_app_utils_ffmpeg at L7
- **T18** [PASS] `Dependency Accuracy` — AsyncTestHubSample phụ thuộc HubConnection (29.92 ms)
  - *Chi tiết*: Found 2 edge(s) matching (AsyncTestHubSample --*--> HubConnection): photobooth_360_hardware_assets_best_http_examples_signalrcore_asynctesthubsample_besthttp_examples_asynctesthubsample --references--> photobooth_360_hardware_assets_best_http_source_signalrcore_hubconnection_besthttp_signalrcore_hubconnection at L45
- **T19** [PASS] `Dependency Accuracy` — HTTPProtocolFactory phụ thuộc HTTP protocol (29.82 ms)
  - *Chi tiết*: Found 15 edge(s) matching (HTTPProtocolFactory --*--> HTTP): photobooth_360_hardware_assets_best_http_source_connections_httpprotocolfactory_besthttp_connections_httpprotocolfactory_get --references--> photobooth_360_hardware_assets_best_http_source_connections_httpprotocolfactory_cs_httprequest at L27
- **T20** [PASS] `Dependency Accuracy` — ffmpeg module import fluent-ffmpeg (29.58 ms)
  - *Chi tiết*: Found 1 edge(s) matching (ffmpeg.js --*--> fluent_ffmpeg): nodeserver_app_utils_ffmpeg --imports_from--> ref_fluent_ffmpeg at L1
- **T21** [PASS] `Structural & Call Flow` — app.js định nghĩa hàm connectMongoDB (20.15 ms)
  - *Chi tiết*: Found 1 structural call/member edge(s): nodeserver_app --contains--> nodeserver_app_connectmongodb
- **T22** [PASS] `Structural & Call Flow` — app.js định nghĩa hàm startServer (20.23 ms)
  - *Chi tiết*: Found 1 structural call/member edge(s): nodeserver_app --contains--> nodeserver_app_startserver
- **T23** [PASS] `Structural & Call Flow` — controller data.js định nghĩa all (20.53 ms)
  - *Chi tiết*: Found 1 structural call/member edge(s): nodeserver_app_controller_data --contains--> nodeserver_app_controller_data_all
- **T24** [PASS] `Structural & Call Flow` — controller file.js xử lý upload (20.61 ms)
  - *Chi tiết*: Found 1 structural call/member edge(s): nodeserver_app_controller_file --contains--> nodeserver_app_controller_file_upload
- **T25** [PASS] `Structural & Call Flow` — ffmpeg utils định nghĩa hàm thumbnail (20.59 ms)
  - *Chi tiết*: Found 2 structural call/member edge(s): nodeserver_app_utils_ffmpeg --contains--> nodeserver_app_utils_ffmpeg_thumbnail2
- **T26** [PASS] `Structural & Call Flow` — AsyncTestHubSample có method Start (15.55 ms)
  - *Chi tiết*: Found 1 structural call/member edge(s): photobooth_360_hardware_assets_best_http_examples_signalrcore_asynctesthubsample_besthttp_examples_asynctesthubsample --method--> photobooth_360_hardware_assets_best_http_examples_signalrcore_asynctesthubsample_besthttp_examples_asynctesthubsample_start
- **T27** [PASS] `Structural & Call Flow` — AsyncTestHubSample có OnConnectButton (15.56 ms)
  - *Chi tiết*: Found 1 structural call/member edge(s): photobooth_360_hardware_assets_best_http_examples_signalrcore_asynctesthubsample_besthttp_examples_asynctesthubsample --method--> photobooth_360_hardware_assets_best_http_examples_signalrcore_asynctesthubsample_besthttp_examples_asynctesthubsample_onconnectbutton
- **T28** [PASS] `Structural & Call Flow` — HTTPProtocolFactory có GetProtocolFromUri (15.46 ms)
  - *Chi tiết*: Found 1 structural call/member edge(s): photobooth_360_hardware_assets_best_http_source_connections_httpprotocolfactory --contains--> photobooth_360_hardware_assets_best_http_source_connections_httpprotocolfactory_getprotocolfromuri
- **T29** [PASS] `Structural & Call Flow` — controller file.js định nghĩa delete (20.69 ms)
  - *Chi tiết*: Found 1 structural call/member edge(s): nodeserver_app_controller_file --contains--> nodeserver_app_controller_file_delete
- **T30** [PASS] `Structural & Call Flow` — controller data.js định nghĩa upload (20.67 ms)
  - *Chi tiết*: Found 1 structural call/member edge(s): nodeserver_app_controller_data --contains--> nodeserver_app_controller_data_upload
- **T31** [PASS] `Semantic Query` — Tìm luồng khởi động server express (2602.83 ms)
  - *Chi tiết*: Query rc=0, output_len=5025, expected=['app.js', 'listen', 'express']
- **T32** [PASS] `Semantic Query` — Tìm luồng kết nối websocket socket.io (2622.61 ms)
  - *Chi tiết*: Query rc=0, output_len=4986, expected=['socket', 'io', 'connection']
- **T33** [PASS] `Semantic Query` — Tìm cấu hình hệ thống / database (2569.32 ms)
  - *Chi tiết*: Query rc=0, output_len=4955, expected=['config', 'db', 'port']
- **T34** [PASS] `Semantic Query` — Tìm chức năng upload tệp tin (2580.39 ms)
  - *Chi tiết*: Query rc=0, output_len=5028, expected=['file', 'upload', 'multer']
- **T35** [PASS] `Semantic Query` — Tìm xử lý video ffmpeg (2676.29 ms)
  - *Chi tiết*: Query rc=0, output_len=5006, expected=['ffmpeg', 'exec', 'video']
- **T36** [PASS] `Semantic Query` — Tìm kết nối SignalR Hub (2939.57 ms)
  - *Chi tiết*: Query rc=0, output_len=4970, expected=['signalr', 'hub', 'messagepack']
- **T37** [PASS] `Semantic Query` — Tìm định tuyến routes (2834.29 ms)
  - *Chi tiết*: Query rc=0, output_len=4885, expected=['routes', 'router', 'express']
- **T38** [PASS] `Semantic Query` — Tìm module mã hóa và chứng chỉ (2668.8 ms)
  - *Chi tiết*: Query rc=0, output_len=5028, expected=['certificate', 'crypto', 'x509', 'tls']
- **T39** [PASS] `Semantic Query` — Tìm giao thức xác thực TLS (2810.74 ms)
  - *Chi tiết*: Query rc=0, output_len=5034, expected=['tls', 'client', 'handshake']
- **T40** [PASS] `Semantic Query` — Tìm thuật toán Elliptic Curve (2679.81 ms)
  - *Chi tiết*: Query rc=0, output_len=4950, expected=['curve', 'ec', 'key']
- **T41** [PASS] `Architectural Impact` — Vết lan truyền khi đổi nodeserver config (909.66 ms)
  - *Chi tiết*: Affected rc=0, expected ['app.js', 'routes', 'socket', 'controller', 'ffmpeg'] in output: True
- **T42** [PASS] `Architectural Impact` — Vết lan truyền khi đổi data model (908.98 ms)
  - *Chi tiết*: Affected rc=0, expected ['controller', 'data', 'routes'] in output: True
- **T43** [PASS] `Architectural Impact` — Vết lan truyền khi đổi file model (925.72 ms)
  - *Chi tiết*: Affected rc=0, expected ['controller', 'file', 'upload'] in output: True
- **T44** [PASS] `Architectural Impact` — Vết lan truyền khi đổi ffmpeg utils (915.43 ms)
  - *Chi tiết*: Affected rc=0, expected ['file', 'video', 'controller'] in output: True
- **T45** [PASS] `Architectural Impact` — Truy vấn danh sách God nodes kiến trúc (917.32 ms)
  - *Chi tiết*: God nodes identified in 917.3ms
- **T46** [PASS] `Architectural Impact` — Xác thực cụm kiến trúc Cryptography (1.41 ms)
  - *Chi tiết*: Found 'Cryptography' in GRAPH_REPORT.md: True
- **T47** [PASS] `Architectural Impact` — Xác thực cụm kiến trúc TLS Protocol (1.51 ms)
  - *Chi tiết*: Found 'TLS' in GRAPH_REPORT.md: True
- **T48** [PASS] `Architectural Impact` — Xác thực cụm kiến trúc BestHTTP Core (1.47 ms)
  - *Chi tiết*: Found 'BestHTTP' in GRAPH_REPORT.md: True
- **T49** [PASS] `Architectural Impact` — Xác thực cụm kiến trúc Certificate Management (1.38 ms)
  - *Chi tiết*: Found 'Certificate' in GRAPH_REPORT.md: True
- **T50** [PASS] `Architectural Impact` — Giải thích ngữ cảnh kiến trúc nút app.js (explain) (2482.0 ms)
  - *Chi tiết*: Explain output length=314 chars
