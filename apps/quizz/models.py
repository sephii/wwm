import itertools
import logging
import random

from django.db import models


logger = logging.getLogger('models')


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

    password = models.CharField(blank=True, max_length=128)
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

    def to_dict(self):
        return {
            'id': self.id,
            'categories': [category.name
                           for category in self.categories.all()],
            'status': self.status,
            'nb_players': self.nb_players,
            'max_players': self.max_players,
            'creator': self.owner.name,
            'money': self.LEVELS_VALUES[self.current_level - 1],
            'has_password': self.password != '',
        }

    def get_question(self):
        question = Question.objects.filter(
            difficulty=self.get_current_difficulty(), active=True,
            category__in=self.categories.all()
        ).order_by('?')[0]

        return question

    def get_next_player_id(self):
        players_list = [player.id for player in self.players.all()]
        random.seed(self.get_rand_seed())
        random.shuffle(players_list)
        logger.info('players list is %s', players_list)

        iterator = itertools.cycle(players_list)

        if self.current_player is not None:
            logger.info('current player is not none, its {0}'.format(
                self.current_player_id)
            )

            first_player = iterator.next()

            iterator = itertools.dropwhile(
                lambda x: x != self.current_player_id, iterator
            )

            # skip the current player
            current_player = iterator.next()
            logger.info('current player iterator is {0}'.format(
                current_player
            ))

            next_player = iterator.next()

            # We cycled through all the players, pass to the next level
            if next_player == first_player:
                self.current_level += 1
                self.save()
        else:
            next_player = iterator.next()

        logger.info('next player is {0}'.format(next_player))

        return next_player

    def get_random_answers(self):
        if self.current_question is None:
            raise IndexError('There\'s no current question on the game')

        question = self.current_question
        answers = [question.answer_1, question.answer_2, question.answer_3,
                   question.answer_4]
        random.seed(self.get_rand_seed())
        random.shuffle(answers)

        return answers

    def get_rand_seed(self):
        return float('0.' + str(self.created_at.microsecond))

    def get_current_difficulty(self):
        return self.current_level / 5 + 1

    def get_waiting_time(self):
        return ((float(self.current_level) / len(self.LEVELS_VALUES))
                * random.randint(3, 6))

    def is_answer_correct(self, answer):
        return self.current_question.answer_1 == answer


class Player(models.Model):
    name = models.CharField(max_length=20)
    game = models.ForeignKey(Game, related_name='players', null=True)

    def __unicode__(self):
        return self.name
