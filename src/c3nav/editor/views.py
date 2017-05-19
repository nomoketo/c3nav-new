from functools import wraps

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache

from c3nav.mapdata.models import LocationGroup, Section
from c3nav.mapdata.models.base import EDITOR_FORM_MODELS


def sidebar_view(func):
    @wraps(func)
    def with_ajax_check(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if request.is_ajax() or 'ajax' in request.GET:
            if isinstance(response, HttpResponseRedirect):
                return render(request, 'editor/redirect.html', {'target': response['location']})
            return response
        return render(request, 'editor/map.html', {'content': response.content})
    return never_cache(with_ajax_check)


@sidebar_view
def main_index(request):
    return render(request, 'editor/index.html', {
        'sections': Section.objects.all(),
        'child_models': [{
            'title': LocationGroup._meta.verbose_name_plural,
            'url': reverse('editor.locationgroups.list'),
        }],
    })


@sidebar_view
def section_detail(request, pk):
    section = get_object_or_404(Section, pk=pk)

    return render(request, 'editor/section.html', {
        'sections': Section.objects.all(),
        'section': section,
        'section_url': 'editor.section',
        'section_as_pk': True,

        'child_models': [{
            'title': Space._meta.verbose_name_plural,
            'url': reverse('editor.spaces.list', kwargs={'section': pk}),
            'count': section.spaces.count(),
        }, {
            'title': Door._meta.verbose_name_plural,
            'url': reverse('editor.doors.list', kwargs={'section': pk}),
            'count': section.doors.count(),
        }],
    })


@sidebar_view
def space_detail(request, section, pk):
    section = get_object_or_404(Section, pk=pk)

    return render(request, 'editor/section.html', {
        'sections': Section.objects.all(),
        'section': section,
        'section_url': 'editor.section',
        'section_as_pk': True,

        'child_models': [{
            'title': Space._meta.verbose_name_plural,
            'url': reverse('editor.spaces.list', kwargs={'section': pk}),
            'count': section.spaces.count(),
        }, {
            'title': Door._meta.verbose_name_plural,
            'url': reverse('editor.doors.list', kwargs={'section': pk}),
            'count': section.doors.count(),
        }],
    })


@sidebar_view
def edit(request, pk=None, model=None, section=None, space=None, explicit_edit=False):
    model = EDITOR_FORM_MODELS[model]

    obj = None
    if pk is not None:
        # Edit existing map item
        kwargs = {'pk': pk}
        if section is not None:
            kwargs.update({'section__id': section})
        elif space is not None:
            kwargs.update({'space__id': space})
        obj = get_object_or_404(model, **kwargs)
        if False:  # todo can access
            raise PermissionDenied

    new = obj is None
    # noinspection PyProtectedMember
    ctx = {
        'path': request.path,
        'pk': pk,
        'model_title': model._meta.verbose_name,
        'new': new,
        'title': obj.title if obj else None,
    }

    if model == Section:
        ctx.update({
            'section': obj,
            'back_url': reverse('editor.index') if new else reverse('editor.section', kwargs={'pk': pk}),
        })
    elif hasattr(obj, 'section'):
        ctx.update({
            'section': obj.section,
            'back_url': reverse('editor.section', kwargs={'pk': obj.section.pk}),
        })
    elif hasattr(obj, 'space'):
        ctx.update({
            'section': obj.space.section,
            'back_url': reverse('editor.space', kwargs={'pk': obj.space.pk}),
        })
    else:
        if not request.resolver_match.url_name.endswith('.edit'):
            raise ValueError('url_name does not end with .edit')
        ctx.update({
            'back_url': reverse(request.resolver_match.url_name[:-4]+'list'),
        })

    if request.method == 'POST':
        if obj is not None and request.POST.get('delete') == '1':
            # Delete this mapitem!
            if request.POST.get('delete_confirm') == '1':
                if not settings.DIRECT_EDITING:
                    # todo: suggest changes
                    raise NotImplementedError
                obj.delete()
                if model == Section:
                    ctx.update({'target': reverse('editor.index')})
                return redirect(reverse('editor.index') if model == Section else ctx['back_url'])
            return render(request, 'editor/delete.html', ctx)

        form = model.EditorForm(instance=obj, data=request.POST, request=request)
        if form.is_valid():
            # Update/create objects
            obj = form.save(commit=False)

            if form.titles is not None:
                obj.titles = {}
                for language, title in form.titles.items():
                    if title:
                        obj.titles[language] = title

            if not settings.DIRECT_EDITING:
                # todo: suggest changes
                raise NotImplementedError

            obj.save()
            form.save_m2m()

            return redirect(ctx['back_url'])
    else:
        form = model.EditorForm(instance=obj, request=request)

    ctx.update({
        'form': form,
    })

    return render(request, 'editor/edit.html', ctx)


@sidebar_view
def list_objects(request, model=None, section=None, space=None):
    model = EDITOR_FORM_MODELS[model]
    if not request.resolver_match.url_name.endswith('.list'):
        raise ValueError('url_name does not end with .list')

    reverse_kwargs = {}
    if section is not None:
        reverse_kwargs['section'] = section
    if space is not None:
        reverse_kwargs['space'] = space

    # noinspection PyProtectedMember
    ctx = {
        'create_url': reverse(request.resolver_match.url_name[:-4]+'create', kwargs=reverse_kwargs),
        'path': request.path,
        'model_name': model.__name__.lower(),
        'model_title': model._meta.verbose_name,
        'model_title_plural': model._meta.verbose_name_plural,
    }

    queryset = model.objects.all().order_by('id')
    for obj in queryset:
        reverse_kwargs['pk'] = obj.pk
        obj.edit_url = reverse(request.resolver_match.url_name[:-4]+'edit', kwargs=reverse_kwargs)
    reverse_kwargs.pop('pk', None)

    if space is not None:
        space = get_object_or_404(Section, pk=section)
        queryset = queryset.filter(space=space)
        ctx.update({
            'back_url': reverse('editor.space', kwargs={'pk': space.pk}),
            'back_title': _('back to space'),
        })
    elif section is not None:
        section = get_object_or_404(Section, pk=section)
        queryset = queryset.filter(section=section)
        ctx.update({
            'back_url': reverse('editor.section', kwargs={'pk': section.pk}),
            'back_title': _('back to space'),
        })
    else:
        ctx.update({
            'back_url': reverse('editor.index'),
            'back_title': _('back to overview'),
        })

    ctx.update({
        'objects': queryset,
    })

    return render(request, 'editor/list.html', ctx)
