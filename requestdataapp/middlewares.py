from django.http import HttpRequest, HttpResponse


def set_useragent_request_middleware(get_response):

    print("Initial call")

    def middleware(request: HttpRequest) -> HttpResponse:
        print("Before get_response")
        request.user_agent = request.META.get('HTTP_USER_AGENT')
        response = get_response(request)
        print("After get_response")
        return response
    return middleware

class CoontRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest) -> HttpResponse:
        self.requests_count += 1
        print("requests count", self.requests_count)
        response = self.get_response(request)
        self.responses_count += 1
        print("responses count", self.responses_count)
        return response

    def process_exception(self, request: HttpRequest, exception):
        self.exceptions_count += 1
        print("exceptions count:", self.exceptions_count)