from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django.forms import ModelForm, DateTimeInput, DateTimeField, forms
from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker

from notification.models import Mailing


class MailingForm(ModelForm):
    class Meta:
        model = Mailing
        fields = ['date_dispatch', 'date_stop', 'description', 'text', 'tags', 'mobile_operator']
        widgets = {
            'date_dispatch': DateTimePicker(
                options={
                    'useCurrent': True,
                    'collapse': False,
                },
                attrs={
                    'append': 'fa fa-calendar',
                    'icon_toggle': True,
                }
            ),
            'date_stop': DateTimePicker(
                options={
                    'useCurrent': True,
                    'collapse': False,
                },
                attrs={
                    'append': 'fa fa-calendar',
                    'icon_toggle': True,
                }
            ),
        }
