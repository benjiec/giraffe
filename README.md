### Blast and Sequence Feature Detection

Giraffe consists of two tools: Giraffe feature detection, and Hippo feature
database manager.

User can define features using Hippo, assign features to databases, build NCBI
blast databases, and use Giraffe API to detect features in a given query
sequence.

This software was originally written by Misha Wolfson and Benjie Chen,
copyrighted by Addgene, and released under the MIT License. See LICENSE file.
It is now maintained by Benjie Chen. Originally, Giraffe included a Javascript
application for visualizing features on a sequence. That tool has now been
moved to [giraffe-ui](http://github.com/benjiec/giraffe-ui).


### Try it out

Requirements:

  * System requirements: see provison/provision.sh (e.g. you can use this to
    provision a Vagrant instance).

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

To test it out, install [giraffe-ui](http://github.com/benjiec/giraffe-ui) and
point the example ```analyze.html``` and ```draw.html``` files to

```
http://0.0.0.0:8000/giraffe/analyze/
```


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
{
  "query_start": ...,
  "query_end": ...,
  "subject_start": ...,
  "subect_end": ...,
  "label": ...,
  ...
}
```

Features from blast also has the following attributes

```
{
  ...
  "alignment": {
    "query": ...,
    "match": ...,
    "subject": ...
  }
}
```

The format of the JSON is "standardized" in
[giraffe-features](http://github.com/benjiec/giraffe-features).

By default, feature detection returns features (from blast), and for DNA
sequences, restriction sites and ORFs. If you set blastonly=1 in the URL, it
will not detect restriction sites or ORFs.  You can also set input=protein and
send in a protein sequence as query.

You can use Hippo to build DNA or protein blast databases. Giraffe uses blastn
to blast DNA queries against DNA blast databases, blastx to blast DNA queries
against protein blast databases, blastp to blast protein queries against
protein blast databases, tblastn to blast protein queries against DNA blast
databases.

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
