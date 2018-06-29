from django.conf import settings
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import json
import logging

logger = logging.getLogger(__name__)

def get_user_groups(request):
    user_id = request.user.username
    admin_group_id = settings.ADMIN_GROUP_ID

    if settings.MOCK_VOOT and settings.DEBUG:
        with open('fim_catalog/openconext/mock_json/voot2/voot2_groups.json') as data_file:
            groups = json.load(data_file)
        # If user is a mock admin override the default group name
        if settings.MOCK_VOOT_USER_IS_ADMIN:
            admin_group_id = 'id1'
    else:
        client_id = settings.VOOT_OAUTH_CLIENT_ID
        client_secret = settings.VOOT_OAUTH_CLIENT_SECRET
        token_url = settings.VOOT_OAUTH_TOKEN_URL
        voot_url = settings.VOOT_URL

        client = BackendApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)
        r = oauth.get(voot_url + '/internal/groups/{}'.format(user_id))

        if r.status_code != 200:
            logger.error("Did not receive an HTTP 200 response from VOOT endpoint")
            return False

        groups = json.loads(r.text)

    try:
        if len(groups) == 0:
            logger.debug("User not part of any groups")
        else:
            for g in groups:
                if admin_group_id in g.items():
                  return True
    except AttributeError as e:
        logger.error("Unable to check voot group data: {}".format(e))

    return False
