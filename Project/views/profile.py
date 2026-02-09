from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

from Project.Forms.register import UserUpdateForm  # Твоя форма из Forms/register.py


@login_required
def profile_view(request):
    user_form = UserUpdateForm(instance=request.user)
    pass_form = PasswordChangeForm(request.user)  # Стандартная форма Django

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Личные данные обновлены!')
                return redirect('profile')  # РЕЖЕТ ПОВТОРНЫЙ POST

        elif 'change_password' in request.POST:
            pass_form = PasswordChangeForm(request.user, request.POST)
            if pass_form.is_valid():
                user = pass_form.save()
                update_session_auth_hash(request, user)  # Чтобы не выкинуло из системы
                messages.success(request, 'Пароль успешно изменен!')
                return redirect('profile')

    return render(request, 'profile.html', {
        'user_form': user_form,
        'pass_form': pass_form
    })