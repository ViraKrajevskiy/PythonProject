from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from Project.Forms.register import UserUpdateForm


@login_required
def profile_view(request):
    # Если метод POST, обрабатываем одну из двух форм
    if request.method == 'POST':

        # 1. Обработка обновления личных данных и фото
        if 'update_profile' in request.POST:
            # ВАЖНО: передаем request.FILES, иначе фото не сохранится
            user_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Личные данные и аватар успешно обновлены!')
                return redirect('profile')
            else:
                messages.error(request, 'Произошла ошибка при обновлении профиля.')

        # 2. Обработка смены пароля
        elif 'change_password' in request.POST:
            pass_form = PasswordChangeForm(request.user, request.POST)
            if pass_form.is_valid():
                user = pass_form.save()
                # Обновляем сессию, чтобы пользователя не разлогинило после смены пароля
                update_session_auth_hash(request, user)
                messages.success(request, 'Пароль успешно изменен!')
                return redirect('profile')
            else:
                messages.error(request, 'Пожалуйста, исправьте ошибки в форме пароля.')
                # Если форма пароля невалидна, нам нужно прокинуть пустую user_form для рендера
                user_form = UserUpdateForm(instance=request.user)

    else:
        # Если метод GET, просто показываем заполненные формы
        user_form = UserUpdateForm(instance=request.user)
        pass_form = PasswordChangeForm(request.user)

    return render(request, 'profile.html', {
        'user_form': user_form,
        'pass_form': pass_form
    })