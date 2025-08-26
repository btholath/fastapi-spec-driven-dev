cd /workspaces/fastapi-spec-driven-dev
source .venv/bin/activate
docker-compose down
docker system prune -f --volumes
DOCKER_BUILDKIT=0 docker-compose up --build -d