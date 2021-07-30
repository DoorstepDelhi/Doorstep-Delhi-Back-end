from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from webtraffic.choices import (
    website_category_choices,
    traffic_source_choices,
    website_hit_type_choices,
    website_status_choices,
)


class Website(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    name = models.CharField(max_length=256, null=True, blank=True)
    url = models.URLField()
    timer = models.PositiveIntegerField()
    category = models.CharField(max_length=5, choices=website_category_choices)
    daily_hits = models.PositiveSmallIntegerField()
    total_hits = models.PositiveIntegerField()
    status = models.CharField(max_length=5, choices=website_status_choices)
    traffic_source = models.CharField(max_length=5, choices=traffic_source_choices)
    high_quality = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    page_scroll = models.BooleanField(default=False)
    clicks = models.BooleanField(default=False)
    reload_page = models.BooleanField(default=False)

    cost_per_visit = models.PositiveIntegerField()

    def __str__(self):
        if self.name:
            return self.name
        return self.url


class WebsiteHit(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    website = models.ForeignKey("webtraffic.Website", on_delete=models.CASCADE, related_name='website_hits')
    type = models.CharField(max_length=1, choices=website_hit_type_choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.website)


@receiver(pre_save, sender=Website)
def my_call(sender, instance, *args, **kwargs):
    cost = 2 * instance.timer
    if instance.category == "WS":
        cost += 10
    elif instance.category == "P":
        cost += 25
    elif instance.category == "A":
        cost += 20

    if instance.high_quality:
        cost += 40
    if instance.page_scroll:
        cost += 20
    if instance.clicks:
        cost += 20
    if instance.reload_page:
        cost += 20
    instance.cost_per_visit = cost
