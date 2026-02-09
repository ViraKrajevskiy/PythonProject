from django import forms
from django.contrib.auth.forms import UserCreationForm
from Project.models import User

# Форма регистрации
class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name")

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")

        # Проверка уникальности связки Имя + Фамилия
        if User.objects.filter(first_name=first_name, last_name=last_name).exists():
            raise forms.ValidationError("Пользователь с таким именем и фамилией уже зарегистрирован!")

        return cleaned_data

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        # Только те поля, которые пользователю разрешено менять самому
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем Bootstrap классы для красоты
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Проверяем уникальность логина, исключая текущего пользователя
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Этот логин уже занят другим пользователем!")
        return username