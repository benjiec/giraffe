from django.core.management.base import BaseCommand, CommandError
from hippo.models import Feature_Database
import os
import tempfile
import subprocess
from giraffe.features import clean_sequence, NCBI_BIN_DIR, NCBI_DAT_DIR


class Command(BaseCommand):
  def handle(self, *args, **options):
    for feature_db in Feature_Database.objects.all():
      print 'building %s using %s' % (feature_db.name, NCBI_BIN_DIR)

      infile = None
      with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        infile = f.name
        for feature in feature_db.features.all():
          #print feature.name
          f.write(">gnl|hippo-%s|%s-%s %s\n%s\n" % (
                   feature_db.name,
                   feature.type.type,
                   feature.id,
                   feature.name, clean_sequence(feature.sequence)))

      cmd = "%s/makeblastdb -in %s -out %s/%s -title %s -dbtype nucl -parse_seqids -input_type fasta" % (
              NCBI_BIN_DIR, infile, NCBI_DAT_DIR, feature_db.name, feature_db.name)

      r = subprocess.call(cmd.split(' '))
      if r != 0:
        print 'Cannot makeblastdb for %s' % (feature_db.name,)

      os.unlink(infile)

