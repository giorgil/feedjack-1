# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from feedjack import views


import itertools as it, operator as op, functools as ft
from types import StringTypes, NoneType

specs = dict(feed=('feed', r'\d+'), tag=r'[^/]+')

urljoin = lambda pieces: '/'.join(it.imap(op.methodcaller('strip', '/'), pieces))

def specs_sets(tpl, specs, make_redirects=False):
	if isinstance(specs, dict): specs = specs.items()
	for spec_set in it.chain.from_iterable(
			it.permutations(specs, n) for n in xrange(len(specs), 0, -1) ):
		url = list()
		for spec, pat in spec_set:
			if not isinstance(pat, (StringTypes, NoneType)): pat_spec, pat = pat
			else: pat_spec = spec
			pat = '{0}/(?P<{1}>{2})'.format(spec, pat_spec, pat)\
				if pat is not None else '(?P<{0}>{1})'.format(pat_spec, spec)
			if make_redirects: pat = (pat, '{0}/%({1})s'.format(spec, pat_spec))
			url.append(pat)
		yield tpl.format(urljoin(url)) if not make_redirects else\
			( tpl.format(urljoin(it.imap(op.itemgetter(0), url))),
				urljoin(it.imap(op.itemgetter(1), url)) )


urlpatterns = list()

# New-style syndication links
urlpatterns.extend( (url, views.atomfeed)
	for url in specs_sets('^syndication/atom/{0}/?$', specs) )
urlpatterns.extend( (url, views.rssfeed)
	for url in specs_sets('^syndication/rss/{0}/?$', specs) )
urlpatterns.extend([
	(r'^syndication/atom/?$', views.atomfeed),
	(r'^syndication/rss/?$', views.rssfeed),
	(r'^syndication/opml/?$', views.opml),
	(r'^syndication/foaf/?$', views.foaf) ])

# New-style pages
urlpatterns.extend( (url, views.mainview)
	for url in specs_sets('^{0}/?$', specs) )
# Index page
urlpatterns.append((r'^$', views.mainview))

# Ajax Stuff
urlpatterns.append((r'^mark-post/(?P<post_id>[0-9]*)/(?P<mark>[A-Z])/$', views.mark_post))

#urlpatterns = patterns('', *urlpatterns)
# new django way. TODO: cleanup the creation of the urls
urlpatterns = [url(*x) for x in urlpatterns]
