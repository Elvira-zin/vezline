create_env:
	cp ./config/docker/env ./config/docker/.env

up:
	docker-compose up --build

down:
	docker-compose down

force_up:
	docker-compose up --force-recreate

env_load:
	eval $(config/docker/env_load.sh config/docker/venv.env)

bash:
	docker exec -it now_django bash