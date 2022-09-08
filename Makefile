.PHONY: image push apply-crd run

image:
	make -C build image

push:
	make -C build push

push-prod:
	make -C build push-prod

apply-crd:
	kubectl apply -f deployment/crds.yaml

run:
	kopf run main.py --verbose

start-app:
	kubectl apply -f test-manifests/hello-world.yml -n default

drop-app:
	kubectl delete -f test-manifests/hello-world.yml -n default
