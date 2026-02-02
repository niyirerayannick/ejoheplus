import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from careers.models import CareerQuestion, CareerOption


class Command(BaseCommand):
    help = "Seed RIASEC career discovery questions from JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing questions and options before seeding.',
        )

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'seed', 'riasec_questions.json')
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        with open(file_path, 'r', encoding='utf-8') as handle:
            data = json.load(handle)

        if options['reset']:
            CareerOption.objects.all().delete()
            CareerQuestion.objects.all().delete()

        created_questions = 0
        updated_questions = 0
        for index, item in enumerate(data, start=1):
            prompt = item.get('question_text', '').strip()
            riasec = item.get('riasec', '').strip()
            if not prompt or not riasec:
                continue

            question, created = CareerQuestion.objects.get_or_create(
                prompt=prompt,
                defaults={
                    'category': riasec,
                    'order': index,
                    'is_active': True,
                },
            )
            if not created:
                question.category = riasec
                question.order = index
                question.is_active = True
                question.save(update_fields=['category', 'order', 'is_active'])
                CareerOption.objects.filter(question=question).delete()
                updated_questions += 1
            else:
                created_questions += 1

            for option in item.get('options', []):
                CareerOption.objects.create(
                    question=question,
                    text=option.get('label', '').strip(),
                    value=int(option.get('value', 3)),
                )

        self.stdout.write(self.style.SUCCESS(
            f"RIASEC questions seeded. Created: {created_questions}, Updated: {updated_questions}"
        ))
