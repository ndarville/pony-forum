from markdown                       import markdown
from smartypants                    import smartyPants as smartypants
import bleach
import datetime
import json
import os

# cf. http://meta.osqa.net/question/9722
from django.conf                    import settings as project_settings
from django.contrib                 import messages, auth
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.models     import User
from django.contrib.auth.views      import login
from django.contrib.sites.models    import Site
from django.core.paginator          import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers       import reverse
from django.db.utils                import DatabaseError
from django.http                    import HttpResponse, HttpResponseRedirect
from django.shortcuts               import render, get_object_or_404

from forum.models                   import Category, Post, Report,\
                                           Subscription, Thread, UserProfile
from forum.forms                    import CustomRegistrationForm
from registration                   import views as registration_views


#   views.py TOC:
#
#
##  helper constants
##  helper errors
##  helper functions
#
##  home
#
##  subscriptions
#
##  category
##  thread
##  post
#
##  user
##  user_content
#
##  add
##  create
##  reply
##  edit
#
##  moderate_thread
##  merge_thread
##  move_thread
##  remove
##  report
##  reports
#
##  pm
#
##  custom_login
##  custom_logout
##  custom_register
##  settings
#
##  site_configuration
#
##  saves_and_bookmarks
#
##  simple_js
##  nonjs
##      subscribe
##      bookmark
##      lock
##      sticky
##      save
##      thank
##      agree


MAX_THREAD_TITLE_LENGTH   = Thread._meta.get_field("title_plain").max_length
MAX_CATEGORY_TITLE_LENGTH = Category._meta.get_field("title_plain").max_length
POSTS_PER_PAGE            = getattr(project_settings, "POSTS_PER_PAGE", 25)
THREADS_PER_PAGE          = getattr(project_settings, "THREADS_PER_PAGE", 25)
USER_POSTS_PER_PAGE       = getattr(project_settings, "USER_CONTENT_PER_PAGE", 10)
USER_THREADS_PER_PAGE     = getattr(project_settings, "USER_CONTENT_PER_PAGE", 25)
BOOKMARKS_PER_PAGE        = getattr(project_settings, "BOOKMARKS_PER_PAGE", 35)
SAVES_PER_PAGE            = getattr(project_settings, "SAVES_PER_PAGE", 10)
SUBSCRIPTIONS_PER_PAGE    = getattr(project_settings, "SUBSCRIPTIONS_PER_PAGE", 25)


long_title_error  = "Your chosen title was too long. Keep it under %i characters."
operational_error = """
<p><strong>Mumbo jumbo:</strong> Django threw an \
<code>OperationalError</code> exception.</p>

<p><strong>English:</strong> Either: \
You used characters not supported by the database.</p>

<p>Or: The forum&rsquo;s database is having an aneurysm.</p>

<p>Regardless: This should not happen, so notify your admin. \
S/he might want to contact the site&rsquo;s host in return.</p>

<p>These three links will help you get to the bottom of this:</p>

<ul>
    <li><a href="http://groups.google.com/group/django-users/\
    browse_thread/thread/429447086fca6412?pli=1">\
    Django users discussion</a></li>
    <li><a href="https://docs.djangoproject.com/en/dev/ref/unicode/">\
    Django docs</a></li>
    <li><a href="http://rentzsch.tumblr.com/post/9133498042/\
    howto-use-utf-8-throughout-your-web-stack">\
    How-To guide</a></li>
</ul>
"""
post_request_error = "An unidentified error occured. Please try again."
submit_error = "An unidentified error occured during submission. Save your work and try again."


def paginate(request, items, num_items):
    """Create and return a paginator."""
    paginator = Paginator(items, num_items)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        items = paginator.page(page)
    except (InvalidPage, EmptyPage):
        items = paginator.page(paginator.num_pages)

    return items


def prettify_title(title):
    """Sanitizes all (ALL) HTML elements in titles while prettifying the quotes
    and dashes used in the titles of threads and categories.
    """
    return bleach.clean(
        smartypants(title, "2"),
        tags=[], attributes={})


