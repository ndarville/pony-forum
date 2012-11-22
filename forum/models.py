import datetime

from django.contrib.auth.models import User
from django.db                  import models
from django.db.models.signals   import post_save


BOOLEAN_CHOICES = (
    ('Y', 'Yes'),
    ('N', 'No'),
    ('U', 'Undecided'),
)

def relative_date(date):
    """Displays a date relative to now."""
    delta = datetime.datetime.now() - date  # UTC?
    s = delta.seconds
    d = delta.days

    if d == 0:
        if s < 60:
            return "Just now"
        elif s < 120:
            return "1 minute ago"
        elif s < 3600:
            s /= 60
            return "%d minutes ago" % s
        elif s < 7200:
            return "1 hour ago"
        elif s < 86400:
            s /= 3600
            return "%d hours ago" % s
    else:
        if d == 1:
            return "Yesterday"
        elif d < 7:
            return "%d days ago" % d
        elif d == 7:
            return "1 week ago"
        elif d/7 < 4:
            d /= 7
            return "%d weeks ago" % d
        elif d/7 == 4:
            return "One month ago"
        else:
            return date


class Category(models.Model):
    """Contains threads."""
    title_plain  = models.CharField(max_length=50, unique=True,
                                    verbose_name="Plain title")
    title_html   = models.TextField(verbose_name="Formatted title")
##  description  = models.CharField(max_length=70)
#   thread_count = models.IntegerField(default=0)
#   post_count   = models.IntegerField(default=0)
    #: The sequential placement of the category in the "home" page
##  position     = models.AutoField(unique=True)

    class Meta:
        verbose_name_plural = "categories"
        permissions = (
            ("remove_category", "Remove categories"),
            ("merge_category",  "Merge multiple categories together"),
        )

    def __unicode__(self):
        return self.title_plain

    def post_count(self):
        """Shows the number of posts in an entire category."""
        return Post.objects.filter(thread__category = self.id).count()


class Thread(models.Model):
    """Contains posts."""
    creation_date     = models.DateTimeField(default=datetime.datetime.now())
    latest_reply_date = models.DateTimeField(default=datetime.datetime.now())
    title_plain       = models.CharField(max_length=70, unique=True)
    title_html        = models.TextField()
    category          = models.ForeignKey(Category)
    author            = models.ForeignKey(User)
    is_sticky         = models.BooleanField(default=False)
    is_locked         = models.BooleanField(default=False)
    is_removed        = models.BooleanField(default=False)
#   poll              = models.ForeignKey(Poll, null=True, blank=True)
    bookmarker        = models.ManyToManyField(User, null=True, blank=True,
                                               related_name="bookmarks")
    subscriber        = models.ManyToManyField(User, null=True, blank=True,
                                               related_name="subscriptions")
    #: Users granted moderator rights on a per-thread basis
#   threadmins        = models.ManyToManyField(User, null=True, blank=True)

    class Meta:
        ordering = ["-creation_date"]
        permissions = (
            ("remove_thread", "Remove (and restore) threads"),
            ("merge_thread",  "Merge multiple threads together"),
            ("sticky_thread", "Stick a thread to the top of the thread list"),
            ("move_thread",   "Move a thread to another category"),
            ("lock_thread",   "Lock (and unlock) threads"),
#           ("ban_user_in_thread",
#                             "Ban user from posting in thread permanently"),
#           ("timeout_user_in_thread",
#                             "Ban user from posting in thread temporarily"),
            ("is_threadmin",  "Give a user mod-like permissions in a thread"),
        )

    def __unicode__(self):
        return self.title_plain

    def relative_date(self):
        """Shows the time since the last post in a thread."""
        return relative_date(self.latest_reply_date)

##    def create(self, *args, **kwargs):
##        """Alters the default create method for Thread."""
##        now = datetime.datetime.now()
#       self.author = self.request.user
#       self.author.thread_count += 1
#       self.author.save()
#
#       self.category = category # wrong
#       self.category.thread_count +=1
#       self.category.save()
#
#       self.subscriber.add(self.author)
##        self.creation_date = now
##        self.latest_reply_date = now
##        self.title_html = prettify_title(self.title_plain)
##        super(Thread, self).create(*args, **kwargs)

    relative_date.short_description = "Latest post"


