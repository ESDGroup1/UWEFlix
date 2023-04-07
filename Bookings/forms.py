from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    ADULT_TICKET_PRICE = 10
    STUDENT_TICKET_PRICE = 8
    CHILD_TICKET_PRICE = 6

    ADULT_TICKET = 'ADULT'
    STUDENT_TICKET = 'STUDENT'
    CHILD_TICKET = 'CHILD'

    TICKET_TYPES = [
        (ADULT_TICKET, 'Adult'),
        (STUDENT_TICKET, 'Student'),
        (CHILD_TICKET, 'Child')
    ]

    ticket_type = forms.ChoiceField(choices=TICKET_TYPES, widget=forms.RadioSelect())
    quantity = forms.IntegerField(min_value=1, max_value=10, initial=1)

    class Meta:
        model = Booking
        fields = ('ticket_type', 'quantity')

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity > 10:
            raise forms.ValidationError("You cannot book more than 10 tickets")
        return quantity

    def get_ticket_price(self):
        ticket_type = self.cleaned_data.get('ticket_type')
        quantity = self.cleaned_data.get('quantity')
        if ticket_type == self.ADULT_TICKET:
            return self.ADULT_TICKET_PRICE * quantity
        elif ticket_type == self.STUDENT_TICKET:
            return self.STUDENT_TICKET_PRICE * quantity
        elif ticket_type == self.CHILD_TICKET:
            return self.CHILD_TICKET_PRICE * quantity
        else:
            return 0

