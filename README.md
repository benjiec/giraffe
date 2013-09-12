### Sequence Feature Detection and Mapping

This software is mostly divided into two parts: Giraffe and Hippo. Giraffe is a
set of Javascripts that visualize sequences and sequence features, as well as a
Django/Python program to detect ORFs, restriction sites, and features from a
sequence. You can use the Javascripts independently from the Django program as
well. Hippo is a Django/Python frontend for managing NCBI Blast databases; these
databases are used by Giraffe when detecting features.

Hippo and Giraffe can be used together to construct database of sequence
features, detect features in plasmid sequences, and visualize the features on a
plasmid map. Giraffe can also parse features from a GenBank input sequence.

Hippo and Giraffe provide a convenient way to use Blast for your own
application. You can build Blast databases using Hippo, then use Giraffe to
blast query sequence against the database. Hippo offers a Django admin UI to
manage the blast DB, while Giraffe handles calling blast, parsing blast
results, and visualizing detected features.

This is version 2 of the distribution, which is significantly different from
version 1 in many ways. If you want version 1, checkout the v1.1 branch of the
repository.

This software was originally written by Misha Wolfson and Benjie Chen,
copyrighted by Addgene, and released under the MIT License. See LICENSE file.
It is now maintained by Benjie Chen.


### Giraffe - Visualization

You can use Giraffe Javascripts independently of the Django service, to
visualize a sequence you already have a list of features for.

See src/giraffe/templates/giraffe/{analyze,draw}.html.

Documentation: limited, but src/giraffe/static/javascripts/giraffe/README
describes how to use just the Javascript plasmid drawing widget.


### Giraffe - Sequence feature detection

Requirements:

  * System requirements: see provison/provision.sh (you can use this to
    provision a Vagrant instance, e.g.)

  * Python requirements: pip install -r requirements.txt

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

This will return a JSON array of [sequence_len, array of features, sequence].

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


