import jinja2
import yaml

jinja_env = jinja2.Environment(
    loader=jinja2.PackageLoader(__package__)
)


def render_template(template_name, context):
    """
    Render Jinja template with given context.

    :return JSON object
    """
    template = jinja_env.get_template(template_name)
    body = yaml.safe_load(template.render(context))
    return body


def filter_keys_by_prefix(key_dict, prefix):
    """
    Returns dict having only keys with given path prefix.
    """
    prefix = f'{prefix}/'
    filtered = {
        k.split('/', 1)[-1]: v
        for k, v in key_dict.items()
        if k.startswith(prefix)
    }
    return filtered


def test_job_status(body, status_name):
    """
    Examine the job body to see if its status is status_name.
    """
    status = body['status']
    if 'conditions' in status:
        for i in status['conditions']:
            if i['type'] == status_name and i['status'].lower() == 'true':
                return True
    return False
