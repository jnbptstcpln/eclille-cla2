from django import template

from cla_monitoring.alerts import admin_alerts as get_admin_alerts

register = template.Library()


@register.inclusion_tag("cla_monitoring/admin_alerts.html", takes_context=True)
def admin_alerts(context):
    user = context.get("user")
    return {"alerts": get_admin_alerts(user) if user is not None and user.is_authenticated else []}
