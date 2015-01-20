import re
import os
from Bio.Seq import Seq
from giraffe_features import Giraffe_Feature_Base, Aligned_Feature, Feature_Type_Choices
from hippo import clean_sequence, Blast_Accession


##################################
# BLAST
#

from django.conf import settings
from Bio.Blast.Applications import NcbiblastnCommandline
from Bio.Blast.Applications import NcbiblastpCommandline
from Bio.Blast.Applications import NcbiblastxCommandline
from Bio.Blast.Applications import NcbitblastnCommandline
from Bio.Blast import NCBIXML
import tempfile
import subprocess

def blast(sequence, dbobj, input_type='dna', protein=False,
          identity_threshold=0.85, evalue_threshold=0.0001, feature_threshold=None, circular=True):
  """
  Blast sequence against specified feature database. If input type is 'dna',
  using blastn if protein=False (default), or blastx if protein=True. If input
  type is 'protein', using tblastn if protein=False, or blastp if protein=True.

  identity_threshold: only return results with identity rate greater than this
  threshold. Can be None. Default is 0.85.

  evalue_threshold: only return results with evalue smaller than this
  threshold. Default is 0.001.

  feature_threshold: only return results that span at least this amount of a
  feature. Can be None (default). E.g. if set to 0.99, only results spanning an
  entire feature are returned.
  """

  infile = None
  feature_list = []
  input = clean_sequence(sequence)
  if circular is True:
    input2 = input+input
  else:
    input2 = input

  with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    infile = f.name 
    f.write(">Query\n%s\n" % (input2,))

  outfile = "%s.out.xml" % (infile,)
  if protein:
    if input_type == 'dna':
      blast_cl = NcbiblastxCommandline(query=infile, db="%s" % (dbobj.protein_db_name(),), soft_masking=True,
                                       evalue=evalue_threshold, word_size=3, outfmt=5, out=outfile,
                                       max_target_seqs=500)
    else:
      blast_cl = NcbiblastpCommandline(query=infile, db="%s" % (dbobj.protein_db_name(),), soft_masking=True,
                                       evalue=evalue_threshold, word_size=3, outfmt=5, out=outfile,
                                       max_target_seqs=500)
  else:
    if input_type == 'dna':
      blast_cl = NcbiblastnCommandline(query=infile, db="%s" % (dbobj.dna_db_name(),), soft_masking=True,
                                       evalue=evalue_threshold, word_size=6, outfmt=5, out=outfile,
                                       max_target_seqs=500)
    else:
      blast_cl = NcbitblastnCommandline(query=infile, db="%s" % (dbobj.dna_db_name(),), soft_masking=True,
                                        evalue=evalue_threshold, word_size=6, outfmt=5, out=outfile,
                                        max_target_seqs=500)

  cl = str(blast_cl)
  cl = "%s/%s" % (settings.NCBI_BIN_DIR, cl)
  r = subprocess.call(cl.split(" "))
  if r != 0:
    # blast can fail if blastdb is not there, which can happen if there were no
    # sequences available to build a db
    print "Blast failed: %s" % (cl,)

    try:
      os.unlink(outfile)
      os.unlink(infile)
    except:
      pass

    return []

  with open(outfile, "r") as f:
    blast_record = NCBIXML.read(f)
    for alignment in blast_record.alignments:
      accession = Blast_Accession(alignment.accession)
      for hsp in alignment.hsps:

        # since we doubled up the input, ignore hits starting after the input
        if hsp.query_start > len(input):
          continue

        # check identity threshold
        if identity_threshold is not None and \
           1.0*hsp.identities/len(hsp.sbjct) < identity_threshold:
          continue

        if hsp.sbjct_end > hsp.sbjct_start:
          clockwise = True
          hit_start = hsp.sbjct_start
          hit_end = hsp.sbjct_end
        else:
          clockwise = False
          hit_end = hsp.sbjct_start
          hit_start = hsp.sbjct_end

        # check feature threshold
        if feature_threshold is not None and \
           1.0*(1+abs(hit_end-hit_start))/accession.feature_length < feature_threshold:
          continue

        # print "hit %s evalue %s" % (alignment.hit_def, hsp.expect)
        # print "  query %s-%s, sbjct %s-%s" % (hsp.query_start, hsp.query_end, hsp.sbjct_start, hsp.sbjct_end)

        start = hsp.query_start
        end = hsp.query_end
        if end > len(input):
          end = end % len(input)

        feature = alignment.hit_def

        if hit_start != 1 or hit_end != accession.feature_length:
          feature = '%s (%s-%s/%s)' % (feature, hit_start, hit_end, accession.feature_length)

        f = Aligned_Feature(alignment.hit_def, feature,
                            start, end, hsp.sbjct_start, hsp.sbjct_end,
                            accession.type,
                            hsp.query, hsp.match, hsp.sbjct,
                            hsp.expect, hsp.identities)
        setattr(f, 'feature_id', accession.feature_id)
        feature_list.append(f)

  os.unlink(outfile)
  os.unlink(infile)

  # remove truncated features across circular boundary
  filtered = []
  for f in feature_list:
    trumped = False
    if f.query_start == 1:
      # see if this feature is trumped by another one
      for other_f in feature_list:
        # same ending, direction, feature, but other_f is across circular
        # boundary (start > end)
        if other_f.query_start != f.query_start and \
           other_f.query_end == f.query_end and \
           other_f.feature_id == f.feature_id and \
           other_f.query_start > other_f.query_end:
          trumped = True
          break
    if not trumped:
      filtered.append(f)

  return filtered



