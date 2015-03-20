def context_processors(request):
    return {
            q: request.GET['q'],
            pubname: request.GET['pubname'],
            }

