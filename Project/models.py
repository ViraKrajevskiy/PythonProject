from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import UniqueConstraint


# 1. Кастомная модель пользователя
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Директор'),
        ('investor', 'Инвестор'),
        ('developer', 'Разработчик'),
        ('teacher', 'Учитель'),
        ('other', 'Прочее'),
    ]
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='other')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    # Ссылка на фото в Google Drive (если задана — показываем её вместо загрузки)
    avatar_drive_id = models.CharField(max_length=128, blank=True, null=True)

    def get_avatar_url(self):
        """URL аватара: из Google Drive или загруженный файл."""
        if self.avatar_drive_id:
            return f'https://drive.google.com/thumbnail?id={self.avatar_drive_id}&sz=w200'
        if self.avatar:
            return self.avatar.url
        return None

    class Meta:
        constraints = [
            UniqueConstraint(fields=['first_name', 'last_name'], name='unique_full_name')
        ]

    # Решаем конфликты с именами обратных связей
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='project_user_groups',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='project_user_permissions',
        blank=True,
    )
