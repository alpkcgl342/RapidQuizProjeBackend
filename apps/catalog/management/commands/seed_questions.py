"""Soru havuzunu fixture dosyalarından yükler (§12).

İdempotenttir: kategori `slug` ile, soru `external_ref` ile, şık ise
(soru, display_order) ile eşleştirilip güncellenir veya oluşturulur.
Tüm dosyalar önce doğrulanır; tek bir hata varsa hiçbir şey yazılmaz.
"""

import json
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.catalog.models import AnswerOption, Category, Question, validate_option_set

DEFAULT_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "questions"
CATEGORY_KEYS = {"slug", "name", "color_hex", "icon"}


class Command(BaseCommand):
    help = "Soru havuzunu apps/catalog/fixtures/questions/*.json dosyalarından yükler."

    def add_arguments(self, parser):
        parser.add_argument("--dir", type=Path, default=DEFAULT_DIR, help="Fixture klasörü")

    def handle(self, *args, **options):
        files = sorted(Path(options["dir"]).glob("*.json"))
        if not files:
            raise CommandError(f"Fixture bulunamadı: {options['dir']}")

        payloads = [(f, self._load_and_validate(f)) for f in files]

        stats = {"categories": 0, "created": 0, "updated": 0}
        with transaction.atomic():
            for _, data in payloads:
                self._import(data, stats)

        self.stdout.write(
            self.style.SUCCESS(
                f"{stats['categories']} kategori işlendi; "
                f"{stats['created']} soru oluşturuldu, {stats['updated']} soru güncellendi."
            )
        )

    def _load_and_validate(self, path: Path) -> dict:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"{path.name}: geçersiz JSON ({exc})") from exc

        category = data.get("category") or {}
        missing = CATEGORY_KEYS - category.keys()
        if missing:
            raise CommandError(f"{path.name}: kategori alanları eksik: {sorted(missing)}")

        seen = set()
        for i, q in enumerate(data.get("questions") or []):
            where = f"{path.name} soru #{i + 1} ({q.get('external_ref', '?')})"
            ref = q.get("external_ref")
            if not ref or len(ref) > 40:
                raise CommandError(f"{where}: external_ref zorunlu ve en fazla 40 karakter.")
            if ref in seen:
                raise CommandError(f"{where}: external_ref tekrar ediyor.")
            seen.add(ref)
            if not (q.get("text") or "").strip() or len(q["text"]) > 300:
                raise CommandError(f"{where}: soru metni boş olamaz, en fazla 300 karakter.")
            if q.get("difficulty", 2) not in (1, 2, 3):
                raise CommandError(f"{where}: difficulty 1, 2 veya 3 olmalı.")
            opts = q.get("options") or []
            if any(len(o.get("text", "")) > 200 for o in opts):
                raise CommandError(f"{where}: şık metni en fazla 200 karakter.")
            try:
                validate_option_set((o.get("text", ""), bool(o.get("is_correct"))) for o in opts)
            except ValidationError as exc:
                raise CommandError(f"{where}: {' '.join(exc.messages)}") from exc
        return data

    def _import(self, data: dict, stats: dict) -> None:
        c = data["category"]
        category, _ = Category.objects.update_or_create(
            slug=c["slug"],
            defaults={
                "name": c["name"],
                "description": c.get("description", ""),
                "color_hex": c["color_hex"],
                "icon": c["icon"],
                "display_order": c.get("display_order", 0),
            },
        )
        stats["categories"] += 1

        for q in data.get("questions") or []:
            question, created = Question.objects.update_or_create(
                external_ref=q["external_ref"],
                defaults={
                    "category": category,
                    "text": q["text"].strip(),
                    "explanation": q.get("explanation", ""),
                    "difficulty": q.get("difficulty", 2),
                },
            )
            stats["created" if created else "updated"] += 1
            for order, opt in enumerate(q["options"]):
                AnswerOption.objects.update_or_create(
                    question=question,
                    display_order=order,
                    defaults={"text": opt["text"].strip(), "is_correct": bool(opt["is_correct"])},
                )
