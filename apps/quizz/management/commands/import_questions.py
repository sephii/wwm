import codecs
from django.core.management.base import BaseCommand

from apps.quizz.models import Question, Category


class Command(BaseCommand):
    def handle(self, addrport="", *args, **options):
        with codecs.open('apps/quizz/fixtures/game_of_thrones.txt', 'r', 'utf-8') as f:
            lines = f.readlines()

        category = Category.objects.get_or_create(name=lines[0])[0]

        for lineno in range(2, len(lines), 7):
            Question.objects.create(
                category=category,
                difficulty=int(lines[lineno]),
                question=lines[lineno + 1],
                answer_1=lines[lineno + 2],
                answer_2=lines[lineno + 3],
                answer_3=lines[lineno + 4],
                answer_4=lines[lineno + 5],
                active=True
            )
