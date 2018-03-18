from image.models import Image, Comment
from image.serializers import ImageSerializer, CommentSerializer
from utils import redis_utils
from rest_framework.renderers import JSONRenderer

def get_image_info(image_id):
    pass

def get_image_comment(image_id, page, len):
    data = Comment.objects.filter(image_id=image_id).filter(stauts=0).order_by('-create_time')
    nums = data.__len__()
    comments = CommentSerializer(data, many=True)
    return nums, comments.data[page*len:(page+1)*len]
