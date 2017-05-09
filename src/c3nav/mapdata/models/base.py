from collections import OrderedDict

from django.db import models
from django.utils.translation import get_language

EDITOR_FORM_MODELS = OrderedDict()


class EditorFormMixin(models.Model):
    EditorForm = None

    class Meta:
        abstract = True

    @property
    def title(self):
        if not hasattr(self, 'titles'):
            return self.name
        lang = get_language()
        if lang in self.titles:
            return self.titles[lang]
        return next(iter(self.titles.values())) if self.titles else self.name
