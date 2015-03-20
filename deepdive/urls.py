from django.conf.urls import patterns,url,include
from deepdive import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^article/(?P<articleId>[A-Za-z0-9]+)$', views.article, name='article'),
        url(r'^tag/(?P<proctype>[A-Za-z0-9]+)/(?P<tag>[A-Za-z0-9_]+)$', views.tag_type, name='tag_type'),
        url(r'^tag/(?P<tag>[A-Za-z0-9_]+)$', views.tag, name='tag'),
        url(r'^tag_overview/(?P<tag>[A-Za-z0-9_]+)$', views.tag_overview, name='tag_overview'),
        url(r'^proc/$', views.processingForm, name='processingForm'),
        url(r'^pub/(?P<pubpermalink>[A-Za-z0-0]+)$', views.pub, name='publication'),
        url(r'^search-form/$', views.search_form, name='search'),
        url(r'^search/$', views.search, name='search'),
        url(r'^bundle_testing/$', views.bundlefiles, name='bundle_files'),
        url(r'^test/$', views.test_count_session, name='session_test'),
        )
