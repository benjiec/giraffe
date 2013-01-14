import time
from django.shortcuts import render_to_response
from django.template import RequestContext
import hippo.models


def test_draw(request,hash,db_name):
    """
    Get features of a sequence, using the sequence's sha-1 hash as the
    identifier.
    """
    db = hippo.models.Feature_Database.objects.get(name=db_name)
    sequence = hippo.models.Sequence.objects.get(db=db,hash=hash)
    ts = int(time.mktime(sequence.modified.timetuple()))

    return render_to_response(
        'hippo/draw.html', { "hash" : hash, "mtime" : ts },
        context_instance=RequestContext(request)
    )


def test_analyze(request,hash,db_name):
    """
    Get features of a sequence, using the sequence's sha-1 hash as the
    identifier.
    """
    db = hippo.models.Feature_Database.objects.get(name=db_name)
    sequence = hippo.models.Sequence.objects.get(db=db,hash=hash)
    ts = int(time.mktime(sequence.modified.timetuple()))

    return render_to_response(
        'hippo/analyze.html', { "hash" : hash, "mtime" : ts },
        context_instance=RequestContext(request)
    )



