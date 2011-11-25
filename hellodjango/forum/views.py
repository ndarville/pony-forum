from datetime                       import datetime  # reply, create
from markdown                       import markdown
from MySQLdb                        import OperationalError
from smartypants                    import smartyPants as smartypants
import bleach

from django.conf                    import settings
from django.contrib                 import messages, auth  # notifications, login, register
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.models     import User  # register
from django.contrib.sites.models    import Site  # current_site
from django.core.urlresolvers       import reverse  # reply, create, edit
from django.db.utils                import DatabaseError
from django.http                    import HttpResponse, HttpResponseRedirect
from django.shortcuts               import render, get_object_or_404

from forum.models                   import Category, Post, Report,\
                                           Subscription, Thread, UserProfile


#   views.py TOC:
#
#
##  helper constants
##  helper errors
##  helper functions
#
##  home
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
##  settings_js
##  subscription_js
##  thread_js
##  user_js
#
##  moderate_thread
##  merge_thread
##  move_thread
##  lock_thread
##  remove
##  report
##  reports
#
##  logout
##  settings


LOGIN_URL                 = getattr(settings, "LOGIN_URL", "/accounts/login/")
MAX_THREAD_TITLE_LENGTH   = Thread._meta.get_field("title_plain").max_length
MAX_CATEGORY_TITLE_LENGTH = Category._meta.get_field("title_plain").max_length


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


def amazon_referral(text):
    return "regex blahblahblah"


#def module_exists(module_name):
#    try:
#        __import__(module_name)
#    except ImportError:
#        return False
#    else:
#        return True


def email_is_taken(email):
    """Checks whether the e-mail submitted is already in user by someone
    in the database.

    Also checks whether the user uses a +filter as supported in Gmail.
    More info: 
    """
    if "+" in email:
        # Get the part "example+" of "name+filter@example.com"
        email_head = email.split("+")[0] + "+"
        # Get the second part, "@example.com"
        email_tail = email.split("@")[1]
        # Check if it matches "name+" and "@example.com",
        # thus disregarding the +filters
        try:
            User.objects.get(email__startswith=email_head,
                             email__endswith=email_tail)
        except UserDoesNotExist:
            pass
        else:
            return True
    try:
        User.objects.get(email__exact=email)
    except User.DoesNotExist:
        return False
    else:
        return True


