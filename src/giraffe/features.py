from Bio.Alphabet import IUPAC
from Bio.Seq import Seq
import re
import os


##################################
# Sequence cleaning
#

def clean_sequence(sequence):
  sequence = sequence.strip()
  sequence = re.sub(r'\s+', '', sequence)
  # this throws exception if DNA is not valid
  sequence = str(Seq(sequence, IUPAC.unambiguous_dna))
  return sequence



##################################
# Feature types
#

class Constant_Choices:

  @classmethod
  def choices(cls):
    choices = []
    for attr in dir(cls):
      v = getattr(cls, attr)
      if type(v) == type((1,2)):
        choices.append(v)
    return choices

  @classmethod
  def by_value(cls, value):
    for v in cls.choices():
      if v[0] == value:
        return v
    return (None, None)

  @classmethod
  def by_label(cls, label):
    for v in cls.choices():
      if v[1] == label:
        return v
    return (None, None)

  @classmethod
  def str(cls, value_or_tuple):
    if type(value_or_tuple) == type((1,2)):
      return value_or_tuple[1]
    else:
      return cls.by_value(value_or_tuple)[1]

  @classmethod
  def value(cls, str_or_tuple):
    if type(str_or_tuple) == type((1,2)):
      return str_or_tuple[0]
    else:
      return cls.by_label(str_or_tuple)[0]


class Feature_Type_Choices(Constant_Choices):
  # these have to match with Giraffe value IDs
  #
  FEATURE       = (1,  'Feature')
  PROMOTER      = (2,  'Promoter')
  PRIMER        = (3,  'Primer')
  ENZYME        = (4,  'Enzyme')
  GENE          = (5,  'Gene')
  ORIGIN        = (6,  'Origin')
  REGULATORY    = (7,  'Regulatory')
  TERMINATOR    = (8,  'Terminator')
  EXACT_FEATURE = (9,  'ExactFeature')
  ORF           = (10, 'Orf')
  PROTEIN       = (11, 'Protein')

  @staticmethod
  def labels():
    return [t[1] for t in Feature_Type_Choices.choices()]



##################################
# Detected features
#

class Detected_Feature_Base(object):

  def __init__(self, name, label, start, end, clockwise, type):
    self.name = name
    self.label = label
    self.start = start
    self.end = end
    self.clockwise = clockwise
    self.type = type
    if type not in Feature_Type_Choices.labels():
      raise Exception("Invalid type: %s" % (type,))

  def to_dict(self):
    t = Feature_Type_Choices.by_label(self.type)
    return dict(start=self.start,
                end=self.end,
                clockwise=self.clockwise,
                label=self.label,
                name=self.name,
                type_id=t[0],
                show_feature=1)


class Aligned_Feature(Detected_Feature_Base):

  def __init__(self, name, label, start, end, clockwise, type, query, match, subject):
    super(Aligned_Feature, self).__init__(name, label, start, end, clockwise, type)
    self.query = query
    self.match = match
    self.subject = subject

  def to_dict(self):
    r = super(Aligned_Feature, self).to_dict()
    r['alignment'] = { 'query': self.query, 'match': self.match, 'subject': self.subject }
    return r



##################################
# BLAST
#

from django.conf import settings

class Blast_Accession(object):

  @staticmethod
  def make(type, feature_id, feature_length):
    return '%s-%s-%s' % (type, feature_id, feature_length)

  def __init__(self, accession):
    a = accession.split('-')
    self.type = a[0]
    self.feature_id = int(a[1])
    self.feature_length = int(a[2])


from Bio.Blast.Applications import NcbiblastnCommandline
from Bio.Blast import NCBIXML
import tempfile
import subprocess

