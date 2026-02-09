from django.db import models

from django.conf import settings

from Project.models import User


class Board(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boards')
    is_public = models.BooleanField(default=False) # ВОТ ЭТО ПОЛЕ
    created_at = models.DateTimeField(auto_now_add=True)

class BoardMember(models.Model):
    ROLE_CHOICES = [
        ('viewer', 'Просмотр'),   # Только видит
        ('editor', 'Изменение'), # Может двигать задачи и менять текст
        ('admin', 'Админ'),     # Может приглашать других и удалять
    ]

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')

    class Meta:
        unique_together = ('board', 'user') # Один юзер не может быть добавлен дважды

class Column(models.Model):
    board = models.ForeignKey(Board, related_name='columns', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

class Task(models.Model):
    column = models.ForeignKey(Column, related_name='tasks', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    label_color = models.CharField(max_length=20, null=True, blank=True, default="#ffffff")
    due_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    task_role = models.CharField(max_length=50, blank=True, null=True, help_text="Напр: Разработчик, Аналитик")

    def __str__(self):
        return self.text