def prettify_title(title):
    """Sanitizes all (ALL) HTML elements in titles while prettifying the quotes
    and dashes used in the titles of threads and categories.
    """
    return bleach.clean(\
                        smartypants(title, "2"),\
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

        If this is the case, you can replace the line

        (...)

        with

        (...)

        You will still need to save existing titles and posts again
        for them to be affected by the change.

    NB (Bleach and Encoding):
        Bleach always returns a unicode object, whether you give it a
        bytestring or a unicode object, but Bleach does not attempt to detect
        incoming character encodings, and will assume UTF-8.

        If you are using a different character encoding, you should convert
        from a bytestring to unicode before passing the text to Bleach.
    """
    ALLOWED_TAGS       = [
                          'a',
                          'abbr',
                          'acronym',
                          'b',
                          'blockquote',
                          'code',
                          'em',
                          'i',
                          'img',
                          'li',
                          'ol',
                          'p',
                          'pre',
                          'strong',
                          'sub',
                          'sup',
                          'ul',
                      ### Tables:
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
                          'img':     ['alt', 'src']
                         }
    return bleach.clean(\
                        markdown(
                                 smartypants(\
                                 # issue: https://github.com/jsocol/bleach/issues/49
                                 #            bleach.linkify(string, skip_pre=True)),\
                                 # Delete the following line and uncomment
                                 # the line above, if the issue is fixed.
                                             string, "2"),\
                                 extensions=['tables'],\
                                 safe_mode='escape'),\
                        tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)


def username_is_taken(username):
    try:
        User.objects.get(username__exact=username)
    except User.DoesNotExist:
        return False
    else:
        return True


def home(request):
    """The landing page displaying categories, new and popular threads
    as well as unread threads the user has subscribed to.
    """
    subscribed_threads = False
    categories  = Category.objects.all()
    threads     = Thread.objects.exclude(is_removed__exact=True)
    new_threads = threads[:5]    

    if not request.user.is_anonymous() and request.user.subscriptions.all():
        subscribed_threads = threads.filter(subscriber__exact=request.user)[:5]

    # updates = request.user.subscription_set.all()
    # update.last_read < update.thread.latest_reply_date
    ## or update.last_read == None  # (or something)
    # link to newest post
    # number of new posts
    return render(request, 'home.html',
                          {'full_url'    : request.build_absolute_uri(),
                           'current_site': Site.objects.get_current(),
                           'categories'  : categories,
                           'new_threads' : new_threads,
                           'subs'        : subscribed_threads})


@login_required(login_url=LOGIN_URL)
def subscriptions(request):
    """Manage and observe all your subscriptions to threads with new posts."""
    has_subs      = False
    updated_subs  = False
    inactive_subs = False
    threads       = Thread.objects.exclude(is_removed__exact=True)
    new_threads   = threads[:5]

    if request.user.subscriptions.all():
        has_subs      = True
        updated_subs  = threads.filter(subscriber__exact=request.user)[:5]
        inactive_subs = False

    return render(request, 'subscriptions.html',
                          {'full_url'     : request.build_absolute_uri(),
                           'current_site' : Site.objects.get_current(),
                           'new_threads'  : new_threads,
                           'has_subs'     : has_subs,
                           'updated_subs' : updated_subs,
                           'inactive_subs': inactive_subs})


def category(request, category_id):
    """Category with threads ordered by latest posts."""
    category         = get_object_or_404(Category, pk=category_id)
    all_threads      = category.thread_set.all()
    category_threads = all_threads.order_by("-latest_reply_date")\
                       .exclude(is_sticky__exact=True)
#                       .only("latest_reply_date")
    stickies         = all_threads.exclude(is_sticky__exact=False)

    # Threadbar code from home()
    subscribed_threads = False
    threads     = Thread.objects.exclude(is_removed__exact=True)
    new_threads = threads[:5]    

    if not request.user.is_anonymous() and request.user.subscriptions.all():
        subscribed_threads = threads.filter(subscriber__exact=request.user)[:5]

    return render(request, 'category.html',
                          {'current_site'    : Site.objects.get_current(),
                           'category'        : category,
                           'category_threads': category_threads,
                           'stickies'        : stickies,
                           'new_threads'     : new_threads,
                           'subs'            : subscribed_threads})


def thread(request, thread_id, author_id):
    """Thread with all the belonging posts."""
    thread = get_object_or_404(Thread, pk=thread_id)

    if not thread.is_removed or request.user.has_perm('forum.remove_thread'):
        posts = thread.post_set.all()

        if not request.user.has_perm('forum.remove_thread') or not request.user.has_perm('forum.remove_post'):
            posts     = posts.exclude(is_removed__exact=True)
        if author_id != "Everyone":  # User has specified an author(_id)
            posts     = posts.filter(author__exact=author_id)

        posts = posts.exclude(is_removed__exact=True)\
                .order_by("creation_date")\
#        anchor_number = forloop.counter
        anchor_number = '???'
        return render(request, 'thread.html',
                              {'current_site' : Site.objects.get_current(),
                               'thread_id'    : thread_id,
                               'thread'       : thread,
                               'posts'        : posts,
                               'anchor_number': anchor_number})
    else:
        messages.info(request, "The thread %s has been removed and no longer available." % thread.title_html)
        return HttpResponseRedirect(reverse('forum.views.category', args=(thread.category.id,)))


def post(request, post_id):
    """View a single post object."""
    post = get_object_or_404(Post, pk=post_id)

    if not post.thread.is_removed or request.user.has_perm('forum.remove_thread'):
        if not post.is_removed or request.user.has_perm('forum.remove_thread') \
           or request.user.has_perm('forum.remove_post'):
            anchor_number = '???'
            return render(request, 'post.html',
                                  {'current_site' : Site.objects.get_current(),
                                   'post_id'      : post_id,
                                   'post'         : post,
                                   'anchor_number': anchor_number})
        else:
            messages.info(request, "The post by %s has been removed and no longer available." % post.author)
            return HttpResponseRedirect(reverse('forum.views.thread', args=(post.thread.id,)))
    else:
        messages.info(request, "The thread %s has been removed and no longer available." % post.thread.title_html)
        return HttpResponseRedirect(reverse('forum.views.category', args=(post.thread.category.id,)))
    

def user(request, user_id):
    """Shows another user's profile.

    Uses the `person` variable to disambiguate from `user`,
    which is used in templates for the user viewing a page.

    `latest_posts_amount` determines the amount of latest posts to show.
    """
    person = get_object_or_404(User, pk=user_id)
    posts = person.post_set.all()\
            .exclude(is_removed__exact=True)\
            .exclude(thread__is_removed__exact=True)\
            .order_by("-creation_date")
    return render(request, 'user.html',
                          {'current_site': Site.objects.get_current(),
                           'person'      : person,
                           'posts'       : posts})


def user_content(request, user_id, object_type):
    """Shows all posts or threads by specific user."""
    person = get_object_or_404(User, pk=user_id)

    if object_type == "post":
        objects    = person.post_set.all()\
                     .exclude(thread__is_removed__exact=True)\
                     .order_by("-creation_date")
    else:  # ..... == "thread"
        objects    = person.thread_set.all()\
                     .exclude(is_removed__exact=True)\
                     .order_by("-creation_date")
    return render(request, 'user_content.html',
                          {'current_site': Site.objects.get_current(),
                           'type'        : object_type,
                           'person'      : person,
                           'objects'     : objects})


@permission_required('forum.add_category', login_url=LOGIN_URL)
def add(request):
    """Add a new category."""
    title_plain = False

    if request.method == 'POST':  # Form has been submitted
        title_plain = request.POST['title']
        title_html  = prettify_title(title_plain)
        if len(title_plain) > MAX_CATEGORY_TITLE_LENGTH:
            messages.error(request, long_title_error % MAX_CATEGORY_TITLE_LENGTH)
        else:
            c = Category(title_plain=title_plain, title_html=title_html)
            c.save()
            return HttpResponseRedirect("/")
    return render(request, 'add.html',
                          {'full_url'    : request.build_absolute_uri(),
                           'current_site': Site.objects.get_current(),
                           'title'       : title_plain})


@login_required(login_url=LOGIN_URL)
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
                now       = datetime.now()  # UTC?
                text_html = sanitized_smartdown(text_plain)
                try:
                    t = Thread(title_plain=title_plain, title_html=title_html,
                               author=user, category=category,
                               creation_date=now, latest_reply_date=now)
                    t.save()
                    p = Post(thread=t, creation_date=now, author=user,
                             content_plain=text_plain, content_html=text_html)
                    p.save()
                    t.subscriber.add(request.user)
                except OperationalError:  # Database interaction error
                    messages.error(request, "%s") % operational_error
                else:
                    # After successful submission
                    return HttpResponseRedirect(reverse('forum.views.thread',
                        args=(user.thread_set.all().order_by('-creation_date')[0].id,)))
        elif "preview" in request.POST:  # "preview" button pressed
            preview_plain = text_plain
            preview_html  = sanitized_smartdown(text_plain)

    return render(request, 'create.html',
                          {'full_url'     : request.build_absolute_uri(),
                           'current_site' : Site.objects.get_current(),
                           'category'     : category,
                           'title'        : title_plain,
                           'preview_plain': preview_plain,
                           'preview_html' : preview_html})


@login_required(login_url=LOGIN_URL)
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
        return HttpResponseRedirect(reverse('forum.views.category', args=(thread.category.id,)))

    if request.method == 'POST':  # Form been submitted
        text = request.POST['content']
        if "submit" in request.POST:  # "submit" button pressed
            user = request.user
            now  = datetime.now()  # UTC?
            html = sanitized_smartdown(text)
            try:
                p = Post(thread=thread, author=user, creation_date=now,
                         content_plain=text, content_html=html)
                p.save()
                thread.latest_reply_date = now
                thread.save()
            except OperationalError:  # Database interaction error
                messages.error(request, "%s") % operational_error
            else:
                # After successful submission
                return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))
        elif "preview" in request.POST:  # "preview" button pressed
            preview_plain = text
            preview_html  = sanitized_smartdown(text)

    return render(request, 'reply.html',
                          {'current_site' : Site.objects.get_current(),
                           'thread'       : thread,
                           'preview_plain': preview_plain,
                           'preview_html' : preview_html})


@login_required(login_url=LOGIN_URL)
def edit(request, post_id):
    """Lets the author edit his or her post."""
    post          = get_object_or_404(Post, pk=post_id)
    preview_plain = False
    preview_html  = False

    if post.thread.is_removed:
        messages.info(request, "The thread %s has been removed and is no longer available." % post.thread.title_html)
        return HttpResponseRedirect(reverse('forum.views.category', args=(post.thread.category.id,)))
    elif post.is_removed:
        messages.info(request, "Your post has been removed and is no longer available.")
        return HttpResponseRedirect(reverse('forum.views.thread', args=(post.thread.id,)))

    if request.method == 'POST':  # Form has been submitted
        text = request.POST['content']
        if "submit" in request.POST:  # "submit" button pressed
            post.content_plain = text
            post.content_html  = sanitized_smartdown(text)
            post.save()
            return HttpResponseRedirect(reverse('forum.views.thread', args=(post.thread.id,)))
        elif "preview" in request.POST:  # "preview" button pressed
            preview_plain = text
            preview_html  = sanitized_smartdown(text)
    # The post author or a moderator/admin visits the link
    elif request.user == post.author or request.user.has_perm('forum.change_post'):
        pass
    else:  # Someone who is not the author goes to the edit link
        return HttpResponseRedirect(reverse('forum.views.post', args=(post.id,)))

    return render(request, 'edit.html',
                          {'current_site' : Site.objects.get_current(),
                           'post'         : post,
                           'preview_plain': preview_plain,
                           'preview_html' : preview_html})


def subscription_js(request):
    if request.is_ajax() and request.method == "POST":
        thread_id = request.POST['thread_id']
        action    = request.POST['action'].lower()
        thread    = get_object_or_404(Thread, pk=thread_id)

        if action == "unsubscribe":
            thread.subscriber.remove(request.user)
            new_action = "Subscribe"
        else:
            thread.subscriber.add(request.user)
            new_action = "Unsubscribe"

        HttpResponse(new_action)


# @login_required(login_url=LOGIN_URL)  # Doesn't work
def thread_js(request):
    if request.is_ajax() and request.method == "POST":
        # if not logged in ...
      
        object_id = request.POST['object_id']
        action    = request.POST['action'].lower()

        if "bookmark" in action or "subscribe" in action:
            obj = get_object_or_404(Thread, pk=object_id)
        else:
            obj = get_object_or_404(Post, pk=object_id)

        # Check that it exists before adding and not when removing
        if "agree" in action:
            if action == "agree":
                obj.agrees.add(request.user)
                new_action = "Unagree"
            else:
                obj.agrees.remove(request.user)
                new_action = "Agree"

        elif "bookmark" in action:
            if action == "bookmark":
                obj.bookmarker.add(request.user)
                new_action = "Unbookmark"
            else:
                obj.bookmarker.remove(request.user)
                new_action = "Bookmark"

        elif "save" in action:
            if action == "save":
                obj.saves.add(request.user)
                new_action = "Unsave"
            else:
                obj.saves.remove(request.user)
                new_action = "Save"

        elif "subscribe" in action:
            if action == "subscribe":
                obj.subscriber.add(request.user)
                new_action = "Unsubscribe"
            else:
                obj.subscriber.remove(request.user)
                new_action = "Subscribe"

        elif "thank" in action:
            if action == "thank":
                obj.thanks.add(request.user)
                new_action = "Unthank"
            else:
                obj.thanks.remove(request.user)
                new_action = "Thank"

        return HttpResponse(new_action)

#        if action.endswith("e"):
#            success = action + "d"
#        else:
#            success = action + "ed"


# @login_required(login_url=LOGIN_URL)  # Doesn't work
def user_js(request):
    if request.is_ajax() and request.method == "POST":     
        person_id = request.POST['person_id']
        text      = request.POST['text'].lower()
        person    = get_object_or_404(User, pk=person_id)

        if text.startswith("follow"):
            request.user.get_profile().follows.add(person)
            new_text = "Unfollow user"
        elif text.startswith("unfollow"):
            request.user.get_profile().follows.remove(person)
            new_text = "Follow user"

        elif text.startswith("add"):
            request.user.get_profile().ignores.add(person)
            new_text = "Remove user from shit list"
        elif text.startswith("remove"):
            request.user.get_profile().ignores.add(person)
            new_text = "Add user to shit list"

        return HttpResponse(new_text)


@permission_required('forum.lock_thread', login_url=LOGIN_URL)
def lock_thread(request, thread_id):
    """Lets the permitted user lock a thread,
    i.e., prevent people from posting in it.

    Also allows an undo by choosing to unlock it.
    """
    thread = get_object_or_404(Thread, pk=thread_id)

    if thread.is_removed and not request.user.has_perm('forum.remove_thread'):
        messages.info(request, "The has thread been removed.")
        return HttpResponseRedirect(reverse('forum.views.category', args=(thread.category.id,)))

    if request.method == 'POST':  # Form has been submitted
        if 'lock' in request.POST:  # Lock command
            thread.is_locked = True
        else:  # Unlock command
            thread.is_locked = False
        
        thread.save()
        return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))
    else:  # Otherwise, show clean, normal page with no populated data
        return render(request, 'lock.html',
                              {'current_site': Site.objects.get_current(),
                               'thread'      : thread})


@permission_required('forum.sticky_thread', login_url=LOGIN_URL)
def sticky_thread(request, thread_id):
    """Lets the permitted user sticky a thread,
    thereby sticking it to the top of the thread list.

    Also allows an undo by choosing to unsticky it.
    """
    thread = get_object_or_404(Thread, pk=thread_id)

    if thread.is_removed and not request.user.has_perm('forum.remove_thread'):
        messages.info(request, "The has thread been removed.")
        return HttpResponseRedirect(reverse('forum.views.category', args=(thread.category.id,)))

    if request.method == 'POST':  # Form has been submitted
        if 'sticky' in request.POST:  # Lock command
            thread.is_sticky = True
        else:  # Unlock command
            thread.is_sticky = False
        
        thread.save()
        return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))
    else:  # Otherwise, show clean, normal page with no populated data
        return render(request, 'sticky.html',
                              {'current_site': Site.objects.get_current(),
                               'thread'      : thread})


@permission_required('forum.merge_thread', login_url=LOGIN_URL)
def merge_thread(request, thread_id):
    """Merge the posts of two threads into one single thread.

    The posts are ordered chronologically in the new thread,
    the old threads are locked, and a notification post is created
    in all three threads.
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
            now  = datetime.now()  # UTC?
            user = request.user
            t    = Thread(title_plain=new_title_plain, title_html=new_title_html,
                          creation_date=now, author=user, category=thread.category,
                          latest_reply_date=now)
            t.save()
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
            message = "(*%s* was merged with *%s* by *%s* into *[%s](%s)*%s)" % \
                            (thread.title_html,
                             other_thread.title_html,
                             user.username,
                             new_title_html,
                             t.get_absolute_url(),
                             end)
            html = sanitized_smartdown(message)
            p1   = Post(creation_date=now, author=user, thread=t, 
                        content_plain=message, content_html=html)
            p2   = Post(creation_date=now, author=user, thread=thread, 
                        content_plain=message, content_html=html)
            p3   = Post(creation_date=now, author=user, thread=other_thread,
                        content_plain=message, content_html=html)
            p1.save()
            p2.save()
            p3.save()
        # Lock original threads
            thread.is_locked       = True
            other_thread.is_locked = True
            thread.save()
            other_thread.save()
            return HttpResponseRedirect(reverse('forum.views.thread', args=(t.id,)))

    return render(request, 'merge.html',
                          {'full_url'    : request.build_absolute_uri(),
                           'current_site': Site.objects.get_current(),
                           'thread'      : thread,
                           'other_thread': other_thread,
                           'new_title'   : new_title_plain})


@permission_required('forum.change_thread', login_url=LOGIN_URL)
def moderate_thread(request, thread_id):
    """Change the title of a thread."""
    thread      = get_object_or_404(Thread, pk=thread_id)
    title_plain = thread.title_plain

    if request.method == 'POST':  # Form has been submitted
        title_plain = request.POST['title']
        title_html  = prettify_title(title_plain)
        if len(title_plain) > MAX_THREAD_TITLE_LENGTH:
            messages.error(request, long_title_error % MAX_THREAD_TITLE_LENGTH)
        else:
            try:
                thread.title_plain = title_plain
                thread.title_html  = title_html
                thread.save()
            except OperationalError:  # Database interaction error
                messages.error(request, "%s")
            else:
                return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))
    return render(request, 'moderate.html',
                          {'full_url'    : request.build_absolute_uri(),
                           'current_site': Site.objects.get_current(),
                           'thread'      : thread,
                           'title'       : title_plain})


