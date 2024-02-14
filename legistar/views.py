from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.utils import timezone
from legistar.models import Legislation, Person, ActionVote, LegislationAction


def group_by(objs, key):
    result = []
    for obj in objs:
        if len(result) == 0:
            result.append((key(obj), [obj]))
        elif result[-1][0] == key(obj):
            result[-1][1].append(obj)
        else:
            result.append((key(obj), [obj]))
    return result


def legislation(request, file_number):
    template = loader.get_template("legislation/legislation.html")
    legislation = Legislation.objects.get(file_number=file_number)
    context = {"legislation": legislation}
    return HttpResponse(template.render(context, request))


def person(request, id_):
    template = loader.get_template("legislation/person.html")
    person = Person.objects.get(id=id_)
    person_votes = ActionVote.objects.filter(person=person).order_by("-action__date")[
        :100
    ]
    context = {
        "person": person,
        "votes": person_votes,
        "legislation": person.legislation_set.all()[:50],
    }
    return HttpResponse(template.render(context, request))


def index(request):
    template = loader.get_template("legislation/index.html")
    legislation_active = (
        Legislation.objects.filter(status__in=["ENACTED", "ADOPTED"])
        .exclude(legislation_type="COMMUNICATION")
        .order_by("-final_action")[:40]
    )
    legislation = Legislation.objects.exclude(
        legislation_type="COMMUNICATION"
    ).order_by("-created")[:20]
    actions = LegislationAction.objects.exclude(
        legislation__legislation_type="COMMUNICATION"
    ).exclude(
        date__gte=timezone.now()
    ).order_by("-date")
    context = {
        "active": group_by(legislation_active, lambda x: x.final_action),
        "legislation": group_by(legislation, lambda x: x.created),
        "actions": group_by(actions, lambda x: x.date),
    }
    return HttpResponse(template.render(context, request))


def githash(request):
    return HttpResponse(settings.GIT_HASH, content_type="text/plain")
