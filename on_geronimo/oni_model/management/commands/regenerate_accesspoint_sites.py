from django.core.management.base import BaseCommand
from django.db.models import Count

from on_geronimo.oni_model.models import AccessPoint, AccessPointSite
from on_geronimo.oni_model.utils import (
    get_center_of_points, get_dynamic_site_radius, MINIMUM_SITE_POPULATION)


class Command(BaseCommand):

    help = "Generate Accesspoint Sites based on locations"

    def _remove_dislocated_accesspoints_from_sites(self):
        """ Remove all AccessPoints from each Site that are outside of the maximum site radius """
        # remove accesspoints without position
        for site in AccessPointSite.objects.all():
            for ap in site.accesspoints.filter(position__isnull=True):
                self.stdout.write(self.style.NOTICE(
                    "Removing {} from {} due to its missing position".format(ap, site)))
                ap.site = None
                ap.save()
        # remove accesspoints outside of the range of the site
        for site in AccessPointSite.objects.all():
            site_position = site.position
            site_population = site.accesspoints.count()
            if site_position:
                for ap in site.accesspoints.filter(
                        position__distance_gt=(
                            site_position, 1.25 * get_dynamic_site_radius(site_population))):
                    self.stdout.write(self.style.NOTICE(
                        "Removing {} from {} due to its distance: {}"
                        .format(ap, site, site_position.distance(ap.position))))
                    ap.site = None
                    ap.save()

    def _remove_underpopulated_sites(self):
        """ Remove sites with a too small number of associated Accesspoints """
        for site in (AccessPointSite.objects
                     .annotate(ap_count=Count("accesspoints"))
                     .filter(ap_count__lt=MINIMUM_SITE_POPULATION)):
            self.stdout.write(self.style.NOTICE("Removing underpopulated {}".format(site)))
            site.delete()

    def _remove_overlapping_sites(self):
        """ Remove sites that overlap another site """
        unprocessed_sites = set(AccessPointSite.objects.all())
        while unprocessed_sites:
            site = unprocessed_sites.pop()
            overlapping_sites = set(
                ap.site for ap in (AccessPoint.objects
                                   .filter(site__isnull=False)
                                   .exclude(site__id=site.id)
                                   .filter(position__distance_lt=(
                                       site.position,
                                       get_dynamic_site_radius(MINIMUM_SITE_POPULATION)))))
            for other_site in overlapping_sites:
                if site.accesspoints.count() > other_site.accesspoints.count():
                    removal_site = other_site
                    remaining_site = site
                    if other_site in unprocessed_sites:
                        unprocessed_sites.remove(other_site)
                    break_loop_now = False
                else:
                    removal_site = site
                    remaining_site = other_site
                    break_loop_now = True
                self.stdout.write(self.style.NOTICE(
                    "Removing {} due to spatial conflict with {}"
                    .format(removal_site, remaining_site)))
                removal_site.delete()
                if break_loop_now:
                    # the "site" is removed - we may not run the inner loop again
                    break

    def _add_new_accesspoints_to_sites(self):
        """ Add Accesspoints to existing sites if they are in range """
        for site in AccessPointSite.objects.all():
            site_position = site.position
            if site_position:
                site_population = site.accesspoints.count()
                for new_ap in (
                        AccessPoint.objects
                        .filter(site__isnull=True)
                        .filter(position__isnull=False)
                        .exclude(site=site)
                        .filter(position__distance_lt=(
                            site_position, get_dynamic_site_radius(site_population)))):
                    self.stdout.write(self.style.NOTICE("Adding {} to {}".format(new_ap, site)))
                    new_ap.site = site
                    new_ap.save()

    def _get_access_points_for_site(self, start_position):
        current_position = start_position
        candidate_population = MINIMUM_SITE_POPULATION
        # Run multiple rounds to find a suitable collection of APs for the new site.
        # This is necessary due to the feedback loop caused by the shift of the center with every
        # new point.
        for tolerance in (2.5, 2.0, 1.6, 1.3, 1.0):
            candidates = AccessPoint.objects.filter(
                site__isnull=True, position__isnull=False,
                position__distance_lt=(current_position,
                                       tolerance * get_dynamic_site_radius(candidate_population)))
            candidate_population = candidates.count()
            current_position = get_center_of_points(ap.position for ap in candidates)
            if not current_position:
                # the radius decreased until no accesspoints remained
                return []
        return list(candidates)

    def _create_new_sites(self):
        unprocessed_aps = {ap for ap in AccessPoint.objects.filter(site__isnull=True,
                                                                   position__isnull=False)}
        while unprocessed_aps:
            ap = unprocessed_aps.pop()
            neighbour_aps = self._get_access_points_for_site(ap.position)
            if len(neighbour_aps) >= MINIMUM_SITE_POPULATION:
                new_site = AccessPointSite()
                new_site.save()
                for new_ap in neighbour_aps:
                    try:
                        unprocessed_aps.remove(new_ap)
                    except KeyError:
                        # the starting AP as well as previously handled (outlier) APs
                        pass
                    new_ap.site = new_site
                    new_ap.save()
                self.stdout.write(self.style.NOTICE("Created: {}".format(new_site)))

    def handle(self, *args, **options):
        self._remove_dislocated_accesspoints_from_sites()
        self._remove_underpopulated_sites()
        self._remove_overlapping_sites()
        self._add_new_accesspoints_to_sites()
        self._create_new_sites()