@permission_required('forum.move_thread', login_url=LOGIN_URL)
def move_thread(request, thread_id):
    """Move a thread to another category."""
    thread     = get_object_or_404(Thread, pk=thread_id)
    categories = Category.objects.all()

    if request.method == 'POST':  # Form has been submitted
        category = get_object_or_404(Category, pk=request.POST['category'])

        thread.category = category
        thread.save()
        return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))
    else:  # Otherwise, show clean, normal page with no populated data
        return render(request, 'move.html',
                              {'current_site': Site.objects.get_current(),
                               'thread'      : thread,
                               'categories'  : categories})


@login_required(login_url=LOGIN_URL)
def remove(request, object_id, object_type):
    """Lets the permitted user remove a post or thread.

    A database deletion is not performed upon removal;
    the post or thread is merely hidden in the template.

    An actual deletion has to be done manually in the admin settings or shell.
    """
    if object_type == "post":
        obj    = get_object_or_404(Post, pk=object_id)
        thread = obj.thread
        if not request.user.has_perm('forum.remove_post'):
            return HttpResponseRedirect(reverse('forum.views.post', args=(obj.id,)))
    else:  # ... == thread
        obj    = get_object_or_404(Thread, pk=object_id)
        thread = obj
        if not request.user.has_perm('forum.remove_thread'):
            return HttpResponseRedirect(reverse('forum.views.thread', args=(obj.id,)))

    if request.method == 'POST':  # Form has been submitted
        if 'remove' in request.POST:  # Remove command
            obj.is_removed = True
        else:  # Restore command
            obj.is_removed = False
        obj.save()
        return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))
    else:
        return render(request, 'remove.html',
                              {'current_site': Site.objects.get_current(),
                               'type'        : object_type,
                               'obj'         : obj,
                               'thread'      : thread})


