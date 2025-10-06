# 🐳 Docker Deployment Guide for InfoTransform

This guide explains how to run InfoTransform using Docker, making it easy to deploy on any developer's laptop without manual setup of Python, Node.js, or dependencies.

## 📋 Prerequisites

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **OpenAI API Key** (required for AI processing)

### Installing Docker

- **Windows/macOS**: Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux**: Install Docker Engine and Docker Compose from your package manager

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/owenffff/InfoTransform.git
cd InfoTransform
```

### 2. Configure Environment Variables

Create a `.env` file from the template:

```bash
cp .env.docker .env
```

Edit `.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Build and Run

**Production Mode** (optimized, no hot-reload):

```bash
docker-compose up --build
```

**Development Mode** (with hot-reload for code changes):

```bash
docker-compose -f docker-compose.dev.yml up --build
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📦 Docker Commands Reference

### Starting Services

```bash
# Start in production mode (detached)
docker-compose up -d

# Start in development mode with live reload
docker-compose -f docker-compose.dev.yml up

# Rebuild and start (use after code changes in production)
docker-compose up --build
```

### Stopping Services

```bash
# Stop services (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (clears data)
docker-compose down -v
```

### Viewing Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs -f infotransform
```

### Managing Containers

```bash
# List running containers
docker-compose ps

# Restart services
docker-compose restart

# Execute command in running container
docker-compose exec infotransform bash

# View resource usage
docker stats
```

## 🔧 Configuration

### Port Configuration

Default ports can be changed in your `.env` file:

```bash
# External port mappings (host:container)
PORT=8000          # Backend API port
FRONTEND_PORT=3000 # Frontend UI port
```

To use different ports, modify `docker-compose.yml`:

```yaml
ports:
  - "8080:8000"  # Map host port 8080 to container port 8000
  - "3001:3000"  # Map host port 3001 to container port 3000
```

### Volume Mounts

Data is persisted in the following directories:

- `./data/uploads` - Uploaded files
- `./data/temp_extracts` - Temporary file extractions
- `./logs` - Application logs

These directories are automatically created and mounted as Docker volumes.

## 🏗️ Architecture

The Docker setup uses two configurations:

### Production (`Dockerfile` + `docker-compose.yml`)

- Multi-stage build for optimized image size
- Pre-built Next.js frontend (fast startup)
- Production-optimized dependencies
- Health checks for monitoring
- Automatic restart on failure

### Development (`Dockerfile.dev` + `docker-compose.dev.yml`)

- Source code mounted as volumes
- Hot-reload for frontend and backend
- Full dev dependencies included
- Faster iteration for development

## 🐛 Troubleshooting

### Port Already in Use

If ports 3000 or 8000 are already in use:

```bash
# Find and kill process using port
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9

# Or change ports in docker-compose.yml
```

### Container Won't Start

```bash
# Check logs for errors
docker-compose logs

# Remove old containers and rebuild
docker-compose down -v
docker-compose up --build
```

### Permission Issues (Linux)

If you encounter permission errors with volumes:

```bash
# Fix ownership of data directories
sudo chown -R $USER:$USER data/ logs/
```

### Out of Memory

Increase Docker memory allocation:

- **Docker Desktop**: Settings → Resources → Memory (set to at least 4GB)

### API Key Not Working

Verify your `.env` file:

```bash
# Check if .env exists and has correct format
cat .env | grep OPENAI_API_KEY

# Ensure no spaces around the = sign
# Correct:   OPENAI_API_KEY=sk-...
# Incorrect: OPENAI_API_KEY = sk-...
```

## 🔒 Security Best Practices

1. **Never commit `.env` file** - It contains sensitive API keys
2. **Use environment-specific `.env` files** - Keep production keys separate
3. **Restrict CORS in production** - Edit `config/config.yaml` to allow only specific origins
4. **Enable API key authentication** - Set `security.api_key_required: true` in production
5. **Use secrets management** - Consider Docker secrets for production deployments

## 🚢 Deploying to Production

### Cloud Deployment Options

**1. Docker Compose on VPS**

```bash
# On your server
git clone <repo>
cd InfoTransform
cp .env.docker .env
# Edit .env with production keys
docker-compose up -d
```

**2. AWS ECS / Google Cloud Run**

- Build and push image to container registry
- Configure environment variables in cloud console
- Deploy from container registry

**3. Kubernetes**

```bash
# Build and tag image
docker build -t infotransform:v1.0 .

# Push to registry
docker push your-registry/infotransform:v1.0

# Create Kubernetes deployment (example)
kubectl create deployment infotransform --image=your-registry/infotransform:v1.0
```

### Production Checklist

- [ ] Set strong `SECRET_KEY` in `.env`
- [ ] Restrict CORS origins in `config/config.yaml`
- [ ] Enable API key authentication
- [ ] Set up HTTPS/TLS with reverse proxy (nginx, traefik)
- [ ] Configure log rotation for `./logs`
- [ ] Set up monitoring and health checks
- [ ] Regular backups of `./data/uploads`
- [ ] Use Docker secrets for sensitive data

## 📊 Monitoring

### Health Checks

The backend includes built-in health checks:

```bash
# Check if services are healthy
docker-compose ps

# Manual health check
curl http://localhost:8000/docs
```

### Resource Monitoring

```bash
# Real-time resource usage
docker stats infotransform

# Check disk usage
docker system df
```

## 🔄 Updating the Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d

# Check logs
docker-compose logs -f
```

## 📝 Advanced Usage

### Custom Docker Network

Create a custom network for integration with other services:

```bash
docker network create infotransform-net
```

Update `docker-compose.yml` to use the external network.

### Using Docker Compose Profiles

Add profiles for different deployment scenarios:

```yaml
services:
  infotransform:
    profiles: ["production"]
  
  infotransform-dev:
    profiles: ["development"]
```

Run with:

```bash
docker-compose --profile production up
```

## 💡 Tips

1. **Faster Rebuilds**: Use BuildKit for improved build performance
   ```bash
   DOCKER_BUILDKIT=1 docker-compose build
   ```

2. **Clean Docker Cache**: Free up disk space
   ```bash
   docker system prune -a
   ```

3. **Inspect Container**: Debug issues inside the container
   ```bash
   docker-compose exec infotransform bash
   ```

4. **Copy Files**: Transfer files to/from container
   ```bash
   docker cp local-file.txt infotransform:/app/
   docker cp infotransform:/app/logs/app.log ./
   ```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [InfoTransform Main README](./README.md)
- [InfoTransform CLAUDE.md](./CLAUDE.md) - Development guidelines

## 🆘 Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section above
2. Review Docker logs: `docker-compose logs -f`
3. Verify `.env` configuration
4. Open an issue on [GitHub](https://github.com/owenffff/InfoTransform/issues)

---

**Ready to transform documents?** Run `docker-compose up` and visit http://localhost:3000 🚀
