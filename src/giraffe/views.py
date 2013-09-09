from django.http import HttpResponse
import features
import orfs
import json
import gb
import httplib


def _post(request):
    """
    Post a sequence and run the sequence through blast and orf detection.
    Expects: db and sequence
    Response: JSON list of features
    """

    from hippo.models import Feature_Database

    is_gb = False
    db_name = request.REQUEST['db'].strip()
    db = Feature_Database.objects.get(name=db_name)

    sequence = request.REQUEST['sequence']
    gb_features = []

    # parse genbank
    if sequence.strip().startswith('LOCUS'):
      is_gb = True
      sequence, gb_features = gb.parse_genbank(sequence.lstrip())

    # clean sequence
    sequence = features.clean_sequence(sequence)

    feature_list = gb_features

    if not is_gb or ('gbonly' not in request.REQUEST) or request.REQUEST['gbonly'] != '1':
      # feature detection
      feature_list += features.blast(sequence, db, protein=False)
      feature_list += features.blast(sequence, db, protein=True)
      # restriction site search
      feature_list += features.find_restriction_sites(sequence)
      # ORFs and tags
      orf_list, tag_list = orfs.detect_orfs_and_tags(sequence)
      feature_list += orf_list
      feature_list += tag_list

    res = [x.to_dict() for x in feature_list]
    # print 'returning %s' % (res,)

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

    # allow cross origin API calls
    http_res['Access-Control-Allow-Origin'] = '*'
    http_res['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    http_res['Access-Control-Max-Age'] = 1000

    return http_res
 

def post(request):
  try:
    return _post(request)
  except Exception as e:
    import traceback, sys
    traceback.print_exc(file=sys.stdout)
    raise(e)


def _blast2(request):
    """
    Post query and subject sequences, returns alignment of the two using blastn.
    Expects: query, subject
    Response: JSON dictionary with subject and query strings
    """

    if (not 'subject' in request.REQUEST) or (not 'query' in request.REQUEST):
      res = []

    else:
      subject = features.clean_sequence(request.REQUEST['subject'])
      query = features.clean_sequence(request.REQUEST['query'])
      res = features.blast2(subject, query)

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

    # allow cross origin API calls
    http_res['Access-Control-Allow-Origin'] = '*'
    http_res['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    http_res['Access-Control-Max-Age'] = 1000
    return http_res
 

def blast2(request):
  return _blast2(request)
  try:
    return _blast2(request)
  except Exception as e:
    print str(e)
    raise(e)

