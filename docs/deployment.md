# Deployment

## Single-Machine (Linux)

### Systemd Service

Create `/etc/systemd/system/hakid.service`:

```ini
[Unit]
Description=Haki Cognitive OS Daemon
After=network.target

[Service]
Type=simple
User=haki
ExecStart=/usr/local/bin/haki daemon
Restart=always
RestartSec=10
Environment="HAKI_LLM_API_KEY=sk-..."
Environment="HAKI_DATA_DIR=/var/lib/haki"
WorkingDirectory=/var/lib/haki

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable hakid
sudo systemctl start hakid
sudo systemctl status hakid
```

## Docker

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY pyproject.toml .
RUN pip install -e .

RUN mkdir -p /data
ENV HAKI_DATA_DIR=/data
VOLUME /data

EXPOSE 8765

CMD ["haki", "daemon"]
```

### Docker Compose

```yaml
version: "3.8"
services:
  haki:
    build: .
    ports:
      - "8765:8765"
    environment:
      HAKI_LLM_API_KEY: ${HAKI_LLM_API_KEY}
      HAKI_LLM_MODEL: gpt-4o-mini
      HAKI_DATA_DIR: /data
    volumes:
      - haki_data:/data
    restart: unless-stopped

volumes:
  haki_data:
```

## GPU Support

For Lab fine-tuning, add NVIDIA runtime:

```yaml
# docker-compose.gpu.yml
services:
  haki:
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
```

Build with GPU extras:

```dockerfile
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04
RUN apt-get update && apt-get install -y python3.10 python3-pip
WORKDIR /app
COPY pyproject.toml .
RUN pip install -e ".[gpu]"
```

## Production Checklist

- [ ] Reverse proxy (nginx/traefik) for MCP port
- [ ] TLS for any external-facing endpoints
- [ ] Encrypted storage for `memory.db`
- [ ] Log rotation for `~/.haki/lab/logs/`
- [ ] Monitoring on health endpoint (`haki health`)
- [ ] Backup strategy for `memory.db` and trained adapters
- [ ] Resource limits (GPU memory, disk quota)

## Environment Variables for Prod

```bash
# /etc/haki/env
HAKI_DATA_DIR=/var/lib/haki
HAKI_LLM_API_KEY=sk-...
HAKI_HEALTH_INTERVAL=60
HAKI_LAB_GPU=true
HAKI_LAB_TIME_BUDGET=600
```

## Multi-User / Multi-Tenant

Haki is currently single-user by design. For multi-tenant:

1. Run separate instances per user (isolate `HAKI_DATA_DIR`)
2. Add auth layer in MCP bridge
3. Containerize per-tenant

## Cloud Deploy

| Platform | Notes |
|----------|-------|
| **AWS** | ECS/Fargate + EFS for storage |
| **GCP** | Cloud Run (stateless) or GKE |
| **Azure** | Container Instances |
| **Hetzner** | CX51 + Docker ($12/mo) |

## Monitoring

```bash
# Health check endpoint
haki health --json

# Metrics from logs
cat ~/.haki/lab/logs/*.log | grep "val_bpb"

# Disk usage
du -sh ~/.haki/
```
