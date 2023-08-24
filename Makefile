run:
	cd shop && uvicorn main:app --reload

create_environment: environment.yml
	conda env create -f environment.yml

activate:
	conda activate shop-online-api

update_environment:
	conda env update -f environment.yml
