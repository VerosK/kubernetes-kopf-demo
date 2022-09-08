MODULE := python-operator

REGISTRY ?= localhost

IMAGE_NAME := $(REGISTRY)/$(MODULE)
CONTAINER_ENGINE := $(shell command -v podman 2> /dev/null | echo docker)



.PHONY: image push prod push-prod

image: requirements.txt
	(cd ../; $(CONTAINER_ENGINE) build -t $(IMAGE_NAME) -f build/Containerfile . )
	@echo

requirements.txt: ../Pipfile.lock
	( cd ../; pipenv lock --requirements >build/requirements.txt )

push: image
	$(CONTAINER_ENGINE) push $(IMAGE_NAME)

latest: image
	$(CONTAINER_ENGINE) tag $(IMAGE_NAME) $(IMAGE_NAME):latest

push-latest: prod
	$(CONTAINER_ENGINE) push $(IMAGE_NAME):latest
