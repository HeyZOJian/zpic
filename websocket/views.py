from django.shortcuts import render
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
# Create your views here.
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from . import utils as ws_utils
from rest_framework.response import Response
import logging
import json
logger = logging.getLogger()


@login_required
@api_view(['GET','DELETE'])
def notice(request):
    if request.method == 'GET':
        result = {}
        notice_list = ws_utils.get_all_unread_notice(request.user.id)
        return Response(notice_list)
    elif request.method == 'DELETE':
        notice_id = request.GET.get('notice_id')
        if notice_id:
            ws_utils.read_notice(request.user.id, notice_id)
        return Response("ok")


