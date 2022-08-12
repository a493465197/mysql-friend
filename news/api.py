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
import datetime
import json
import difflib
import string 
import math
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
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
    return HttpResponse(json.dumps({'code': 0, 'msg': 'Register Success'}))

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
    if models.users.objects.filter(username = body.get('username'), password = body.get('password')).count() > 0:
        h = HttpResponse(json.dumps({'code': 0, 'msg': 'Ligin Success'}))
    else:
        h = HttpResponse(json.dumps({'code': -1, 'msg': 'Ligin Fail'}))
    h.set_cookie('username', body.get('username'))

    #add push
    today = datetime.date.today()
    pushCount = models.push.objects.filter(**{'username': body.get('username'), 'time':today }).count()
    if pushCount == 0:
        users = models.users.objects.filter().values()
        my = models.users.objects.filter(**{'username': body.get('username')}).values()[0]
        ret = []
        for u in users:
            if u.get('username') == body.get('username'):
                continue
            like_movies = difflib.SequenceMatcher(None, my.get('like_movies'), u.get('like_movies')).ratio() /2 
            like_movies_title = difflib.SequenceMatcher(None, my.get('like_movies_title'), u.get('like_movies_title')).ratio() / 2
            # like_age = (20 - math.fabs(my.get('age') - u.get('age')))/100/3.3
            pusername_like_movies = ''
            qs = models.rating.objects.filter(**{'username': u.get('username')})
            if qs.count():
                qslist = list(qs.values())
                qslist.sort(key=lambda it: it['rating'], reverse= True)
                pusername_like_movies = ','.join(map(lambda x: x['title'], qslist[0:2]))
            ret.append({
                'username': my.get('username'),
                'pusername': u.get('username'),
                'time': today,
                'like': like_movies+like_movies_title,
                'like_movies_title': like_movies_title*2,
                # 'like_age': like_age,
                'like_movies': like_movies*2,
                'pusername_like_movies': pusername_like_movies,
            })
        ret.sort(key=lambda it: it['like'], reverse=True)
        ret[0:9]
        print(ret[0:9])
        for p in ret[0:9]:
            models.push(**p).save()
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

def getMyPush(request):
    ret = models.movies.objects.filter().order_by('time').values()
    today = datetime.date.today().strftime("%Y-%m-%d")
    user = request.COOKIES.get('username')
    cur = connection.cursor()
    cur.execute("SELECT *,p.like_age p_like_age,p.like_movies p_like_movies,p.like_movies_title p_like_movies_title FROM `newsweb_push` p LEFT JOIN newsweb_users u ON u.username = p.pusername WHERE p.username = '" + user +"'" + "and p.time='" + today + "'")
    res = dictfetchall(cur)
    return JsonResponse({
        'code': 0,
        'value': res
    })

def getMyChat(request):
    user = request.COOKIES.get('username')
    cur = connection.cursor()
    
    sql = "SELECT * FROM `newsweb_message` WHERE time IN (SELECT MAX(time) FROM `newsweb_message` GROUP BY username, pusername HAVING pusername='"+user+"')"
    cur.execute(sql)
    res = dictfetchall(cur)
    return JsonResponse({
        'code': 0,
        'value': res
    })

def send(request):
    body = json.loads(request.body)
    models.message(**body).save()
    return JsonResponse({
        'code': 0,
        # 'value': 1
    })

def getMessage(request):
    body = json.loads(request.body)

    res = models.message.objects.filter(**{'username__in': [request.COOKIES.get('username'),body.get('pusername')],'pusername__in': [request.COOKIES.get('username'),body.get('pusername')]}).order_by('time').values()
    return JsonResponse({
        'code': 0,
        'value': list(res)
    })

def upload(request):
    file = request.FILES.get("file", None)
    r = str(random.random())
    destination = open(os.path.join(BASE_DIR,'media',r+file.name),'wb+')
    for chunk in file.chunks():      # 分块写入文件
        destination.write(chunk)
        destination.close()
    return HttpResponse(json.dumps({
        'code': 0,
        'value': '/assets/'+r+file.name
    }))

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