def sanitized_smartdown(string):
    """Formats a piece of text with SmartyPants, Markdown
    and all the specified Markdown extensions. It also
    escapes (or sanitizes) all HTML elements that are not explicitly
    whitelisted in the `bleach.clean()` function.

    Returns:
        A reformatted string parsed by markdown() and smartdown() and
        sanitized by bleach.clean().

    Args:
        `bleach.clean()` takes a string and purges all tags, attributes, and
        styles that are not whitelisted to be escaped.

        These are defined in ALLOWED_TAGS, ALLOWED_ATTRIBUTES, and ..._STYLES
        respectively---the two former of which are defined explicitly
        in this code for better management and extension.

        Read more about `bleach` at https://github.com/jsocol/bleach.

        `markdown()` takes a string and an optional list argument containing
        all the extensions to be used with it.

        `smartypants()` takes a string to be formatted.

    NB (SmartyPants and Quotes):
        For non-English-language boards, the SmartyPants quotes may
        be different from how they are used in your country (e.g. France).

    NB (Bleach and Encoding):
        Bleach always returns a unicode object, whether you give it a
        bytestring or a unicode object, but Bleach does not attempt to detect
        incoming character encodings, and will assume UTF-8.

        If you are using a different character encoding, you should convert
        from a bytestring to unicode before passing the text to Bleach.
    """
    ALLOWED_TAGS = [
        'a',
        'abbr',
        'acronym',
        'blockquote',
        'code',
        'del',
        'em',
        'h1',
        'h2',
        'h3',
        'h4',
        'h5',
        'i',
        'img',
        'ins',
        'li',
        'ol',
        'p',
        'pre',
        'strong',
        'sub',
        'sup',
        'ul',
    # Tables:
        'table',
        'caption',
        'thead',
        'tbody',
        'tfoot',
        'tr',
        'th',
        'td'
    ]

    ALLOWED_ATTRIBUTES = {
        'a':       ['href', 'title'],
        'acronym': ['title'],
        'abbr':    ['title'],
        'h1':      ['id'],
        'h2':      ['id'],
        'h3':      ['id'],
        'h4':      ['id'],
        'h5':      ['id'],
        'img':     ['alt', 'id', 'src', 'title'],
        'th':      ['colspan', 'rowspan'],
        'td':      ['colspan', 'rowspan']
    }

    MD_EXTENSIONS = [
        'attr_list',
        'fenced_code',
        'tables'
    ]

    return bleach.clean(
        smartypants(
            markdown(
                text=string,
                extensions=MD_EXTENSIONS,
                #output_format='html5',
                #lazy_ol=True,
                safe_mode=False),
            "2"),
        tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)


def home(request):
    """The landing page displaying categories, new and popular threads
    as well as unread threads the user has subscribed to.
    """
    subscribed_threads = False
    categories  = Category.objects.all()
    threads     = Thread.objects.exclude(is_removed__exact=True)
    new_threads = threads[:5]
    site        = Site.objects.get_current()

    if not request.user.is_anonymous() and request.user.subscriptions.all():
        subscribed_threads = threads.filter(subscriber__exact=request.user)[:5]

    # updates = request.user.subscription_set.all()
    # update.last_read < update.thread.latest_reply_date
    ## or update.last_read == None  # (or something)
    # link to newest post
    # number of new posts

    site_config_error, email_config_error = False, False
    if request.user.is_staff:
        if site.domain == "example.com" or site.name == "example.com":
            site_config_error = True
        if project_settings.EMAIL_HOST_USER == "myusername@gmail.com":
            email_config_error = True

    return render(request, 'home.html',
                  {'categories':         categories,
                   'new_threads':        new_threads,
                   'subs':               subscribed_threads,
                   'site_config_error':  site_config_error,
                   'email_config_error': email_config_error})


@login_required()
def subscriptions(request):
    """Manage and observe all your subscriptions to threads with new posts."""
    threads       = Thread.objects.exclude(is_removed__exact=True)
    new_threads   = threads[:5]

    objects       = threads.filter(subscriber__exact=request.user)
    new_subs      = objects[:5]
  # unread_subs   = Replace news_subs with this one
    objects       = paginate(request, objects, SUBSCRIPTIONS_PER_PAGE)

    return render(request, 'subscriptions.html',
                  {'new_threads': new_threads,
                   'new_subs':    new_subs,
                   'objects':     objects})


def category(request, category_id):
    """Category with threads ordered by latest posts."""
    category         = get_object_or_404(Category, pk=category_id)
    all_threads      = category.thread_set.all()
    category_threads = all_threads.order_by("-latest_reply_date")\
                       .exclude(is_sticky__exact=True)
#                       .only("latest_reply_date")
    category_threads = paginate(request, category_threads, THREADS_PER_PAGE)
    stickies         = all_threads.exclude(is_sticky__exact=False)

    return render(request, 'category.html',
                  {'category':         category,
                   'category_threads': category_threads,
                   'stickies':         stickies})


def thread(request, thread_id, author_id):
    """Thread with all the belonging posts."""
    thread = get_object_or_404(Thread, pk=thread_id)

    if not thread.is_removed or request.user.has_perm('forum.remove_thread'):
        posts = thread.post_set.all().select_related()

        if not request.user.has_perm('forum.remove_thread') or not request.user.has_perm('forum.remove_post'):
            posts     = posts.exclude(is_removed__exact=True)
        if author_id != "Everyone":  # User has specified an author(_id)
            posts     = posts.filter(author__exact=author_id)

        posts = posts.exclude(is_removed__exact=True)\
                .order_by("creation_date")
        posts = paginate(request, posts, POSTS_PER_PAGE)
#        anchor_number = forloop.counter
        anchor_number = '???'

        return render(request, 'thread.html',
                      {'thread_id':     thread_id,
                       'thread':        thread,
                       'posts':         posts,
                       'anchor_number': anchor_number})
    else:
        messages.info(request, "The thread %s has been removed and no longer available." % thread.title_html)
        return HttpResponseRedirect(reverse('forum.views.category', args=(thread.category_id,)))


