from django.db import models


class DDAHFile(models.Model):
    title = models.CharField(max_length=256)
    file = models.FileField(upload_to='compromisos')

    def __unicode__(self):
        return self.title
