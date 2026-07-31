# Deep search report — 2026-07-31-stt-wordlevel

- Agent: 3 · finding sau dedup: 9 · route hỏng: 0

| # | Claim | Nguồn | Route xác nhận | Score |
|---|---|---|---|---|
| 1 | Google Cloud Speech-to-Text hỗ trợ word-level timestamps trong chế độ Streaming  | https://cloud.google.com/speech-to-text/docs/async-time-offsets | API thương mại realtime word-level: Deepgram AssemblyAI Google Azure OpenAI Realtime (1) | 10 |
| 2 | Azure Speech Service hỗ trợ word-level timestamps trong real-time streaming thôn | https://learn.microsoft.com/en-us/azure/ai-services/speech-service/ | API thương mại realtime word-level: Deepgram AssemblyAI Google Azure OpenAI Realtime (1) | 10 |
| 3 | TorchAudio cung cấp API forced alignment dựa trên thuật toán CTC segmentation vớ | https://pytorch.org/audio/stable/tutorials/forced_alignment_tutorial.html | kỹ thuật word-level timestamp + benchmark latency: forced alignment CTC streaming (1) | 10 |
| 4 | OpenAI Audio Transcription API hỗ trợ tham số timestamp_granularities[] với giá  | https://platform.openai.com/docs/api-reference/audio/createTranscription | API thương mại realtime word-level: Deepgram AssemblyAI Google Azure OpenAI Realtime (1) | 9 |
| 5 | NVIDIA Riva streaming ASR hỗ trợ word-level timestamp thông qua thiết lập enable | https://docs.nvidia.com/deeplearning/riva/user-guide/docs/asr/asr-overview.html | open-source streaming STT word timestamp: Whisper faster-whisper Vosk NVIDIA Riva Parakeet (1) | 9 |
| 6 | faster-whisper hỗ trợ word-level timestamp bằng cách thiết lập tham số word_time | https://github.com/SYSTRAN/faster-whisper | open-source streaming STT word timestamp: Whisper faster-whisper Vosk NVIDIA Riva Parakeet (1) | 9 |
| 7 | Vosk (alphacep/vosk-api) hỗ trợ word-level timestamp trong chế độ streaming bằng | https://github.com/alphacep/vosk-api | open-source streaming STT word timestamp: Whisper faster-whisper Vosk NVIDIA Riva Parakeet (1) | 9 |
| 8 | Thuật toán FastEmit giải quyết hạn chế trễ của CTC/Transducer trong chế độ strea | https://arxiv.org/abs/2010.11148 | kỹ thuật word-level timestamp + benchmark latency: forced alignment CTC streaming (1) | 9 |
| 9 | NVIDIA Parakeet (thuộc họ mô hình NeMo ASR với kiến trúc TDT / RNNT / CTC) hỗ tr | https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/models.html | open-source streaming STT word timestamp: Whisper faster-whisper Vosk NVIDIA Riva Parakeet (1) | 8 |

Sinh lúc: 2026-07-31T15:43:28+07:00 · rank tất định bằng code (route xác nhận → URL sống → có quote → score → thứ tự route).
