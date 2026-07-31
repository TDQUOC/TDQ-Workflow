# Deep search report — 2026-07-31-stt-wordlevel-claude

- Agent: 3 · finding sau dedup: 16 · route hỏng: 0

| # | Claim | Nguồn | Route xác nhận | Score |
|---|---|---|---|---|
| 1 | Deepgram Streaming API (WebSocket) trả timestamp cho TỪNG từ trong chế độ live s | https://developers.deepgram.com/docs/recovering-from-connection-errors-and-timeouts-when-live-streaming-audio | API thương mại realtime word-level: Deepgram AssemblyAI Google Azure OpenAI Realtime (1) | 9 |
| 2 | OpenAI Realtime transcription (model gpt-live-transcribe) KHÔNG trả word-level t | https://developers.openai.com/api/docs/guides/realtime-transcription | API thương mại realtime word-level: Deepgram AssemblyAI Google Azure OpenAI Realtime (1) | 9 |
| 3 | Google Cloud Speech-to-Text hỗ trợ word time offsets (start/end mỗi từ, độ phân  | https://docs.cloud.google.com/speech-to-text/docs/v1/speech-to-text-requests | API thương mại realtime word-level: Deepgram AssemblyAI Google Azure OpenAI Realtime (1) | 9 |
| 4 | Azure AI Speech (Speech SDK, realtime recognition) trả offset + duration cho từn | https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-speech-recognition-results | API thương mại realtime word-level: Deepgram AssemblyAI Google Azure OpenAI Realtime (1) | 9 |
| 5 | AssemblyAI Universal-Streaming (WebSocket wss://streaming.assemblyai.com/v3/ws)  | https://www.assemblyai.com/docs/speech-to-text/universal-streaming | API thương mại realtime word-level: Deepgram AssemblyAI Google Azure OpenAI Realtime (1) | 9 |
| 6 | NVIDIA Riva ASR hỗ trợ streaming mode trả intermediate transcript độ trễ thấp và | https://docs.nvidia.com/deeplearning/riva/user-guide/docs/asr/asr-overview.html | open-source streaming STT word timestamp: Whisper faster-whisper Vosk NVIDIA Riva Parakeet (1) | 9 |
| 7 | Deepgram công bố transcription latency (thời gian server xử lý và trả kết quả) c | https://developers.deepgram.com/docs/measuring-streaming-latency | API thương mại realtime word-level: Deepgram AssemblyAI Google Azure OpenAI Realtime (1) | 8 |
| 8 | faster-whisper là backend được khuyến nghị cho realtime Whisper streaming, với c | https://github.com/SYSTRAN/faster-whisper | open-source streaming STT word timestamp: Whisper faster-whisper Vosk NVIDIA Riva Parakeet (1) | 8 |
| 9 | Vosk (nền Kaldi) là STT mã nguồn mở offline hỗ trợ streaming API với phản hồi ze | https://github.com/alphacep/vosk-api | open-source streaming STT word timestamp: Whisper faster-whisper Vosk NVIDIA Riva Parakeet (1) | 8 |
| 10 | whisper_streaming (UFAL) hiện thực chế độ realtime streaming cho Whisper dựa trê | https://github.com/ufal/whisper_streaming | open-source streaming STT word timestamp: Whisper faster-whisper Vosk NVIDIA Riva Parakeet (1) | 8 |

(Chỉ hiện top 10/16 — đủ trong merged.json)

Sinh lúc: 2026-07-31T15:46:56+07:00 · rank tất định bằng code (route xác nhận → URL sống → có quote → score → thứ tự route).
