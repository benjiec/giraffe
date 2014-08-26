### Sequence Feature Detection and Mapping

This repository consists of two tools: Giraffe and Hippo. Giraffe includes a
set of javascripts that visualize sequences and sequence features, and a Django
app that blast query against DNA or protein sequences, detects features,
restriction sites, and ORFs from a sequence. You can use the javascripts
independently from the Django program. Hippo is a Django frontend for managing
NCBI blast databases. User can create sequences, assign them to databases, and
use Django management commands to build NCBI blast databases. Giraffe uses NCBI
blast to detect features in the query sequence.

Hippo and Giraffe provide a convenient way to use Blast for your own
application. You can build blast databases using Hippo, then use Giraffe to
blast query sequence against the database. Hippo offers a Django admin UI to
manage the blast DB, while Giraffe handles calling blast, parsing blast
results, and visualizing detected features.

This software was originally written by Misha Wolfson and Benjie Chen,
copyrighted by Addgene, and released under the MIT License. See LICENSE file.
It is now maintained by Benjie Chen.


### Giraffe - Visualization

You can use Giraffe javascripts independently of the Django service, to
visualize a sequence you already have a list of features for.

See src/giraffe/templates/giraffe/{analyze,draw}.html.


### Giraffe - Sequence feature detection and blast

Requirements:

  * System requirements: see provison/provision.sh (you can use this to
    provision a Vagrant instance, e.g.)

  * Python requirements: pip install -r requirements.txt
    (Currently supports Django 1.5 or higher)

  * NCBI: install NCBI Blast toolkit (this takes awhile): cd ncbi; . install


Install Django service and build default database:

```
git clone git@github.com:benjiec/giraffe.git
cd giraffe
(cd src; python manage.py migrate)
(cd src; python manage.py build_blastdb)
```

Run test server:

```
cd src; python manage.py runserver 0.0.0.0:8000
```

Then goto http://0.0.0.0:8000/giraffe/demo/


### API

You can POST a sequence to "/giraffe/analyze/", with the following params:

```
db=default&sequence=your_dna_sequence_or_genbank_sequence_here
```

There are some other params you can set, e.g. identity_threshold,
feature_threshold, circular. See giraffe/views.py and giraffe/features.py.

This will return a JSON array of [sequence_len, array of features, sequence].
Each feature in the feature array has, among other attributes

```
{ "query_start": ...,
  "query_end": ...,
  "subject_start": ...,
  "subect_end": ...,
  "accession": ...,
  "alignment": {
    "query": ...,
    "match": ...,
    "subject": ...
  }
}
```

The accession value is the Feature.name attribute from the Hippo database.

Programmatically, you can construct new blast databases using Hippo. E.g.

```
from hippo.models import Feature, Feature_Type, Feature_Database
db = Feature_Database(name='my_db')
db.save()
ft = Feature_Type.objects.get(type='Promoter')
feature = Feature(type=ft, name='Promoter1', sequence='AGCTATTTCGGAGTCGGCGATTACGATCGGCGATCG')
feature.save()
db.features.add(feature)
db.build()
```

You can then query against database. E.g.

```
from hippo.models import Feature_Database
from giraffe.features import blast

db = Feature_Database.objects.get(name='my_db')
query = '...' # some query sequence
features = blast(query, db)
```


### Hippo as a BLAST frontend

Use Django admin to add features, group features into databases. Use the
build_blastdb django management command to build your databases, then Giraffe
can use the databases for feature detection. Alternatively, call the
```build``` method on a ```Feature_Database object``` directly.
