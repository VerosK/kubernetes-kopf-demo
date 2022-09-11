# Kopf demo

This is a demo of Kopf, a framework for Kubernetes operators prepared 
for the Pycon.sk 2022 talk.

## The goal

* Create `PythonApplication` object in Kubernetes 

* Operator should start Job corresponding to the PythonApplication object

* After Job is finished, Operator should update PythonApplication object with the result

* Profit!

## How to run

* Bring your own Kubernetes cluster. I used `minikube` for this demo.

* Create PythonApp CRD

      kubectl apply -f deployment/crds.yaml


* run the operator locally (in a separate background terminal)

      kopf run main.py --verbose

  This step may require to create and use Python virtualenv. 


* create PythonApplication object and watch Job resource being created.

      kubectl apply -f test-manifests/hello-world.yml -n default

* drop PythonApplication object.

      kubectl delete -f test-manifests/hello-world.yml -n default

### License

CC0 1.0 Universal (CC0 1.0). Public Domain Dedication.

No warranty. Use at your own risk.  It it breaks, you should keep both pieces.
