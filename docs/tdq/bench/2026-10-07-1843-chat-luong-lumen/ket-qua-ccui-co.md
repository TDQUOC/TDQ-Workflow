| # | Vị trí chính (file:dòng, hàm) | Vị trí phụ | Số lượt tool | Tool đã dùng |
|---|---|---|---|---|
| 1 | src/modules/chat/utils/pageTitleNotification.ts:88 showCompletionTitleIndicator | cùng file:29 clearTitleIndicator | 2 | lumen, Bash |
| 2 | src/modules/chat/hooks/useInputHistory.ts:138 handleHistoryKeyDown (trong useInputHistory:96) | - | 3 | lumen, Grep×2 |
| 3 | server/modules/hosts/host-secret.service.ts:58 createHostSecretBox (AES-256-GCM) | cùng file:24 loadOrCreateHostSecretKey (randomBytes, ghi flag wx, mode 0600) | 3 | lumen, Grep×2 |
| 4 | server/modules/file-tree/file-tree.service.ts:73 validateFilename | - | 1 | lumen |
| 5 | src/shared/hooks/useVersionCheck.ts:15 compareVersions | - | 4 | lumen, Grep, Read×2 |
| 6 | src/modules/git-panel/utils/commitGraph.ts:34 computeCommitGraph | src/modules/git-panel/history/CommitGraphStrip.tsx:20 | 2 | lumen, Grep |
| 7 | server/modules/file-tree/file-tree.service.ts:91 resolvePathInsideProject | server/shared/utils.ts:210 resolvePathUnderRoots | 3 | lumen×2 (1 lỗi), Grep |
| 8 | server/shared/claude-cli-path.ts:79 resolveWindowsClaudeExecutablePath | cùng file:35 resolveClaudeWrapperBinary | 2 | lumen, Grep |
| 9 | src/modules/chat/utils/streamingMarkdown.ts:61 splitStreamingMarkdown | - | 3 | lumen×2 (1 lỗi), Grep |
| 10 | src/modules/chat/utils/sessionMessageReconciliation.ts:109 removeOptimisticUserEchoes | - | 3 | lumen×2 (1 lỗi), Grep |
| 11 | server/modules/websocket/services/chat-run-registry.service.ts:135 decorateAndRecordEvent | cùng file:355 completeRun | 4 | lumen, Grep×2, Bash |
| 12 | server/modules/providers/services/sessions-watcher.service.ts:84 schedulePendingWatcherFlush | cùng file:126 flushPendingWatcherUpdate | 2 | lumen, Grep |

Tổng: 32 lượt tính theo câu (lượt gọi chung được tính cho nhiều câu); thực gọi 23 lượt (+1 ToolSearch nạp schema). 3 lượt lumen lỗi "k value in knn query too large" khi path là thư mục con (server/, src/).
