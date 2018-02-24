# -*- coding: utf-8 -*-

from qiniu import Auth, put_file, etag
import time
import os
#需要填写你的 Access Key 和 Secret Key
access_key = 'ywOK01u24Qmi2LJqWQJ5wv3AuQFlq8h5m9kW9way'
secret_key = 'iBNSQJiguA-Rq0psHjZroFTwK12Ry2FWrJDwlx9M'

#构建鉴权对象
q = Auth(access_key, secret_key)

#要上传的空间
bucket_name = 'zpic'

bucket_url = 'p4lixx258.bkt.clouddn.com'


def upload_to_qiniu_and_get_url(obj):

    filename = str(time.time()).replace('.', '-') + '.png'
    localfile = os.getcwd()+'/upload/'+filename
    f = open(os.getcwd() + '/upload/' + filename, "wb")
    for line in obj.chunks():
        f.write(line)
    f.close()
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, filename, 3600)
    ret, info = put_file(token, filename, localfile)
    if ret:
        os.remove(localfile)
    return "http://"+bucket_url+"/"+filename