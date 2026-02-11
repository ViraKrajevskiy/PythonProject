from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from Project.Models_main.new import Board, Column, Task
from Project.models import User
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('role',)}),
    )
admin.site.register(User, CustomUserAdmin)
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