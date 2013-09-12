from django.test import TestCase
from django.core.urlresolvers import reverse
from hippo.models import Feature, Feature_Type, Feature_Database
import json, random


from giraffe.features import blast

class BlastTest(TestCase):

  def setUp(self):
    ft_gene = Feature_Type(type='Gene')
    ft_gene.save()

    self.dna = 'ATTGCGGATCGCGAATGCGATCG'
    self.pro = 'MKKKAPSI'
    self.pro_dna = 'ATGAAGAAGAAAGCACCAAGCATA'

    self.feature1 = Feature(type=ft_gene, name='G1', sequence=self.dna)
    self.feature1.as_dna()
    self.feature1.save()

    self.feature2 = Feature(type=ft_gene, name='G2', sequence=self.pro)
    self.feature2.as_protein()
    self.feature2.save()

    self.feature_db = Feature_Database(name='test')
    self.feature_db.save()
    self.feature_db.features.add(self.feature1, self.feature2)

  def test_blast(self):
    self.feature_db.build()

    query = 'G'*100+self.dna+'A'*40
    feature_list = blast(query, self.feature_db)

    self.assertEquals(len(feature_list), 1)
    self.assertEquals(feature_list[0].name, self.feature1.name)
    self.assertEquals(feature_list[0].start, 101)
    self.assertEquals(feature_list[0].end, 100+len(self.dna))
    self.assertEquals(feature_list[0].clockwise, True)

  def test_blast_evalue_threshold(self):
    self.feature_db.build()

    query = 'G'*100+self.dna+'A'*40
    feature_list = blast(query, self.feature_db)
    self.assertEquals(len(feature_list), 1)
    feature_list = blast(query, self.feature_db, evalue_threshold=1E-50)
    self.assertEquals(len(feature_list), 0)

  def test_blast_identity_threshold(self):
    self.feature_db.build()

    q = self.dna
    # make two changes
    q = q[0:3]+'C'+q[4:6]+'C'+q[7:]
    self.assertEquals(len(q), len(self.dna))
    query = 'G'*100+q+'A'*40

    feature_list = blast(query, self.feature_db, identity_threshold=None)
    self.assertEquals(len(feature_list), 1)
    self.assertEquals(feature_list[0].start, 101)
    self.assertEquals(feature_list[0].end, 100+len(self.dna))
    self.assertEquals(feature_list[0].clockwise, True)

    feature_list = blast(query, self.feature_db, identity_threshold=0.99)
    self.assertEquals(len(feature_list), 0)
 
  def test_blast_feature_threshold(self):
    self.feature_db.build()

    query = 'G'*100+self.dna[0:12]+'A'*40
    feature_list = blast(query, self.feature_db, feature_threshold=None)
    self.assertEquals(len(feature_list), 1)
    self.assertEquals(feature_list[0].start, 101)
    self.assertEquals(feature_list[0].end, 100+12)
    self.assertEquals(feature_list[0].clockwise, True)

    feature_list = blast(query, self.feature_db, feature_threshold=0.8)
    self.assertEquals(len(feature_list), 0)
 
  def test_get_feature_from_blast_result(self):
    self.feature_db.build()

    query = 'G'*100+self.dna+'A'*40
    feature_list = blast(query, self.feature_db)
    self.assertEquals(len(feature_list), 1)
    self.assertEquals(feature_list[0].feature.id, self.feature1.id)

  def test_returns_one_result_from_across_circular_boundary(self):
    self.feature_db.build()
    q = 'G'*100+self.dna+'A'*40
    query = q[110:]+q[0:110]
    feature_list = blast(query, self.feature_db)
    # if we don't remove truncated features across circular boundary, we'd see
    # 2 results, one for truncated feature, one for full feature
    self.assertEquals(len(feature_list), 1)

  def test_returns_correct_coordinates_across_circular_boundary(self):
    self.feature_db.build()

    q = 'G'*100+self.dna+'A'*40
    query = q[110:]+q[0:110]

    feature_list = blast(query, self.feature_db)
    self.assertEquals(feature_list[0].start, len(q)-10+1)
    self.assertEquals(feature_list[0].end, len(self.dna)-10)
    self.assertEquals(feature_list[0].clockwise, True)


class IntegrationTest(TestCase):

  def setUp(self):
    ft_gene = Feature_Type(type='Gene')
    ft_gene.save()

    self.dna = 'ATTGCGGATCGCGAATGCGATCG'
    self.pro = 'MKKKAPSI'
    self.pro_dna = 'ATGAAGAAGAAAGCACCAAGCATA'

    self.feature1 = Feature(type=ft_gene, name='G1', sequence=self.dna)
    self.feature1.as_dna()
    self.feature1.save()

    self.feature2 = Feature(type=ft_gene, name='G2', sequence=self.pro)
    self.feature2.as_protein()
    self.feature2.save()

    self.feature_db = Feature_Database(name='test')
    self.feature_db.save()
    self.feature_db.features.add(self.feature1, self.feature2)


  def test_build_db(self):
    self.feature_db.build()


  def test_blastn(self):
    self.feature_db.build()

    data = {'db': self.feature_db.name, 'sequence': self.dna}
    url = reverse('giraffe-analyze')
    resp = self.client.post(url, data)
    self.assertEquals(resp.status_code, 200)
    res = json.loads(resp.content)

    self.assertEquals(res[0], len(self.dna))
    self.assertItemsEqual(res[1],
      [{"show_feature": 1, "layer": "Detected Features",
        "name": "G1", "type_id": 5, "label": "G1", 
        "start": 1, "end": 0, "clockwise": True,
        "alignment": {  "query": "ATTGCGGATCGCGAATGCGATCG",
                        "match": "|||||||||||||||||||||||",
                      "subject": "ATTGCGGATCGCGAATGCGATCG"}},

       {"show_feature": 1, "layer": "Restriction Enzymes",
        "name": "NruI", "type_id": 4, "elucidate": "TCG^_CGA", "label": "NruI", 
        "start": 9, "cut": 11, "end": 14, "clockwise": True},

       {"show_feature": 1, "layer": "Restriction Enzymes",
        "name": "ClaI", "type_id": 4, "elucidate": "AT^CG_AT", "label": "ClaI",
        "start": 20, "cut": 21, "end": 2, "clockwise": True}
      ]
    )


  def test_blastx(self):
    self.feature_db.build()

    q = 'A'+self.pro_dna+'T'
    data = {'db': self.feature_db.name, 'sequence': q}
    url = reverse('giraffe-analyze')
    resp = self.client.post(url, data)
    self.assertEquals(resp.status_code, 200)
    res = json.loads(resp.content)

    self.assertEquals(res[0], len(q))
    self.assertItemsEqual(res[1], [
      {"show_feature": 1, "layer": "Detected Features",
       "start": 2, "end": 25, "clockwise": True,
       "name": "G2", "type_id": 5, "label": "G2",
       "alignment": {"query": "MKKKAPSI", "match": "MKKKAPSI", "subject": "MKKKAPSI"}},
    ])


  def test_blast2(self):
    data = {'subject': self.dna, 'query': self.dna[0:22]+'T'}

    url = reverse('blast2')
    resp = self.client.post(url, data)
    self.assertEquals(resp.status_code, 200)
    res = json.loads(resp.content)

    self.assertItemsEqual(res, [
      { "subject_start": 1, "subject_end": 22,
        "query_start": 1, "query_end": 22,
        "evalue": 5.81644e-07,
          "query": "ATTGCGGATCGCGAATGCGATC",
          "match": "||||||||||||||||||||||",
        "subject": "ATTGCGGATCGCGAATGCGATC" },
    ])
 
