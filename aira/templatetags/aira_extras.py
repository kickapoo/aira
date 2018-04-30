from django.contrib.auth.models import User
from django import template

register = template.Library()


def user_or_supervisor(logged_user, kwargs_username):
    """
     Return user, supervised
    """
    if logged_user.username == kwargs_username:
        user = logged_user
        supervised = False
    else:
        user = User.objects.get(username=kwargs_username)
        supervised = True
    return (user, supervised)


@register.inclusion_tag('tags/menu.html')
def menu(logged_user, kwargs, url_name):
    """
        Top Menu
    """

    this_user, supervised = user_or_supervisor(logged_user,
                                               logged_user.username)
    if 'username' in kwargs:
        this_user, supervised = user_or_supervisor(logged_user,
                                                   kwargs['username'])
    return {
        'user': this_user,
        'supervised': supervised,
        'url_name': url_name
    }


@register.inclusion_tag('tags/list_supervised_users.html')
def supervised_users_list(logged_user, kwargs_username):
    """
        Supervised
    """
    return {
        'user': logged_user,
        'request_to_view_user_field': kwargs_username,
    }


@register.inclusion_tag('tags/is_virtual.html')
def virtual(agrifield):
    return {
        'agrifield': agrifield,
    }


@register.inclusion_tag('tags/map.html')
def leaflet_map():
    """Creates the container for Leaflet Map display.
       CSS container selector id: map-box ex. $('#map-box')
       CSS map selector id: map ex.$('#map')
    """
    return


@register.inclusion_tag('tags/agrifields_as_cards.html')
def agrifields_as_cards(object_list):
    return {
        'object_list': object_list
    }
