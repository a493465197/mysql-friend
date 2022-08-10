import code
from django.shortcuts import render
from requests import delete
from scrapy import cmdline
import random
import os
# Create your views here.
from django.db import connection
from django.http import HttpResponse
from django.http import JsonResponse
from newsWeb import models
import json

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def getInfo(request):
    if request.COOKIES.get('username') == None:
        return HttpResponse(json.dumps({}))

    ret = models.users.objects.filter(username = request.COOKIES.get('username')).values()
    ret = list(ret)

    return HttpResponse(json.dumps({
        'code': 0,
        'value': ret[0]
    }))

def reg(request):
    models.users(**json.loads(request.body)).save()
    return HttpResponse(json.dumps({'code': 0, 'msg': '注册成功'}))

def addDoc(request):
    count = models.movies.objects.filter(**{'title': json.loads(request.body).get('title')}).count()
    if count == 0:
        models.movies(**json.loads(request.body)).save()
        return HttpResponse(json.dumps({'code': 0, 'msg': 'add success'}))

    else:
        return HttpResponse(json.dumps({'code': -1, 'msg': 'has same movies'}))

    

def addRating(request):
    body = json.loads(request.body)
    h = models.rating.objects.filter(**{'username': body.get('username'), 'title': body.get('title')})
    print(h.count())
    if h.count() != 0:
        h.update(**body)
    else:
        models.rating(**body).save()
    # models.movies.up(**json.loads(request.body)).save()
    userRate = models.rating.objects.filter(**{'username': body.get('username')}).order_by('-rating',).values()[0]
    user = models.users.objects.filter(**{'username': body.get('username')})
    movie = models.movies.objects.get(**{'title': userRate.get('title')})
    temp = user[0].like_movies + ',' + movie.genre
    user.update(**{'like_movies': ','.join(list(set(temp.split(','))))})
    user.update(**{'like_movies_title': movie.title})
    return HttpResponse(json.dumps({'code': 0, 'msg': 'rating success'}))

def login(request):
    body = json.loads(request.body)
    print(models.users.objects.filter(username = body.get('username'), password = body.get('password')))
    if models.users.objects.filter(username = body.get('username'), password = body.get('password')).count() > 0:
        h = HttpResponse(json.dumps({'code': 0, 'msg': '登录成功'}))
    else:
        h = HttpResponse(json.dumps({'code': -1, 'msg': '登录失败'}))
    h.set_cookie('username', body.get('username'))
    return h

def isLogin(request):
    user = request.COOKIES.get('username')
    print(user)
    if user:
        return JsonResponse({
            'code': 0
        })
    else:
        return JsonResponse({
            'code': 1
        })


def docList(request):
    ret = models.movies.objects.filter().order_by('time').values()
    cur = connection.cursor()
    cur.execute("SELECT *,SUM(r.rating)/count(r.rating) rating_avg,m.title title FROM newsweb_movies m left JOIN newsweb_rating r ON m.title = r.title GROUP BY m.title")
    res = dictfetchall(cur)
    return JsonResponse({
        'code': 0,
        'value': res
    })

def updateDoc(request):
    body = json.loads(request.body)

    h = models.newsina.objects.get(**{'id1': body.get('id1')})
    h.update(**{'content': body.get('content')})
    h.save()

    return HttpResponse(json.dumps({
        'code': 0,
        'value': 'ok'
    }))
def setInfo(request):
    body = json.loads(request.body)

    h = models.users.objects.get(**{'username': body.get('currUser') or body.get('username')})
    if body.get('currUser'):
        body.pop('currUser')
    h.update(**body)
    h.save()

    return HttpResponse(json.dumps({
        'code': 0,
        'value': 'ok'
    }))

def hendleGet(request):
    body = json.loads(request.body)
    id1 = str(random.random())[2:10]
    # cmdline.execute('scrapy crawl newsina_spider'.split())
    if body.get('value') == 'xl':
        models.run(**{'type': '新浪网', 'username': request.COOKIES.get('username'), 'id1': id1}).save()
        os.system('scrapy crawl newsina_spider -a id1=' + id1)
    if body.get('value') == 'tx':
        models.run(**{'type': '腾讯网', 'username': request.COOKIES.get('username'), 'id1': id1}).save()
        os.system('scrapy crawl qq_spider -a id1=' + id1)
    if body.get('value') == 'rm':
        models.run(**{'type': '人民网', 'username': request.COOKIES.get('username'), 'id1': id1}).save()
        os.system('scrapy crawl rm_spider -a id1=' + id1)
    return HttpResponse(json.dumps({
        'code': 0,
        'value': 'ok'
    }))


def runList(request):
    ret = models.run.objects().values().limit(200).order_by('-time')
    for i in ret:
        i['id'] = ''
    ret = list(ret)
    return HttpResponse(json.dumps({
        'code': 0,
        'value': ret
    }))

def logout(request):
    h = HttpResponse(json.dumps({'code': 0, 'msg': '登出成功'}))
    h.delete_cookie('username')
    return h

def userList(request):
    ret = models.users.objects.filter().values().limit(200)
    for i in ret:
        i['id'] = ''
    ret = list(ret)
    return HttpResponse(json.dumps({
        'code': 0,
        'value': ret
    }))

def delUser(request):
    body = json.loads(request.body)
    ret = models.users.objects.get(**{'username': body.get('username')})
    ret.delete()
    ret.save()
    return HttpResponse(json.dumps({
        'code': 0,
    }))

def delDoc(request):
    body = json.loads(request.body)
    ret = models.newsina.objects.get(**{'id1': body.get('id1')})
    ret.delete()
    ret.save()
    return HttpResponse(json.dumps({
        'code': 0,
    }))

def addTag(request):
    body = json.loads(request.body)
    ret = models.newsina.objects().values().limit(200)
    flag = False
    for i in ret:
        i['id'] = ''
        if i.get('content').find(body.get('value')) >= 0:
            flag = True
            findItem = models.newsina.objects.get(**{'id1': i['id1']})
            findItem.update(**{'keywords': findItem['keywords'] + ',' + body.get('value')})
            findItem.update(**{'lids': findItem['lids'] + ',' + body.get('value')})
            findItem.save()
    ret = list(ret)
    if flag:
        return HttpResponse(json.dumps({
            'code': 0,
        }))
    else:
        return HttpResponse(json.dumps({
            'code': -1,
            'msg': '没有找到相关新闻'
        }))
