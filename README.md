
A custom Widget and Field for MultipleChoiceAdmin field.

The default ModelMultipleChoiceField accepts a queryset but that causes an issue the moment your queryset goes big. If suppose you are using this field in Admin view for some model then this particular field will cause the whole page to lag and increase the loading time for the page.

This field instead of passing ".objects.all()" or ".objects.filter([some filter args])" we pass *.values* which is lighter on widget. This gives an option to pass a Model Object which will be used to handle the passed *values*

Recently I faced the same issue so I wrote the following widget and field for it.


##### How to use?

```python

    from libs.fields import CustomModelMultipleChoiceField
    ...
    ...
    ...

    class SomeModelAdminForm(forms.ModelForm):
        ...
        schools = CustomModelMultipleChoiceField(label="schools", query=Schools.objects.all().values('id', 'school_name', 'city', 'state'), query_object=Schools, fields_order=['school_name', 'city', 'state'])
        ...
```

##### Dependency:
1. Select2.js

I use select2.js to allow user to filter passed objects similar to django's internal SelectFilter.js


Its a very basic implementation and I tried to make it as generic as possible but would love to know the feedback and issues and pull requests to make it better.

Also currently the render file holds everything for HTML and JS code. Need to be moved in to selecthelper.js and some template

Thanks

