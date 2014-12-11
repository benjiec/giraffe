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
    self.assertEquals(feature_list[0].query_start, 101)
    self.assertEquals(feature_list[0].query_end, 100+len(self.dna))
    self.assertEquals(feature_list[0].subject_start, 1)
    self.assertEquals(feature_list[0].subject_end, len(self.dna))

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
    self.assertEquals(feature_list[0].query_start, 101)
    self.assertEquals(feature_list[0].query_end, 100+len(self.dna))
    self.assertEquals(feature_list[0].subject_start, 1)
    self.assertEquals(feature_list[0].subject_end, len(self.dna))

    feature_list = blast(query, self.feature_db, identity_threshold=0.99)
    self.assertEquals(len(feature_list), 0)
 
  def test_blast_feature_threshold(self):
    self.feature_db.build()
    p = 0.8
    n = int(len(self.dna)*p)

    query = 'G'*100+self.dna[0:n]+'A'*40
    feature_list = blast(query, self.feature_db, feature_threshold=None)
    self.assertEquals(len(feature_list), 1)
    self.assertEquals(feature_list[0].query_start, 101)
    self.assertEquals(feature_list[0].query_end, 100+n)
    self.assertEquals(feature_list[0].subject_start, 1)
    self.assertEquals(feature_list[0].subject_end, n)

    feature_list = blast(query, self.feature_db, feature_threshold=p)
    self.assertEquals(len(feature_list), 0)
 
  def test_get_feature_from_blast_result(self):
    self.feature_db.build()

    query = 'G'*100+self.dna+'A'*40
    feature_list = blast(query, self.feature_db)
    self.assertEquals(len(feature_list), 1)
    self.assertEquals(feature_list[0].feature_id, self.feature1.id)

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
    self.assertEquals(feature_list[0].query_start, len(q)-10+1)
    self.assertEquals(feature_list[0].query_end, len(self.dna)-10)
    self.assertEquals(feature_list[0].subject_start, 1)
    self.assertEquals(feature_list[0].subject_end, len(self.dna))


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


  def test_finds_orf_in_both_directions_and_across_boundary(self):
    self.feature_db.build()

    query = 'G'*100+'ATG'+'C'*3000+'TAG'+'CTA'+'G'*1800+'CAT'

    data = {'db': self.feature_db.name, 'sequence': query}
    url = reverse('giraffe-analyze')
    resp = self.client.post(url, data)
    self.assertEquals(resp.status_code, 200)
    res = json.loads(resp.content)

    self.assertEquals(res[0], len(query))
    self.assertItemsEqual(res[1],
      [
       {'orf_frame': 1,
        'layer': 'ORFs',
        'type_id': 10,
        'subject_start': 1,
        'subject_end': 3+3000+3,
        'query_start': 100+1,
        'query_end': 100+3+3000+3,
        'label': 'ORF frame 2',
        'name': 'ORF frame 2'},
       {'orf_frame': 0,
        'layer': 'ORFs',
        'type_id': 10,
        'subject_start': 3+1800+3,
        'subject_end': 1,
        'query_start': 100+3+3000+3+1,
        'query_end': 100+3+3000+3+3+1800+3,
        'label': 'ORF frame 1',
        'name': 'ORF frame 1'},
       # across circular boundary, there is AT, then G, it ends with the first
       # stop codon after C*3000
       {'orf_frame': 2,
        'layer': 'ORFs',
        'type_id': 10,
        'subject_start': 1,
        'subject_end': 3+99+3+3000+3,
        'query_start': len(query)-2+1,
        'query_end': 100+3+3000+3,
        'label': 'ORF frame 3',
        'name': 'ORF frame 3'}
      ]
  )


  def test_does_not_find_orf_across_boundary_if_not_in_circular_mode(self):
    self.feature_db.build()

    query = 'G'*100+'ATG'+'C'*3000+'TAG'+'CTA'+'G'*1800+'CAT'

    data = {'db': self.feature_db.name, 'sequence': query, 'circular': 0}
    url = reverse('giraffe-analyze')
    resp = self.client.post(url, data)
    self.assertEquals(resp.status_code, 200)
    res = json.loads(resp.content)

    self.assertEquals(res[0], len(query))
    self.assertItemsEqual(res[1],
      [
       {'orf_frame': 1,
        'layer': 'ORFs',
        'type_id': 10,
        'subject_start': 1,
        'subject_end': 3+3000+3,
        'query_start': 100+1,
        'query_end': 100+3+3000+3,
        'label': 'ORF frame 2',
        'name': 'ORF frame 2'},
       {'orf_frame': 0,
        'layer': 'ORFs',
        'type_id': 10,
        'subject_start': 3+1800+3,
        'subject_end': 1,
        'query_start': 100+3+3000+3+1,
        'query_end': 100+3+3000+3+3+1800+3,
        'label': 'ORF frame 1',
        'name': 'ORF frame 1'}
      ]
  )


  def test_find_tags_within_orf(self):
    self.feature_db.build()

    query = 'G'*100+'ATG'+'C'*3000+'CAT'*6+'TAG'

    data = {'db': self.feature_db.name, 'sequence': query, 'circular': 0}
    url = reverse('giraffe-analyze')
    resp = self.client.post(url, data)
    self.assertEquals(resp.status_code, 200)
    res = json.loads(resp.content)

    self.assertEquals(res[0], len(query))
    self.assertItemsEqual(res[1],
      [
       {'orf_frame': 1,
        'layer': 'ORFs',
        'type_id': 10,
        'subject_start': 1,
        'subject_end': 3+3000+3*6+3,
        'query_start': 100+1,
        'query_end': 100+3+3000+3*6+3,
        'label': 'ORF frame 2',
        'name': 'ORF frame 2'},
       {'layer': 'Detected Features',
        'type_id': 1,
        'subject_start': 1,
        'subject_end': 3*6,
        'query_start': 100+3+3000+1,
        'query_end': 100+3+3000+3*6,
        'label': '6xHIS',
        'name': '6xHIS'}
      ]
  )


  def test_blastn(self):
    self.feature_db.build()

    data = {'db': self.feature_db.name, 'sequence': self.dna}
    url = reverse('giraffe-analyze')
    resp = self.client.post(url, data)
    self.assertEquals(resp.status_code, 200)
    res = json.loads(resp.content)

    self.assertEquals(res[0], len(self.dna))
    self.assertItemsEqual(res[1],
      [{"layer": "Detected Features",
        "name": "G1",
        "type_id": 5,
        "label": "G1", 
        "query_start": 1,
        "query_end": 23,
        "subject_start": 1,
        "subject_end": 23,
        "evalue": 6.01355e-11,
        "identities": 23,
        "alignment": {  "query": "ATTGCGGATCGCGAATGCGATCG",
                        "match": "|||||||||||||||||||||||",
                      "subject": "ATTGCGGATCGCGAATGCGATCG"}},

       {"layer": "Restriction Enzymes",
        "name": "NruI", "type_id": 4, "elucidate": "TCG^_CGA", "label": "NruI", 
        "query_start": 9, "cut": 11, "query_end": 14, "subject_start": 1, "subject_end": 6},

       {"layer": "Restriction Enzymes",
        "name": "ClaI", "type_id": 4, "elucidate": "AT^CG_AT", "label": "ClaI",
        "query_start": 20, "cut": 21, "query_end": 2, "subject_start": 1, "subject_end": 6},
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
      {"layer": "Detected Features",
       "query_start": 2,
       "query_end": 25,
       "subject_start" : 1,
       "subject_end" : 8,
       "name": "G2",
       "type_id": 5,
       "label": "G2",
       "alignment": {"query": "MKKKAPSI", "match": "MKKKAPSI", "subject": "MKKKAPSI"},
       "evalue": 5.42133e-5,
       "identities": 8
      }
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
