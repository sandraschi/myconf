# Custom LiveKit SOTA Image
FROM livekit/livekit-server:latest
COPY livekit.yaml /etc/livekit.yaml
CMD ["--config", "/etc/livekit.yaml"]
