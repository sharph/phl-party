from django.db import models
from autoslug import AutoSlugField

# Create your models here.


class Person(models.Model):
    name = models.CharField(max_length=70)
    slug = AutoSlugField(populate_from="name", unique=True)

    def __repr__(self):
        return f"<Person: {self.name}>"


class Legislation(models.Model):
    title = models.TextField()
    legistar_id = models.IntegerField()
    legistar_guid = models.CharField(max_length=100)
    file_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=50)
    legislation_type = models.CharField(max_length=20)
    created = models.DateField()
    final_action = models.DateField(null=True)
    sponsors = models.ManyToManyField(Person)

    @property
    def text(self):
        return (
            LegislationText.objects.filter(legislation=self)
            .order_by("-updated")[0]
            .text
        )

    @property
    def text_html(self):
        return (
            LegislationText.objects.filter(legislation=self)
            .order_by("-updated")[0]
            .text_html
        )

    @property
    def actions(self):
        return LegislationAction.objects.filter(legislation=self).order_by(
            "-date", "-id"
        )

    def __str__(self):
        return f"<{self.legislation_type}: {self.title[:50]}>"


class LegislationText(models.Model):
    legislation = models.ForeignKey("Legislation", models.CASCADE)
    text = models.TextField()
    text_html = models.TextField(null=True)
    updated = models.DateTimeField(auto_now_add=True)


class LegislationAction(models.Model):
    legislation = models.ForeignKey("Legislation", models.CASCADE)
    action = models.CharField(max_length=100)
    action_text = models.TextField(null=True)
    action_by = models.CharField(max_length=200, null=True)
    result = models.CharField(max_length=100)
    date = models.DateField()
    mover = models.ForeignKey("Person", models.CASCADE, null=True, related_name="mover")
    seconder = models.ForeignKey(
        "Person", models.CASCADE, null=True, related_name="seconder"
    )

    @property
    def votes(self):
        return ActionVote.objects.filter(action=self)


class ActionVote(models.Model):
    action = models.ForeignKey("LegislationAction", models.CASCADE)
    person = models.ForeignKey("Person", models.CASCADE)
    vote = models.CharField(max_length=20)


def import_legislation(legislation, legistar_id, legistar_guid):
    legislation_obj, _ = Legislation.objects.update_or_create(
        file_number=legislation["file_number"],
        defaults={
            "title": legislation["title"],
            "legistar_id": legistar_id,
            "legistar_guid": legistar_guid,
            "status": legislation["status"],
            "legislation_type": legislation["type"],
            "created": legislation["created"],
            "final_action": legislation["final_action"],
        },
    )
    LegislationText.objects.get_or_create(
        legislation=legislation_obj,
        text=legislation["text"],
        defaults={"text_html": legislation["text_html"]},
    )
    sponsors = []
    if legislation["sponsors"] is not None:
        for sponsor in legislation["sponsors"]:
            sponsors.append(Person.objects.get_or_create(name=sponsor)[0])
    legislation_obj.sponsors.set(sponsors)
    for action in legislation["actions"]:
        action_obj, _ = LegislationAction.objects.update_or_create(
            legislation=legislation_obj,
            date=action["date"],
            action=action["action"],
            defaults={
                "action_by": action["action_by"],
                "action_text": action["action_text"] if "action_text" in action else "",
                "result": action["result"],
                "mover": None
                if "mover" not in action or action["mover"] == ""
                else Person.objects.get_or_create(name=action["mover"])[0],
                "seconder": None
                if "seconder" not in action or action["seconder"] == ""
                else Person.objects.get_or_create(name=action["seconder"])[0],
            },
        )
        if "votes" in action:
            for voter, vote in action["votes"].items():
                ActionVote.objects.update_or_create(
                    action=action_obj,
                    person=Person.objects.get_or_create(name=voter)[0],
                    defaults={"vote": vote},
                )
    return legislation_obj
