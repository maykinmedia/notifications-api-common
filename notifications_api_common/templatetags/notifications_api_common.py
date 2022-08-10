from django.template import Library
from django.template.defaultfilters import stringfilter

register = Library()


@register.filter
@stringfilter
def is_local(host: str):
    local_hosts = ["localhost", "127.0.0.1"]
    hostname = host.rsplit(":")[0]
    if hostname in local_hosts:
        return True
    return False
