import itertools
import random
import uuid
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Question(models.Model):
    question = models.TextField()

    answer_1 = models.CharField(max_length=100)
    answer_2 = models.CharField(max_length=100)
    answer_3 = models.CharField(max_length=100)
    answer_4 = models.CharField(max_length=100)

    difficulty = models.PositiveSmallIntegerField()

    active = models.BooleanField(default=False)
    category = models.ForeignKey(Category)

    def __unicode__(self):
        return self.question

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
    LEVELS_VALUES = [100, 200, 300, 500, 1000, 2000, 4000, 8000, 16000, 32000,
                     64000, 125000, 250000, 500000, 1000000]

    is_private = models.BooleanField(default=False)
    secret_id = models.CharField(max_length=12, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES,
                                              default=STATUS_WAITING)
    categories = models.ManyToManyField(Category, related_name='games')
    max_players = models.PositiveSmallIntegerField(default=4)
    nb_players = models.PositiveSmallIntegerField(default=0)
    owner = models.ForeignKey('Player', related_name='+')
    current_player = models.ForeignKey('Player', related_name='+', null=True)
    current_question = models.ForeignKey('Question', related_name='+',
                                         null=True)
    current_level = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return str(self.id)

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
            difficulty=self.get_current_difficulty(), active=True,
            category__in=self.categories.all()
        ).order_by('?')[0]

        return question

    def get_next_player_id(self):
        players_list = [player.id for player in self.players.all()]
        random.shuffle(players_list, self.get_rand_seed)

        iterator = itertools.cycle(players_list)
        iterator = itertools.dropwhile(lambda x: x != self.current_player.id,
                                       iterator)
        # skip the current player
        iterator.next()
        next_player = iterator.next()

        if next_player == self.owner_id:
            self.current_level += 1
            self.save()

        return next_player

    def get_rand_seed(self):
        return float('0.' + str(self.created_at.microsecond))

    def get_current_difficulty(self):
        return self.current_level / 5 + 1


class Player(models.Model):
    name = models.CharField(max_length=20)
    game = models.ForeignKey(Game, related_name='players', null=True)
    #is_admin = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name
