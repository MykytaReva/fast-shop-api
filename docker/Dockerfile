FROM ubuntu:latest

WORKDIR /app

RUN apt-get update && apt-get install -y python3 python3-venv python3-pip

RUN python3 -m venv env
RUN . env/bin/activate && pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt


#ENV CONDA_ENV_PATH /opt/shop-online-api
#
#RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh \
#    && bash /tmp/miniconda.sh -b -p /opt/conda \
#    && rm /tmp/miniconda.sh
#
#ENV PATH="/opt/conda/bin:${PATH}"
#COPY environment.yml /tmp/environment.yml
#RUN conda env create -f /tmp/environment.yml
#ENV PATH /opt/conda/envs/shop-online-api/bin:$PATH

COPY . .

EXPOSE 8000

CMD ["uvicorn", "shop.main:app", "--host", "0.0.0.0", "--port", "8000"]
