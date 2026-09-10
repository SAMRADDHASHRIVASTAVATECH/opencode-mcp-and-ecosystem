# Latency and performance
Start with `latency="low"`, `blocksize=0`, 48 kHz and one channel. PortAudio chooses host-optimal callback sizes. Increase host latency if underruns occur. Shared WASAPI is most compatible; exclusive mode can lower latency but prevents shared application access and is not exposed by this backend yet.

The callback performs no disk I/O, model loading or MCP work. Stateful delay currently loops per frame and should be avoided at very large channel/block configurations. Monitor backend CPU load, process CPU/memory, callback age, underruns and overruns. AI conversion adds chunk/context/inference latency and must use a bounded worker queue that drops stale audio rather than blocking callbacks; that adapter is not installed.

## Local deterministic benchmark
On the supplied Linux sandbox, 10 seconds of mono 48 kHz audio in 480-frame blocks through gate, low shelf, robot modulation, compressor, delay and limiter took 2.329 s wall time (4.29× real-time; mean 2.329 ms per 10 ms block; process RSS about 101.3 MiB). This is a synthetic DSP benchmark, not an audio-device, Windows, round-trip, Discord or AI-model latency measurement.
