from image.models import Image, Comment
from image.serializers import ImageSerializer, CommentSerializer
from utils import redis_utils
from rest_framework.renderers import JSONRenderer
from account import utils as account_utils


def get_image_info(image_id):
    info = redis_utils.get_image_info(image_id)
    if info == None:
        image = Image.objects.get(id=image_id)
        serializer = ImageSerializer(image)
        print(serializer.data)
        redis_utils.set_image_info(serializer.data)
        info = eval(JSONRenderer().render(serializer.data))
    info['content_num'] = get_image_comments_num(image_id)
    info['like_num'] = get_image_likes_num(image_id)
    info['author'] = account_utils.get_user_info(user_id=info.get('author'))
    redis_utils.add_view_num(image_id)
    return info


def get_image_comments_num(image_id):
    data = Comment.objects.filter(image_id=image_id).filter(stauts=0).order_by('-create_time')
    return data.__len__()

def get_image_comments(image_id, page, len):
    data = Comment.objects.filter(image_id=image_id).filter(stauts=0).order_by('-create_time')
    nums = data.__len__()
    comments = CommentSerializer(data, many=True)
    info = eval(JSONRenderer().render(comments.data))[page*len:(page+1)*len]
    for i in info:
        user_id = i['publisher']
        user_info = account_utils.get_user_info(user_id)
        i['publisher'] = user_info
    return nums, info


def get_image_likes_num(image_id):
    users = redis_utils.get_image_likes(image_id)
    return users.__len__()

def get_image_likes(image_id, page, len):
    users = redis_utils.get_image_likes(image_id)
    return users.__len__(),users[page*len : (page+1)*len]