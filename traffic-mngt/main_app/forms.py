from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User
from django import forms
from .models import Accident
from django.forms import TextInput, Textarea, Select


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ("email",)
        

class AccidentForm(forms.ModelForm):
    class Meta:
        model = Accident
        fields = ['camera_serial', 'snapshot']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Giao diện
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (TextInput, Textarea, Select)):
                css_class = widget.attrs.get('class', '')
                widget.attrs['class'] = f'{css_class} form-control'.strip()

        # Cho phép bỏ qua snapshot
        self.fields['snapshot'].required = False