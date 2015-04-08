from django import forms


class CustomModelMultipleChoiceField(forms.Field):
    """A MultipleChoiceField whose choices are a model QuerySet."""

    def __init__(self, query, query_object, fields_order, *args, **kwargs):
        self.widget = CustomSelectMultipleWidget(query=query, fields_order=fields_order)
        self.query_object = query_object
        super(CustomModelMultipleChoiceField, self).__init__(*args, **kwargs)

    def clean(self, value):
        objects = self.query_object.objects.filter(id__in=value)
        return objects
