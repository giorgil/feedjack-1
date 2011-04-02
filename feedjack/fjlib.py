# -*- coding: utf-8 -*-


from django.conf import settings
from django.db import connection
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.utils.encoding import smart_unicode, force_unicode

from feedjack import models
from feedjack import fjcache

import itertools as it, operator as op, functools as ft
from datetime import datetime
from urllib import quote


_xml_c0ctl_chars = bytearray(
	set(it.imap(chr, xrange(32)))\
		.difference('\x09\x0a\x0d').union('\x7f'))
_xml_c0ctl_trans = dict(it.izip(
	_xml_c0ctl_chars, u'_'*len(_xml_c0ctl_chars) ))

def c0ctl_escape(string):
	'Produces template-safe valid xml-escaped string.'
	return force_unicode(string).translate(_xml_c0ctl_trans)


def getquery(query):
	'Performs a query and get the results.'
	try:
		conn = connection.cursor()
		conn.execute(query)
		data = conn.fetchall()
		conn.close()
	except: data = list()
	return data


def get_extra_content(site, ctx):
	'Returns extra data useful to the templates.'
	# get the subscribers' feeds
	feeds = site.active_feeds
	ctx['feeds'] = feeds.order_by('name')
	# get the last_modified/checked time
	mod, chk = op.itemgetter('modified', 'checked')(feeds.timestamps)
	chk = chk or datetime(1970, 1, 1)
	ctx['last_modified'], ctx['last_checked'] = mod or chk, chk
	ctx['site'] = site
	ctx['media_url'] = '{0}feedjack/{1}'.format(settings.MEDIA_URL, site.template)


def get_posts_tags(subscribers, object_list, feed_id, tag_name):
	'''Adds a qtags property in every post object in a page.
		Use "qtags" instead of "tags" in templates to avoid unnecesary DB hits.'''

	tagd = dict()
	user_obj = None
	tag_obj = None
	tags = models.Tag.objects.extra(
	  select=dict(post_id='{0}.{1}'.format(
			*it.imap( connection.ops.quote_name,
				('feedjack_post_tags', 'post_id') ) )),
	  tables=['feedjack_post_tags'],
	  where=[
		'{0}.{1}={2}.{3}'.format(*it.imap( connection.ops.quote_name,
			('feedjack_tag', 'id', 'feedjack_post_tags', 'tag_id') )),
		'{0}.{1} IN ({2})'.format(
		  connection.ops.quote_name('feedjack_post_tags'),
		  connection.ops.quote_name('post_id'),
		  ', '.join([str(post.id) for post in object_list]) ) ] )

	for tag in tags:
		if tag.post_id not in tagd: tagd[tag.post_id] = list()
		tagd[tag.post_id].append(tag)
		if tag_name and tag.name == tag_name: tag_obj = tag

	subd = dict()
	for sub in subscribers: subd[sub.feed.id] = sub
	for post in object_list:
		if post.id in tagd: post.qtags = tagd[post.id]
		else: post.qtags = list()
		post.subscriber = subd[post.feed.id]
		if feed_id and feed_id == post.feed.id: user_obj = post.subscriber

	return user_obj, tag_obj


def get_page(site, page=1, tag=None, feed=None):
	'Returns a paginator object and a requested page from it.'

	posts = models.Post.objects.filtered(site, feed=feed, tag=tag)\
		.sorted(site.order_posts_by).select_related()

	paginator = Paginator(posts, site.posts_per_page)
	try: return paginator.page(page)
	except InvalidPage: raise Http404


def page_context(request, site, tag=None, feed_id=None):
	'Returns the context dictionary for a page view.'
	try: page = int(request.GET.get('page', 1))
	except ValueError: page = 1

	page = get_page(site, page=page, tag=tag, feed=feed_id)
	subscribers = site.active_subscribers

	if site.show_tagcloud and page.object_list:
		from feedjack import fjcloud
		# This will hit the DB once per page instead of once for every post in
		# a page. To take advantage of this the template designer must call
		# the qtags property in every item, instead of the default tags
		# property.
		user_obj, tag_obj = get_posts_tags(subscribers, page.object_list, feed_id, tag)
		tag_cloud = fjcloud.getcloud(site, feed_id)
	else:
		from django.core.exceptions import ObjectDoesNotExist
		tag_obj, tag_cloud = None, tuple()
		try:
			user_obj = models.Subscriber.objects\
				.get(site=site, feed=feed_id) if feed_id else None
		except ObjectDoesNotExist: raise Http404


	ctx = dict(
		object_list = page.object_list,
		is_paginated = page.paginator.num_pages > 1,
		results_per_page = site.posts_per_page,
		has_next = page.has_next(),
		has_previous = page.has_previous(),
		page = page.number,
		next = page.number + 1,
		previous = page.number - 1,
		pages = page.paginator.num_pages,
		hits = page.paginator.count,
		last_modified = max(it.imap(
				op.attrgetter('date_updated'), page.object_list ))\
			if len(page.object_list) else datetime(1970, 1, 1) )

	get_extra_content(site, ctx)
	ctx['tagcloud'] = tag_cloud
	ctx['tag'] = tag_obj
	ctx['subscribers'] = subscribers

	# New
	ctx['feed'] = models.Feed.objects.get(id=feed_id) if feed_id else None
	ctx['url_suffix'] = ''.join((
		'/feed/{0}'.format(feed_id) if feed_id else '',
		'/tag/{0}'.format(quote(tag)) if tag else '' ))

	# Deprecated
	ctx['user_id'] = feed_id # totally misnamed and inconsistent with user_obj
	ctx['user'] = user_obj

	return ctx
