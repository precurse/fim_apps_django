from django.conf import settings
import logging
from . import metadata, pdpclient

logger = logging.getLogger(__name__)


def get_app_list(request):
    m_data = metadata.get_metadata()

    app_list = []

    for e in m_data:
        sp = e["entityid"]
        idp = request.META['Shib-Authenticating-Authority']

        # Hide SPs without names
        if e.get("name:en") is None:
            logger.error("SP {} has no name:en entry in metadata".format(sp))
            continue

        if e.get("coin:policy_enforcement_decision_required", "0") == "1":
            if not pdpclient.is_user_authorized_for_sp(request, sp):
                continue

        e['loginUrl'] = get_app_url(e)

        # Use placeholder logo if unset in metadata
        # if e.get("logo:0:url", "https://.png") == "https://.png":
        #     e["logo:0:url"] = flask.url_for("static", filename="images/placeholder.png")

        if e.get("allowedall") == "yes":
            app_list.append(clean_app_keys(e))
        elif e.get("allowedEntities") is not None:
            if idp in e["allowedEntities"]:
                app_list.append(clean_app_keys(e))

    return app_list

def clean_app_keys(entity):
    '''
    Takes entity dictionary and replaces ":" with "_" to work with django templating
    '''
    return { x.replace(':', '_'): entity[x] for x in entity.keys() }

def get_app_url(entity):
    # Use URL from metadata or generate IdP-initiated URL
    login_url = settings.EB_URL + '/authentication/idp/unsolicited-single-sign-on?sp-entity-id={}{}'
    app_url = entity.get("coin:application_url", None)

    if not app_url or app_url == "":
        return login_url.format(entity["entityid"], "")
    else:
        return login_url.format(entity["entityid"], "&RelayState="+app_url)

    return app_url
