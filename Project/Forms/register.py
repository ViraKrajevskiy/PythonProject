from django import forms
from django.contrib.auth.forms import UserCreationForm
from Project.models import User


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name")

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")

        # Оптимизация: проверяем только если оба поля заполнены
        if first_name and last_name:
            if User.objects.filter(first_name=first_name, last_name=last_name).exists():
                raise forms.ValidationError("Пользователь с таким именем и фамилией уже зарегистрирован!")
        return cleaned_data


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "avatar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Массовое обновление атрибутов виджетов (оптимизировано)
        for field_name, field in self.fields.items():
            css_class = 'form-control-file' if field_name == 'avatar' else 'form-control'
            field.widget.attrs.update({'class': css_class})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Исключаем текущего пользователя из поиска по БД
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Этот логин уже занят другим пользователем!")
        return username