from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import UniqueConstraint

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Директор'),
        ('investor', 'Инвестор'),
        ('developer', 'Разработчик'),
        ('teacher', 'Учитель'),
        ('other', 'Прочее'),
    ]

    # Делаем имя и фамилию обязательными
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='other')

    class Meta:
        constraints = [
            # Это правило делает комбинацию Имя + Фамилия уникальной
            UniqueConstraint(fields=['first_name', 'last_name'], name='unique_full_name')
        ]

    # Твои настройки для групп и прав (оставляем как было)
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