@login_required(login_url=LOGIN_URL)
def report(request, object_id, object_type):
    """Report a post or thread infraction to the moderators."""
    title   = False
    preview = False

    if object_type == "post":
        obj    = get_object_or_404(Post, pk=object_id)
        thread = obj.thread
    else:  # ... == thread
        obj    = get_object_or_404(Thread, pk=object_id)
        thread = obj

# Check for reasons not to let the user file a report
    if object_type == "thread":
        if thread.is_removed:
            messages.info(request, "The thread %s has been removed and is no longer available." % thread.title_html)
            return HttpResponseRedirect(reverse('forum.views.category', args=(thread.category.id,)))
        elif thread.is_locked:
            messages.info(request, "The thread %s has been locked and can not be reported." % thread.title_html)
        # Thread already reported AND unaddressed by moderator
        elif Report.objects.filter(author__exact=request.user)\
                           .filter(thread__exact=obj)\
                           .filter(was_addressed__exact=False):
            messages.info(request, "This %s has already been reported by you." % object_type)
            return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))
    elif object_type == "post":
        if obj.is_removed:
            messages.info(request, "The post has been removed and is no longer available.")
        elif request.user == obj.author:
            messages.error(request, "You cannot report your own posts, silly goose.")
        elif obj.author.is_staff:
            messages.info(request, "The author of the reported post is an admin. \
            You should contact them directly, if you take issue with their content.")
        # Post already reported by user
        elif Report.objects.filter(author__exact=request.user)\
                           .filter(post__exact=obj):
            messages.info(request, "This %s has already been reported by you." % object_type)
        return HttpResponseRedirect(reverse('forum.views.thread', args=(thread.id,)))
    
    if request.method == 'POST':  # Form has been submitted
        title = request.POST['title']
        if "content" in request.POST:  # elaboration provided
            text  = request.POST['content']
        if "submit" in request.POST:  # "submit" button pressed
            if len(title) > MAX_THREAD_TITLE_LENGTH:
                messages.error(request, long_title_error % MAX_THREAD_TITLE_LENGTH)
                preview = text
            else:
                user = request.user
                now  = datetime.now()  # UTC?
                try:
                    r = Report(creation_date=now, author=user,
                               reason_short=title, thread=thread)
                    if "content" in request.POST:
                        r.reason_long = text
                    if object_type == "post":
                        r.post = obj
                    r.save()
                except OperationalError:  # Database interaction error
                    messages.error(request, "%s") % operational_error
                else:
                    # After successful submission
                    return HttpResponseRedirect(reverse('forum.views.thread',
                        args=(thread.id,)))
        elif "preview" in request.POST:  # "preview" button pressed
            preview = text
    return render(request, 'report.html',
                          {'full_url'    : request.build_absolute_uri(),
                           'current_site': Site.objects.get_current(),
                           'obj'         : obj,
                           'type'        : object_type,
                           'thread'      : thread,
                           'title'       : title,
                           'preview'     : preview})


