# Create your views here.
from deepdive.models import Publication, Article, NlpProcessing, OcrProcessing,ProcForm
from collections import OrderedDict
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from bson.objectid import ObjectId
import django_filters
import ConfigParser
import pymongo
import datetime
import re
import pdb
from django.conf import settings
import urllib
from deepdive.serializers import ArticleSerializer

config = ConfigParser.RawConfigParser()
config.read(settings.BASE_DIR + '/deepdiveweb.cfg')

secret_key = config.get('django', 'secret_key')
reader_user = config.get('database', 'reader_user')
reader_password = config.get('database', 'reader_password')
reader_password = urllib.quote_plus(reader_password)

@login_required
def processing(request):
    proctype = "OCR"
    if request.method == "POST":
        form = ProcForm(request.POST)
    return render(request, 'deepdive/tag.html', {'proctype':proctype, 'tag':tag})

class ArticleViewSet(viewsets.ModelViewSet):
    # add a query here + use Article.objects.raw_query( <search junk here> )
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    search_fields = ('title', 'pubname')
#    filter_backends = (filters.SearchFilter,)

@api_view(['GET'])
def article_list(request):
#        cursor = articles.find(
#                {'$text':{'$search':query_string}},
#                {"contents":0,
#                    "ocr_processing":0,
#                    "nlp_processing":0,
#                    "cuneiform_processing":0,
#                    "fonttype_processing":0,
#                 'score':{'$meta': 'textScore'}})
#        cursor = cursor.sort([('score', {'$meta': 'textScore'})]).limit(50)
    if request.method == 'GET':
        if ('q' in request.GET) and request.GET['q'].strip():
            query_string = request.GET['q']
            articles = Article.objects.raw_query({ "pubname": query_string })
            serializer = ArticleSerializer(articles, many=True)
        else:
            articles = Article.objects.raw_query({})
        return Response(serializer.data)

@login_required
def processingForm(request, proctype="OCR"):
    """
    TODO: Docstring for get_name.

    :request: TODO
    :returns: TODO

    """
       # if this is a POST request we need to process the form data
    tag = None
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        # this doesn't seem to be doing what's expected...
        form = ProcForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            tag = form.cleaned_data['tag']
            # ...
            # redirect to a new URL:
#            return HttpResponseRedirect('/thanks/%s'%tag)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProcForm(proctype)

    return render(request, 'deepdive/name.html', {'form': form, 'proctype':proctype, 'tag':tag})

@login_required
def tag(request, tag):
    """
    TODO: Docstring for article.

    :request: TODO
    :returns: TODO

    """
    uri = "mongodb://%s:%s@127.0.0.1/?authMechanism=MONGODB-CR" % (reader_user, reader_password)
    client = pymongo.MongoClient(uri)
    articlesdb = client.articles
    articles = articlesdb.articles
    pubnames = articles.distinct("pubname")
    procdb = client.processing


    publist=[]
    total = {}
    total["fetched"] = 0
    total["ocr"] = {}
    total["ocr"]["total"] = 0
    total["ocr"]["data"] = {"success": 0, "failure":0}
    total["ocr"]["cpudata"] = {"success": 0, "failure":0}
    total["nlp"] = {}
    total["nlp"]["total"] = 0
    total["nlp"]["data"] = {"success": 0, "failure":0}
    total["nlp"]["cpudata"] = {"success": 0, "failure":0}

    processings = {}
    processings["ocr"] = procdb["ocr_processing"]
    processings["nlp"] = procdb["nlp_processing"]

    for pub in pubnames:
        pubDict = {}
        pubDict["title"] = pub
        pubDict["nospace"] = re.sub("[^a-zA-Z0-9\n\.]", "_", pub)
        pubDict["fetched"] = articles.find( { "pubname":pub }).count()
        total["fetched"] += pubDict["fetched"]

        for proctype in ["ocr","nlp"]:
            pubDict[proctype] = getPubCounts(pub, tag, processings[proctype])
            total[proctype]["data"]["success"] += pubDict[proctype]['data'][0][1]
            total[proctype]["data"]["failure"] += pubDict[proctype]['data'][1][1]
            total[proctype]["total"] += pubDict[proctype]["total"]
            total[proctype]["cpudata"]["success"] += pubDict[proctype]['cpudata'][0][1]
            total[proctype]["cpudata"]["failure"] += pubDict[proctype]['cpudata'][1][1]

        publist.append(pubDict)

    # convert to a c3js-ready lists structures
    totalsl = {}
    for proctype in ["ocr", "nlp"]:
        totalsl[proctype] = {}
        totalsl[proctype]["total"] = total[proctype]["total"]
        totalsl["fetched"] = total["fetched"]
        totalsl[proctype]["data"] = []
        totalsl[proctype]["data"].append(['Success', total[proctype]["data"]["success"]])
        totalsl[proctype]["data"].append(['Failure', total[proctype]["data"]["failure"]])
        totalsl[proctype]["cpudata"] = []
        totalsl[proctype]["cpudata"].append(['Success', total[proctype]["cpudata"]["success"]])
        totalsl[proctype]["cpudata"].append(['Failure', total[proctype]["cpudata"]["failure"]])
    client.close()

    context = {
            'tag' : tag,
            'test' : publist,
            'total': totalsl,
            }
    return render(request, 'deepdive/tag.html', context)

