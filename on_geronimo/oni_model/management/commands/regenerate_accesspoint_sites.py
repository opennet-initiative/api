"""
Update the dynamically assembled list of sites (with multiple APs being close together).
"""

from django.core.management.base import BaseCommand

from on_geronimo.oni_model.sites import SiteUpdater


class Command(BaseCommand):

    help = "Generate Accesspoint Sites based on locations"

    def handle(self, *args, **options):
        updater = SiteUpdater(
            status_output_func=lambda msg: self.stdout.write(self.style.NOTICE(msg)))
        updater.update_sites()