@permission_required('forum.use_report', login_url=LOGIN_URL)
def reports(request):
    """Inspect and act on filed reports on threads and posts."""
# Hide reports that have been addressed
    reports = Report.objects.filter(was_addressed__exact=False)
    reports = reports.order_by("creation_date")
    reports = reports.order_by("thread")

    if request.method == 'POST':  # Report has been dismissed
        now    = datetime.now()  # UTC?
        report = get_object_or_404(Report, pk=request.POST['report-id'])
        report.was_addressed  = True
        report.addressed_by   = request.user
        report.date_addressed = now
        report.save()
    return render(request, 'reports.html',
                          {'current_site': Site.objects.get_current(),
                           'reports'     : reports})


# def search(request):
#     query     = request.GET['q']
#     results = []
#     if query:
#         results = Post.objects.filter(content_plain__icontains=query)
#     return render('search/search.html',
#                  {'query'       : query,
#                   'results'     : results,
#                   'full_url'    : request.build_absolute_uri(),
#                   'current_site': Site.objects.get_current()})


# Replaced by the signin view in the userena app
# def login(request):
#     """If SHA1 password, convert to bcrypt on successful log-in:

#     if request.method == 'POST':
#         form = AuthenticationForm(request.POST)

#         if form.is_valid():
#             user = form.get_user()

