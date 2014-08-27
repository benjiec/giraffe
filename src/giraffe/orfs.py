from Bio.Seq import Seq
from giraffe_features import Giraffe_Feature_Base, Feature_Type_Choices
import math
import tags

trans_table = 1 # standard translation table
min_protein_len = 150


class Orf(Giraffe_Feature_Base):

  def __init__(self, name, start, end, size, strand, orf_frame=None):
    sbj_start = 1
    sbj_end = size
    if strand != 1:
      sbj_start = size
      sbj_end = 1
    super(Orf, self).__init__(name, name, start, end, sbj_start, sbj_end, Feature_Type_Choices.ORF[1], 'ORFs')
    self.orf_frame = orf_frame

  def to_dict(self):
    r = super(Orf, self).to_dict()
    if self.orf_frame is not None:
      r['orf_frame'] = self.orf_frame
    return r 


def detect_orfs_and_tags(dna, circular=True):
    orf_list = []
    tag_list = []

    # double up sequence, so we can detect features across 0 bp boundary
    if circular is True:
      seq = Seq(dna*2)
    else:
      seq = Seq(dna)
    seq_len = len(dna)
    aa_len = int(math.floor(seq_len/3.0))

    for strand,nuc in [(+1,seq), (-1,seq.reverse_complement())]:
        for frame in range(3):
            trans = str(nuc[frame:].translate(trans_table))
            trans_len = len(trans)
            aa_start = 0
            aa_end = 0

            # go through the translation and find end codons that follow a
            # start codon.
            while aa_start < trans_len and aa_start < aa_len:
                aa_end = trans.find("*", aa_start)
                has_stop = 1
                if aa_end == -1:
                    # no more stop codon, just abort...
                    break

                # we start looking for a M at the earliest at aa_end-aa_len+1,
                # since we don't want an ORF that's actually bigger than the
                # original sequence
                if aa_start < aa_end-aa_len+1:
                    aa_start = aa_end-aa_len+1
                start_codon = trans.find('M', aa_start, aa_end)

                # is there a start codon? and is it before end of sequence
                # (remember we doubled up the sequence earlier to detect orfs
                # crossing boundaries)
                if start_codon == -1 or start_codon >= aa_len:
                    assert(aa_end != -1)
                    aa_start = aa_end+1
                    continue

                if aa_end-start_codon >= min_protein_len:
                    # the following start and end need to start with
                    # 1, not 0.
                    if strand == 1:
                        start = frame+start_codon*3+1
                        end = frame+aa_end*3+has_stop*3
                        size = end-start+1
                        if end > seq_len:
                            end = end % seq_len
                    else:
                        start = seq_len-frame-aa_end*3-has_stop*3+1
                        end = seq_len-frame-start_codon*3
                        size = end-start+1
                        if start < 0:
                            start = seq_len+start

                    f = Orf(name='ORF frame '+str(frame+1), start=start, end=end,
                            size=size, strand=strand, orf_frame=frame)
                    orf_list.append(f)

                    orf_annotated = f

                    # also try to see if we can find any protein tags
                    # in this ORF
                    for tag_pair in tags.PROTEIN_TAGS:
                        tag = tag_pair[0]
                        peptide = tag_pair[1]
                        tag_aa_start = trans.find(peptide,start_codon,aa_end)
                        if tag_aa_start >= 0 and tag_aa_start < aa_len:
                            tag_aa_end = tag_aa_start+len(peptide)
                            if strand == 1:
                                tag_start = frame+tag_aa_start*3+1
                                tag_end = frame+tag_aa_end*3
                                if tag_start > seq_len:
                                    tag_start = tag_start % seq_len
                                if tag_end > seq_len:
                                    tag_end = tag_end % seq_len
                            else:
                                tag_start = seq_len-frame-tag_aa_end*3+1
                                tag_end = seq_len-frame-tag_aa_start*3
                                if tag_start < 0:
                                    tag_start = seq_len+tag_start

                            sbj_start = 1
                            sbj_end = tag_end-tag_start+1
                            if strand != 1:
                              sbj_start = tag_end-tag_start+1
                              sbj_end = 1
                            f = Giraffe_Feature_Base(label=tag, name=tag,
                                                     query_start=tag_start, query_end=tag_end,
                                                     subject_start=sbj_start, subject_end=sbj_end,
                                                     type=Feature_Type_Choices.FEATURE[1],
                                                     layer='Detected Features')
                            tag_list.append(f)

                aa_start = aa_end+1

    return (orf_list, tag_list)
