from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import UniqueConstraint

class Board(models.Model):
    title = models.CharField(max_length=100)
    # Используем settings.AUTH_USER_MODEL вместо прямой ссылки на User
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_boards')
    is_public = models.BooleanField(default=False)
    enable_comments = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# 3. Участники доски
class BoardMember(models.Model):
    ROLE_CHOICES = [
        ('viewer', 'Просмотр'),
        ('editor', 'Изменение'),
        ('admin', 'Админ'),
    ]
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='board_memberships')  # Добавлено related_name
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')

    class Meta:
        unique_together = ('board', 'user')


# 4. Колонки
class Column(models.Model):
    board = models.ForeignKey(Board, related_name='columns', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)


# 5. Задачи
class Task(models.Model):
    CARD_TYPE_CHOICES = [
        ('task', 'Задача'),
        ('poll', 'Голосование'),
    ]
    column = models.ForeignKey(Column, related_name='tasks', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    label_color = models.CharField(max_length=20, null=True, blank=True, default="#ffffff")
    due_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    task_role = models.CharField(max_length=50, blank=True, null=True)
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES, default='task')

    def __str__(self):
        return self.text


# 5b. Голосование (опрос) — привязан к карточке типа poll
class Poll(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='poll')
    question = models.CharField(max_length=255, blank=True)

    def total_votes(self):
        return sum(opt.votes.count() for opt in self.options.all())


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    votes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='poll_votes', blank=True)

class TaskFile(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='task_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    original_name = models.CharField(max_length=255, blank=True) # Чтобы хранить красивое имя файла

    def __str__(self):
        return f"File for {self.task.text}"

    def is_image(self):
        name = (self.original_name or self.file.name or '').lower()
        return any(name.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp'))

    def save(self, *args, **kwargs):
        if not self.original_name:
            self.original_name = self.file.name
        super().save(*args, **kwargs)

# 6. Комментарии
class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']