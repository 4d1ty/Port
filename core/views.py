from django.shortcuts import render
from story.models import Story
from .utils import paginate


def frontpage(request):
    stories = Story.objects.filter(reply_to__isnull=True).order_by("-created_on")
    paginated_stories = paginate(request, stories)
    return render(request, "core/frontpage.html", {"stories": paginated_stories})
