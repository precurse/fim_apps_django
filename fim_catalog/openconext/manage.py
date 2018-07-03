from django.core.cache import cache
from django.conf import settings
import json
import requests
import logging

logger = logging.getLogger(__name__)

def get_metadata():

    if settings.MOCK_MANAGE and settings.DEBUG:
        logger.debug('Using mock Manage metadata')
        with open('fim_catalog/openconext/mock_json/manage_metadata_sp.json', 'r') as data_file:
            metadata_json = json.load(data_file)
    else:
        metadata_json = cache.get('metadata')

        if not metadata_json:
            logger.info('refreshing metadata cache')
            headers = { "Content-Type": "application/json" }
            post_data = '{"ALL_ATTRIBUTES":true}'

            r = requests.post(settings.MANAGE_URL + '/manage/api/internal/search/saml20_sp',
                             auth=(settings.MANAGE_USER, settings.MANAGE_PASSWORD),
                             headers=headers,
                             data=post_data)

            cache.set('metadata', r.json(), settings.MANAGE_CACHE_TIME)
            metadata_json = r.json()
        else:
            logger.info('metadata cache was used')

    logger.debug(metadata_json)

    return metadata_json
