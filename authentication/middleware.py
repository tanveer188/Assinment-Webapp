from django.urls import resolve
from teacher.models import WebsiteVisit
from datetime import datetime

class WebsiteVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Capture IP address
        ip_address = request.META.get('REMOTE_ADDR')

        # Capture current date and time
        visit_date = datetime.now().date()
        visit_time = datetime.now().time()

        # Capture visited URL and name
        visited_url = request.build_absolute_uri()
        resolver_match = resolve(request.path_info)
        url_name = resolver_match.url_name if resolver_match.url_name is not None else ''

        # Save the website visit
        WebsiteVisit.objects.create(ip_address=ip_address, visit_date=visit_date, visit_time=visit_time,
                                    url_name=url_name, visited_url=visited_url)

        response = self.get_response(request)

        return response