@login_required
def tag_overview(request, tag):
    """
    TODO: Docstring for article.

    :request: TODO
    :returns: TODO

    """
    uri = "mongodb://%s:%s@127.0.0.1/?authMechanism=MONGODB-CR" % (reader_user, reader_password)
    client = pymongo.MongoClient(uri)
    articlesdb = client.articles
    articles = articlesdb.articles
    pubnames = articles.distinct("pubname")
    procdb = client.processing


    publist=[]
    total = {}
    total["fetched"] = 0
    processings = {}
    for proctype in ["ocr", "nlp", "cuneiform", "fonttype"]:
        total[proctype] = {}
        total[proctype]["total"] = 0
        total[proctype]["data"] = {"success": 0, "failure":0}
        total[proctype]["cpudata"] = {"success": 0, "failure":0}
        processings[proctype] = procdb["%s_processing" % proctype]

    for pub in pubnames:
        pubDict = {}
        pubDict["title"] = pub
        pubDict["nospace"] = re.sub("[^a-zA-Z0-9\n\.]", "_", pub)
        pubDict["fetched"] = articles.find( { "pubname":pub }).count()
        total["fetched"] += pubDict["fetched"]

        for proctype in ["ocr","nlp", "cuneiform", "fonttype"]:
            pubDict[proctype] = getPubCounts(pub, tag, processings[proctype])
            total[proctype]["data"]["success"] += pubDict[proctype]['data'][0][1]
            total[proctype]["data"]["failure"] += pubDict[proctype]['data'][1][1]
            total[proctype]["total"] += pubDict[proctype]["total"]
            total[proctype]["cpudata"]["success"] += pubDict[proctype]['cpudata'][0][1]
            total[proctype]["cpudata"]["failure"] += pubDict[proctype]['cpudata'][1][1]

        publist.append(pubDict)

    # convert to a c3js-ready lists structures
    totalsl = {}
    for proctype in ["ocr", "nlp", "cuneiform", "fonttype"]:
        totalsl[proctype] = {}
        totalsl[proctype]["total"] = total[proctype]["total"]
        totalsl["fetched"] = total["fetched"]
        totalsl[proctype]["data"] = []
        totalsl[proctype]["data"].append(['Success', total[proctype]["data"]["success"]])
        totalsl[proctype]["data"].append(['Failure', total[proctype]["data"]["failure"]])
        totalsl[proctype]["cpudata"] = []
        totalsl[proctype]["cpudata"].append(['Success', total[proctype]["cpudata"]["success"]])
        totalsl[proctype]["cpudata"].append(['Failure', total[proctype]["cpudata"]["failure"]])
    client.close()

    context = {
            'tag' : tag,
            'test' : publist,
            'total': totalsl,
            }
    return render(request, 'deepdive/tag_overview.html', context)

