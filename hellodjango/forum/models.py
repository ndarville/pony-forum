import datetime

from django.contrib.auth.models import User
from django.db                  import models
from django.db.models.signals   import post_save


# Accessed by UserProfile.get_formatting_buttons_display()
# minus the () for a template
# 
# FORMATTING_BUTTON_CHOICES = (
#     ('Text Decoration', (
#             ('EM',   'Emphasized'),
#             ('I',    'Italic'),
#             ('S',    'Strong'),
#         )
#     ),
#     ('Lists', (
#             ('OL',   'Ordered list'),    
#             ('UL',   'Unordered list'),
#         )
#     ),
#     ('References', (
#         #    ('FN',   'Footnote'),
#             ('IMG',  'Image'),
#             ('URL',  'Linkification'),
#         )
#     ),
#     ('Code', (
#             ('CODE', 'Code'),
#             ('PRE',  'Multi-line code'),
#         )
#     ),
#     ('Quote', 'Block quote'),
# )


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
    title_plain  = models.CharField(max_length=50)
    title_html   = models.TextField()
##  description  = models.CharField(max_length=70)
#   thread_count = models.IntegerField(default=0) 
#   post_count   = models.IntegerField(default=0)
    #: The sequential placement of the category in the "home" page
##  position     = models.AutoField(unique=True)
    #: M2M user who has chosen to hide the category in the home view
#   hider        = models.ManyToManyField(User, null=True, blank=True
#                                         related_name="hidden_categories")

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
    creation_date     = models.DateTimeField()
    latest_reply_date = models.DateTimeField()
    title_plain       = models.CharField(max_length=70)
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
#   hider             = models.ManyToManyField(User, null=True, blank=True,
#                                              related_name="hidden_threads")
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

    relative_date.short_description = "Latest post"


class Post(models.Model):
    """The reply of a user in a thread. Or its opening post (OP)."""
    creation_date = models.DateTimeField()
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
    creation_date  = models.DateTimeField()
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
    avatar          = models.ImageField(null=True, blank=True,
                                           upload_to="avatars")
    has_dyslexia    = models.BooleanField(default=False,
                                             verbose_name="User has dyslexia")
    has_epilepsy    = models.BooleanField(default=False,
                                             verbose_name="User has epilepsy")
#   post_count      = models.IntegerField(default=0)
#   thread_count    = models.IntegerField(default=0)
##  formatting_buttons = models.BooleanField(default=True)
    #! Automatically subscribe to a thread after posting in it.
    auto_subscribe  = models.BooleanField(default=False,
                                             verbose_name="Automatically subscribe \
                                             to threads posted in")
##  buddies         = models.ManyToManyField(User, null=True, blank=True,
##                                           related_name="buddies")
    ignores         = models.ManyToManyField(User, null=True, blank=True,
                                             related_name="ignores")
    follows         = models.ManyToManyField(User, null=True, blank=True,
                                             related_name="follows")
#   twitter        = models.CharField(blank=True)
#   timezone       = models.CharField(choices=TIMEZONES")

    def __unicode__(self):
        return "%s's profile" % self.user

def create_user_profile(sender, instance, created, **kwargs):
    """Used to extend User using aforementioned UserProfile model."""
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

## If you have not done so already, add this line without the "# " to settings.py:
# AUTH_PROFILE_MODULE = 'forum.UserProfile'
##### UserProfile section END #####
