# Graphify — precision, recall và ranking thực đo

11 file JS nodeserver · 12 truy vấn (6 EN, 6 VI) · file-level relevance trực tiếp · graph giữ nguyên.
Gold set do agent đọc source lập; mẫu có chủ đích, chưa phải gold độc lập do người thẩm định. Không suy rộng toàn dự án.

## Kết quả tổng hợp

```json
{
  "aggregates": {
    "imports": {
      "tp": 57,
      "fp": 0,
      "fn": 5,
      "precision": 1.0,
      "recall": 0.9193548387096774,
      "f1": 0.957983193277311,
      "macro_precision": 1.0,
      "macro_precision_n": 10,
      "macro_recall": 0.956140350877193,
      "macro_recall_n": 10,
      "macro_f1": 0.9744444444444443,
      "macro_f1_n": 10
    },
    "functions": {
      "tp": 22,
      "fp": 0,
      "fn": 5,
      "precision": 1.0,
      "recall": 0.8148148148148148,
      "f1": 0.8979591836734694,
      "macro_precision": 1.0,
      "macro_precision_n": 5,
      "macro_recall": 0.7142857142857143,
      "macro_recall_n": 7,
      "macro_f1": 0.7142857142857143,
      "macro_f1_n": 7
    },
    "scorer_top5_scoped": {
      "tp": 12,
      "fp": 30,
      "fn": 2,
      "precision": 0.2857142857142857,
      "recall": 0.8571428571428571,
      "f1": 0.42857142857142855,
      "macro_precision": 0.3893939393939394,
      "macro_precision_n": 11,
      "macro_recall": 0.8333333333333334,
      "macro_recall_n": 12,
      "macro_f1": 0.45595238095238094,
      "macro_f1_n": 12
    },
    "cli_context_scoped": {
      "tp": 4,
      "fp": 14,
      "fn": 10,
      "precision": 0.2222222222222222,
      "recall": 0.2857142857142857,
      "f1": 0.25,
      "macro_precision": 0.375,
      "macro_precision_n": 7,
      "macro_recall": 0.2916666666666667,
      "macro_recall_n": 12,
      "macro_f1": 0.22685185185185186,
      "macro_f1_n": 12
    }
  },
  "ranking_means": {
    "p_at_5": 0.20000000000000004,
    "r_at_5": 0.8333333333333334,
    "hit_at_5": 0.8333333333333334,
    "rr_at_10": 0.5535714285714286
  }
}
```

## Từng truy vấn

| ID | P@5 | R@5 | Hit@5 | RR@10 | TP/FP/FN top5 scoped | CLI TP/FP/FN |
|---|---:|---:|---:|---:|---|---|
| Q01 | 0.200 | 1.000 | 1 | 0.500 | 1/4/0 | 0/1/1 |
| Q02 | 0.200 | 1.000 | 1 | 1.000 | 1/0/0 | 0/0/1 |
| Q03 | 0.000 | 0.000 | 0 | 0.143 | 0/5/1 | 0/2/1 |
| Q04 | 0.200 | 1.000 | 1 | 0.250 | 1/4/0 | 1/7/0 |
| Q05 | 0.000 | 0.000 | 0 | 0.000 | 0/0/1 | 0/0/1 |
| Q06 | 0.400 | 1.000 | 1 | 1.000 | 2/0/0 | 0/0/2 |
| Q07 | 0.200 | 1.000 | 1 | 1.000 | 1/3/0 | 1/0/0 |
| Q08 | 0.200 | 1.000 | 1 | 1.000 | 1/4/0 | 1/0/0 |
| Q09 | 0.200 | 1.000 | 1 | 0.500 | 1/1/0 | 0/0/1 |
| Q10 | 0.200 | 1.000 | 1 | 0.500 | 1/2/0 | 0/0/1 |
| Q11 | 0.400 | 1.000 | 1 | 0.500 | 2/3/0 | 1/1/1 |
| Q12 | 0.200 | 1.000 | 1 | 0.250 | 1/4/0 | 0/3/1 |

## Diễn giải và giới hạn

