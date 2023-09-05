FROM ubuntu:latest

RUN apt-get update && apt-get install -y wget

ENV CONDA_ENV_PATH /opt/shop-online-api

RUN wget --no-check-certificate  https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -b -p /opt/conda \
    && rm /tmp/miniconda.sh

ENV PATH="/opt/conda/bin:${PATH}"
COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml --insecure
RUN echo "source activate shop-online-api" >> ~/.bashrc
ENV PATH /opt/conda/envs/shop-online-api/bin:$PATH

WORKDIR /app

COPY . .

EXPOSE 8000

CMD ["uvicorn", "shop.main:app", "--host", "0.0.0.0", "--port", "8000"]

