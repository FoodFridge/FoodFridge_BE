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

build:
	# Create a temporary 'build' directory for dependencies
	mkdir build

	# Install dependencies into the 'build' directory
	pip install --no-cache-dir -r requirements.txt -t build/
	pip install --no-cache-dir pip install google-cloud-firestore -t build/

	# Copy the main script, .env, and firebase credentials into 'build'
	cp ./$(MAIN_SCRIPT) ./build
	cp ./$(ENV_FILE) ./build
	cp ./$(FIREBASE_CRED) ./build
	cp ./ingredients.json ./build
	cp -r ./$(APP_DIR) ./build

	# Generate ZIP file name with timestamp
	$(eval TIMESTAMP := $(shell date +"%Y%m%d%H%M%S"))
	$(eval ZIP_FILE := lambda-$(TIMESTAMP).zip)

	# Create the ZIP file with all contents of 'build'
	cd build && zip -r ../$(ZIP_FILE) . && cd ..

	# Clean up the 'build' directory
	rm -rf build/

upload:
	aws s3 cp $(ZIP_FILE) s3://$(S3_BUCKET)/$(ZIP_FILE)

plan:
	cd $(INFRA_DIR) && $(TERRAFORM) init && $(TERRAFORM) plan -var "lambda_zip_file=$(ZIP_FILE)"

deploy:
	cd $(INFRA_DIR) && $(TERRAFORM) apply -auto-approve -var "lambda_zip_file=$(ZIP_FILE)"

destroy:
	cd $(INFRA_DIR) && $(TERRAFORM) destroy -auto-approve

clean:
	rm -f lambda-*.zip
	rm -rf build

all-local: install clean build upload plan deploy

all-aws: install build upload plan deploy