Ranking đo scorer nội bộ trên FULL graph rồi lọc về 11 file judged và khử trùng file theo lần đầu. Đây là ranking scoped lạc quan hơn trải nghiệm full corpus; thứ hạng NODE trong CLI không phải ranking. Raw full order và top10 unjudged có trong JSONL.
P@5 dùng mẫu số cố định 5 (slot thiếu = 0); Recall@5 = TP@5/số file đúng; Hit@5 và RR@10 theo scoped order. Ties giữ thứ tự scorer, không sắp theo gold. FP/FN ranking là tại cutoff 5, không phải toàn danh sách.
Precision không có prediction, recall không có gold hoặc F1 có denominator 0 = null, không tự gán 100%; macro bỏ null và ghi số mẫu n. CLI lỗi không chấm như tập rỗng; báo riêng tỷ lệ lỗi.
Imports so endpoint exact sau normalize ID package/relative path, collision bị từ chối; ID normalize có mất thông tin. Functions là inventory callable theo file, không chứng minh contains ownership hoặc call-flow đúng. Anonymous callbacks và dynamic require ngoài phạm vi gold.
Nguồn/dòng imports trong từng record; function inventory có raw source snapshot trong metadata và raw node location. Chưa có kiểm tra độc lập bởi con người. CLI raw output là toàn bộ response trong budget 1500, không phải toàn bộ graph.
Hash trước/sau phải khớp. Không rebuild graph nên snapshot có thể cũ; hash chỉ chứng minh ổn định lúc đo, không chứng minh graph đồng bộ hoàn toàn với source.

## Fingerprints
```json
{
  "kind": "metadata",
  "at": "2026-10-19T17:23:31.361430+00:00",
  "gold_sha256": "ce0f5e3a21d420d1e8289dbebc146888a4f9680ff029e161fa861d360edaf1fa",
  "graph_sha256": "50127f6b9b5e271ee4b15a91ca8852313f2a350102caf40dc5eed248344f830d",
  "scorer_sha256": "e89a987864986f4ca0e3931425d3cd4ebfff2066efa7b5f7ee001f3e7a908955",
  "source_sha256": {
    "nodeserver/app.js": "ac564a07edf5237b61bbfe9ccc910d44a1f3b34faa8758861f9b86b020018493",
    "nodeserver/config.js": "6461a0bfcd65d0e0a68f22ce85c77f19a8864ed8007b7dabe3de15dbe257d166",
    "nodeserver/app/controller/data.js": "61361520bca4b23994d7aa4b3fa4668794b0c5ec01421f58615e28eac0caaf8a",
    "nodeserver/app/controller/file.js": "4c021939918c81bb06fc5f1e829f9f67aae0de65a69ae1828394f3126b1c36d3",
    "nodeserver/app/models/data.js": "e697eec6eba902b62631d847d097d48eacb17807c7fd679bb7d51486874b7e61",
    "nodeserver/app/models/file.js": "bc934bbff1089c8ca55090114d72d823addd5ba6523e4a89c0a76115daf29fc8",
    "nodeserver/app/routes/express.js": "e3c6648037c609aedce4538a6aca2a2b693bc6c0a1ad432ad7f4357d657b4d3c",
    "nodeserver/app/routes/routes.js": "efeedadd0397fcab2709f469283af60478246192f7ca3687fb050497bbdb90c2",
    "nodeserver/app/socket/socket.js": "77bdc7620c5e9598d5a43f70e338896b2eb9794dca96172745233604f11c6dbe",
    "nodeserver/app/utils/ffmpeg.js": "38a1f029fc1070dded95f5502c3acc97efeadc3ce16fcb845600fadf024947ac",
    "nodeserver/app/utils/fileUtils.js": "72b9498a3311d87df56ae675f4c776761478da814c6887e874941535836d63a1"
  },
  "source_snapshots": "in JSONL"
}
```

### imports · nodeserver/app.js
FP: []
FN: ['nodeserver/app/routes/routes.js', 'nodeserver/app/socket/socket.js', 'pkg:socket.io']

### functions · nodeserver/app/models/data.js
FP: []
FN: ['add', 'addThumbnail', 'updateHash']

### functions · nodeserver/app/models/file.js
FP: []
FN: ['addFile', 'addThumbnail']

### imports · nodeserver/app/routes/express.js
FP: []
FN: ['pkg:connect-mongo', 'pkg:multer']

### Q01 · initialize express server and listen on server port
Scorer scoped top5 FP: ['nodeserver/app/controller/data.js', 'nodeserver/app/controller/file.js', 'nodeserver/app/models/data.js', 'nodeserver/app/routes/express.js']
Scorer scoped top5 FN: []
CLI FP: ['nodeserver/app/routes/express.js']
CLI FN: ['nodeserver/app.js']

