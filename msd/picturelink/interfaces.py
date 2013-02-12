from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from msd.picturelink import picturelinkMessageFactory as _

# -*- extra stuff goes here -*-

class IPictureLink(Interface):
    """A short description, an image and a link"""
