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
        if User.objects.filter(first_name=first_name, last_name=last_name).exists():
            raise forms.ValidationError("Пользователь с таким именем и фамилией уже зарегистрирован!")
        return cleaned_data

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        # ВАЖНО: Добавил "avatar" в список полей
        fields = ("username", "first_name", "last_name", "email", "avatar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            # Для всех полей, кроме аватара, оставляем обычный класс
            # Полю файла лучше не форсировать form-control, если мы стилизовали его отдельно
            if field != 'avatar':
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-control-file'})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Этот логин уже занят другим пользователем!")
        return username