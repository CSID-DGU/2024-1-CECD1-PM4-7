# Makefile for setting virtual Environment
SHELL := /bin/bash

VENV = gguf
PYTHON = python3

all_CPU:
	make install
	make gguf
	make setup_CPU
	make kernel

all_GPU:
	make install
	make gguf
	make setup_GPU
	make kernel

# install required packages
install:
	sudo apt update
	sudo apt-get install libgomp1
	sudo apt install build-essential
	sudo apt-get install cmake
	sudo apt install python3.10-venv
	sudo apt install git
	sudo apt-get install python3-tk

# making virtual env.
gguf:
	${PYTHON} -m venv ${VENV} && \
	source ${VENV}/bin/activate

# setting virtual env.
setup_CPU:
	source ${VENV}/bin/activate && \
	pip install llama-cpp-python && \
	pip install ipykernel && \
	git clone https://github.com/ggerganov/llama.cpp.git && \
	cd ./llama.cpp && \
	pip install -r requirements.txt && \
	pip install torch==2.4.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
	make -j8

setup_GPU: # on progress
	source ${VENV}/bin/activate && \
	pip install llama-cpp-python && \
	pip install ipykernel && \
	pip install jupyter && \
	git clone https://github.com/ggerganov/llama.cpp.git && \
	cd ./llama.cpp && \
	pip install -r requirements.txt && \
	pip install torch==2.4.0 && \
	make -j8

# setting up Jupyter kernel
kernel:
	source ${VENV}/bin/activate && \
	${PYTHON} -m ipykernel install --user --name=${VENV} --display-name "Python (${VENV})"

# remove virtual env.
clean:
	rm -rf ${VENV}
