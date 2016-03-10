from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from image_cropping import ImageRatioField
from easy_thumbnails.files import get_thumbnailer

from citifleet.common.utils import get_full_path


class Benefit(models.Model):
    '''
    Store benefit name, image with cropping and barcode string
    Barcode image is generated in the mobile app
    '''
    image = models.ImageField(_('Card'), upload_to='benefits/')
    name = models.CharField(_('Name'), max_length=255)
    barcode = models.CharField(_('Barcode'), max_length=200)
    cropping = ImageRatioField('image', '1400x900', size_warning=True)

    def __unicode__(self):
        return self.name

    @property
    def image_thumbnail(self):
        '''
        Return url to cropped benefit's image
        '''
        return get_full_path(get_thumbnailer(self.image).get_thumbnail({
            'size': (1400, 900),
            'box': self.cropping,
            'crop': True,
            'detail': True,
        }).url)

    class Meta:
        verbose_name = _('Benefit')
        verbose_name_plural = _('Benefits')
