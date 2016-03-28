import json
import httplib
from django.http import HttpResponse
from Bio.Alphabet import IUPAC
from hippo import clean_sequence
import features
import orfs
import gb


def _post(params, is_ajax):
    """
    Post a sequence and run the sequence through blast and orf detection.
    Expects: db and sequence
    Response: JSON list of features
    """

    from hippo.models import Feature_Database

    is_gb = False
    db_name = params['db'].strip()
    db = Feature_Database.objects.get(name=db_name)

    sequence = params['sequence']
    gb_features = []

    # parse genbank
    if sequence.strip().startswith('LOCUS'):
      is_gb = True
      try:
        sequence, gb_features = gb.parse_genbank(sequence.lstrip())
      except Exception as e:
        sequence = ""
        gb_features = []

    # clean sequence
    input_type = params['input'] if 'input' in params else 'dna'
    if input_type in ['protein']:
      sequence = clean_sequence(sequence, alphabet=IUPAC.protein)
    else:
      sequence = clean_sequence(sequence)

    feature_list = gb_features
    gbonly = 'gbonly' in params and params['gbonly'] in ['1', 'true', 'True']
    blastonly = 'blastonly' in params and params['blastonly'] in ['1', 'true', 'True']

    if not is_gb or gbonly is False:
      args = {}
      if 'identity_threshold' in params:
        args['identity_threshold'] = float(params['identity_threshold'])
      if 'feature_threshold' in params:
        args['feature_threshold'] = float(params['feature_threshold'])
      circular = True
      if 'circular' in params and str(params['circular']).strip().lower() in ['false', 0, '0']:
        circular = False

      # feature detection
      feature_list += features.blast(sequence, db, input_type=input_type, protein=False, circular=circular, **args)
      feature_list += features.blast(sequence, db, input_type=input_type, protein=True, circular=circular, **args)

      if input_type == 'dna' and blastonly is False:
        # restriction site search
        feature_list += features.find_restriction_sites(sequence, circular=circular)
        # ORFs and tags
        orf_list, tag_list = orfs.detect_orfs_and_tags(sequence, circular=circular)
        feature_list += orf_list
        feature_list += tag_list

    res = [x.to_dict() for x in feature_list]
    # print 'returning %s' % (res,)

    # now sort everything by start
    res.sort(cmp=lambda x,y:cmp(int(x['query_start']),int(y['query_start'])))

    res = [len(sequence),res,sequence]
    j = json.JSONEncoder().encode(res)

    if 'jsonp' in params:
        j = params['jsonp']+'('+j+')'
        http_res = HttpResponse(j,mimetype="text/javascript",status=httplib.OK)

    else:
        # technically we should be returning "application/json", but in that
        # case browsers force user to download into a file, and for debugging
        # we want to be able to see the JSON list in browser. looks like most
        # browsers will handle JSON sent back as text/html anyways.
        if is_ajax:
            http_res = HttpResponse(j,mimetype="application/json",status=httplib.OK)
        else:
            http_res = HttpResponse(j,status=httplib.OK)

    # allow cross origin API calls
    http_res['Access-Control-Allow-Origin'] = '*'
    http_res['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    http_res['Access-Control-Max-Age'] = 1000

    return http_res
 

def post(request):
  if 'sequence' in request.REQUEST:
    params = request.REQUEST
  else:
    params = json.loads(request.body)
  return _post(params, request.is_ajax())


def _blast2(params, is_ajax):
    """
    Post query and subject sequences, returns alignment of the two using blastn.
    Expects: query, subject
    Response: JSON dictionary with subject and query strings
    """

    if (not 'subject' in params) or (not 'query' in params):
      res = []

    else:
      subject = clean_sequence(params['subject'])
      query = clean_sequence(params['query'])
      res = features.blast2(subject, query)

    j = json.JSONEncoder().encode(res)

    if 'jsonp' in params:
      j = params['jsonp']+'('+j+')'
      http_res = HttpResponse(j,mimetype="text/javascript",status=httplib.OK)

    else:
      # technically we should be returning "application/json", but in that
      # case browsers force user to download into a file, and for debugging
      # we want to be able to see the JSON list in browser. looks like most
      # browsers will handle JSON sent back as text/html anyways.
      if is_ajax:
        http_res = HttpResponse(j,mimetype="application/json",status=httplib.OK)
      else:
        http_res = HttpResponse(j,status=httplib.OK)

    # allow cross origin API calls
    http_res['Access-Control-Allow-Origin'] = '*'
    http_res['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    http_res['Access-Control-Max-Age'] = 1000
    return http_res
 

def blast2(request):
  try:
    if 'subject' in request.REQUEST:
      params = request.REQUEST
    else:
      params = json.loads(request.body)
    return _blast2(params, request.is_ajax())
  except Exception as e:
    print str(e)
    raise(e)