### Q02 · connect MongoDB and reconnect when disconnected
Scorer scoped top5 FP: []
Scorer scoped top5 FN: []
CLI FP: []
CLI FN: ['nodeserver/app.js']

### Q03 · configure database connection string server socket ports and upload directories
Scorer scoped top5 FP: ['nodeserver/app.js', 'nodeserver/app/controller/data.js', 'nodeserver/app/controller/file.js', 'nodeserver/app/routes/express.js', 'nodeserver/app/socket/socket.js']
Scorer scoped top5 FN: ['nodeserver/config.js']
CLI FP: ['nodeserver/app/controller/data.js', 'nodeserver/app/routes/express.js']
CLI FN: ['nodeserver/config.js']

### Q04 · register HTTP routes for data upload and file deletion
Scorer scoped top5 FP: ['nodeserver/app/controller/data.js', 'nodeserver/app/controller/file.js', 'nodeserver/app/models/file.js', 'nodeserver/app/routes/express.js']
Scorer scoped top5 FN: []
CLI FP: ['nodeserver/app.js', 'nodeserver/app/controller/data.js', 'nodeserver/app/controller/file.js', 'nodeserver/app/models/data.js', 'nodeserver/app/models/file.js', 'nodeserver/app/routes/express.js', 'nodeserver/app/utils/ffmpeg.js']
CLI FN: []

### Q05 · relay websocket hardware startRecord and goproRecordStopped events
Scorer scoped top5 FP: []
Scorer scoped top5 FN: ['nodeserver/app/socket/socket.js']
CLI FP: []
CLI FN: ['nodeserver/app/socket/socket.js']

### Q06 · quản lý khóa chỉnh sửa video và giải phóng khi ngắt kết nối
Scorer scoped top5 FP: []
Scorer scoped top5 FN: []
CLI FP: []
CLI FN: ['nodeserver/app/controller/data.js', 'nodeserver/app/socket/socket.js']

### Q07 · slow motion video using ffmpeg trim setpts concat filter
Scorer scoped top5 FP: ['nodeserver/app/controller/data.js', 'nodeserver/app/controller/file.js', 'nodeserver/app/socket/socket.js']
Scorer scoped top5 FN: []
CLI FP: []
CLI FN: []

### Q08 · tạo ảnh thumbnail PNG 1920x1080 từ video bằng ffmpeg
Scorer scoped top5 FP: ['nodeserver/app/controller/data.js', 'nodeserver/app/controller/file.js', 'nodeserver/app/socket/socket.js', 'nodeserver/config.js']
Scorer scoped top5 FN: []
CLI FP: []
CLI FN: []

### Q09 · tải video gốc lên xử lý chậm và phát thông báo new-video
Scorer scoped top5 FP: ['nodeserver/app/socket/socket.js']
Scorer scoped top5 FN: []
CLI FP: []
CLI FN: ['nodeserver/app/controller/data.js']

### Q10 · liệt kê tài nguyên âm thanh khung hình hiệu ứng theo category
Scorer scoped top5 FP: ['nodeserver/app/socket/socket.js', 'nodeserver/app/utils/fileUtils.js']
Scorer scoped top5 FN: []
CLI FP: []
CLI FN: ['nodeserver/app/controller/file.js']

### Q11 · schema methods save media onlinePath and thumbnail MD5 hash
Scorer scoped top5 FP: ['nodeserver/app/controller/data.js', 'nodeserver/app/controller/file.js', 'nodeserver/app/utils/ffmpeg.js']
Scorer scoped top5 FN: []
CLI FP: ['nodeserver/app/utils/ffmpeg.js']
CLI FN: ['nodeserver/app/models/file.js']

### Q12 · tách tên file và phần mở rộng bằng split lastIndexOf
Scorer scoped top5 FP: ['nodeserver/app/controller/file.js', 'nodeserver/app/models/data.js', 'nodeserver/app/models/file.js', 'nodeserver/app/routes/routes.js']
Scorer scoped top5 FN: []
CLI FP: ['nodeserver/app/controller/file.js', 'nodeserver/app/models/data.js', 'nodeserver/app/models/file.js']
CLI FN: ['nodeserver/app/utils/fileUtils.js']
