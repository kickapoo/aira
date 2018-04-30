#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Note
# A patch command that iters database Agrifields to check Agrifield name unique.
# If not, renames to include Agrifield id and slugify
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from aira.models import Agrifield


class Command(BaseCommand):
    help = "Patch Rename Agrifield to be unique"

    def handle(self, *args, **options):
        names = list(set([af.name for af in Agrifield.objects.all()]))
        for name in names:
            if Agrifield.objects.filter(name=name).count() > 1:
                for af in Agrifield.objects.filter(name=name):
                    af.name = "{}-{}".format(af.name.encode('utf-8'), af.pk)
                    af.slug = slugify(af.name)
                    af.save()
        self.stdout.write('Agrifields names are updated... :)')
