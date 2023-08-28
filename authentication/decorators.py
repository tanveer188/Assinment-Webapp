from django.shortcuts import redirect
from django.http import Http404
def group_required(*groups, redirect_url=None):

    def decorator(function):
        def wrapper(request, *args, **kwargs):
            if request.user.groups.filter(name__in=groups).exists():
                return function(request, *args, **kwargs)
            elif redirect_url:
                return redirect(redirect_url)
            else:
                raise Http404

        return wrapper

    return decorator
