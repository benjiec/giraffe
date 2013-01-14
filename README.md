Giraffe Feature Detection and Mapping
-------------------------------------

Example: http://www.addgene.org:8800/

This software was originally written by Misha Wolfson and Benjie Chen, and
copyrighted by Addgene, and released under the MIT License. See LICENSE file.
It is now maintained by Benjie Chen.

The software is mostly divided into two parts: a Django based service that
detects features within a sequence, and a set of JavaScript widgets that
visualize the sequence, features, digests, etc.


Visualization
-------------

You can use the two parts separately. I.e. you can just use the JavaScript
widget for visualizing and analyzing sequence and features. See HTML files in
the demo directory. Also README file in src/analyze/static/js describes how to
use just the JavaScript plasmid drawing widget.


Feature Detection
-----------------

Requirement for Django service: see requirements.txt for Python dependencies, and
provision/provision.sh for general system dependencies. You can use the later
to setup a Vagrant instance, for example.

Set up MySQL

'''
mysql
> DROP DATABASE giraffe;
> CREATE DATABASE giraffe CHARACTER SET 'utf8'
'''

Install Django service:

'''
git clone git@github.com:benjiec/giraffe.git
cd giraffe
(cd src; python manage.py migrate)
(cd src/hippo/frags; gcc -O6 -o bin/frags frags.c)
(cd src; PYTHONPATH=. python hippo/frags/create_frag_db.py default > hippo/frags/data/default.data)
'''

Run test server

'''
cd src; python manage.py runserver 0.0.0.0:8000
'''

Click on "See an example" to see an example.


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


Building Features DB
--------------------

TBA


