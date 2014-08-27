from Bio import SeqIO
from giraffe_features import Giraffe_Feature_Base, Feature_Type_Choices
import tempfile
import os


class GenbankFeature(Giraffe_Feature_Base):
  def __init__(self, name, start, end, strand, type):
    sbj_start = 1
    sbj_end = end-start+1
    if strand != 1:
      sbj_start = sbj_end
      sbj_end = 1
    super(GenbankFeature, self).__init__(name, name, start, end, sbj_start, sbj_end, type, "GenBank")


def parse_genbank(input):

  with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    infile = f.name 
    f.write('%s' % (input,))
    f.close()

  features = []  
  rec = SeqIO.read(infile, 'genbank')

  for f in rec.features:
    if f.type == 'source':
       continue

    q = f.qualifiers
    ft = Feature_Type_Choices.CUSTOM[1]
    fn = None

    if f.type == 'promoter':
      ft = Feature_Type_Choices.PROMOTER[1]

    elif f.type == 'gene': # not the coding region
      ft = Feature_Type_Choices.GENE[1]
      if 'gene' in q:
        fn = ' '.join(q['gene'])

    elif f.type == 'CDS':
      ft = Feature_Type_Choices.ORF[1]
      if 'product' in q:
        fn = ' '.join(q['product'])
      elif 'gene' in q:
        fn = ' '.join(q['gene'])

    elif f.type in ['rep_origin', 'origin']:
      ft = Feature_Type_Choices.ORIGIN[1]

    elif f.type in ['terminator',]:
      ft = Feature_Type_Choices.TERMINATOR[1]

    elif f.type in ['RBS', '-35_signal', '-10_signal', 'enhancer']:
      ft = Feature_Type_Choices.REGULATORY[1]

    if fn: # already gotten a name from above
      pass
    elif 'name' in q:
      fn = ' '.join(q['name'])
    elif 'label' in q:
      fn = ' '.join(q['label'])
    elif 'note' in q:
      fn = ' '.join(q['note'])
    elif 'standard_name' in q:
      fn = ' '.join(q['standard_name'])
    elif 'product' in q:
      fn = ' '.join(q['product'])
    elif 'locus_tag' in q:
      fn = ' '.join(q['locus_tag'])
    elif 'function' in q:
      fn = ' '.join(q['function'])
    else:
      fn = f.type
    
    #print '%s (%s): %s %s %s: %s' % (f.type, ft, f.location.start, f.location.end, f.location.strand, fn)
    ff = GenbankFeature(fn, int(f.location.start), int(f.location.end), f.location.strand, ft)
    features.append(ff)

  os.unlink(infile)

  return str(rec.seq), features
