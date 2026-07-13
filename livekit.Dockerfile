# Custom LiveKit SOTA Image
FROM livekit/livekit-server:1.7.0
COPY livekit.yaml /etc/livekit.yaml
CMD ["--config", "/etc/livekit.yaml"]
