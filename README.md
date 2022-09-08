# Kopf demo

This is a demo of Kopf, a framework for Kubernetes operators prepared 
for the Pycon.sk 2022 talk.

## The goal

* Create `PythonApplication` object in Kubernetes 

* Operator should start Job corresponding to the PythonApplication object

* After Job is finished, Operator should update PythonApplication object with the result

* Profit!

## How to run

* Create PythonApp CRD

      make crd

* run the operator locally (in a separate background terminal)

      make run

* create PythonApplication object and watch 
 Job object being created

      make start-app


### License

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

No warranty. Use at your own risk.  It it breaks, you should keep both pieces.