def post(request, post_id):
    """View a single post object."""
    post = get_object_or_404(Post.objects.select_related(), pk=post_id)
    thread = post.thread

    if request.user.has_perm('forum.remove_thread') or not thread.is_removed:
        if (not post.is_removed or
                request.user.has_perm('forum.remove_thread') or
                request.user.has_perm('forum.remove_post')):
            return render(request, 'post.html', {'post': post, 'thread': thread})
        else:
            messages.info(request, "The post by %s has been removed and no longer available." % post.author)
            return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))
    else:
        messages.info(request, "The thread %s has been removed and no longer available." % thread.title_html)
        return HttpResponseRedirect(reverse('forum.views.category', args=(thread.category_id,)))


def user(request, user_id):
    """Shows another user's profile.

    Uses the `person` variable to disambiguate from `user`,
    which is used in templates for the user viewing a page.

    `latest_posts_amount` determines the amount of latest posts to show.
    """
    person = get_object_or_404(User, pk=user_id)
    posts  = person.post_set.all().select_related()\
             .exclude(is_removed__exact=True)\
             .exclude(thread__is_removed__exact=True)\
             .order_by("-creation_date")[:10]
    return render(request, 'user.html', {'person': person, 'posts': posts})


def user_content(request, user_id, object_type):
    """Shows all posts or threads by specific user."""
    person = get_object_or_404(User, pk=user_id)

    if object_type == "post":
        objects    = person.post_set.all().select_related()\
                     .exclude(thread__is_removed__exact=True)
        USER_CONTENT_PER_PAGE = USER_POSTS_PER_PAGE
    else:  #   ... == "thread"
        objects    = person.thread_set.all()\
                     .exclude(is_removed__exact=True)
        USER_CONTENT_PER_PAGE = USER_THREADS_PER_PAGE
    objects = objects.order_by("-creation_date")
    objects = paginate(request, objects, USER_CONTENT_PER_PAGE)

    return render(request, 'user_content.html',
                  {'type':    object_type,
                   'person':  person,
                   'objects': objects})


@permission_required('forum.add_category')
def add(request):
    """Add a new category."""
    title_plain = False

    if request.method == 'POST':  # Form has been submitted
        title_plain = request.POST['title']
        title_html  = prettify_title(title_plain)
        if len(title_plain) > MAX_CATEGORY_TITLE_LENGTH:
            messages.error(request, long_title_error % MAX_CATEGORY_TITLE_LENGTH)
        else:
            try:
                Category.objects.create(title_plain=title_plain, title_html=title_html)
            except:
                messages.error(request, post_request_error)
            else:
                return HttpResponseRedirect("/")

    return render(request, 'add.html', {'title': title_plain})


@login_required()
def create(request, category_id):
    """Creation of a new thread from a category id.

    Shows a preview of the thread, if the user pressed
    the 'Preview' button instead of 'Reply'.
    """
    category       = get_object_or_404(Category, pk=category_id)
    preview_plain  = False
    preview_html   = False
    title_plain    = False

    if request.method == 'POST':  # Form has been submitted
        title_plain = request.POST['title']
        title_html  = prettify_title(title_plain)
        text_plain  = request.POST['content']
        if "submit" in request.POST:  # "submit" button pressed
            if len(title_plain) > MAX_THREAD_TITLE_LENGTH:
                messages.error(request, long_title_error % MAX_THREAD_TITLE_LENGTH)
                preview_plain = text_plain
                preview_html  = sanitized_smartdown(text_plain)
            else:
                user      = request.user
                now       = datetime.datetime.now()  # UTC?
                text_html = sanitized_smartdown(text_plain)
                try:
                    t = Thread.objects.create(
                        title_plain=title_plain, title_html=title_html,
                        author=user, category=category,
                        creation_date=now, latest_reply_date=now)
                    Post.objects.create(
                        thread=t, creation_date=now, author=user,
                        content_plain=text_plain, content_html=text_html)
                    t.subscriber.add(user)
                except:
                    messages.error(request, submit_error)
                    preview_plain = text_plain
                    preview_html  = text_html
                else:  # After successful submission
                    category.thread_count += 1
                    category.post_count += 1
                    t.post_count += 1
                    request.user.get_profile().thread_count += 1
                    request.user.get_profile().post_count += 1
                    category.save()
                    t.save()
                    request.user.get_profile().save()

                    return HttpResponseRedirect(reverse('forum.views.thread', args=(t.id,)))
        elif "preview" in request.POST:  # "preview" button pressed
            preview_plain = text_plain
            preview_html  = sanitized_smartdown(text_plain)

    return render(request, 'create.html',
                  {'category':      category,
                   'title':         title_plain,
                   'preview_plain': preview_plain,
                   'preview_html':  preview_html})


