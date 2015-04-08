from django import forms

class CustomSelectMultipleWidget(forms.Widget):
    """
    A SelectMultiple with a JavaScript filter interface.
    Note that the resulting JavaScript assumes that the jsi18n
    catalog has been loaded in the page. This makes use of select2.js
    """

    def __init__(self, attrs=None, query=None, fields_order=None):
        self.query = query
        self.fields_order = fields_order
        super(CustomSelectMultipleWidget, self).__init__(attrs)

    def _media(self):
        """
            Defining all the media files needed by this widget.
        """
        return forms.Media(js=("/static/js/selectHelper.js", "/static/js/select2.js"),
                           css=("/static/css/select2.min.css", ))

    media = property(_media)

    def render(self, name, value, attrs=None):
        output = list()
        options = list()
        cleaned_data = self.clean_query()

        div_start = "<div>"
        div_selected_start = "<br><div style=''><span>Select %s to assign:</span>" % name
        div_end = "</div>"
        
        select_start_tag = "<select id='%s' name='%s' multiple='multiple' size=20 " \
            "style='width: 25%%; height: 100px; overflow: scroll'>" % (
                attrs['id'], attrs['id'])
        select_end_tag = "</select>"
        option_start_tag = "<option name='%s' value='%s'>"
        option_end_tag = "</option>"
        span_new_obj_tag = "<span style='margin-left: 6%%'>Assigned %s:</span>" % name.title()

        delete_from_existing = "<span id='id_unallocate_%(name)s'><span tooltip='Un-assign %(name)s!' " \
            "style='margin-left: 10%%; cursor: pointer'>&#x25c4;" \
            "&#x25c4;&#x25c4;</span><span style='font-weight: bold; " \
            "cursor: pointer'>&nbsp;&nbsp;Un-assign %(title_name)s</span></span>" % {'name': name, 'title_name': name.title()}

        choose_all_tag = "<span style='margin-left: 15%; cursor: pointer' " \
                         "id='choose_all'>Choose All &#x25ba;&#x25ba;</span>"
        remove_all_tag = "<span style='margin-left: 55%; cursor: pointer' " \
                         "id='remove_all'>&#x25c4;&#x25c4; Remove All</span>"

        message_div = "<br><div style='text-alignment: center; display:none; width: 100%%' id='message_span'><span style='font-weight: bold; " \
                      "text-alignment: center; margin-left: 45%%'>All %s have been selected </span>" \
                      "</div>" % name

        spinner_div = "<div id='spinner' style='margin-left: 50%; display: none" \
                      "'><img src='/static/images/spinner.gif'></div>"
        obj_ids = list()

        for obj_id, list_of_values in cleaned_data.iteritems():
            obj_ids.append(obj_id)
            options.append("%s%s%s" % (option_start_tag % (obj_id, obj_id),
                                       ", ".join(list_of_values), option_end_tag))

        output.append("<br>%s\n%s\n%s\n%s\n%s\n%s" % (
            div_selected_start, select_start_tag, "\n".join(options),
            select_end_tag, delete_from_existing,
            span_new_obj_tag))

        if value:
            field_name = attrs['id'].split('_')[1]
            selected_objects_start_tag = "<span style='margin-left: 1%%;'>" \
                "<select name='selected_%s' id='selected_%s' style='height: 100px; " \
                "overflow: scroll; width: 300px; padding-bottom: 20px;' multiple>" % (
                    field_name, field_name)

            selected_options = list()
            for obj in value:
                option_text = ', '.join([getattr(obj, key) for key in self.fields_order])
                selected_options.append("%s%s%s" % (option_start_tag % (obj.id, obj.id),
                                        option_text, option_end_tag))
            output.append("%s\n%s\n%s\n</span>%s" % (
                selected_objects_start_tag, '\n'.join(selected_options), select_end_tag, div_end))

        select2_javascript = """\n\n<script type='text/javascript'>
                    $(document).ready(function() {
                        $('#%(id)s').select2(
                            {
                                placeholder: 'Select %(title_name)s(s)',
                                allowclear: true,
                                minimumInputLength: 3
                            }
                        );

                        var unique = function(list) {
                          var result = [];
                          $.each(list, function(index, elem) {
                            if ($.inArray(elem, result) == -1) result.push(elem);
                          });
                          return result;
                        };

                        $('#id_unallocate_%(name)s').bind('click', function(){
                            $('#message_span').css('display', 'none');
                            var selectedToBeRemoved = $('#selected_%(name)s').val();
                            if (!selectedToBeRemoved){
                                alert('Please select assigned %(name)ss on the right to be removed');
                            } else {
                                for (index=0; index < selectedToBeRemoved.length; index++) {
                                    $('#selected_%(name)s option[value=' + selectedToBeRemoved[index] + ']').remove();
                                };

                                $('#selected_%(name)s option').each(function(){
                                    var current = $('#id_%(name)s').val() ? $('#id_%(name)s').val() : [];
                                    $('#id_%(name)s').val(unique(current.concat($(this).val())));
                                });
                            }
                        });

                        $('#id_%(name)s').bind('change', function(){
                            $('#selected_%(name)s option').each(function(){
                                $('#id_%(name)s').val(unique($('#id_%(name)s').val().concat($(this).val())));
                            });

                            console.log('after: ', $('#id_%(name)s').val());
                        });

                        $('#choose_all').bind('click', function(){
                            $('#spinner').css('display', 'block');
                            $('#selected_%(name)s').find('option').remove();
                            $('#%(id)s').select2('val', [%(obj_ids)s]);
                            $('#message_span').css('display', 'block');
                            $('#spinner').css('display', 'none');
                        });

                        $('#remove_all').bind('click', function(){
                            $('#spinner').css('display', 'block');
                            $('#message_span').css('display', 'block')
                            $('#selected_%(name)s').find('option').remove();
                            $('#message_span span').html('Unallocated all the %(name)s');
                            setTimeout(function(){$('#message_span').css('display', 'none')}, 2000);
                            $('#spinner').css('display', 'none');
                        });

                        $('form').submit(function(event){
                            if (!$('#id_%(name)s').val()) {
                                $('#id_%(name)s').select2('val', [%(existing_assigned_objects)s])
                            }
                        })
                    });
                    </script>
                    """

        output.extend([div_start, choose_all_tag, remove_all_tag, div_end])
        output.extend([message_div, spinner_div])
        output.append(select2_javascript % {'id': attrs['id'], 'name': name,
                                            'obj_ids': ', '.join([str(id) for id in obj_ids]),
                                            'title_name': name.title(),
                                            'existing_assigned_objects': ', '.join([str(obj.id) for obj in value])})
        return mark_safe(''.join(output))

    def clean_query(self):
        """
        A method to take care of the formatting in which the data is desired
        :return: dict

        It returns a dict with key as 'id' of the object and value as list of all the 
        other column values passed as query object.

        Example: Schools
        School id: [SchoolName, SchoolCity, ...]
        {id: [SchoolName, SchoolCity, ...]}

        User can decide how do these extra values(SchoolCity, SchoolState) appear and in
        what order. If some value has null stored in the database then replacing them with
        'N/A'
        """
        if self.fields_order:
            keys = self.fields_order
        else:
            keys = self.query[0].keys()

        try:
            keys.remove('id')
        except ValueError:
            # This exception would mean 'id' was not passed. Thats a good thing.
            pass
        return {obj['id']: [obj[key] if obj[key] else 'N/A' for key in keys] for obj in self.query}

    def value_from_datadict(self, data, files, name):
        """
        Overriding this method to do custom operation

        :param data: gives you a django query dict which needs to be converted to a python dict
        :param files: if any file uploaded
        :param name: name of the field
        :return: python dict or blank list if key not found - can happen as the field is not mandatory
        """
        try:
            return dict(data.iterlists())['id_%s' % name]
        except KeyError:
            logger.info("Input with id - 'id_%(name)ss' was not found in the submitted form. "
                        "Please check if this was intentional. "
                        "This just means that no %(name)s was assigned to the user" % {})
            return []

