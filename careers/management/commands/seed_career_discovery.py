import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from careers.models import (
    Career,
    CareerCategory,
    CareerProgram,
    CareerQuestion,
    CareerOption,
    CareerOptionWeight,
)


class Command(BaseCommand):
    help = "Seed career discovery questions, options, and weights from JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default="data/seed/career_discovery.json",
            help="Path to the career discovery JSON file.",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file"])
        if not file_path.exists():
            self.stderr.write(f"File not found: {file_path}")
            return

        payload = json.loads(file_path.read_text(encoding="utf-8"))
        categories = payload.get("categories", [])

        self.stdout.write("Seeding career discovery data...")

        for category in categories:
            for question_index, question in enumerate(category.get("questions", []), start=1):
                question_obj, _ = CareerQuestion.objects.get_or_create(
                    prompt=question["prompt"],
                    defaults={
                        "category": category["id"],
                        "order": question_index,
                        "is_active": True,
                    },
                )
                if question_obj.category != category["id"]:
                    question_obj.category = category["id"]
                    question_obj.save(update_fields=["category"])

                for option_data in question.get("options", []):
                    option_obj, _ = CareerOption.objects.get_or_create(
                        question=question_obj,
                        text=option_data["label"],
                        defaults={"explanation": option_data.get("explanation", "")},
                    )

                    weight_value = int(option_data.get("weight", 0))
                    if weight_value <= 0:
                        continue

                    career_tags = []
                    scoring_hints = question.get("scoring_hints", {})
                    if "career_tags" in scoring_hints:
                        career_tags = scoring_hints["career_tags"]
                    elif "career_tags_map" in scoring_hints:
                        for tag in option_data.get("tags", []):
                            career_tags += scoring_hints["career_tags_map"].get(tag, [])

                    for career_tag in set(career_tags):
                        career_title = career_tag.replace("_", " ").title()
                        career_slug = slugify(career_title)
                        career_obj, _ = Career.objects.get_or_create(
                            slug=career_slug,
                            defaults={
                                "title": career_title,
                                "overview": f"{career_title} career path and overview.",
                                "skills": "Core skills will be defined by the school.",
                                "education_path": "Typical education pathway will be defined.",
                                "institutions": "Suggested institutions will be listed.",
                                "future_prospects": "Career prospects and growth details.",
                            },
                        )

                        CareerOptionWeight.objects.get_or_create(
                            option=option_obj,
                            career=career_obj,
                            defaults={"weight": weight_value},
                        )

        self.stdout.write(self.style.SUCCESS("Career discovery data seeded."))
