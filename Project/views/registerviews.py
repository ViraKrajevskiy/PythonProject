from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from Project.Forms.register import RegisterForm


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Сохраняем пользователя
            user = form.save()
            # АВТОМАТИЧЕСКИЙ ЛОГИН: чтобы юзеру не пришлось вводить пароль снова
            login(request, user)
            # ПЕРЕАДРЕСАЦИЯ: отправляем на страницу с досками
            return redirect('index')
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # форма сама проверила пароль и нашла юзера
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')