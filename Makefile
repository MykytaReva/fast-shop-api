run:
	cd shop && uvicorn main:app --reload

create_environment: environment.yml
	conda env create -f environment.yml

activate:
	conda activate shop-online-api

update_environment:
	conda env update -f environment.yml

docker:
	docker run -it -p 8000:8000 shop-online-api

docker_build:
	docker build -t shop-online-api -f docker/Dockerfile .
