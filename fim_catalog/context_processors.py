from django.conf import settings

def catalog_title(request):
    return {'CATALOG_TITLE': settings.CATALOG_TITLE}
