from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)


class Question(models.Model):
    question = models.TextField()

    answer_a = models.CharField(max_length=100)
    answer_b = models.CharField(max_length=100)
    answer_c = models.CharField(max_length=100)
    answer_d = models.CharField(max_length=100)

    difficulty = models.PositiveSmallIntegerField()

    correct_answer = models.PositiveSmallIntegerField()
    active = models.BooleanField(default=False)
    category = models.ForeignKey(Category)
