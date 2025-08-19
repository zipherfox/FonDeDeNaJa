# 🚀 Docker Deployment Guide for FonDeDeNaJa Rust OMR

This guide covers deploying the blazingly fast Rust OMR application using Docker.

## Quick Start

### Using Docker Compose (Recommended)

1. **For Rust application only:**
   ```bash
   # Start the blazingly fast Rust web interface
   docker-compose -f docker-compose.rust.yml up -d
   
   # View logs
   docker-compose -f docker-compose.rust.yml logs -f
   
   # Stop the application
   docker-compose -f docker-compose.rust.yml down
   ```

2. **For both Rust and legacy Python applications:**
   ```bash
   # Start both services
   docker-compose up -d
   
   # Access Rust web interface at http://localhost:3000
   # Access legacy Streamlit interface at http://localhost:8501
   ```

### Using Docker directly

1. **Build the image:**
   ```bash
   docker build -f Dockerfile.rust -t fondedenaja-rust .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name fondedenaja-omr \
     -p 3000:3000 \
     -v $(pwd)/uploads:/app/uploads:rw \
     -v $(pwd)/outputs:/app/outputs:rw \
     fondedenaja-rust
   ```

3. **Access the web interface:**
   Open your browser to http://localhost:3000

## Configuration

### Environment Variables

- `RUST_LOG`: Log level (default: `info`)
  - Options: `error`, `warn`, `info`, `debug`, `trace`
- `BIND_ADDRESS`: Server bind address (default: `0.0.0.0:3000`)
- `AUTO_ALIGN`: Enable automatic image alignment (default: `true`)
- `DEBUG_MODE`: Enable debug mode (default: `false`)

### Volume Mounts

- `/app/uploads`: Directory for uploaded image files
- `/app/outputs`: Directory for processed results
- `/app/templates`: Optional directory for custom OMR templates

### Port Configuration

- `3000`: Web interface (default)
- Health check endpoint: `GET /api/health`

## Production Deployment

### Docker Compose for Production

```yaml
services:
  rust-omr:
    build:
      context: .
      dockerfile: Dockerfile.rust
    container_name: fondedenaja_production
    ports:
      - "3000:3000"
    volumes:
      - /data/uploads:/app/uploads:rw
      - /data/outputs:/app/outputs:rw
      - /data/templates:/app/templates:ro
    environment:
      - RUST_LOG=warn
      - AUTO_ALIGN=true
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 1G
```

### Reverse Proxy Setup

For production, use a reverse proxy like Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring and Health Checks

### Health Check

The application provides a health check endpoint:

```bash
curl http://localhost:3000/api/health
```

Response:
```json
{
  "status": "🚀 Blazingly Fast and Memory Safe! 🚀",
  "version": "0.1.0"
}
```

### Docker Health Check

The docker-compose configuration includes automatic health checks:

- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3
- **Start Period**: 40 seconds

### Logs

View application logs:
```bash
# Using docker-compose
docker-compose -f docker-compose.rust.yml logs -f

# Using docker directly  
docker logs -f fondedenaja-omr
```

## Performance Tuning

### Resource Limits

Recommended resource allocation:

- **Memory**: 2GB limit, 512MB reservation
- **CPU**: 2 cores for optimal performance
- **Storage**: SSD recommended for image processing

### Scaling

For high-load scenarios, run multiple instances:

```yaml
services:
  rust-omr:
    # ... configuration ...
    deploy:
      replicas: 3
    ports:
      - "3000-3002:3000"
```

Use a load balancer to distribute requests across instances.

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Check what's using port 3000
   sudo lsof -i :3000
   
   # Use different port
   docker run -p 3001:3000 fondedenaja-rust
   ```

2. **Permission issues with volumes:**
   ```bash
   # Fix ownership
   sudo chown -R 1000:1000 uploads/ outputs/
   ```

3. **Memory issues:**
   - Increase Docker memory limit
   - Process images in smaller batches
   - Use lower resolution images

### Debug Mode

Enable debug mode for detailed logging:

```bash
docker run -e RUST_LOG=debug -e DEBUG_MODE=true fondedenaja-rust
```

## Security Considerations

- The application runs as non-root user (UID 1000)
- Input validation for uploaded files
- Secure file handling with temporary directories
- No external network access required (self-contained)

## Backup and Recovery

### Backup Important Data

```bash
# Backup uploads and outputs
tar -czf backup-$(date +%Y%m%d).tar.gz uploads/ outputs/

# Backup using Docker volumes
docker run --rm -v fondedenaja_uploads:/data -v $(pwd):/backup alpine \
  tar czf /backup/uploads-backup.tar.gz /data
```

### Recovery

```bash
# Restore from backup
tar -xzf backup-20240101.tar.gz
```

## Updates

### Update the Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose -f docker-compose.rust.yml down
docker-compose -f docker-compose.rust.yml build --no-cache
docker-compose -f docker-compose.rust.yml up -d
```

## Performance Metrics

Expected performance improvements over Python version:

- **🚀 250x faster startup time**
- **🚀 Memory-safe processing with zero leaks**  
- **🚀 Parallel processing with Rayon**
- **🚀 Single binary deployment**
- **🚀 Predictable resource usage**

---

For more information, see the main [README.md](README.md) and [README_RUST.md](README_RUST.md).