@login_required()
def reply(request, thread_id):
    """Grabs the contents of the <textarea> in the reply,
    gets the author id, slaps on the time stamp,
    and creates the post.

    Shows a preview of the post, if the user pressed
    the 'Preview' button instead of 'Reply'.
    """
    thread        = get_object_or_404(Thread, pk=thread_id)
    preview_plain = False
    preview_html  = False

    if thread.is_locked:
        messages.info(request, "The thread %s has been locked and can not be posted in." % thread.title_html)
        return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))
    elif thread.is_removed:
        messages.info(request, "The thread %s has been removed and is no longer available." % thread.title_html)
        return HttpResponseRedirect(reverse('forum.views.category', args=(thread.category_id,)))

    if request.method == 'POST':  # Form been submitted
        text = request.POST['content']
        if "submit" in request.POST:  # "submit" button pressed
            user = request.user
            now  = datetime.datetime.now()  # UTC?
            html = sanitized_smartdown(text)
            try:
                Post.objects.create(
                    thread=thread, author=user, creation_date=now,
                    content_plain=text, content_html=html)
            except:
                messages.error(request, submit_error)
                preview_plain = text
                preview_html = html
            else:
                if request.user.get_profile().auto_subscribe:
                    thread.subscriber.add(request.user)
                thread.latest_reply_date = now

                thread.category.post_count += 1
                thread.post_count += 1
                request.user.get_profile().post_count += 1
                thread.category.save()
                thread.save()
                request.user.get_profile().save()

                return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))

        elif "preview" in request.POST:  # "preview" button pressed
            preview_plain = text
            preview_html  = sanitized_smartdown(text)

    return render(request, 'reply.html',
                  {'thread':        thread,
                   'preview_plain': preview_plain,
                   'preview_html':  preview_html})


@login_required()
def edit(request, post_id):
    """Lets the author edit his or her post."""
    post          = get_object_or_404(Post, pk=post_id)
    preview_plain = False
    preview_html  = False

    if post.thread.is_removed:
        messages.info(request, "The thread %s has been removed and is no longer available." % post.thread.title_html)
        return HttpResponseRedirect(reverse('forum.views.category', args=(post.thread.category_id,)))
    elif post.is_removed:
        messages.info(request, "Your post has been removed and is no longer available.")
        return HttpResponseRedirect(reverse('forum.views.thread', args=(post.thread_id,)))

    if request.method == 'POST':  # Form has been submitted
        if "submit" in request.POST:  # "submit" button pressed
            try:
                post.content_plain = request.POST['content']
                post.content_html  = sanitized_smartdown(post.content_plain)
                post.save()
            except:
                messages.error(request, submit_error)
                preview_plain = request.POST['content']
                preview_html = sanitized_smartdown(preview_plain)
            else:
                return HttpResponseRedirect(reverse('forum.views.thread', args=(post.thread_id,)))
        elif "preview" in request.POST:  # "preview" button pressed
            preview_plain = request.POST['content']
            preview_html  = sanitized_smartdown(preview_plain)
    # The post author or a moderator/admin visits the link
    elif request.user == post.author or request.user.has_perm('forum.change_post'):
        pass
    else:  # Someone who is not the author goes to the edit link
        return HttpResponseRedirect(reverse('forum.views.post', args=(post.id,)))

    return render(request, 'edit.html',
                  {'post':          post,
                   'preview_plain': preview_plain,
                   'preview_html':  preview_html})


@permission_required('forum.merge_thread')
def merge_thread(request, thread_id):
    """Merge the posts of two threads into one single thread.

    1. The posts are ordered chronologically in the new thread.
    2. The old threads are locked.
    3. A notification post is created in all three threads.
    """
    thread          = get_object_or_404(Thread, pk=thread_id)
    new_title_plain = thread.title_plain
    new_title_html  = thread.title_html
    other_thread    = False

    if request.method == 'POST' and "cancel" not in request.POST:
        other_thread    = get_object_or_404(Thread, pk=request.POST['other-thread-id'])  # try --- fix
        new_title_plain = request.POST['new-thread-title']
        new_title_html  = prettify_title(new_title_plain)

        if request.method == 'POST' and "merge" in request.POST:
            if len(new_title_plain) > MAX_THREAD_TITLE_LENGTH:
                messages.error(request, long_title_error % MAX_THREAD_TITLE_LENGTH)

        elif request.method == 'POST' and "confirm" in request.POST:
            now  = datetime.datetime.now()  # UTC?
            user = request.user
            try:
                t = Thread.objects.create(
                    title_plain=new_title_plain, title_html=new_title_html,
                    creation_date=now, author=user, category=thread.category,
                    latest_reply_date=now)
            # Update posts in two threads to point to new thread t
                thread.post_set.all().update(thread=t.id)
                other_thread.post_set.all().update(thread=t.id)
            # Make post notification in ALL threads
                # Do not append a redundant full stop
                if  new_title_plain[-1]    not in set([".!?"]) \
                and new_title_plain[-3:-1] not in set(['."', '!"', '?"', ".'", "!'", "?'"]):
                    end = "."
                else:
                    end = ""
                message = "(*%s* was merged with *%s* by *%s* into *[%s](%s)*%s)" % (
                    thread.title_html,
                    other_thread.title_html,
                    user.username,
                    new_title_html,
                    reverse('forum.views.thread', args=(t.id,)),
                    end)
                html = sanitized_smartdown(message)
                Post.objects.bulk_create([
                    Post(creation_date=now, author=user, thread=t,
                         content_plain=message, content_html=html),
                    Post(creation_date=now, author=user, thread=thread,
                         content_plain=message, content_html=html),
                    Post(creation_date=now, author=user, thread=other_thread,
                         content_plain=message, content_html=html)
                ])
            # Lock original threads
                thread.is_locked       = True
                other_thread.is_locked = True
                thread.save()
                other_thread.save()
            except:
                messages.errors(request, post_request_error)
            else:
                return HttpResponseRedirect(reverse('forum.views.thread', args=(t.id,)))

    return render(request, 'merge.html',
                  {'thread':       thread,
                   'other_thread': other_thread,
                   'new_title':    new_title_plain})


