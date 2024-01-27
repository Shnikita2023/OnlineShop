up:
	docker compose -f docker-compose.yaml up -d


down:
	docker compose -f docker-compose.yaml down --remove-orphans && docker volume prune -f && docker network prune -f
