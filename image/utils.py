from image.models import Image, Comment
from image.serializers import ImageSerializer, CommentSerializer
from utils import redis_utils
from rest_framework.renderers import JSONRenderer
from account import utils as account_utils
from account.models import User
from account.serializers import UserIndexSerializer
import re


def get_nickname_from_content(content):
    nickname_list = re.findall(r"@(\S+)", content)
    user_id_dict = {}
    for nickname in nickname_list:
        user = User.objects.filter(nickname=nickname)
        if user:
            user = User.objects.get(nickname=nickname)
            info = UserIndexSerializer(user).data
            user_id_dict[nickname] = info.get('id')
    return user_id_dict

def get_page_and_len(request, default_page, default_len):
    page = default_page
    len = default_len
    if request.GET.__len__() == 2:
        page = int(request.GET.get('page')) - 1
        len = int(request.GET.get('len'))
    return page,len


def get_image_info(user_id, image_id):
    info = redis_utils.get_image_info(image_id)
    if info == None:
        image = Image.objects.get(id=image_id)
        serializer = ImageSerializer(image)
        print(serializer.data)
        redis_utils.set_image_info(serializer.data)
        info = eval(JSONRenderer().render(serializer.data))
    info['comment_num'] = get_image_comments_num(image_id)
    info['like_num'] = get_image_likes_num(image_id)
    info['view_num'] = redis_utils.get_views_num(image_id)
    info['author'] = account_utils.get_user_info(user_id=info.get('author'))
    info['is_like']  = redis_utils.have_liked_image(user_id,image_id)
    redis_utils.add_view_num(image_id)
    return info


def get_image_comments_num(image_id):
    data = Comment.objects.filter(image_id=image_id).filter(stauts=0).order_by('-create_time')
    return data.__len__()


def get_image_comments(image_id, page, len):
    nums, info = redis_utils.get_comments(image_id, page, len)
    info = [eval(i) for i in info]
    if not info:
        data = Comment.objects.filter(image_id=image_id).filter(stauts=0).order_by('-create_time')
        nums = data.__len__()
        comments = CommentSerializer(data, many=True)
        info = eval(JSONRenderer().render(comments.data))[page*len:(page+1)*len]
        for i in info:
            user_id = i['publisher']
            user_info = account_utils.get_user_info(user_id)
            i['publisher_nickname'] = user_info.get('nickname')
            i['publisher_id'] = user_info.get('id')
            redis_utils.add_comments(image_id,i)
    return {'num':nums, 'comments': info}


def add_image_comment(image_id, user, content, reply):
    image = Image.objects.get(id=image_id)
    comment = Comment(publisher=user, content=content, image=image)
    comment.save()
    comment_info = CommentSerializer(comment).data
    comment_info['reply'] = reply
    comment_info['publisher_nickname'] = user.nickname
    comment_info['publisher_id'] = user.id
    print(comment_info)
    redis_utils.add_comments(image_id, comment_info)

def get_image_likes_num(image_id):
    users = redis_utils.get_image_likes(image_id)
    return users.__len__()

def get_image_likes(image_id, page, len):
    users = redis_utils.get_image_likes(image_id)
    return users.__len__(),users[page*len : (page+1)*len]