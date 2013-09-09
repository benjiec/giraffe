from django.test import TestCase
from django.core.urlresolvers import reverse
from hippo.models import Feature, Feature_Type, Feature_Database
import json


class IntegrationTest(TestCase):

  def setUp(self):
    ft_gene = Feature_Type(type='Gene')
    ft_gene.save()

    self.dna = 'ATTGCGGATCGCGAATGCGATCG'
    self.pro = 'MKKKAPSI'
    self.pro_dna = 'ATGAAGAAGAAAGCACCAAGCATA'

    self.feature1 = Feature(type=ft_gene, name='G1', sequence=self.dna, dna_or_protein=1)
    self.feature1.save()

    self.feature2 = Feature(type=ft_gene, name='G2', sequence=self.pro, dna_or_protein=2)
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
          "query": "ATTGCGGATCGCGAATGCGATC",
          "match": "||||||||||||||||||||||",
        "subject": "ATTGCGGATCGCGAATGCGATC" },
    ])
 
