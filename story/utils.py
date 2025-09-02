from django.utils import timezone
from .models import Story


def rate_limit_story_submission(user):
    recent_stories = list(
        Story.objects.filter(created_by=user, reply_to__isnull=True)
        .order_by("-created_on")[:5]
    )
    if len(recent_stories) < 5:
        return False
    oldest = recent_stories[-1].created_on
    seconds_since_oldest = (timezone.now() - oldest).total_seconds()
    return seconds_since_oldest <= 300  # 5 minutes


def rate_limit_story_replies(user):
    recent_replies = list(
        Story.objects.filter(created_by=user, reply_to__isnull=False)
        .order_by("-created_on")[:20]
    )
    if len(recent_replies) < 20:
        return False
    oldest = recent_replies[-1].created_on
    seconds_since_oldest = (timezone.now() - oldest).total_seconds()
    return seconds_since_oldest <= 300  # 5 minutes


def rate_limit_story_submission_time_left(user):
    recent_stories = list(
        Story.objects.filter(created_by=user, reply_to__isnull=True)
        .order_by("-created_on")[:5]
    )
    if len(recent_stories) < 5:
        return 0
    oldest = recent_stories[-1].created_on
    seconds_since_oldest = (timezone.now() - oldest).total_seconds()
    return round(max(0, 300 - seconds_since_oldest))


def rate_limit_story_replies_time_left(user):
    recent_replies = list(
        Story.objects.filter(created_by=user, reply_to__isnull=False)
        .order_by("-created_on")[:20]
    )
    if len(recent_replies) < 20:
        return 0
    oldest = recent_replies[-1].created_on
    seconds_since_oldest = (timezone.now() - oldest).total_seconds()
    return round(max(0, 300 - seconds_since_oldest))



def should_increase_karma_for_submission(user):
    return not rate_limit_story_submission(user)


def should_increase_karma_for_reply(user):
    return not rate_limit_story_replies(user)