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


Install Django service:

'''
git clone git@github.com:benjiec/giraffe.git
cd giraffe
(cd src; python manage.py migrate)
# sqlite database will now be in src
'''

TODO: give instruction for creating ncbi blast database

Run test server

'''
cd src; python manage.py runserver 0.0.0.0:8000
'''

Then goto http://0.0.0.0:8000/demo/, and click on "See an example" to see an
example.


API
---

You can POST a sequence to "/hippo/", with the following params:

'''
db=default&sequence=your_dna_sequence_here
'''

Then you will be redirected to a URL that looks like

'''
/hippo/8de364690dbeb88d2ab63bd66861725539aa3204/default
'''

The "8de3...3204" string is the hash identifier for your sequence. You can use
this hash identifier and this URL to retrieve features in the future (JSON
format).

Also, you can use the hash identifier with the JavaScript widgets. See demo
directory. You can download the HTML files from the demo directory to your
local computer, and load them in your browser. These files show how you can
incorporate Giraffe sequence map and analyzer widgets in your web app.


Using Hippo as a BLAST frontend
-------------------------------

TBA


