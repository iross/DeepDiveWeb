def query_strings(request):
    q = None
    pubname = None
    if 'q' in request.GET:
        q = request.GET['q']
    if 'pubname' in request.GET:
        pubname = request.GET['pubname']
    return {
            'q': q,
            'pubname': pubname,
            }

