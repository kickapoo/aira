#! /usr/bin/env python
# -*- coding: utf-8 -*-

# A patch command that iter database Agrifield to update slug field if not
# exists.

from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from aira.models import Agrifield


class Command(BaseCommand):
    help = "Patch Create Slug Name for Agrifield"

    def handle(self, *args, **options):
        names = list(set([af.name for af in Agrifield.objects.all()]))
        for af in Agrifield.objects.all():
            if af.slug in ['', None]:
                af.slug = slugify(af.name)
                af.save()
        self.stdout.write('Agrifields slug are updated... :)')