@permission_required('forum.change_thread')
def moderate_thread(request, thread_id):
    """Change the title of a thread."""
    thread      = get_object_or_404(Thread, pk=thread_id)
    title_plain = thread.title_plain

    if request.method == 'POST':  # Form has been submitted
        title_plain = request.POST['title']
        if len(title_plain) > MAX_THREAD_TITLE_LENGTH:
            messages.error(request, long_title_error % MAX_THREAD_TITLE_LENGTH)
        else:
            try:
                thread.title_plain = title_plain
                thread.title_html  = prettify_title(title_plain)
                thread.save()
            except:
                messages.error(request, submit_error)
            else:
                return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))
    return render(request, 'moderate.html',
                  {'thread': thread,
                   'title':  title_plain})


@permission_required('forum.move_thread')
def move_thread(request, thread_id):
    """Move a thread to another category."""
    thread     = get_object_or_404(Thread, pk=thread_id)
    categories = Category.objects.all()

    if request.method == 'POST':  # Form has been submitted
        try:
            thread.category = get_object_or_404(Category, pk=request.POST['category'])
            thread.save()
        except:
            messages.error(request, post_request_error)
        else:
            return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))
    # Form has yet to be submitted, or an error occurred during submission
    return render(request, 'move.html',
                  {'thread':     thread,
                   'categories': categories})


@login_required()
def remove(request, object_id, object_type):
    """Lets the permitted user remove a post or thread.

    A database deletion is not performed upon removal;
    the post or thread is merely hidden in the template.

    An actual deletion has to be done manually in the admin settings or Django shell.
    """
    if object_type == "post":
        obj      = get_object_or_404(Post, pk=object_id)
        thread   = obj.thread
        post_obj = obj
        if not request.user.has_perm('forum.remove_post'):
            return HttpResponseRedirect(reverse('forum.views.post', args=(obj.id,)))
    else:  # ... == thread
        obj      = get_object_or_404(Thread, pk=object_id)
        thread   = obj
        post_obj = None
        if not request.user.has_perm('forum.remove_thread'):
            return HttpResponseRedirect(reverse('forum.views.thread', args=(obj.id,)))

    if request.method == 'POST':  # Form has been submitted
        try:
            if 'remove' in request.POST:  # Remove command
                if obj.is_removed:
                    messages.info(request, "The %s was already removed." % object_type)
                obj.is_removed = True
            else:  # Restore command
                if not obj.is_removed:
                    messages.info(request, "The %s was already not removed." % object_type)
                obj.is_removed = False
            obj.save()
        except:
            messages.error(request, post_request_error)
        else:
            return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))

    return render(request, 'simple_action.html',
                  {'object_type': object_type,
                   'obj':         obj,
                   'thread':      thread,
                   'post_obj':    post_obj,
                   'action':     'remove'})


@login_required()
def report(request, object_id, object_type):
    """Report a post or thread infraction to the moderators."""
    title        = False
    preview_html = False

    if object_type == "thread":
        obj      = get_object_or_404(Thread, pk=object_id)
        thread   = obj
        post_obj = None
    # Check for reasons not to let the user file a report
        if obj.is_removed:
            messages.info(request, "The thread %s has been removed and is no longer available." % thread.title_html)
            return HttpResponseRedirect(reverse('forum.views.category', args=(thread.category_id,)))
        elif thread.is_locked:
            messages.info(request, "The thread %s has been locked and can not be reported." % thread.title_html)
        # Thread already reported AND unaddressed by moderator
        elif Report.objects.filter(author__exact=request.user)\
                           .filter(thread__exact=obj)\
                           .filter(was_addressed__exact=False):
            messages.info(request, "This %s has already been reported by you." % object_type)
            return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))
    else:  # ... == post
        obj      = get_object_or_404(Post, pk=object_id)
        thread   = obj.thread
        post_obj = obj
    # Check for reasons not to let the user file a report
        if obj.is_removed:
            messages.info(request, "The post has been removed and is no longer available.")
            return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))
        elif request.user == obj.author:
            messages.error(request, "You cannot report your own posts, silly goose.")
            return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))
        elif obj.author.is_staff:
            messages.info(request, "The author of the reported post is an admin. \
            You should contact them directly, if you take issue with their content.")
            return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))
        # Post already reported by user
        elif Report.objects.filter(author__exact=request.user)\
                           .filter(post__exact=obj):
            messages.info(request, "This %s has already been reported by you." % object_type)
            return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))

    if request.method == 'POST':  # Form has been submitted
        title = request.POST['title']
        if "content" in request.POST:  # Elaboration provided
            text_plain = request.POST['content']
            text_html  = sanitized_smartdown(text_plain)
        if "submit" in request.POST:  # "submit" button pressed
            if len(title) > MAX_THREAD_TITLE_LENGTH:
                messages.error(request, long_title_error % MAX_THREAD_TITLE_LENGTH)
                preview_html = text_html  # buggy if no content?
            else:
                user = request.user
                now  = datetime.datetime.now()  # UTC?
                try:
                    r = Report.objects.create(
                        creation_date=now, author=user,
                        reason_short=title, thread=thread)
                    if "content" in request.POST:
                        r.reason_long_plain = text_plain
                        r.reason_long_html  = text_html
                    if object_type == "post":
                        r.post = obj
                    r.save()
                except:
                    messages.error(request, submit_error)
                    preview_html = text_html
                else:
                    # After successful submission
                    return HttpResponseRedirect(reverse('forum.views.thread',
                                                        args=(thread.id,)))
        elif "preview" in request.POST:  # "preview" button pressed
            preview_html = text_html  # buggy if no content?
    return render(request, 'report.html',
                  {'obj':          obj,
                   'type':         object_type,
                   'thread':       thread,
                   'post_obj':     post_obj,
                   'title':        title,
                   'preview_html': preview_html})


