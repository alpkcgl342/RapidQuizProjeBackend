from django.core.management.base import BaseCommand

from apps.quiz.services import abandon_stale_sessions


class Command(BaseCommand):
    help = "Süresi geçmiş (expires_at) devam eden oturumları 'abandoned' olarak işaretler."

    def handle(self, *args, **options):
        count = abandon_stale_sessions()
        self.stdout.write(self.style.SUCCESS(f"{count} oturum abandoned olarak işaretlendi."))
