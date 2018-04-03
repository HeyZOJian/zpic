from .models import User
from .serializers import UserSimpleSerializer
from utils import redis_utils

def get_user_info(user_id):
    info = redis_utils.get_user_info(user_id)
    if info == None:
        user = User.objects.get(id=user_id)
        serializer = UserSimpleSerializer(user)
        info = serializer.data
        redis_utils.set_user_info(user_id, info)
    return info

def get_page_and_len(request, default_page, default_len):
    page = default_page
    len = default_len
    if request.GET.__len__() == 2:
        page = int(request.GET.get('page')) - 1
        len = int(request.GET.get('len'))
    return page,len