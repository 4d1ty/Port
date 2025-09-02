from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .forms import StoryForm, StoryLinkForm, ReplyStoryForm
from notifications.models import Notification
from .models import Story
from .utils import (
    rate_limit_story_submission,
    rate_limit_story_replies,
    rate_limit_story_replies_time_left,
    rate_limit_story_submission_time_left,
)


@login_required
def submit_story(request):
    if rate_limit_story_submission(request.user):
        messages.error(
            request, f"You are submitting stories too quickly. Please wait {rate_limit_story_submission_time_left(request.user)} seconds."
        )
        return redirect("core:home")

    if request.method == "POST":
        form = StoryForm(request.POST)
        if form.is_valid():
            story = form.save(commit=False)
            story.created_by = request.user
            story.save()
            messages.success(request, "Story added successfully!")
            return redirect("core:home")
    form = StoryForm()
    return render(request, "story/submit_story.html", {"form": form})


@login_required
def submit_story_link(request):
    if request.method == "POST":
        form = StoryLinkForm(request.POST)
        if form.is_valid():
            story = form.save(commit=False)
            story.created_by = request.user
            story.save()
            messages.success(request, "Story added successfully!", extra_tags="ok")
            return redirect("core:home")
    form = StoryLinkForm(request.GET)
    return render(request, "story/submit_story.html", {"form": form})


def story_detail(request, pk):
    story = get_object_or_404(Story, pk=pk)
    reply_form = ReplyStoryForm()
    return render(
        request, "story/story_detail.html", {"story": story, "rform": reply_form}
    )


@login_required
def delete_story(request, pk):
    story = get_object_or_404(Story, pk=pk, created_by=request.user)
    if request.method == "POST":
        story.delete()
        messages.warning(request, "Story deleted successfully!", extra_tags="ok")
        return redirect("core:home")
    return render(request, "story/delete_story.html", {"story": story})


@login_required
def reply_story(request, pk):
    if rate_limit_story_replies(request.user):
        messages.error(
            request, f"You are replying to stories too quickly. Please wait {rate_limit_story_replies_time_left(request.user)} seconds."
        )
        return redirect("core:home")

    story = get_object_or_404(Story, pk=pk)
    if request.method == "POST":
        form = ReplyStoryForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.reply_to = story
            reply.created_by = request.user
            reply.save()
            Notification.notify(
                recipient=story.created_by,
                actor=reply.created_by,
                verb="replied",
                object_type="story",
                object_id=reply.pk,
            )
            messages.success(request, "Reply added successfully!", extra_tags="ok")
            return redirect("story_detail", story.pk)

    return render(request, "story/reply_story_form.html", {"rform": form})


@login_required
def vote_story(request, pk):
    story = get_object_or_404(Story, pk=pk)
    story.vote(request.user)
    return render(request, "story/islands/votes.html", {"story": story})


def search_story(request):
    if query := request.GET.get("q", None):
        stories = Story.objects.filter(
            Q(title__icontains=query)
            | Q(url__icontains=query)
            | Q(content__icontains=query)
            | Q(created_by__username__icontains=query)
        )
        return render(
            request, "story/search_story.html", {"query": query, "stories": stories}
        )
    return redirect("core:home")