def blast(sequence, db):
  infile = None
  feature_list = []
  input = clean_sequence(sequence)

  with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    infile = f.name 
    f.write(">Query\n%s\n" % (input,))

  outfile = "%s.out.xml" % (infile,)
  blast_cl = NcbiblastnCommandline(query=infile, db="%s/%s" % (settings.NCBI_DATA_DIR, db),
                                   evalue=0.001, word_size=6, outfmt=5, out=outfile)
  cl = str(blast_cl)
  cl = "%s/%s" % (settings.NCBI_BIN_DIR, cl)
  r = subprocess.call(cl.split(" "))
  if r != 0:
    raise Exception("Blast failed: %s" % (cl,))
  
  with open(outfile, "r") as f:
    blast_record = NCBIXML.read(f)
    for alignment in blast_record.alignments:
      accession = Blast_Accession(alignment.accession)
      for hsp in alignment.hsps:
        #print "seq %s %s %s" % (accession.type, accession.feature_length, alignment.hit_def,)
        #print 'identities %s/%s' % (hsp.identities, len(hsp.query))
        #print 'qs %s-%s, ms %s-%s' % (hsp.query_start, hsp.query_end, hsp.sbjct_start, hsp.sbjct_end)
        #print '    '+hsp.query[0:75] + '...'
        #print '    '+hsp.match[0:75] + '...'
        #print '    '+hsp.sbjct[0:75] + '...'

        start = hsp.query_start
        end = hsp.query_end
        if hsp.sbjct_end > hsp.sbjct_start:
          clockwise = True
          hit_start = hsp.sbjct_start
          hit_end = hsp.sbjct_end
        else:
          clockwise = False
          hit_end = hsp.sbjct_start
          hit_start = hsp.sbjct_end

        feature = alignment.hit_def
        if hit_start != 1 or hit_end != accession.feature_length:
          feature = '%s (%s-%s/%s)' % (feature, hit_start, hit_end, accession.feature_length)

        f = Aligned_Feature(feature, alignment.hit_def, start, end, clockwise, accession.type,
                            hsp.query, hsp.match, hsp.sbjct)
        feature_list.append(f)

  os.unlink(outfile)
  os.unlink(infile)
  return feature_list



##################################
# Restriction enzyme analysis
#

from Bio.Restriction import CommOnly, RestrictionBatch
from Bio.Restriction import *


class Restriction_Site(Detected_Feature_Base):

  def __init__(self, enzyme, start, end, clockwise, cut):
    name = str(enzyme)
    super(Restriction_Site, self).__init__(name, name, start, end, clockwise, Feature_Type_Choices.ENZYME[1])
    self.enzyme = enzyme
    self.cut = cut

  def to_dict(self):
    r = super(Restriction_Site, self).to_dict()
    r['elucidate'] = self.enzyme.elucidate()
    r['cut'] = self.cut
    return r


_MyEnzymes = [AatII, AflII, AgeI, ApaI, ApaLI, AscI, AseI,
              BamHI, BclI, BglII, BstBI, ClaI, DraI, EagI, EarI,
              EcoRI, EcoRV, FspI, HindIII, HpaI, KpnI, MscI,
              NarI, NcoI, NdeI, NheI, NotI, NruI, PacI,
              PmlI, PstI, PvuII, SacI, SacII, SalI, SmaI,
              SpeI, StuI, XbaI, XhoI, XmaI]
MyEnzymes = RestrictionBatch([x for x in _MyEnzymes if x.elucidate().find('^') >= 0])


def find_restriction_sites(sequence):
  input = Seq(clean_sequence(sequence))
  rc = input.reverse_complement()
  r = MyEnzymes.search(input)
  cutter_list = []
  for enzyme in r:
    v = r[enzyme]
    for cut in v:
      pattern = enzyme.elucidate()
      pattern = re.sub(r'_', '', pattern)
      cut_after = pattern.find('^')
      if cut_after < 0:
        raise Exception('Cannot find cut site for %s (%s)' % (enzyme, pattern))
      # first try fwd
      start = cut-cut_after-1
      end = start+enzyme.size-1
      # print 'try %s vs %s' % (input[start:end+1].lower(), enzyme.site.lower())
      if str(input[start:end+1]).lower() == enzyme.site.lower():
        f = Restriction_Site(enzyme, start+1, end+1, True, cut)
        cutter_list.append(f)
        # print 'found %s' % (f.to_dict(),)
      else:
        end = cut+cut_after+1
        start = end-enzyme.size+1
        # print 'try rc %s vs %s' % (input[start:end+1].reverse_complement().lower(), enzyme.site.lower())
        if str(input[start:end+1].reverse_complement()).lower() == enzyme.site.lower():
          f = Restriction_Site(enzyme, start+1, end+1, False, cut)
          cutter_list.append(f)
          # print 'found %s' % (f.to_dict(),)
        else:
          raise Exception('Cannot find reported cut site %s %s %s %s' % (enzyme, cut, cut_after, pattern)) 

  return cutter_list