@login_required
def tag_type(request, proctype, tag):
    """
    TODO: Docstring for article.

    :request: TODO
    :returns: TODO

    """
    uri = "mongodb://%s:%s@127.0.0.1/?authMechanism=MONGODB-CR" % (reader_user, reader_password)
    client = pymongo.MongoClient(uri)
    articlesdb = client.articles
    articles = articlesdb.articles
    pubnames = articles.distinct("pubname")
    procdb = client.processing
    processings = procdb["%s_processing" % proctype]
    publist=[]
    total = {}
    total["fetched"] = 0
    total["total"] = 0
    total["data"] = {"success": 0, "failure":0}
    total["cpudata"] = {"success": 0, "failure":0}

    pubtotals = processings.find_one( { "tag": tag})["pub_totals"]

    for pub in pubnames:
        pubDict = {}
        pubDict = getPubCounts(pub, tag, processings)
        pubDict["title"] = pub
        pubDict["nospace"] = re.sub("[^a-zA-Z0-9\n\.]", "_", pub)
        pubDict["fetched"] = articles.find( { "pubname":pub }).count()
        total["fetched"] += pubDict["fetched"]
        total["data"]["success"] += pubDict['data'][0][1]
        total["data"]["failure"] += pubDict['data'][1][1]
        total["total"] += pubDict["total"]
        total["cpudata"]["success"] += pubDict['cpudata'][0][1]
        total["cpudata"]["failure"] += pubDict['cpudata'][1][1]

        publist.append(pubDict)

    totalsl = {}
    totalsl["total"] = total["total"]
    totalsl["fetched"] = total["fetched"]
    totalsl["data"] = []
    totalsl["data"].append(['Success', total["data"]["success"]])
    totalsl["data"].append(['Failure', total["data"]["failure"]])
    totalsl["cpudata"] = []
    totalsl["cpudata"].append(['Success', total["cpudata"]["success"]])
    totalsl["cpudata"].append(['Failure', total["cpudata"]["failure"]])

    client.close()
    context = {
            'tag' : tag,
            'test' : publist,
            'total': totalsl,
            }
    return render(request, 'deepdive/tag_type.html', context)

def getPubCounts(pubname, tag, processingColl):
    """

    :pubname: TODO
    :tag: TODO
    :processingColl: TODO
    :returns: Dictionary with counts for # fetched, # ocr'ed, and the
    cpu time spent (includes succeed/failure designation)

    pubdict = {
         "data": [["Success": n_success],["Failure": n_failure]],
         "cpudata": [["Success": cputime_success],["Failure": cputime_failure]]
              },
    The format of the data is for ease of use in c3js plots (http://c3js.org/)

    """
    pubtotals = processingColl.find_one( { "tag": tag})["pub_totals"]

    pubDict = {}
    pubDict["data"]=[]
    pubDict["total"] = 0

    try:
        totals = pubtotals[pubname]
    except KeyError:
        totals = {}
        totals["success"] = 0
        totals["failure"] = 0
        totals["cpusuccess"] = 0
        totals["cpufailure"] = 0

    temp = {"failure": ["Failure", 0], "success": ["Success", 0] }
    try:
        temp['success'] = ['Success', int(totals['success'])]
        pubDict["total"] += int(totals['success'])
    except KeyError:
        temp['success'] = ['Success', 0]
    try:
        temp["failure"] = ['Failure', int(totals['failure'])]
        pubDict["total"] += int(totals['failure'])
    except KeyError:
        temp["failure"] = ['Failure', 0]
    pubDict["data"].append(temp['success'])
    pubDict["data"].append(temp['failure'])

    pubDict["cpudata"]=[]
    temp = {"failure": ["Failure", 0], "success": ["Success", 0] }
    try:
        temp['success'] = ['Success', totals['cpusuccess']]
    except KeyError:
        temp['success'] = ['Success', 0]
    try:
        temp['failure']= ['Failure', totals['cpufailure']]
    except KeyError:
        temp['failure']= ['Failure', 0]
    pubDict["cpudata"].append(temp["success"])
    pubDict["cpudata"].append(temp["failure"])
    return pubDict