class Post(models.Model):
    """The reply of a user in a thread. Or its opening post (OP)."""
    creation_date = models.DateTimeField(default=datetime.datetime.now())
    content_plain = models.TextField()
    content_html  = models.TextField()
    author        = models.ForeignKey(User)
    thread        = models.ForeignKey(Thread)
    co_editors    = models.ManyToManyField(User, null=True, blank=True,
                                           verbose_name="co-editor",
                                           related_name="co-editors")
    agrees        = models.ManyToManyField(User, null=True, blank=True,
                                           related_name="agrees")
    thanks        = models.ManyToManyField(User, null=True, blank=True,
                                           related_name="thanks")
    saves         = models.ManyToManyField(User, null=True, blank=True,
                                           related_name="saves")
    is_removed    = models.BooleanField(default=False)

    class Meta:
        ordering = ["creation_date"]
        permissions = (
            ("remove_post", "Can remove posts"),
        )

    def __unicode__(self):
        end = len(self.content_plain) > 40 and "..." or ""
        return u"%s: %s%s" % (self.author, self.content_plain[:40], end)

    def relative_date(self):
        """Returns the age of the post as a relative date
        between now and creation_date.
        """
        return relative_date(self.creation_date)

#    def create(self, *args, **kwargs):
#        """Alters the default create method for Post."""
#        # https://docs.djangoproject.com/en/1.3/topics/db/managers/
##        now = datetime.datetime.now()
#       self.author = self.request.user
#       self.author.post_count += 1
#       self.author.save()
#
#       if not self.thread:
#           self.thread = thread # wrong
#       self.thread.thread_count +=1
#       self.thread.save()
#
##        self.creation_date = now
#        self.content_plain="The code worked."
#        self.content_html = prettify_title(self.content_plain)
#        if request.user.auto_subscribe:
#            thread.subscriber.add(request.user)
#        super(Post, self).create(*args, **kwargs)


class Subscription(models.Model):
    """Manages all the users subscribed to new posts in threads."""
    subscriber     = models.ManyToManyField(User, related_name="subscriber")
    thread         = models.ManyToManyField(Thread, related_name="subscribed_thread")
    last_read_post = models.ManyToManyField(Post, related_name="latest_read_post")
##  last_read_time = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return u"%s's subscription of %s" % (self.subscriber, self.thread.title_plain)


class Report(models.Model):
    """Model for filing reports against the posts and threads of users."""
    creation_date  = models.DateTimeField(default=datetime.datetime.now())
    reason_short   = models.CharField(max_length=80)
    reason_long    = models.TextField(blank=True)
    author         = models.ForeignKey(User, related_name="reporter")
    thread         = models.ForeignKey(Thread, related_name="thread_reports")
    post           = models.ForeignKey(Post, null=True, blank=True,
                                       related_name="post_reports")
    was_addressed  = models.BooleanField(default=False)
    addressed_by   = models.ForeignKey(User, null=True, blank=True)
    date_addressed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["thread", "creation_date"]
        permissions = (
            ("use_reports", "Can see and dismiss reports"),
        )

    def __unicode__(self):
        return u"%s reported something in %s." % (self.author, self.thread)

    def relative_date(self):
        """Shows the time since the last post in a thread."""
        return relative_date(self.creation_date)
    relative_date.short_description = "Latest post"


class UserProfile(models.Model):
    """Extends the default User model.

    Remember to change your AUTH_PROFILE_MODULE to
    "forum.UserProfile" in settings.py to support it.
    """
    user            = models.OneToOneField(User, related_name="profile")
    post_count      = models.IntegerField(default=0)
    thread_count    = models.IntegerField(default=0)
    #! http://lightbird.net/dbe/forum2.html
    # avatar          = models.ImageField(null=True, blank=True,
    #                                     upload_to="images/avatars/")
    #! Disclose your dyslexia to read a more accessible font
    has_dyslexia    = models.CharField(default='U', max_length=1,
                                       choices=BOOLEAN_CHOICES,
                                       verbose_name="User has dyslexia")
    #! Disclose your epilepsy so animated .gif images are hidden by default
    has_epilepsy    = models.CharField(default='U', max_length=1,
                                       choices=BOOLEAN_CHOICES,
                                       verbose_name="User has epilepsy")
    #! Disclose your colour blindness to benefit from potential future features
    # has_c_blindness = models.BooleanField(default=False,
    #                                       verbose_name="User has epilepsy")
    #! Automatically subscribe to a thread after posting in it.
    auto_subscribe  = models.BooleanField(default=True,
                                          verbose_name="Automatically subscribe \
                                          to threads posted in")
    ignores         = models.ManyToManyField(User, null=True, blank=True,
                                             related_name="ignores")
    follows         = models.ManyToManyField(User, null=True, blank=True,
                                             related_name="follows")
    # timezone        = models.CharField(choices=TIMEZONES")
    twitter         = models.CharField(max_length=20, blank=True)

    def __unicode__(self):
        return "%s's profile" % self.user

def create_user_profile(sender, instance, created, **kwargs):
    """Used to extend User using aforementioned UserProfile model."""
    if created and not kwargs.get('raw', False):
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

## If this has not been done so already,
## add this line without the "# " to settings.py:
# AUTH_PROFILE_MODULE = 'forum.UserProfile'