@permission_required('forum.use_report')
def reports(request):
    """Inspect and act on filed reports on threads and posts."""
# Hide reports that have been addressed
    reports = Report.objects.filter(was_addressed__exact=False)
    reports = reports.order_by("creation_date")
    reports = reports.order_by("thread")

    if request.method == 'POST':  # Report has been dismissed
        report = get_object_or_404(Report, pk=request.POST['report-id'])
        report.was_addressed  = True
        report.addressed_by   = request.user
        report.date_addressed = datetime.datetime.now()  # UTC?
        report.save()
    return render(request, 'reports.html', {'reports': reports})


def search(request):
    return render(request, 'placeholder.html', {})


def custom_login(request, **kwargs):
    """Redirects logged-in users, and allows others to log in."""
    if request.user.is_authenticated():  # User logged in
        return HttpResponseRedirect(reverse('forum.views.home', args=()))
    else:
        return login(request, **kwargs)


def custom_logout(request):
    """Logs out the user with a message confirmation."""
    if request.user.is_authenticated():  # User logged in
        auth.logout(request)
    messages.success(request, "Logged out successfully.")

    return HttpResponseRedirect(reverse('forum.views.home', args=()))


def custom_register(request, **kwargs):
    """Registers users and redirects those who are already authenticated."""
    site = Site.objects.get_current()

    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('forum.views.home', args=()))
    else:
        site_config_error, email_config_error = False, False
        if site.domain == "example.com" or site.name == "example.com":
            site_config_error = True
        if project_settings.EMAIL_HOST_USER == "myusername@gmail.com":
            email_config_error = True

        return registration_views.register(request,
            backend='registration.backends.default.DefaultBackend',
            template_name='registration/registration_form.html',
            extra_context={
                'site_config_error':  site_config_error,
                'email_config_error': email_config_error,
                'max_username_length':
                    User._meta.get_field("username").max_length},
            form_class=CustomRegistrationForm)


@login_required()
def settings(request):
    """Here the user can manage his or her user settings."""
    if request.method == "POST":  # Changes submitted
        profile = request.user.get_profile()
        profile.has_dyslexia = request.POST['has_dyslexia']
        profile.auto_subscribe = request.POST['auto_subscribe'] == "True"
        profile.save()
        messages.success(request, "New settings saved.")

    return render(request, 'settings.html', {})


@login_required()
def site_configuration(request):
    """Displays all configurable environment variables to admins."""
    if not request.user.is_staff:
        messages.error(request,
                       "You need staff status to configure the site.")
        return HttpResponseRedirect(reverse('forum.views.home', args=()))

    site = Site.objects.get_current()

    if request.method == "POST":  # Changes submitted
        site.name = request.POST['site_name']
        site.domain = request.POST['site_domain']
        site.save()
        messages.success(request, "New settings saved.")

    return render(request, 'site_configuration.html', {
        'EMAIL_HOST_USER':
            project_settings.EMAIL_HOST_USER != "myusername@gmail.com",
        'EMAIL_HOST_PASSWORD':     project_settings.EMAIL_HOST != "mypassword",
        'EMAIL_USE_TLS':           project_settings.EMAIL_USE_TLS,
        'LOCAL_DEVELOPMENT':       project_settings.LOCAL_DEVELOPMENT,
        'TIME_ZONE':               project_settings.TIME_ZONE,
        'LANGUAGE_CODE':           project_settings.LANGUAGE_CODE,
        'ACCOUNT_ACTIVATION_DAYS': project_settings.ACCOUNT_ACTIVATION_DAYS,
        'REGISTRATION_OPEN':       project_settings.REGISTRATION_OPEN,
        'POSTS_PER_PAGE':          project_settings.POSTS_PER_PAGE,
        'THREADS_PER_PAGE':        project_settings.THREADS_PER_PAGE,
        'USER_POSTS_PER_PAGE':     project_settings.USER_POSTS_PER_PAGE,
        'USER_THREADS_PER_PAGE':   project_settings.USER_THREADS_PER_PAGE,
        'SUBSCRIPTIONS_PER_PAGE':  project_settings.SUBSCRIPTIONS_PER_PAGE,
        'BOOKMARKS_PER_PAGE':      project_settings.BOOKMARKS_PER_PAGE,
        'SAVES_PER_PAGE':          project_settings.SAVES_PER_PAGE,
        'DEFAULT_FROM_EMAIL':      project_settings.DEFAULT_FROM_EMAIL,
        'HAS_SITE_NAME':           site.name != "example.com",
        'HAS_SITE_DOMAIN':         site.domain != "example.com",
        'SITE_NAME':               site.name,
        'SITE_DOMAIN':             site.domain
    })


