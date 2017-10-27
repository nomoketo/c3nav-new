from functools import wraps

from django.http import HttpResponseNotModified, HttpResponseRedirect
from django.shortcuts import render

from c3nav.editor.models import ChangeSet
from c3nav.mapdata.models.access import AccessPermission


def sidebar_view(func=None, select_related=None):
    if func is None:
        def wrapped(inner_func):
            return sidebar_view(inner_func, select_related)
        return wrapped

    @wraps(func)
    def with_ajax_check(request, *args, **kwargs):
        request.changeset = ChangeSet.get_for_request(request, select_related)

        if request.is_ajax() or 'ajax' in request.GET:
            request.META.pop('HTTP_IF_NONE_MATCH', None)

        response = func(request, *args, **kwargs)
        if request.is_ajax() or 'ajax' in request.GET:
            if isinstance(response, HttpResponseRedirect):
                return render(request, 'editor/redirect.html', {'target': response['location']})
            if not isinstance(response, HttpResponseNotModified):
                response.write(render(request, 'editor/fragment_nav.html', {}).content)
            response['Cache-Control'] = 'no-cache'
            return response
        if isinstance(response, HttpResponseRedirect):
            return response
        response = render(request, 'editor/map.html', {'content': response.content})
        response['Cache-Control'] = 'no-cache'
        return response

    return with_ajax_check


def etag_func(request, *args, **kwargs):
    return (request.changeset.raw_cache_key_by_changes + ':' +
            AccessPermission.cache_key_for_request(request, with_update=False))