#             if user.password.startswith('sha1'):
#                 user.set_password(form['password'])
#                 user.save()

#     https://docs.djangoproject.com/en/1.3/topics/auth/#how-to-log-a-user-in
#     """
#     if request.user.is_authenticated():  # User already logged in
#         return HttpResponseRedirect("/")
#     elif request.method == 'POST':  # Form has submitted
#         username = request.POST.get('username', '')
#         password = request.POST.get('password', '')
#         user     = auth.authenticate(username=username, password=password)
#         if user is not None:  # Credentials correct
#             if user.is_active:  # User is activated
#                 auth.login(request, user)
# #                # Password has not - yet - been converted by bcrypt
# #                if request.user.password.startswith('sha1') and "bcrypt" in settings.INSTALLED_APPS:
# #                    user.set_password(password)
#                 messages.success(request, "You were logged in, %s." % request.user.username)
#                 return HttpResponseRedirect("/")
#             else:  # User is disabled (digitally)
#                 messages.error(request, "Your user account is disabled.")
#                 return HttpResponseRedirect("/disabled/")
#         else:  # Form invalid
#             messages.error(request, "Invalid credentials. Try again.")
#             return HttpResponseRedirect("/invalid/")
#     else:  # User not logged in *and* hasn't submitted the form: clean form
#         return render(request, 'login.html',
#                               {'full_url'    : request.build_absolute_uri(),
#                                'current_site': Site.objects.get_current()})


