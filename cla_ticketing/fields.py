
from django.forms.widgets import FileInput


class CustomFileInput(FileInput):
    template_name = 'cla_ticketing/forms/widgets/custom_file_input.html'

    def is_initial(self, value):
        """
        Return whether value is considered to be initial value.
        """
        return bool(value and getattr(value, 'url', False))

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update({
            'is_initial': self.is_initial(value)
        })
        return context
