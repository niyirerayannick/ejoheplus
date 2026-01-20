import json
from datetime import date, timedelta
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from accounts.models import User
from opportunities.models import Opportunity
from training.models import Course
from mentorship.models import MentorProfile


class Command(BaseCommand):
    help = "Seed jobs, scholarships, mentors, and trainings from JSON files."

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR)
        seed_dir = base_dir / "data" / "seed"

        jobs = self._load(seed_dir / "jobs.json")
        scholarships = self._load(seed_dir / "scholarships.json")
        mentors = self._load(seed_dir / "mentors.json")
        trainings = self._load(seed_dir / "trainings.json")

        partner = self._get_or_create_partner()
        self._seed_mentors(mentors)
        self._seed_opportunities(jobs + scholarships, partner)
        self._seed_trainings(trainings, partner)

        self.stdout.write(self.style.SUCCESS("Seed completed."))

    def _load(self, path):
        if not path.exists():
            self.stdout.write(self.style.WARNING(f"Missing seed file: {path}"))
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def _get_or_create_partner(self):
        user, created = User.objects.get_or_create(
            username="partner_demo",
            defaults={
                "email": "partner@ejoheplus.com",
                "role": "partner",
            },
        )
        if created:
            user.set_password("ChangeMe123!")
            user.save()
        return user

    def _seed_mentors(self, mentors):
        for mentor in mentors:
            email = mentor.get("email", "").lower()
            if not email:
                continue
            full_name = mentor.get("full_name", "").strip()
            username = self._unique_username(email.split("@")[0] or full_name or "mentor")
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": username,
                    "role": "mentor",
                    "first_name": full_name.split(" ")[0] if full_name else "",
                    "last_name": " ".join(full_name.split(" ")[1:]) if full_name else "",
                    "phone": mentor.get("phone", ""),
                    "bio": mentor.get("bio", ""),
                    "is_mentor_approved": mentor.get("status", "").lower() == "approved",
                },
            )
            if created:
                user.set_password("ChangeMe123!")
                user.save()

            MentorProfile.objects.update_or_create(
                mentor=user,
                defaults={
                    "professional_title": mentor.get("professional_title", ""),
                    "company": mentor.get("company", ""),
                    "years_of_experience": mentor.get("years_of_experience", 0) or 0,
                    "expertise_areas": ", ".join(mentor.get("expertise_areas", [])),
                    "availability_hours": mentor.get("availability_hours", ""),
                },
            )

    def _seed_opportunities(self, opportunities, partner):
        for item in opportunities:
            title = item.get("title", "")
            slug = item.get("slug") or slugify(title)
            status = item.get("status", "active").lower()
            deadline = item.get("deadline") or (date.today() + timedelta(days=30)).isoformat()
            Opportunity.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "type": item.get("type", "job"),
                    "category": item.get("category", ""),
                    "description": item.get("description", ""),
                    "requirements": item.get("requirements", ""),
                    "benefits": item.get("benefits", ""),
                    "deadline": date.fromisoformat(deadline),
                    "created_by": partner,
                    "is_active": status == "active",
                },
            )

    def _seed_trainings(self, trainings, partner):
        for item in trainings:
            title = item.get("title", "")
            slug = item.get("slug") or slugify(title)
            instructor_email = item.get("instructor_email", "").lower()
            instructor = None
            if instructor_email:
                instructor = User.objects.filter(email=instructor_email).first()
            if not instructor:
                instructor = User.objects.filter(role="mentor").first()
            created_by = instructor or partner

            status = item.get("status", "active").lower()
            Course.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "category": item.get("category", ""),
                    "description": item.get("description", ""),
                    "overview": item.get("overview", ""),
                    "instructor": instructor,
                    "created_by": created_by,
                    "duration_hours": item.get("duration_hours", 0) or 0,
                    "level": item.get("level", "beginner"),
                    "price": item.get("price", "0.00") or "0.00",
                    "is_free": bool(item.get("is_free", True)),
                    "is_active": status == "active",
                },
            )

    def _unique_username(self, base):
        base_slug = slugify(base) or "mentor"
        username = base_slug
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_slug}{counter}"
            counter += 1
        return username