@login_required()
def saves_and_bookmarks(request, object_type):
    """Shows the user's saved posts and/or bookmarked threads."""
    if object_type == "save":
        objects    = request.user.saves.all().select_related()\
                     .exclude(thread__is_removed__exact=True)
        USER_CONTENT_PER_PAGE = SAVES_PER_PAGE
    else:  #   ... == "bookmark"
        objects    = request.user.bookmarks.all()
        USER_CONTENT_PER_PAGE = BOOKMARKS_PER_PAGE
    # objects = objects.order_by("-creation_date") -saved_date
    objects = paginate(request, objects, USER_CONTENT_PER_PAGE)

    return render(request, 'saves_and_bookmarks.html',
                  {'type':    object_type,
                   'objects': objects})


def simple_js(request):
    """Lets users do one of the following:

    From the user view:

    * follow a user
    * add a user to a shit list

    From the thread or post view:

    * bookmark threads
    * subscribe to threads

    * agree with posts
    * thank users for posts
    * save posts

    or

    * bookmark and unbookmark threads from the bookmarks view
    * save and unsave posts from the saves view
    * subscribe to and unsubscribe from threads in the subscription view
    """
    if request.is_ajax() and request.method == "POST":
        object_id = request.POST['object_id']
        action    = request.POST['action'].lower()
        href      = request.POST['href']

        if 'follow' in href or 'ignore' in href:
            person = get_object_or_404(User, pk=object_id)
        elif 'bookmark' in href or 'subscribe' in href:
            thread = get_object_or_404(Thread, pk=object_id)
        elif 'save' in href or 'thank' in href or 'agree' in href:
            post = get_object_or_404(Post, pk=object_id)

        # User JS
        if "follow" in href:
            if action.startswith("follow"):
                request.user.get_profile().follows.add(person)
                new_action = "Unfollow user"
            else:
                request.user.get_profile().follows.remove(person)
                new_action = "Follow user"
        elif "ignore" in href:
            if action.startswith("add"):
                request.user.get_profile().ignores.add(person)
                new_action = "Remove from shit list"
            else:
                request.user.get_profile().ignores.remove(person)
                new_action = "Add to shit list"
        # Thread JS
        elif "bookmark" in action:
            # Not to be confused with the action related
            # to the bookmark view
            if action == "bookmark":
                thread.bookmarker.add(request.user)
                new_action = "Unbookmark"
            else:
                thread.bookmarker.remove(request.user)
                new_action = "Bookmark"

        elif "subscribe" in action:
            # Not to be confused with the action related
            # to the subscriptions view
            if action == "subscribe":
                thread.subscriber.add(request.user)
                new_action = "Unsubscribe"
            else:
                thread.subscriber.remove(request.user)
                new_action = "Subscribe"

        elif "agree" in action:
            if action == "agree":
                post.agrees.add(request.user)
                new_action = "Unagree"
            else:
                post.agrees.remove(request.user)
                new_action = "Agree"

        elif "save" in action:
            if action == "save":
                post.saves.add(request.user)
                new_action = "Unsave"
            else:
                post.saves.remove(request.user)
                new_action = "Save"

        elif "thank" in action:
            if action == "thank":
                post.thanks.add(request.user)
                new_action = "Unthank"
            else:
                post.thanks.remove(request.user)
                new_action = "Thank"

        # Bookmarks JS
        elif "bookmark" in href:
            if action == "re-bookmark":
                thread.bookmarker.add(request.user)
                new_action = "Unbookmark"
            else:
                thread.bookmarker.remove(request.user)
                new_action = "Re-bookmark"

        # Saves JS
        elif "save" in href:
            if action == "re-save":
                post.saves.add(request.user)
                new_action = "Remove"
            else:
                post.saves.remove(request.user)
                new_action = "Re-save"

        # Subscriptions JS
        elif "subscribe" in href:
            if action == "re-subscribe":
                thread.subscriber.add(request.user)
                new_action = "Unsubscribe"
            else:
                thread.subscriber.remove(request.user)
                new_action = "Re-subscribe"

        return HttpResponse(new_action)


