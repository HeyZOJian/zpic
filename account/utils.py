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