from django.conf import settings
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import json
import logging

logger = logging.getLogger(__name__)

def get_user_groups(user_id):

    if settings.MOCK_VOOT and settings.DEBUG:
        logger.debug("Using Mock VOOT client")
        groups = json.load(open('fim_catalog/openconext/mock_json/voot2/voot2_groups.json'))
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

        logging.debug("Got groups: {}".format(r.text))
        groups = json.loads(r.text)

    return groups

def is_user_admin(request):
    admin_group_id = settings.ADMIN_GROUP_ID
    user_id = request.user.username
    user_groups = get_user_groups(user_id)

    if settings.MOCK_VOOT and settings.DEBUG:
        if settings.MOCK_VOOT_USER_IS_ADMIN:
            admin_group_id = 'id1'

    if len(user_groups) == 0:
        logger.debug("User not part of any groups")
    else:
        for g in user_groups:
            if admin_group_id in g['id']:
              return True
