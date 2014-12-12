import re
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC, _verify_alphabet

def clean_sequence(sequence, strict=False, alphabet=None, exception=True):
  sequence = sequence.strip()
  sequence = re.sub(r'\s+', '', sequence)
  if strict: # throws exception if DNA is not valid
    if alphabet is None:
      alphabet = IUPAC.unambiguous_dna
    if not _verify_alphabet(Seq(sequence.upper(), alphabet)):
      if exception is True:
        raise Exception("Sequence %s contains illegal character. Expecting %s only." %\
                        (sequence, alphabet.letters))
      else:
        return None
  return sequence


class Blast_Accession(object):

  @staticmethod
  def make(type, feature_id, feature_length):
    return '%s-%s-%s' % (type, feature_id, feature_length)

  def __init__(self, accession):
    a = accession.split('-')
    self.type = a[0]
    self.feature_id = int(a[1])
    self.feature_length = int(a[2])