#@login_required
def index(request):
    """
    TODO: Docstring for article.

    :request: TODO
    :returns: TODO

    """
    FORMAT="%Y-%m-%d %H:%M:%S"
    PROCTYPES = ["ocr","nlp","cuneiform","fonttype"]
    uri = "mongodb://%s:%s@127.0.0.1/?authMechanism=MONGODB-CR" % (reader_user, reader_password)
    client = pymongo.MongoClient(uri)
    timedb = client.fetching_metrics
    timesdict = {}
    totalsdict = {}
    proctype_dict={}
    rangedict = OrderedDict()

    # fetching plots
    times = ["hour","day","week", "month"]
    for timeframe in times:
        fetchColl = timedb["%s_view" % timeframe]
        docs = fetchColl.find()
        times=[]
        totals=[]
        range={}

        # dicts for proctype data lists
        total={}
        success={}
        failure={}
        cputime={}
        proctype_totals = {}
        proctype_dict[timeframe] = {}

        range["cputime"] = {}
        range["success"]={}
        range["success"]["total"]=0
        range["failure"]={}
        range["failure"]["total"]=0
        i=0

        success={}
        for proctype in PROCTYPES:
            total[proctype] = []
            success[proctype] = []
            failure[proctype] = []
            cputime[proctype] = []
            proctype_totals[proctype]=[]
            proctype_dict[timeframe][proctype] = {}
        for timestamp in docs:
            cputotal = 0
            times.append(timestamp['time'].strftime(FORMAT))
            totals.append(timestamp['total']['fetched'])
            for proctype in PROCTYPES:
                total[proctype].append(timestamp['total'][proctype]['total'])
                success[proctype].append(timestamp['total'][proctype]['success'])
                try:
                    cputotal+=timestamp['total'][proctype]['cpusuccess']
                except KeyError:
                    pass
                try:
                    cputotal+=timestamp['total'][proctype]['cpufailure']
                except KeyError:
                    pass
                cputime[proctype].append(float(cputotal)/3600.0)
            i=i+1

        times = ['times'] + times
        totals = ['totals'] + totals

        # get the "completed in this timeframe" numbers
        range["fetched"] = totals[-1]-totals[1]
        range["cputime"]["total"] = 0
        # for proctype for success/failures
        for proctype in PROCTYPES:
            range["success"][proctype] = int(success[proctype][-1] - success[proctype][0])
            range["failure"][proctype] = int(total[proctype][-1] - success[proctype][-1]) -\
                int(total[proctype][0] - success[proctype][0])
            proctype_totals[proctype] = [proctype] + total[proctype]
            proctype_dict[timeframe][proctype] = proctype_totals[proctype]
            range["success"]["total"] += range["success"][proctype]
            range["failure"]["total"] += range["failure"][proctype]
            if cputime[proctype][0] == 0: # only needed until DB fills in
                ind = next((i for i, x in enumerate(cputime[proctype]) if x), None)
                range["cputime"]["total"] += int(cputime[proctype][-1] - cputime[proctype][ind])
            else:
                range["cputime"]["total"] += int(cputime[proctype][-1] - cputime[proctype][0])

        timesdict[timeframe] = times
        totalsdict[timeframe] = totals
        rangedict[timeframe] = range

    # processing plots
    articlesdb = client.articles
    articles = articlesdb.articles
    pubnames = articles.distinct("pubname")
    procdb = client.processing

    publist=[]
    processings = {}
    total = {}
    total["fetched"] = 0
    for proctype in ["ocr","nlp","cuneiform","fonttype"]:
        total[proctype] = {}
        total[proctype]["total"] = 0
        total[proctype]["data"] = {"success": 0, "failure":0}
        total[proctype]["cpudata"] = {"success": 0, "failure":0}
        processings[proctype] = procdb["%s_processing" % proctype]
    for pub in pubnames:
        pubDict = {}
        pubDict["title"] = pub
        pubDict["nospace"] = re.sub("[^a-zA-Z0-9\n\.]", "_", pub)
        pubDict["fetched"] = articles.find( { "pubname":pub }).count()
        total["fetched"] += pubDict["fetched"]

        for proctype in ["ocr","nlp","cuneiform","fonttype"]:
            pubDict[proctype] = getPubCounts(pub, "elsevier_002", processings[proctype])
            total[proctype]["data"]["success"] += pubDict[proctype]['data'][0][1]
            total[proctype]["data"]["failure"] += pubDict[proctype]['data'][1][1]
            total[proctype]["total"] += pubDict[proctype]["total"]
            total[proctype]["cpudata"]["success"] += pubDict[proctype]['cpudata'][0][1]
            total[proctype]["cpudata"]["failure"] += pubDict[proctype]['cpudata'][1][1]
    client.close()

    fetched_total = totalsdict["hour"][-1]

    context = {
            'times' : timesdict,
            'timeslist': times,
            'totals': totalsdict,
            'proctypedict': proctype_dict,
            'ranges': rangedict,
            'fetched_total': fetched_total,
            'timeframes': [ i for i in timesdict.keys() ],
            'totalOCR': total["ocr"]["data"]["success"],
            'totalNLP': total["nlp"]["data"]["success"],
            'totalCuneiform': total["cuneiform"]["data"]["success"],
            'totalFonttype': total["fonttype"]["data"]["success"],
            }
    return render(request, 'deepdive/index.html', context)

