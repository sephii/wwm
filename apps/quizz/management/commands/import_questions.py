import codecs
from itertools import cycle
from django.core.management.base import BaseCommand

from apps.quizz.models import Question, Category


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.category = None

    def handle(self, addrport="", *args, **options):
        syntax = [
            'difficulty',
            'question',
            'answer_1',
            'answer_2',
            'answer_3',
            'answer_4',
        ]

        syntax_cycle = cycle(syntax)
        question = None

        with codecs.open('apps/quizz/fixtures/game_of_thrones.txt', 'r', 'utf-8') as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                print(line)

                if not line or line.startswith('#'):
                    continue

                if lineno == 1:
                    self.category = Category.objects.get_or_create(
                        name=line
                    )[0]
                    continue

                method_name = 'import_{0}'.format(syntax_cycle.next())
                print(method_name)
                syntax_method = getattr(self, method_name)

                question = syntax_method(line, question)

    def import_difficulty(self, line, question):
        question = Question(category=self.category, active=True)
        question.difficulty = int(line)
        return question

    def import_question(self, line, question):
        question.question = line
        return question

    def import_answer_1(self, line, question):
        question.answer_1 = line
        return question

    def import_answer_2(self, line, question):
        question.answer_2 = line
        return question

    def import_answer_3(self, line, question):
        question.answer_3 = line
        return question

    def import_answer_4(self, line, question):
        question.answer_4 = line
        question.save()
        return None
