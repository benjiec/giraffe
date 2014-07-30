from django.core.management.base import BaseCommand, CommandError
from hippo.models import Feature_Database
from django.conf import settings


class Command(BaseCommand):
  def handle(self, *args, **options):

    for feature_db in Feature_Database.objects.all():
      #print 'building %s using %s' % (feature_db.name, settings.NCBI_BIN_DIR)
      feature_db.build()

