from django.utils import translation


class AdminLocaleMiddleware:

    def __init__(self, process_request):
        self.process_request = process_request

    def __call__(self, request):

        if request.path.startswith('/admin'):
            translation.activate("en")
            request.LANGUAGE_CODE = translation.get_language()

        response = self.process_request(request)

        return response
