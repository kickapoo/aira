Aira: An Irrigation Advisor

Aira is a web application that calculates soil water balance in order
to provide the users with irrigation advice. Its input should be
prepared with [pthelma](http://pthelma.readthedocs.org/). It is under
heavy development.

How to run a development instance:

  1. Copy or symlink `aira_project/settings/local-example.py` to
     `aira_project/settings/local.py`.

  2. Set `DJANGO_SETTINGS_MODULE=aira_project.settings.local`

  3. Execute `python manage.py migrate`.

  4. Execute `python manage.py loaddata en.json`.

  5. Execute `python manage.py demo_user`.

  6. Execute `python manage.py runserver`.

Copyright (C) 2014-2015 TEI of Epirus

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.
