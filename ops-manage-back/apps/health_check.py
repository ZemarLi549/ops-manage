import logging

from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):

    def get(self, request, *args, **params):
        # logger.info("params:%s", params)
        # logger.info("request.data:%s", request.data)

        # return format: "OK:appname:release_tag"
        # e.g: "OK:dlg-app:reg_20181227_01"
        try:
            hc_path = settings.HEALTH_CHECK_PATH

            with open(hc_path, 'r') as f:
                content = f.read()

            return HttpResponse(content, content_type='text/plain')
        except Exception as e:
            return HttpResponse(str(e), content_type='text/plain', status=500)
