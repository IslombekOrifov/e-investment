from django.db import models
from django.utils.timezone import now


class News(models.Model):
    title = models.CharField(max_length=256)
    body = models.TextField()
    image = models.ImageField(upload_to='files/news/', default='default.jpg')
    date_created = models.DateTimeField(blank=True, null=True, default=None)

    def save(self, *args, **kwargs):
        self.date_created = now()
        return super(News, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.title
