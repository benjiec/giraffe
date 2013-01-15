from django.http import HttpResponse
import features
import json
import httplib
import orfs


from django.shortcuts import redirect
from django.core.urlresolvers import reverse


def post(request):
    """
    Post a sequence and run the sequence through blast and orf detection.
    Expects: db and sequence
    Response: JSON list of features
    """

    db_name = request.REQUEST['db'].strip()
    sequence = features.clean_sequence(request.REQUEST['sequence'])

    orf_list, tag_list = orfs.detect_orfs_and_tags(sequence)
    res = [x.to_dict() for x in orf_list+tag_list]

    # now sort everything by start
    res.sort(cmp=lambda x,y:cmp(int(x['start']),int(y['start'])))

    res = [len(sequence),res,sequence]
    j = json.JSONEncoder().encode(res)

    if 'jsonp' in request.REQUEST:
        j = request.REQUEST['jsonp']+'('+j+')'
        http_res = HttpResponse(j,mimetype="text/javascript",status=httplib.OK)

    else:
	# technically we should be returning "application/json", but in that
	# case browsers force user to download into a file, and for debugging
	# we want to be able to see the JSON list in browser. looks like most
	# browsers will handle JSON sent back as text/html anyways.
        if request.is_ajax():
            http_res = HttpResponse(j,mimetype="application/json",status=httplib.OK)
        else:
            http_res = HttpResponse(j,status=httplib.OK)

    return http_res
 
