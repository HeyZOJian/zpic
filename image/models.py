from django.db import models
from account.models import User
# Create your models here.


class Image(models.Model):
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='images')
    img_url = models.URLField(blank=False)
    title = models.CharField(max_length=512, blank=True)
    create_time = models.DateTimeField(auto_now=True)
    comment_num = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return str(self.author) + ":" + str(self.img_url)


class Comment(models.Model):
    """
    评论表
    """
    publisher =  models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='comments')
    # reply_id = models.IntegerField(blank=True)
    # reply_nickname = models.CharField(max_length=24, blank=True)
    content = models.CharField(max_length=256, blank=False)
    create_time = models.DateTimeField(auto_now=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='comments')
    stauts = models.IntegerField(default=0)

    def __str__(self):
        return str(self.publisher)+":"+self.content