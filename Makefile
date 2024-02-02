up:
	docker compose -f app.yaml up


down:
	(docker compose -f docker-compose.yaml down --remove-orphans \ && docker volume prune -f && docker network prune -f
