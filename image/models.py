from django.db import models
from account.models import User
# Create your models here.


class Image(models.Model):
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='images')
    img_url = models.URLField(blank=False)
    title = models.CharField(max_length=256,blank=True)
    create_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.author) + ":" + str(self.img_url)