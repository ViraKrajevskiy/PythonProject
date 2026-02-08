from django.db import models

class Board(models.Model):
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Column(models.Model):
    board = models.ForeignKey(Board, related_name='columns', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

class Task(models.Model):
    column = models.ForeignKey(Column, related_name='tasks', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  # Описание
    due_date = models.DateTimeField(blank=True, null=True)  # Дедлайн
    label_color = models.CharField(max_length=20, default="transparent") # Цвет метки (hex или class)
    is_completed = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.text