@login_required()
def nonjs(request, action, object_id):
    """An HTML fall-back for when the JavaScript required
    for some views is off.
    """
    next = request.META.get('HTTP_REFERER', '')

    if action in ['follow', 'ignore']:
        obj = get_object_or_404(User, pk=object_id)
        object_type = 'user'
        thread = None
        post_obj = None
    elif action in ['save', 'thank', 'agree']:
        obj = get_object_or_404(Post, pk=object_id)
        object_type = 'post'
        thread = obj.thread
        post_obj = obj
    else:
        obj = get_object_or_404(Thread, pk=object_id)
        object_type = 'thread'
        thread = obj
        post_obj = None

    if request.method == 'POST':  # Form has been submitted
        if 'follow' in action:
            if 'follow' in request.POST:  # Follow command
                request.user.get_profile().follows.add(obj)
                messages.info(request, "Now following %s." % obj.username)
            else:
                request.user.get_profile().follows.remove(obj)
                messages.info(request, "Unfollowed %s." % obj.username)

        elif 'ignore' in action:
            if 'ignore' in request.POST:  # Ignore command
                request.user.get_profile().ignores.add(obj)
                messages.info(request,
                              "Added %s to shit list." % obj.username)
            else:
                request.user.get_profile().ignores.remove(obj)
                messages.info(request,
                              "Removed %s from shit list." % obj.username)

        elif 'subscribe' in action:
            if 'subscribe' in request.POST:  # Subscribe command
                thread.subscriber.add(request.user)
                messages.info(request, "Subscribed to thread.")
            else:  # Unsubscribe command
                thread.subscriber.remove(request.user)
                messages.info(request, "Unsubscribed from thread.")
            thread.save()

        elif 'bookmark' in action:
            if 'bookmark' in request.POST:  # Bookmark command
                thread.bookmarker.add(request.user)
                messages.info(request, "Bookmarked thread.")
            else:  # Unbookmark command
                thread.bookmarker.remove(request.user)
                messages.info(request, "Unbookmarked thread.")
            thread.save()

        elif 'lock' in action:
            # Lets the permitted user lock a thread,
            # i.e., prevent people from posting in it.
            #
            # Also allows the opposite action, i.e. to unlock it.
            if thread.is_removed and not request.user.has_perm('forum.remove_thread'):
                messages.info(request, "The has thread been removed.")
                return HttpResponseRedirect(reverse(
                    'forum.views.category', args=(thread.category_id,)))
            if not request.user.has_perm('forum.lock_thread'):
                messages.error(request,
                    "You do not have permission to lock and unlock threads.")
                return HttpResponseRedirect(next)
            if 'lock' in request.POST:  # Lock command
                if thread.is_locked:
                    messages.info(request, "The thread was already locked.")
                thread.is_locked = True
                messages.info(request, "Thread was locked.")
            else:  # Unlock command
                if not thread.is_locked:
                    messages.info(request, "The thread was already not locked.")
                thread.is_locked = False
                messages.info(request, "Thread was unlocked.")
            thread.save()

        elif 'sticky' in action:
            # Lets the permitted user sticky a thread,
            # thereby sticking it to the top of the thread list.
            #
            # Also allows the opposite action, i.e. to unsticky it.
            if thread.is_removed and not request.user.has_perm('forum.remove_thread'):
                messages.info(request, "The has thread been removed.")
                return HttpResponseRedirect(reverse(
                    'forum.views.category', args=(thread.category_id,)))
            if not request.user.has_perm('forum.sticky_thread'):
                messages.error(request,
                    "You do not have permission to sticky and unsticky threads.")
                return HttpResponseRedirect(next)
            if 'sticky' in request.POST:  # Lock command
                if thread.is_sticky:
                    messages.info(request, "The thread was already sticky.")
                thread.is_sticky = True
                messages.info(request, "Thread was stickied.")
            else:  # Unsticky command
                if not thread.is_sticky:
                    messages.info(request, "The thread was already not sticky.")
                thread.is_sticky = False
                messages.info(request, "Thread was unstickied.")
            thread.save()

        elif 'save' in action:
            if 'save' in request.POST:  # Save command
                obj.saves.add(request.user)
                messages.info(request, "Saved post.")
            else:  # Unsave command
                obj.saves.remove(request.user)
                messages.info(request, "Unsaved post.")
            obj.save()

        elif 'thank' in action:
            if 'thank' in request.POST:  # Thank command
                obj.thanks.add(request.user)
                messages.info(request, "Thanked author of the post.")
            else:  # Unthank command
                obj.thanks.remove(request.user)
                messages.info(request, "Unthanked author of the post.")
            obj.save()

        elif 'agree' in action:
            if 'agree' in request.POST:  # Agree command
                obj.agrees.add(request.user)
                messages.info(request, "Agreed with the author in the post.")
            else:  # Unagree command
                obj.agrees.remove(request.user)
                messages.info(request, "Unagreed with the author of the post.")
            obj.save()

        return HttpResponseRedirect(next)
    else:  # Otherwise, show clean, normal page with no populated data
        canonical_url = reverse('forum.views.nonjs', args=(action, object_id))
        return render(request, 'simple_action.html',
                      {'thread':        thread,
                       'obj':           obj,
                       'post_obj':      post_obj,
                       'object_type':   object_type,
                       'action':        action,
                       'object_id':     object_id,
                       'canonical_url': canonical_url,
                       'next':          next})
