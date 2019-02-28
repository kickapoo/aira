from django.conf import settings


def map(request):
    query_element = ''
    thunderforest_api_key = getattr(settings, 'AIRA_THUNDERFOREST_API_KEY',
                                    None)
    if thunderforest_api_key:
        query_element = 'apikey={}'.format(thunderforest_api_key)
    map_js = 'aira.thunderforestApiKeyQueryElement = "{}";'.format(
        query_element)
    return {
        'map_js': map_js,
        'google_maps_api_key': getattr(settings, "AIRA_GOOGLE_MAPS_API_KEY", ""),
    }
