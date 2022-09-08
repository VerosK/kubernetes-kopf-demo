import datetime
import os

import kopf
import kubernetes
from kubernetes import client

from .helpers import render_template, test_job_status

API_GROUP = 'wftech.eu'
OPERATOR_PREFIX = 'python.wftech.eu'
API_VERSION = 'v1'
API_PLURAL = 'pythonapps'
PYTHON_APP_LABEL = f'{OPERATOR_PREFIX}/python-app'
JOB_NAME_ANNOTATION = f'{OPERATOR_PREFIX}/job-name'

# setup Kubernetes API server
if os.environ.get('KUBERNETES_PORT', None):
    print("Using in-cluster Kubernetes config")
    kubernetes.config.load_incluster_config()
else:
    print("Using default Kubernetes config")
    kubernetes.config.load_kube_config(os.environ.get('KUBECONFIG'))


# noinspection PyUnusedLocal
@kopf.on.startup()
def startup_fn(logger, **kwargs):
    print("Operator is starting")


# noinspection PyUnusedLocal
@kopf.on.create(API_GROUP, API_VERSION, API_PLURAL)
def on_app_create(status, body, name, namespace, spec, **_):
    """
    This is called on creation of the object
    """
    print(f"Created object {namespace}/{name} ")

    kopf.event(
        body,
        type='Operator',
        reason='Created',
        message=f"App has been found",
    )


@kopf.on.event(API_GROUP, API_VERSION, API_PLURAL)
def ensure_job(body, **kwargs):
    """
    Ensure PythonApp has attached Job obect
    """

    annotations = body.metadata.annotations
    job_name_annotation = f'{OPERATOR_PREFIX}/job-name'
    job_name = annotations.get(job_name_annotation, None)

    if not job_name:
        create_job(body=body, **kwargs)


def create_job(name, namespace, spec, status, body, logger,
               **_):
    """
    Create job for my PythonAppobject.
    :return job name
    """

    # render job template
    context = dict(
        namespace=namespace,
        app_name=name,
        source=spec['source'],
        memory_limit_mb=spec['memoryLimitMib'],
        time_limit_seconds=spec['timeLimitSeconds'],
        image_name=spec['imageName'],
    )
    job_body = render_template(f'app.yml', context)
    job_body['metadata']['labels'][PYTHON_APP_LABEL] = name

    # set ownerReference to PythonApp object
    kopf.adopt(job_body)

    # start the job
    batch_api = client.BatchV1Api()
    api_response = batch_api.create_namespaced_job(
        namespace=namespace, body=job_body)

    api_job_name = api_response.metadata.name

    # enumerate event
    logger.info(f"Created new job: {api_job_name}")
    kopf.event(
        body,
        type="JobStarted",
        reason="Created",
        message=f"Created job: {api_job_name}",
    )

    # ensure job field
    patch = dict(
        metadata=dict(
            annotations={
                JOB_NAME_ANNOTATION: api_job_name,
            },
        ),
        status=dict(
            jobName=api_job_name,
            jobStatus='Created',
        )
    )

    api = client.CustomObjectsApi()
    api.patch_namespaced_custom_object(
        group=API_GROUP,
        version=API_VERSION,
        namespace=namespace,
        plural=API_PLURAL,
        name=name,
        body=patch,
    )

    logger.info(f"Created new job {api_job_name}")
    kopf.event(
        body,
        type="Job",
        reason="Created",
        message=f"Created Job: {api_job_name}",
    )

    return api_job_name


job_label_filters = {
    # python.wftech.eu/python-app
    PYTHON_APP_LABEL: kopf.PRESENT,
}


@kopf.on.event('batch', 'v1', 'jobs', labels=job_label_filters)
def handle_batch_job_events(body, type, namespace, name, labels, **kwargs):
    """
    Handle completion of K8s batch/v1 Jobs managed by our operator

    When the job is finished, update status of the PythonApp object
    """
    if type != 'MODIFIED':
        return

    is_complete = test_job_status(body, 'Complete')
    is_failed = test_job_status(body, 'Failed')

    if not is_complete and not is_failed:
        return

    app_name = labels[PYTHON_APP_LABEL]

    # get PythonApp object
    api = client.CustomObjectsApi()
    obj = api.get_namespaced_custom_object(
        group=API_GROUP,
        version=API_VERSION,
        namespace=namespace,
        plural=API_PLURAL,
        name=app_name,
    )

    # emit event
    kopf.event(
        objs=obj,
        type=f"Job",
        reason="Finished",
        message=f"Job '{name}' finished",
    )

    # create patch object
    patch = dict(
        status=dict(
            jobStatus="Completed",
            jobFinishedAt=str(datetime.datetime.utcnow()),
        )
    )
    # patch PythonApp object status fields
    api.patch_namespaced_custom_object(
        group=API_GROUP,
        version=API_VERSION,
        namespace=namespace,
        plural=API_PLURAL,
        name=app_name,
        body=patch,
    )
