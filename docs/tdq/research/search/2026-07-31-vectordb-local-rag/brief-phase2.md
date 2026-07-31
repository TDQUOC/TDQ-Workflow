# BRIEF — Vector database chạy local cho RAG (2026)

## Câu hỏi
Chọn vector database/thư viện vector search chạy LOCAL (self-host, không managed cloud)
cho ứng dụng RAG cỡ nhỏ–vừa (≤10 triệu vector, 1 máy): các lựa chọn đáng dùng nhất 2026
là gì, điểm mạnh/yếu, và khác nhau ở đâu về hiệu năng, bộ nhớ, tính năng filter/hybrid search?

## Ngữ cảnh
- Ưu tiên: dễ nhúng (embedded/in-process hoặc 1 container), có client Python,
  còn được maintain tích cực trong 2025–2026.
- Ứng viên đã biết (không giới hạn): Qdrant, Chroma, Weaviate, Milvus/Milvus Lite,
  LanceDB, pgvector, sqlite-vec, FAISS.
- Cần cả benchmark/so sánh độc lập lẫn tài liệu chính thức.

## Tiêu chí rank
1. Nguồn chính thức hoặc benchmark độc lập có số liệu > bài viết tổng hợp.
2. Thông tin 2025–2026 > cũ hơn.
3. Có số liệu cụ thể (QPS, recall, RAM, giới hạn vector) > mô tả chung.

## Dữ kiện đã có
- Chưa có số liệu nào — cần evidence từ nguồn.

## Hướng từ phase 1
Phase 1 (agy tổng quát + Claude scout) đã phủ rộng. Phase 2 CHỈ đào sâu 3 hướng sau,
ưu tiên số liệu benchmark có phương pháp đo rõ và giới hạn kỹ thuật cụ thể:
1. Benchmark đối đầu pgvector/pgvectorscale vs Qdrant ở 50M vector: phương pháp đo /
   recall / tail latency / index build (seed: tigerdata.com/blog/pgvector-vs-qdrant
   và qdrant.tech benchmarks).
2. Giới hạn nhóm embedded local: sqlite-vec (brute-force / ANN roadmap) + Milvus Lite
   (concurrency / giới hạn ghi) + LanceDB (IVF-PQ trên đĩa khi data > RAM).
3. Hybrid search chạy local: Qdrant Query API (BM25/miniCOIL + fusion RRF/DBSF) so với
   Weaviate hybrid và pgvector + full-text — tính năng thật và số liệu nếu có.
