"""Definition of the Picture Link content type
"""
import urlparse
from urllib import quote

from zope.interface import implements, directlyProvides

from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from AccessControl import ClassSecurityInfo


from Products.CMFCore.utils import getToolByName

from Products.Archetypes import atapi
from Products.Archetypes.interfaces import IObjectPostValidation

from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.configuration import zconf


from Products.validation import V_REQUIRED

from msd.picturelink import picturelinkMessageFactory as _
from msd.picturelink.interfaces import IPictureLink
from msd.picturelink.config import PROJECTNAME


PictureLinkSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.TextField(
        name='description',
        storage = atapi.AnnotationStorage(),
        required=False,
        accessor='getHTMLDescription',
        searchable=1,
        #default='',
        validators = ('isTidyHtmlWithCleanup',),
        #validators = ('isTidyHtml',),
        default_output_type = 'text/x-html-safe',
        widget=atapi.RichWidget(
            label=_(u"Summary"),
            description=_(u"A short piece of text, use the Additional field for a very long entry"),
            rows = 10,
            allow_buttons=(
                'bg-basicmarkup',
                'bold-button',
                'italic-button',
                'bg-drawers',
                'linklibdrawer-button',
                'linkdrawer-button',
                ),
        ),
    ),

    atapi.TextField(
        name='text',
        storage = atapi.AnnotationStorage(),
        required=False,
        searchable=1,
        #default='',
        schemata ='default',
        validators = ('isTidyHtmlWithCleanup',),
        #validators = ('isTidyHtml',),
        default_output_type = 'text/x-html-safe',
        widget=atapi.RichWidget(
            label=_(u"Additional Text"),
            description=_(u"For a longer description, enter text here"),
            rows = 25,
        ),
    ),
    

    atapi.ImageField(
        name='image',
        storage = atapi.AnnotationStorage(),
        required=False,
        #searchable=1,
        #default='',
        #schemata ='default',
        max_size = 'no',
        sizes= {'large'   : (768, 768),
                'preview' : (400, 400),
                'mini'    : (200, 200),
                'thumb'   : (128, 128),
                'tile'    :  (64, 64),
                'icon'    :  (32, 32),
                'listing' :  (16, 16),
               },
        validators=(('isNonEmptyFile', V_REQUIRED),
                    ('checkImageMaxSize', V_REQUIRED)),
        widget=atapi.ImageWidget(
            description = _(u'help_pl_image', default=u'Image will be scaled to a sensible size.'),
            label= _(u'label_pl_image', default=u'Image'),
        ),
    ),

    atapi.StringField('imageCaption',
        required = False,
        searchable = True,
        widget = atapi.StringWidget(
            description = '',
            label = _(u'label_image_caption', default=u'Image Caption'),
            size = 40)
        ),

    atapi.StringField(
        name='remoteUrl',
        storage = atapi.AnnotationStorage(),
        required=False,
        #searchable=1,
        default = "http://",
        #schemata ='default',
        widget=atapi.StringWidget(
            description = '',
            label = _(u'label_url', default=u'URL'),
        ),
    ),


))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

PictureLinkSchema['title'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(PictureLinkSchema, folderish=True, moveDiscussion=False)

class PictureLink(folder.ATFolder):
    """A description, image and link"""
    implements(IPictureLink)

    portal_type = "Picture Link"
    schema = PictureLinkSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    security       = ClassSecurityInfo()
    
    
    def __bobo_traverse__(self, REQUEST, name):
        """Give transparent access to image scales. This hooks into the
        low-level traversal machinery, checking to see if we are trying to
        traverse to /path/to/object/image_<scalename>, and if so, returns
        the appropriate image content.
        """
        if name.startswith('image'):
            field = self.getField('image')
            image = None
            if name == 'image':
                image = field.getScale(self)
            else:
                scalename = name[len('image_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return super(PictureLink, self).__bobo_traverse__(REQUEST, name)
        
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        if 'title' not in kwargs:
            kwargs['title'] = self.getImageCaption()
        return self.getField('image').tag(self, **kwargs)
    
    security.declareProtected(View, 'Description')    
    def Description(self):
        """ Override the usual accessor to deal with richtext
        """
        text = self.getField('description').get(self)

        portal_transforms = getToolByName(self, 'portal_transforms')
        data = portal_transforms.convertTo('text/plain', text)

        return data.getData()
    
	security.declareProtected(View, 'getDescription')
    def getDescription(self):
        
        return self.Description()

	security.declareProtected(ModifyPortalContent, 'setRemoteUrl')
    def setRemoteUrl(self, value, **kwargs):
        """remute url mutator

        Use urlparse to sanify the url
        Also see http://dev.plone.org/plone/ticket/3296
        """
        if value:
            value = urlparse.urlunparse(urlparse.urlparse(value))
        self.getField('remoteUrl').set(self, value, **kwargs)


    security.declareProtected(View, 'getRemoteUrl')
    def getRemoteUrl(self):
        """Sanitize output
        """
        value = self.Schema()['remoteUrl'].get(self)
        if not value: value = '' # ensure we have a string
        return quote(value, safe='?$#@/:=+;$,&')


atapi.registerType(PictureLink, PROJECTNAME)
