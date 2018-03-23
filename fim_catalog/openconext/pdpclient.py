from django.conf import settings
import requests
import json
import logging

logger = logging.getLogger(__name__)

def is_user_authorized_for_sp(request, service_provider):
    if settings.MOCK_PDP and settings.DEBUG:
        if settings.MOCK_PDP_SP_DENY:
            pdp_json = {'Response': [ { 'Decision': 'Deny'  } ]}
        else:
            pdp_json = {'Response': [ { 'Decision': 'Allow'  } ]}
    else:
        headers = { "Content-Type": "application/json" }

        user_id = request.META['name-id']
        idp = request.META['Shib-Authenticating-Authority']

        pdp_policy = {
            "Request": {
                "ReturnPolicyIdList": False,
                "CombinedDecision": False,
                "AccessSubject": {
                    "Attribute": [{
                        "AttributeId": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
                        "Value": user_id
                    }]
                },
                "Resource": {
                    "Attribute": [
                        {
                            "AttributeId": "SPentityID",
                            "Value": service_provider
                        },
                        {
                            "AttributeId": "IDPentityID",
                            "Value": idp
                        }
                    ]
                }
            }
        }

        r = requests.post(settings.PDP_URL + '/pdp/api/decide/policy', auth=(settings.PDP_USER, settings.PDP_PASSWORD), headers=headers, data=json.dumps(pdp_policy))

        if r.status_code != 200:
            logger.error("Unexpected status code {} for {}".format(r.status_code, settings.PDP_URL))
            return False

        pdp_json = r.json()

    try:
        return pdp_json['Response'][0]['Decision'] != "Deny"
    except (KeyError, TypeError, IndexError, ValueError):
        logger.error("Unexpected response body for {}. No Reponse Decision found.".format(settings.PDP_URL))

    return False

