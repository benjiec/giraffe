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

You can use Giraffe independently. See HTML files in src/giraffe/demo
directory. Also README file in src/giraffe/static/js describes how to use just
the Javascript plasmid drawing widget.


Giraffe - Sequence feature detection
------------------------------------

Requirements:

  * System requirements: see provison/provision.sh (you can use this to
    provision a Vagrant instance, e.g.)

  * Python requirements: pip install -r requirements.txt

  * NCBI: install NCBI Blast toolkit (this takes awhile): cd ncbi; . install


Install Django service and build default database:

'''
git clone git@github.com:benjiec/giraffe.git
cd giraffe
(cd src; python manage.py migrate)
(cd src; python manage.py build_blastdb)
'''

Run test server:

'''
cd src; python manage.py runserver 0.0.0.0:8000
'''

Then goto http://0.0.0.0:8000/giraffe/demo/


API
---

You can POST a sequence to "/hippo/", with the following params:

'''
db=default&sequence=your_dna_sequence_here
'''

This will return a JSON array of [sequence_len, array of features, sequence].


Hippo as a BLAST frontend
-------------------------

TBA

