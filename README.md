Sequence Feature Detection and Mapping
--------------------------------------

This software is mostly divided into two parts: Giraffe and Hippo. Giraffe is a
set of Javascripts that visualize sequences and sequence features, as well as a
Django/Python program to detect ORFs, restriction sites, and features from a
sequence. You can use the Javascripts independently from the Django program as
well. Hippo is a Django/Python frontend for managing NCBI Blast databases.

Hippo and Giraffe can be used together to construct database of sequence
features, detect features in plasmid sequences, and visualize the features on a
plasmid map.

This is version 2 of the distribution, which is significantly different from
version 1 in many ways. If you want version 1, checkout the v1.1 branch of the
repository.

This software was originally written by Misha Wolfson and Benjie Chen,
copyrighted by Addgene, and released under the MIT License. See LICENSE file.
It is now maintained by Benjie Chen.


Giraffe - Visualization
-----------------------

You can use Giraffe Javascripts independently of the Django service, to
visualize a sequence you already have a list of features for.

Django examples: see src/giraffe/templates/giraffe/{analyze,draw}.html.

Rails: add the following to your Gemfile

```
git "git://github.com/benjiec/giraffe.git" do
  gem "giraffe-js-rails"
end
```

Then for your Javascript asset file (e.g. vendor/assets/javascripts/vendor.js), include

```
//= require giraffe-js
```

(If you need jQuery UI tooltip, which comes with jQuery UI 1.9+, use
giraffe-js-with-tooltip).  And for your CSS asset file (e.g. vendor/assets/stylesheets/vendor.css), include

```
*= require giraffe-js
```

Documentation: limited, but src/giraffe/static/javascripts/giraffe/README
describes how to use just the Javascript plasmid drawing widget.


Giraffe - Sequence feature detection
------------------------------------

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


API
---

You can POST a sequence to "/hippo/", with the following params:

```
db=default&sequence=your_dna_sequence_here
```

This will return a JSON array of [sequence_len, array of features, sequence].


Hippo as a BLAST frontend
-------------------------

TBA

