# ZPIC
仿Instagram网站
Django + Django REST framework + PostgreSQL + Redis

## TODO：
- ~~图片标签~~
- ~~图片评论~~
- ~~图片点赞~~
- ~~个人资料设置~~
- ~~查看朋友圈~~
- ~~搜索用户~~
- 上线获取离线消息
- 持久化通知消息
- 删除已读通知
- vue上传图片

## redis

1.图片点赞
like:<图片id>

类型 | key
--- | --- 
set | 用户nickname

2.图片浏览量 

周浏览量 views:week

月浏览量 views:month

类型 | key | score
--- | --- | ---
zset | 图片id | 图片浏览量



- 访问量，点赞量，评论量超过阀值在写入数据库


