from prometheus_client import Counter, Histogram

STREAM_COUNTER = Counter(
    "soundverse_streams_total",
    "Total number of audio streams served",
    ["clip_id"],
)

STREAM_LATENCY = Histogram(
    "soundverse_stream_duration_seconds",
    "Latency of stream endpoint in seconds",
    ["clip_id"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)
