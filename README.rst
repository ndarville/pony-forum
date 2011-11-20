Django on DotCloud
==================

This code shows how to run a very simple Django application on DotCloud.
It is fully functional, in the sense that you don't have any hand-editing
to do to deploy it: it automatically deploys a PostgreSQL database,
includes it in ``settings.py``, creates a superuser for you, and uses
Django 1.3 ``collectstatic``. *Batteries Included!*

To run this code on DotCloud, you need a `DotCloud account
<https://www.dotcloud.com/accounts/register/>`_ (free tier available).
Then clone this repository, and push it to DotCloud::

  $ git clone git://github.com/jpetazzo/django.git
  $ cd django
  $ dotcloud push hellodjango

Happy hacking! Remember: each time you modify something, you need to
git add + git commit your changes before doing ``dotcloud push``.

This repository is also a step-by-step tutorial: each commit corresponds
to one step, with the commit message providing explanations. 

You can view the whole tutorial, and the modified files at each step,
with at least three different methods:

* by using GitHub's awesome `compare view
  <https://github.com/jpetazzo/django/compare/begin...end>`_:
  you will see the list of commits involved in the tutorial, and by
  clicking on each individual commit, you will see the file modifications
  for this step;
* by running ``git log --patch --reverse begin..end`` in your local
  repository, for a text-mode equivalent (with the added benefit of being
  available offline!);
* by browsing a more `traditional version 
  <http://docs.dotcloud.com/tutorials/python/django/>`_ on DotCloud's
  documentation website.

You can also learn more by diving into `DotCloud documentations
<http://docs.dotcloud.com/>`_, especially the one for the `Python service
<http://docs.dotcloud.com/services/python/>`_ which is used by this app.

