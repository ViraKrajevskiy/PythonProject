from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from Project.Models_main.new import Board, Column, Task
from Project.models import User


# Настройка отображения нашего кастомного пользователя
class CustomUserAdmin(UserAdmin):
    # Колонки, которые будут видны в общем списке пользователей
    # Добавили 'first_name', 'last_name' и 'role'
    list_display = ('username', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')

    # По каким полям можно быстро фильтровать список справа
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')

    # Поиск по имени, фамилии и логину
    search_fields = ('username', 'first_name', 'last_name', 'email')

    # Порядок сортировки (сначала последние зарегистрированные)
    ordering = ('-date_joined',)

    # Настройка полей внутри карточки редактирования пользователя
    # Мы берем стандартные наборы полей Django и добавляем к ним нашу роль
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('role',)}),
    )

    # Настройка полей для формы создания нового пользователя через админку
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('role',)}),
    )


# Регистрируем модель User с нашими настройками
admin.site.register(User, CustomUserAdmin)


# Регистрируем остальные модели для управления досками
@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    search_fields = ('title',)


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'board', 'order')
    list_filter = ('board',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'column', 'is_completed', 'is_archived', 'due_date')
    list_filter = ('is_completed', 'is_archived', 'column__board')
    search_fields = ('text', 'description')