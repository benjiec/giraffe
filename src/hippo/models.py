from django.db import models
from django.db import utils
from django.conf import settings
import giraffe.features
import datetime
import re


class Feature_Type(models.Model):
  type = models.CharField(max_length=64)

  def __unicode__(self):
    return self.type

  def save(self, *args, **kwargs):
    if self.type not in giraffe.features.Feature_Type_Choices.labels():
      raise Exception("Invalid type: %s, expecting one of %s" % (
                      self.type,
                      ' '.join(giraffe.features.Feature_Type_Choices.labels())))
    return super(Feature_Type, self).save(*args, **kwargs)

  class Meta:
    verbose_name = "Feature Type"


class Feature(models.Model):
  DNA = 1
  PROTEIN = 2

  type = models.ForeignKey(Feature_Type)
  name = models.CharField(max_length=32,db_index=True)
  sequence = models.TextField()
  dna_or_protein = models.IntegerField('DNA or Protein',
                                       choices=((DNA, 'DNA'), (PROTEIN, 'Protein')), default=DNA)
  last_modified = models.DateTimeField(auto_now=True,db_index=True)

  def save(self, *args, **kwargs):
    from Bio.Alphabet import IUPAC
    if self.is_dna():
      alphabet = IUPAC.unambiguous_dna
    else:
      alphabet = IUPAC.protein
    self.sequence = giraffe.features.clean_sequence(self.sequence, strict=True, alphabet=alphabet)
    return super(Feature,self).save(*args, **kwargs)

  def __unicode__(self):
    return self.name

  class Meta:
    ordering = ('type', 'name')

  def as_dna(self):
    self.dna_or_protein = Feature.DNA

  def as_protein(self):
    self.dna_or_protein = Feature.PROTEIN

  def is_dna(self):
    return self.dna_or_protein == Feature.DNA

  def is_protein(self):
    return self.dna_or_protein == Feature.PROTEIN


class Feature_Database(models.Model):

  name = models.CharField(max_length=64,unique=True)
  features = models.ManyToManyField(Feature, blank=True, null=True)
  last_built = models.DateTimeField(null=True,blank=True)

  def __unicode__(self):
    return self.name

  class Meta:
    verbose_name = "Feature Database"

  def dna_db_type(self):
    return 'nucl'

  def protein_db_type(self):
    return 'prot'

  def dna_db_name(self):
    return "%s/%s-%s" % (settings.NCBI_DATA_DIR, self.name, self.dna_db_type())

  def protein_db_name(self):
    return "%s/%s-%s" % (settings.NCBI_DATA_DIR, self.name, self.protein_db_type())

  def __build_db(self, dna_or_protein):
    import os, tempfile, subprocess
    from Bio.Alphabet import IUPAC
    from giraffe.features import clean_sequence, Blast_Accession

    is_dna = False
    infile = None

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
      infile = f.name
      for feature in self.features.all():
        if feature.dna_or_protein == dna_or_protein:
          if feature.is_dna():
            is_dna = True
            alphabet = IUPAC.unambiguous_dna
          else:
            is_dna = False
            alphabet = IUPAC.protein

          data = clean_sequence(feature.sequence, strict=True, alphabet=alphabet)
          f.write(">gnl|%s|%s %s\n%s\n" % (
                  self.name,
                  Blast_Accession.make(type=feature.type.type, feature_id=feature.id, feature_length=len(data)),
                  feature.name, data))

    outfn = self.dna_db_name() if is_dna else self.protein_db_name()
    dbtype = self.dna_db_type() if is_dna else self.protein_db_type()

    cmd = "%s/makeblastdb -in %s -out %s -title %s -dbtype %s -parse_seqids -input_type fasta" % (
          settings.NCBI_BIN_DIR, infile, outfn, self.name, dbtype)

    r = subprocess.call(cmd.split(' '))
    if r != 0:
      print 'Cannot makeblastdb for %s' % (self.name,)

    os.unlink(infile)

  def build(self):
    self.__build_db(Feature.DNA)
    self.__build_db(Feature.PROTEIN)

