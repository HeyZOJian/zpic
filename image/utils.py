from image.models import Image
from image.serializers import ImageSerializer
from utils import redis_utils


def get_image_info(image_id):
    info = redis_utils.get_image_info(image_id)
    if info == None:
        image = Image.objects.get(id=image_id)
        info = ImageSerializer(image).data
        redis_utils.set_image_info(info)
    redis_utils.add_view_num(image_id)
    return info