import random
import uuid
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)


class Question(models.Model):
    question = models.TextField()

    answer_1 = models.CharField(max_length=100)
    answer_2 = models.CharField(max_length=100)
    answer_3 = models.CharField(max_length=100)
    answer_4 = models.CharField(max_length=100)

    difficulty = models.PositiveSmallIntegerField()

    active = models.BooleanField(default=False)
    category = models.ForeignKey(Category)

    def get_random_answers(self):
        answers = getattr(self, '_answers', None)

        if answers is None:
            answers = [self.answer_1, self.answer_2, self.answer_3,
                       self.answer_4]
            random.shuffle(answers)

            setattr(self, '_answers', answers)

        return answers


class Game(models.Model):
    STATUS_WAITING = 1
    STATUS_PLAYING = 2
    STATUS_FINISHED = 3
    STATUS_CHOICES = (
        (STATUS_WAITING, 'Waiting'),
        (STATUS_PLAYING, 'Playing'),
        (STATUS_FINISHED, 'Finished'),
    )

    is_private = models.BooleanField(default=False)
    secret_id = models.CharField(max_length=12, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES,
                                              default=STATUS_WAITING)
    categories = models.ManyToManyField(Category, related_name='games')
    max_players = models.PositiveSmallIntegerField(default=4)
    nb_players = models.PositiveSmallIntegerField(default=0)

    def __init__(self, *args, **kwargs):
        self.current_level = 1

        super(Game, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.secret_id:
            self.secret_id = str(uuid.uuid4())[-12:]

        super(Game, self).save(*args, **kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'categories': [category.name
                           for category in self.categories.all()],
            'status': self.status,
            'nb_players': self.nb_players,
            'max_players': self.max_players,
        }

    def get_question(self):
        question = Question.objects.filter(
            difficulty=self.current_level, active=True
        ).order_by('?')[0]

        return question


class Player(models.Model):
    name = models.CharField(max_length=20)
    game = models.ForeignKey(Game, related_name='players', null=True)
    #is_admin = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name