def logout(request):
    if request.user.is_authenticated():  # User logged in
        auth.logout(request)
    messages.success(request, "Logged out successfully.")
    return HttpResponseRedirect("/")


# Replaced by the `signup` view in the userena app
# def register(request):
#     """Handles user registration.
#
#     Throws an error if passwords or e-mails do not match,
#     and if username and e-mail are not unique.
#     """
#     if request.user.is_authenticated():  # User already logged in
#         return HttpResponseRedirect("/")
#     elif request.method == 'POST':  # Form has been submitted
#         username  = request.POST.get('username', '')
#         email     = request.POST.get('email', '')
#         email2    = request.POST.get('email-verification', '')        
#         password  = request.POST.get('password', '')
#         password2 = request.POST.get('password-verification', '')
#         if password != password2:
#             messages.error(request, "Your two passwords did not match.")
#         elif email != email2:
#             messages.error(request, "Your two e-mail addresses did not match.")            
#         elif email_is_taken(email):
#             messages.error(request, "There is already a user with that e-mail address.")
#         elif username_is_taken(username):
#             messages.error(request, "There is already a user with that name.")
#         else:
#             user = User.objects.create_user(username, email, password)
#             user.save()
#             auth.login(request, auth.authenticate(username=username, password=password))
#             messages.success(request, "Registration complete! Now would be a good time \
#             to check your settings.")
#             return HttpResponseRedirect("/")
#     return render(request, 'register.html',  # Clean form on first visit
#                           {'full_url'    : request.build_absolute_uri(),
#                            'current_site': Site.objects.get_current()})


@login_required(login_url=LOGIN_URL)
def settings(request):
    """Place for the user to change and manage his or her user settings."""
    if request.is_ajax() and request.method == "POST":  # Changes submitted
        messages.success(request, "New settings saved.")
        HttpResponse("Done!")
    
    return render(request, 'settings.html', {'current_site': Site.objects.get_current()})


#@login_required(login_url=LOGIN_URL)
#def saves_and_bookmarks(request, object_type):
#    """Shows the user's saved posts and/or bookmarked threads."""
#    if object_type == "save":
#        objects = request.user.saves.all()
#    else:  # Bookmarks
#        objects = request.user.bookmarks.all()