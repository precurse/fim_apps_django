from django.contrib.auth.middleware import RemoteUserMiddleware
from fim_catalog import settings

class ShibbolethDeveloperMode(RemoteUserMiddleware):

    def process_request(self, request):
        if settings.SHIBBOLETH_MOCK_HEADERS and settings.DEBUG:
            request.META[self.header] = settings.MOCK_SHIB_USERID
            request.META['name-id'] = settings.MOCK_SHIB_USERID
            request.META['displayName'] = settings.MOCK_SHIB_DISPLAYNAME
            request.META['Shib-InetOrgPerson-mail'] = settings.MOCK_SHIB_EMAIL
            request.META['Shib-Authenticating-Authority'] = settings.MOCK_SHIB_IDP
