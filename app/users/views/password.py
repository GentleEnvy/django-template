from django.conf import settings
from django.http import HttpResponseRedirect
from drf_spectacular.utils import OpenApiResponse

from app.base.utils.common import response_204
from app.base.utils.schema import extend_schema
from app.base.views.base import BaseView

PASSWORD_SUCCESS_URL = settings.VERIFICATION_PASSWORD_SUCCESS_URL
PASSWORD_FAILURE_URL = settings.VERIFICATION_PASSWORD_FAILURE_URL


class UsersPasswordView(BaseView):
    @extend_schema(
        responses={
            200: None, 302: OpenApiResponse(
                description=f'redirect:\n\n{"&nbsp;" * 4}что-то пошло не так: '
                            f'{PASSWORD_FAILURE_URL}\n\n{"&nbsp;" * 4}всё'
                            f' нормально: {PASSWORD_SUCCESS_URL % "&lt;session_id&gt;"}'
            )
        }
    )
    def get(self, _, **__):
        return self.handle()
    
    @response_204
    def post(self, _):
        return self.handle()
    
    def put(self, _):
        return self.handle()
    
    def _create_response(self, result_data):
        if self.method == 'get':
            return HttpResponseRedirect(result_data)
        return super()._create_response(result_data)
