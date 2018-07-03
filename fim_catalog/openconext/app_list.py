from django.conf import settings
import logging
from . import manage, pdpclient

logger = logging.getLogger(__name__)


def get_app_list(request):
    m_data = manage.get_metadata()

    app_list = []

    for e in m_data:
        sp_data = {}
        metadata_fields = e["data"].get("metaDataFields")
        sp_entityid = e["data"].get("entityid")
        sp_name = metadata_fields.get("name:en")
        sp_state = e["data"].get("state")
        sp_app_url = metadata_fields.get("coin:application_url")
        sp_logo_url = metadata_fields.get("logo:0:url", "https://.png")
        sp_logo_width = metadata_fields.get("logo:0:width", "50")
        sp_logo_height = metadata_fields.get("logo:0:height", "50")
        sp_allowed_all = e["data"].get("allowedall")
        sp_allowed_entities = e["data"].get("allowedEntities")
        sp_login_url_template = settings.EB_URL + "?sp-entity-id={}{}"
        sp_pdp_required = metadata_fields.get("coin:policy_enforcement_decision_required", "0") == "1"
        idp = request.META['Shib-Authenticating-Authority']

        if sp_state != "prodaccepted":
            logger.debug("Service {} is not state='prodaccepted'")
            continue

        # Hide SPs without names
        if sp_name is None:
            logger.debug("SP {} has no name:en entry in metadata".format(sp_entityid))
            continue
        elif sp_name.startswith(settings.CATALOG_PREFIX_HIDE):
            logger.debug("SP {} excluded due to {} prefix".format(sp_entityid, settings.CATALOG_PREFIX_HIDE))
            continue

        if sp_pdp_required:
            if not pdpclient.is_user_authorized_for_sp(request, sp_entityid):
                continue

        sp_login_url = get_app_url(sp_entityid, sp_login_url_template, sp_app_url)

        # Use placeholder logo if unset in metadata
        # if e.get("logo:0:url", "https://.png") == "https://.png":
        #     e["logo:0:url"] = flask.url_for("static", filename="images/placeholder.png")

        sp_data["name_en"] = sp_name
        sp_data["loginUrl"] = sp_login_url
        sp_data["logo_url"] = sp_logo_url
        sp_data["logo_width"] = sp_logo_width
        sp_data["logo_height"] = sp_logo_height

        if sp_allowed_all:
            app_list.append(sp_data)
        elif sp_allowed_entities is not None:
            if idp in sp_allowed_entities:
                app_list.append(sp_data)

    return app_list

def get_app_url(sp_entityid, sp_login_url_template, sp_app_url):
    # Use URL from metadata or generate IdP-initiated URL

    if not sp_app_url or sp_app_url == "":
        return sp_login_url_template.format(sp_entityid, "")
    else:
        return sp_login_url_template.format(sp_entityid, "&RelayState="+sp_app_url)

    return app_url
