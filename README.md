Sequence Feature Detection and Mapping
--------------------------------------

This software was originally written by Misha Wolfson and Benjie Chen,
copyrighted by Addgene, and released under the MIT License. See LICENSE file.
It is now maintained by Benjie Chen.

The software is mostly divided into two parts. Giraffe is a set of Javascripts
that visualize sequences and sequence features. Hippo is a Django/Python
frontend for NCBI Blast. Hippo and Giraffe can be used together to construct
database of sequence features, detect features in plasmid sequences, and
visualize the features on a plasmid map.


Giraffe - Visualization
-----------------------

You can use Giraffe independently. See HTML files in src/giraffe/demo
directory. Also README file in src/giraffe/static/js describes how to use just
the Javascript plasmid drawing widget.


Hippo - BLAST sequence feature detection
----------------------------------------

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


Using Hippo as a BLAST frontend
-------------------------------

TBA