@login_required
def article(request, articleId):
    """
    TODO: Docstring for article.

    :request: TODO
    :returns: TODO

    """
#    article = Article.objects.using('articles').filter( { "_id" : articleId } )
    context = {
            '_id' : articleId,
            }
    return render(request, 'deepdive/article.html', context)
    context = {
            'tag' : tag,
            'test' : publist,
            'total': total,
            }
    return render(request, 'deepdive/tag.html', context)

@login_required
def pub(request, pubpermalink):
    """
    TODO: Docstring for pub.

    :request: TODO
    :pubpermalink: TODO
    :returns: TODO

    """

    uri = "mongodb://%s:%s@127.0.0.1/?authMechanism=MONGODB-CR" % (reader_user, reader_password)
    client = pymongo.MongoClient(uri)
    pubsdb = client.publications_dev
    pubs = pubsdb.publications
    procdb = client.processing
    pubname = pubs.find_one({"_id": pubpermalink})["pubname"]
    articlesdb = client.articles
    articles = articlesdb["articles"]
    pubdict = {}
    pubdict["pubname"] = pubname
    pubdict["fetched"] = articles.find({"pubname": pubname}).count()
    for proctype in ["ocr", "nlp", "cuneiform", "fonttype"]:
        processingColl=procdb["%s_processing" % proctype]
        pubdict[proctype] = getPubCounts(pubname, "elsevier_002", processingColl)["data"]

    articleslist = list(articles.find({"pubname": pubname}).limit(20))
    # todo: probably want to parse things out here, instead of passing the full articles


    client.close()
    context = {
            'pub' : pubdict,
            'articles': articleslist
            }
    return render(request, 'deepdive/pub.html', context)

@login_required
def article(request, articleId):
    """
    TODO: Docstring for article.

    :request: TODO
    :returns: TODO

    """
#    article = Article.objects.using('articles').filter( { "_id" : articleId } )

    uri = "mongodb://%s:%s@127.0.0.1/?authMechanism=MONGODB-CR" % (reader_user, reader_password)
    client = pymongo.MongoClient(uri)
    articlesdb = client.articles_dev
    articles = articlesdb["articles"]
    article = articles.find_one({"_id": ObjectId(articleId)})
    client.close()

    context = {
            '_id' : articleId,
            'article': article,
            }
    return render(request, 'deepdive/article.html', context)

@login_required
def search(request):
#    found_entries = None
    # todo: limit number of results shown
    articlesList=[]
    uri = "mongodb://%s:%s@127.0.0.1/?authMechanism=MONGODB-CR" % (reader_user, reader_password)
    client = pymongo.MongoClient(uri)

    articlesdb = client.articles_dev
    articles = articlesdb["articles"]


    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        cursor = articles.find(
                {'$text':{'$search':query_string}},
                {"contents":0,
                    "ocr_processing":0,
                    "nlp_processing":0,
                    "cuneiform_processing":0,
                    "fonttype_processing":0,
                 'score':{'$meta': 'textScore'}})
        cursor = cursor.sort([('score', {'$meta': 'textScore'})]).limit(50)
        for art in cursor:
            art["id"] = art["_id"]
            articlesList.append(art)

#        db.articles.find({$text:{$search:'Adaville'}}, {contents:0,ocr_processing:0,nlp_processing:0,cuneiform_processing:0,fonttype_processing:0,score:{$meta: 'textScore'}}).sort({score:{$meta:'textScore'}}).pretty().limit(5)
#        found_entries = Article.objects.search(query_string, raw=True)
    return render(request,
            'deepdive/search_results.html',
            { 'query_string': query_string,
                    'found_entries': articlesList, })
