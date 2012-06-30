Intro (original feedjack).
--------------------

Feedjack is a feed aggregator writen in Python using the Django web development
framework.

Like the Planet feed aggregator:

* It downloads feeds and aggregate their contents in a single site
* The new aggregated site has a feed of its own (atom and rss)
* It uses Mark Pilgrim’s excelent FeedParser
* The subscribers list can be exported as OPML and FOAF

Original FeedJack also has some advantages:

* Handles historical data, you can read old posts
* Parses a lot more info, including post categories
* Generates pages with posts of a certain category
* Generates pages with posts from a certain subscriber
* Generates pages with posts of a certain category from a certain subcriber
* A cloud tag/folksonomy (hype 2.0 compliant) for every page and every
  subscriber
* Uses Django templates
* The administration is done via web (using Django's kickass autogenerated
  and magical admin site), and can handle multiple planets
* Extensive use of django’s internal cache engine. Most of the time you
  will have no database hits when serving pages.

[Original feedjack](http://www.feedjack.org/) project looks abandoned though -
no real updates since 2008 (with quite a lively history before that).

Feedparser itself isn't in much better shape, for that matter - releases weren't
a frequent thing there up to 2011 (svn looked a bit more alive though), but then
Mark Pilgrim pulled out from the internets (4 October 2011), so guess it will
get worse unless someone picks up the development.
It's purpose is fairly simple though and feed formats haven't really changed
since 2005, so it's not so bad yet.
Feel free to update this paragraph if there are now more-or-less mainstream
forks.


Fork
--------------------

* (fixed) Bugs:
  * hashlib warning
  * field lenghts
  * non-unique date sort criteria
  * Always-incorrect date_modified setting (by treating UTC as localtime)
  * Misc unicode handling fixes.

* Features:

  * Proper transactional updates, so single feed failure is guaranteed not to
    produce inconsistency or crash the parser.

  * Simple individual Post filters, built in python (callable, accepting Post
    object and optional parameters, returning True/False), attached (to individual
    Feeds) and configured (additional parameters to pass) via database (or admin
    interface).

  * As complex as needed cross-referencing filters for tasks like site-wide
    elimination of duplicate entries from a different feeds (by arbitrary
    comparison functions as well), and automatic mechanism for invalidation of
    their results.

  * Sane, configurable logging in feedjack_update, without re-inventing the wheel
    via encode, prints and a tons of if's.

  * "immutable" flag for feeds, so their posts won't be re-fetched if their
    content or date changes (for feeds that have "commets: N" thing).

  * Dropped a chunk of obsolete code (ripped from old django) - ObjectPaginator in
    favor of native Paginator.

  * Minimalistic "fern" and "plain" (merged from [another
    fork](http://git.otfbot.org/feedjack.git/)) styles, image feed oriented
    "fern_grid" style.

  * Quite a few code optimizations.
  * ...and there's usually more stuff in the CHANGES file.


Installation
--------------------

This feedjack fork is a regular package for Python 2.7 (not 3.X), but not in
pypi, so can be installed from a checkout with something like that:

	python setup.py install

That will install feedjack to a python site-path, so it can be used as a django
app.

Note that to install stuff in system-wide PATH and site-packages, elevated
privileges are often required.
Use
[~/.pydistutils.cfg](http://docs.python.org/install/index.html#distutils-configuration-files)
or [virtualenv](http://pypi.python.org/pypi/virtualenv) to do unprivileged
installs into custom paths.

Better way would be to use [pip](http://pip-installer.org/) to install all the
necessary dependencies as well:

	% pip install -e 'git://github.com/mk-fg/feedjack.git#egg=feedjack'

After that you must set up your Feedjack static directory inside your Django
[STATIC_URL](http://docs.djangoproject.com/en/dev/ref/settings/#static-url)
directory.
It must be set in a way that Feedjack’s static directory can be reached at
"STATIC_URL/feedjack/".

For instance, if your STATIC_URL resolves to /var/www, and Feedjack was installed
in /usr/lib/python2.7/site-packages/feedjack, just type this:

    ln -s /usr/lib/python2.7/site-packages/feedjack/static/feedjack /var/www/feedjack

Alternatively, standard
[django.contrib.staticfiles](https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/)
app [can be used to copy/link static
files](https://docs.djangoproject.com/en/dev/howto/static-files/) with
"django-admin.py collectstatic" command.

You must also add 'feedjack' in your settings.py under
[INSTALLED_APPS](http://docs.djangoproject.com/en/dev/ref/settings/#installed-apps)
and then [manage.py
syncdb](http://docs.djangoproject.com/en/dev/ref/django-admin/#syncdb) from the
command line.

Then you must add an entry in your Django "urls.py" file.
Just include feedjack.urls like this:

    urlpatterns = patterns( '',
      (r'^admin/', include('django.contrib.admin.urls')),
      (r'', include('feedjack.urls')) )

After that you might want to check out /admin section to create a feedjack site,
otherwise sample default site will be created for you on the first entry.


### Requirements

* [Python 2.7](python.org)
* [Feedparser 4.1+](feedparser.org)
* [Django 1.1+](djangoproject.com)
* (optional) [lxml](http://lxml.de) - used for html mangling in some themes (fern, plain)


### Update from older versions

The only non-backwards-compatible changes should be in the database schema and
are documented in
[CHANGES_DATABASE](https://raw.github.com/mk-fg/feedjack/master/CHANGES_DATABASE)
file.



Configuration
--------------------

The first thing you want to do is add a Site. To do this just open the admin
site and create your first planet. You must use a valid address in the URL
field, since it will be used to identify the current planet when there are
multiple planets in the same instance, and to generate all the links.

Now you must add subscribers to your first planet. A subscriber is a relation
between a Feed and a Site, so when you add your first subscriber, you must also
add your first Feed by clicking in the “+” button at the right of the Feed
combobox.

Feedjack has been designed to use Django’s internal cache engine to store
database intensive data like that tagclouds, so it is highly recomended that you
configure a CACHES or CACHE_BACKEND in your Django settings (memcached, db or
file).

Now that you have everything set up, just run the feedjack_update.py script to
retrieve the data from the feeds and that’s all. Note that you must have a
memcached, db or file CACHES in order to see the updated feeds immediately.

See [django project
documentation](http://docs.djangoproject.com/en/dev/topics/cache/#setting-up-the-cache)
for more info.


Bugs, development, support
--------------------

All the issues with this fork should probably be reported to respective github
project/fork, since code here can be quite different from the original project.

Until 2012, fork was kept in [fossil](http://www.fossil-scm.org/) repo
[here](http://fraggod.net/code/fossil/feedjack/).

Original version is available at [feedjack site](http://www.feedjack.org/).


Links
--------------------

* Other known non-github forks
  * http://git.otfbot.org/feedjack.git/
  * http://code.google.com/p/feedjack-extension/
