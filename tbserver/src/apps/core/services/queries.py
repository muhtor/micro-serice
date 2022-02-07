from django.apps import apps


class MainDBQuery:

    def __init__(self, model=None):
        self.Model = model

    def _get_object(self, *args, **kwargs):
        try:
            return self.Model.objects.get(*args, **kwargs)
        except self.Model.DoesNotExist:
            return None

    def _get_queryset(self, *args, **kwargs):
        try:
            return self.Model.objects.filter(*args, **kwargs)
        except self.Model.DoesNotExist:
            return None

    def _set_default_model(self, app, model):
        model = apps.get_model(app_label=app, model_name=model)
        self.Model = model
        return self.Model

    def get_value_by_init_model(self, qs: bool = False, *args, **kwargs):
        if self.Model:
            if qs:
                return self._get_queryset(*args, **kwargs)
            else:
                return self._get_object(*args, **kwargs)
        else:
            return None

    def get_value_by_string_model(self, app_name=None, model_name=None, qs: bool = False, *args, **kwargs):
        if app_name and model_name:
            self._set_default_model(app=app_name, model=model_name)
            if qs:
                return self._get_queryset(*args, **kwargs)
            else:
                return self._get_object(*args, **kwargs)
        else:
            return None