##################################
# Restriction enzyme analysis
#

from Bio.Restriction import CommOnly, RestrictionBatch
from Bio.Restriction import *


class Restriction_Site(Giraffe_Feature_Base):

  def __init__(self, enzyme, start, end, clockwise, cut):
    name = str(enzyme)
    super(Restriction_Site, self).__init__(name, name, start, end,
                                           1, len(enzyme.site),
                                           Feature_Type_Choices.ENZYME[1], 'Restriction Enzyme')
    self.enzyme = enzyme
    self.cut = cut
    self.layer = 'Restriction Enzymes'

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


def find_restriction_sites(sequence, circular=True):
  input_seq = clean_sequence(sequence)
  if circular is True:
    input2 = Seq(input_seq+input_seq)
  else:
    input2 = Seq(input_seq)
  r = MyEnzymes.search(input2)
  cutter_list = []
  for enzyme in r:
    v = r[enzyme]
    for cut in v:
      cut_after = cut-1
      if cut_after <= 0:
        cut_after += len(input2)
      pattern = enzyme.elucidate()
      pattern = re.sub(r'_', '', pattern)
      cut_off = pattern.find('^')
      if cut_off < 0:
        raise Exception('Cannot find cut site for %s (%s)' % (enzyme, pattern))
      # first try fwd
      start = cut-cut_off-1
      end = start+enzyme.size-1
      # print 'try %s vs %s' % (input2[start:end+1].lower(), enzyme.site.lower())
      if str(input2[start:end+1]).lower() == enzyme.site.lower():
        if start < len(input_seq):
          end = end % len(input_seq)
          cut_after = cut_after % len(input_seq)
          f = Restriction_Site(enzyme, start+1, end+1, True, cut_after)
          cutter_list.append(f)
          # print 'found %s' % (f.to_dict(),)
      else:
        end = cut+cut_off+1
        start = end-enzyme.size+1
        # print 'try rc %s vs %s' % (input2[start:end+1].reverse_complement().lower(), enzyme.site.lower())
        if str(input2[start:end+1].reverse_complement()).lower() == enzyme.site.lower():
          if start < len(input_seq):
            end = end % len(input_seq)
            cut_after = cut_after % len(input_seq)
            f = Restriction_Site(enzyme, start+1, end+1, False, cut_after)
            cutter_list.append(f)
            # print 'found %s' % (f.to_dict(),)
        else:
          raise Exception('Cannot find reported cut site %s %s %s %s' % (enzyme, cut, cut_off, pattern)) 

  return cutter_list



##################################
# BLAST2
#

def blast2(subject, query):
  subject = clean_sequence(subject)
  query = clean_sequence(query)

  with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    subject_file = f.name 
    f.write(">Subject\n%s\n" % (subject,))
    #print 'subject=%s' % (subject,)

  with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    query_file = f.name 
    f.write(">Query\n%s\n" % (query,))
    #print 'query=%s' % (query,)

  outfile = "%s.out.xml" % (query_file,)
  blast_cl = NcbiblastnCommandline(query=query_file, subject=subject_file,
                                   evalue=0.001, word_size=6,
                                   # these params were tested to allow gaps in
                                   # alignments. i.e. large number of bps
                                   # misaligned or gapped.
                                   gapextend=4, gapopen=0, reward=2,
                                   outfmt=5, out=outfile)
  cl = str(blast_cl)
  cl = "%s/%s" % (settings.NCBI_BIN_DIR, cl)
  r = subprocess.call(cl.split(" "))

  if r != 0:
    try:
      os.unlink(outfile)
      os.unlink(subject_file)
      os.unlink(query_file)
    except:
      pass

    raise Exception("Blast failed: %s" % (cl,))
 
  res = []
 
  with open(outfile, "r") as f:
    blast_record = NCBIXML.read(f)
    for alignment in blast_record.alignments:
      for hsp in alignment.hsps:
        res.append({ "query_start": hsp.query_start,
                     "query_end": hsp.query_end,
                     "subject_start": hsp.sbjct_start,
                     "subject_end": hsp.sbjct_end,
                     "evalue": hsp.expect,
                     "query": hsp.query,
                     "match": hsp.match,
                     "subject": hsp.sbjct, })

  os.unlink(outfile)
  os.unlink(subject_file)
  os.unlink(query_file)
  return res
