from django.http import HttpResponse
import features
import orfs
import json
import httplib


def _post(request):
    """
    Post a sequence and run the sequence through blast and orf detection.
    Expects: db and sequence
    Response: JSON list of features
    """

    db_name = request.REQUEST['db'].strip()
    sequence = features.clean_sequence(request.REQUEST['sequence'])

    # feature detection
    feature_list = features.blast(sequence, db_name)

    # restriction site search
    cutter_list = features.find_restriction_sites(sequence)

    # ORFs and tags
    orf_list, tag_list = orfs.detect_orfs_and_tags(sequence)

    res = [x.to_dict() for x in feature_list+cutter_list+orf_list+tag_list]

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
 

def post(request):
  try:
    return _post(request)
  except Exception as e:
    print str(e)
    raise(e)

