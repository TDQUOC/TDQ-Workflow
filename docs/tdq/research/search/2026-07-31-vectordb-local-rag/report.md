# Deep search report — 2026-07-31-vectordb-local-rag

- Agent: 5 · finding sau dedup: 31 · route hỏng: 0

| # | Claim | Nguồn | Route xác nhận | Score |
|---|---|---|---|---|
| 1 | pgvector là mở rộng Postgres phù hợp cho các lượng công việc dưới 5 triệu vector | https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDfhwVbIs21AmD4Ynk6QPPzfa4fqoUvnPdLfzSGL35mrcm9tc0ZR9GyMTBV4t9R3X2T6ALs_J1VJcM58cYQaDdgdtBppgoc4HM-99nDseZO87KKI8umnHZyiQ5EnUoDgSIj93SIokn | tổng quát: vector database chạy local cho RAG 2026 — lựa chọn (1) | 10 |
| 2 | pgvector hỗ trợ cả tìm kiếm hàng xóm gần nhất chính xác (exact) và gần đúng (app | https://github.com/pgvector/pgvector | điểm mạnh yếu (1) | 10 |
| 3 | Trên bộ dữ liệu 50 triệu vector Cohere (768 chiều) ở mức recall 99%, Postgres kế | https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQW-TwESg19HphSPMO09u88YyyLQrKKGL56Z3_zgj3xpmzBL0JIFOnwpQRaVch5ltaQguU5TtGd9LYkfc-LNCvmEY8Co64DGnW-f_kEd6-ge59f8EUjZ3ghJnnot6b9ISwjRLILwy7 | số liệu (1) | 10 |
| 4 | Ở quy mô 50 triệu vector (768 chiều), PostgreSQL kết hợp pgvector và pgvectorsca | https://www.tigerdata.com/blog/pgvector-vs-qdrant | scout: vector database chạy local cho RAG 2026, benchmark pgvector pgvectorscale vs Qdrant 50M vector: phương pháp đo + recall + tail latency + index build (1) | 10 |
| 5 | Weaviate hỗ trợ hybrid search kết hợp vector search và keyword (BM25F) search ou | https://docs.weaviate.io/weaviate/search/hybrid | hybrid search local: Qdrant Query API BM25 miniCOIL fusion vs Weaviate vs pgvector full-text (1) | 10 |
| 6 | Qdrant Query API (từ v1.10.0) hỗ trợ hybrid search chạy local/server-side thông  | https://qdrant.tech/documentation/concepts/hybrid-queries/ | hybrid search local: Qdrant Query API BM25 miniCOIL fusion vs Weaviate vs pgvector full-text (1) | 10 |
| 7 | Qdrant được đánh giá cao cho production RAG tự host nhờ engine Rust tối ưu SIMD, | https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQNmIFzYDmDnY3XdWMspgWxSflAnN2opuJv9T7Mc4t9O7CzSi0KuqsZdBS0GJn_HuSeDdSkLRcDqOnMSO7xcCSYIHVhTPWw_JXr14bSPOBEoyigL1R-BKLkzEmzG17KRxGVLFOU5S9sQssjpUAHuqRSRN-SXA= | tổng quát: vector database chạy local cho RAG 2026 — lựa chọn (1) | 9 |
| 8 | Chroma là chuẩn chung cho lập trình RAG prototype local nhờ API Python thân thiệ | https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9bG_08kmcaG6qGHUs5-0X5mabFSkn4MnY3Yx7PXzS5ZhF9p_PlR2a8ueNZlZNEptsM4iqI2Zu0YAerv9ldKRDqXzuGVb57cXywbioxpk8JuSTKt2tMtIvnEVbKjF6phqlQJCxUWazW_k= | tổng quát: vector database chạy local cho RAG 2026 — lựa chọn (1) | 9 |
| 9 | PostgreSQL với extension pgvector là lựa chọn hàng đầu cho RAG sản xuất ở quy mô | https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfRE2NzmX3rUA6pq-nqB1YDGvsM9G_JHO-rtywD8Ry91nZTNR061IEu7gf3K9zTxkUxQ5IbJ6GwdS1YOeMb0YJwfSWsOQxe16AQUyknpAxAUCZTSOSLiAenXQB6kht9ja7Yi9fWhIrdtZR3JTG | tổng quát: vector database chạy local cho RAG 2026 — lựa chọn (1) | 9 |
| 10 | LanceDB là vector database dạng embedded/serverless chạy trực tiếp trong môi trư | https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7yMRf2OjTyFXsb4Q0tiNmwUM59qLv1fyt_ZlhLDdwI41qnWOno5aSvDqIeM7xF6KzriUlKJkzQ4vjSESI-mDK1nVbRMZ7pMj3B0JqwPqM_EMKYqd5i7ruaW-E0Y9gsBw09ER7pubr69hnblVDpzKz2bNgYoL9LX49_IIuwvZpcEuoS5CK | tổng quát: vector database chạy local cho RAG 2026 — lựa chọn (1) | 9 |

(Chỉ hiện top 10/31 — đủ trong merged.json)

Sinh lúc: 2026-07-31T17:09:51+07:00 · rank tất định bằng code (route xác nhận → URL sống → có quote → score → thứ tự route).
