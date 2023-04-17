from django import forms
from .models import PaymentDetails
from datetime import datetime
from django.forms.widgets import SelectDateWidget

class MonthYearWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        months = [(i, datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)]
        years = [(i, i) for i in range(datetime.now().year, datetime.now().year+10)]
        _widgets = (
            forms.Select(choices=months),
            forms.Select(choices=years),
        )
        super().__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.month, value.year]
        return [None, None]

class MonthYearField(forms.MultiValueField):
    widget = MonthYearWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(),
            forms.IntegerField(),
        )
        super().__init__(fields, *args, **kwargs)

    def compress(self, values):
        if all(values):
            return datetime(year=values[1], month=values[0], day=1)
        return None

class PaymentDetailsForm(forms.ModelForm):
    expdate = MonthYearField()

    class Meta:
        model = PaymentDetails
        fields = ['account_number', 'cvv', 'expdate']
