.PHONY: install build plan deploy destroy clean upload-to-s3

PYTHON = python3
TERRAFORM = terraform

APP_DIR = app
MAIN_SCRIPT = run.py
INFRA_DIR = infra/api
VENV = venv
ENV_FILE = .env
FIREBASE_CRED = firebase_credentials.json
S3_BUCKET = foodfridge-20240127052946263200000001

install:
	$(PYTHON) -m pip install -r requirements.txt

build: clean
	# Create a temporary 'build' directory for dependencies
	mkdir build

	# Install dependencies into the 'build' directory
	pip install --no-cache-dir -r requirements.txt -t build/
	pip install --no-cache-dir pip install google-cloud-firestore -t build/

	# Copy the main script, .env, and firebase credentials into 'build'
	# Assuming these files are in the same directory as the Makefile
	cp ./$(MAIN_SCRIPT) ./build
	cp ./$(ENV_FILE) ./build
	cp ./$(FIREBASE_CRED) ./build
	cp -r ./$(APP_DIR) ./build

	# Create the lambda.zip file with all contents of 'build'
	cd build && zip -r ../lambda.zip . && cd ..

	# Clean up the 'build' directory
	rm -rf build/

upload:
	aws s3 cp lambda.zip s3://$(S3_BUCKET)/lambda.zip

plan:
	cd $(INFRA_DIR) && $(TERRAFORM) init && $(TERRAFORM) plan

deploy: upload
	cd $(INFRA_DIR) && $(TERRAFORM) apply -auto-approve

destroy:
	cd $(INFRA_DIR) && $(TERRAFORM) destroy -auto-approve

clean:
	rm -f
	rm -rf build

all: install build plan deploy
