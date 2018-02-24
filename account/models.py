from django.db import models
from django.contrib.auth.models import AbstractUser


# 用户表
class User(AbstractUser):
    nickname = models.CharField(max_length=32, blank=True, unique=True)
    profile_photo_url = models.URLField(blank=True)
    description = models.CharField(max_length=256 ,blank=True)
    follow_num = models.IntegerField(default=0,blank=True)
    following_num = models.IntegerField(default=0,blank=True)
    image_num = models.IntegerField(default=0,blank=True)

    class Meta:
        pass

    def __str__(self):
        return self.nickname


# 用户关系表
class UserRelationship(models.Model):
    user_a = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_a')
    user_b = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_b')
    relation_type = models.IntegerField(blank=False, default=0)

    class Meta:
        unique_together = ('user_a', 'user_b', 'relation_type')

    def __str__(self):
        relation = ""
        if self.relation_type == 0:
            relation = "关注"
        elif self.relation_type == 1:
            relation = "拉黑"
        elif self.relation_type == 2:
            relation = "互相关注"
        return self.user_a.nickname + relation + self.user_b.nickname
