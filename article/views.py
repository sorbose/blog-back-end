import traceback

from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError
from django.db.models import Q as djQ
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.views import View
from django.core import serializers
import json

import article
from .models import *
from account.models import BlogUser
from django.http.request import HttpRequest
from django.http.response import HttpResponseForbidden


# Create your views here.

def JSONCORS(success: bool, data: dict):
    data['success'] = success
    return JsonResponse(data=data, headers={'Access-Control-Allow-Origin': '*',
                                            'Access-Control-Allow-Headers': '*',
                                            'Access-Control-Allow-Credentials': 'true'})


class TagCreateView(View):
    def get(self, req: HttpRequest):
        if not req.user.is_superuser:
            return HttpResponseForbidden('need superuser access')
        try:
            Tag.objects.create(name=req.GET.get('name'), describe=req.GET.get('desc'))
        except IntegrityError as e:
            return JSONCORS(False, {'msg': str(e)})
        return JSONCORS(True, {'tag_name': req.GET.get('name')})


class TagDeleteView(View):
    def get(self, req: HttpRequest):
        if not req.user.is_superuser:
            return HttpResponseForbidden('need superuser access')
        try:
            name = req.GET.get('name')
            obj = Tag.objects.get(name=name)
            obj.delete()
        except ObjectDoesNotExist as e:
            return JSONCORS(False, {'msg': str(e)})
        return JSONCORS(True, {'deleted': name})


class TagQueryView(View):
    def get(self, req: HttpRequest):
        if req.GET.get('all') == '1':
            return JSONCORS(True, {'data': list(Tag.objects.all().values())})
        obj = Tag.objects.filter(name=req.GET.get('name'))
        return JSONCORS(True, {'data': list(obj.values())})


class TagUpdateView(View):
    def get(self, req: HttpRequest):
        if not req.user.is_superuser:
            return HttpResponseForbidden('need superuser access')
        try:
            name = req.GET.get('name')
            new_desc = req.GET.get('new_desc')
            obj = Tag.objects.get(name=name)
            obj.desc = new_desc
            obj.save()
        except ObjectDoesNotExist as e:
            return JSONCORS(False, {'msg': str(e)})
        return JSONCORS(True, {'name': name, 'new_desc': obj.desc})


class CategoryCreateView(View):
    def get(self, req: HttpRequest):
        if not req.user.is_superuser:
            return HttpResponseForbidden('need superuser access')
        try:
            Category.objects.create(name=req.GET.get('name'), describe=req.GET.get('desc'))
        except IntegrityError as e:
            return JSONCORS(False, {'msg': str(e)})
        return JSONCORS(True, {'tag_name': req.GET.get('name')})


class CategoryDeleteView(View):
    def get(self, req: HttpRequest):
        if not req.user.is_superuser:
            return HttpResponseForbidden('need superuser access')
        try:
            name = req.GET.get('name')
            obj = Category.objects.get(name=name)
            obj.delete()
        except ObjectDoesNotExist as e:
            return JSONCORS(False, {'msg': str(e)})
        return JSONCORS(True, {'deleted': name})


class CategoryQueryView(View):
    def get(self, req: HttpRequest):
        if req.GET.get('all') == '1':
            return JSONCORS(True, {'data': list(Category.objects.all().values())})
        obj = Category.objects.filter(name=req.GET.get('name'))
        return JSONCORS(True, {'data': list(obj.values())})


class CategoryUpdateView(View):
    def get(self, req: HttpRequest):
        if not req.user.is_superuser:
            return HttpResponseForbidden('need superuser access')
        try:
            name = req.GET.get('name')
            new_desc = req.GET.get('new_desc')
            obj = Category.objects.get(name=name)
            obj.desc = new_desc
            obj.save()
        except ObjectDoesNotExist as e:
            return JSONCORS(False, {'msg': str(e)})
        return JSONCORS(True, {'name': name, 'new_desc': obj.desc})


class CategoryResetCountView(View):
    def get(self, req: HttpRequest):
        try:
            name = req.GET.get('name')
            obj = Category.objects.get(name=name)
            old_number = obj.number_with_this
            obj.reset_number_with_this()
            new_number = obj.number_with_this
        except ObjectDoesNotExist as e:
            return JSONCORS(False, {'msg': str(e)})
        return JSONCORS(True, {'old': old_number, 'new': new_number})


class TagResetCountView(View):
    def get(self, req: HttpRequest):
        try:
            name = req.GET.get('name')
            obj = Tag.objects.get(name=name)
            old_number = obj.number_with_this
            obj.reset_number_with_this()
            new_number = obj.number_with_this
        except ObjectDoesNotExist as e:
            return JSONCORS(False, {'msg': str(e)})
        return JSONCORS(True, {'old': old_number, 'new': new_number})


class ArticleCreateView(View):
    def post(self, req: HttpRequest):
        now = timezone.now()
        is_public = req.POST.get('is_public')
        if is_public == None:
            is_public = 1
        try:
            category = Category.objects.get(name=req.POST['category'])
            tags = Tag.objects.filter(name__in=tuple(req.POST['tag'].split(';')))
        except ObjectDoesNotExist as e:
            return JSONCORS(False, {'msg': str(e) + " Please check whether the tag and category exist"})
        except MultiValueDictKeyError as e:
            return JSONCORS(False,{'msg':'MultiValueDictKeyError'+str(e)})
        try:
            article = Article(title=req.POST['title'], author=req.user,
                              content=req.POST['content'], create_time=now,
                              category_name=category,
                              is_public=is_public)
        except MultiValueDictKeyError as e:
            return JSONCORS(False, {'msg': 'MultiValueDictKeyError: lack ' + str(e)})
        article.save()
        article.tag_name.set(tags)
        for i in range(len(tags)):
            tags[i].update_number_with_this(1)
        category.update_number_with_this(1)
        return JSONCORS(True, {'id': article.id, 'title': article.title, 'time': now})


class ArticleDeleteView(View):
    def post(self, req: HttpRequest):
        try:
            id = req.POST['id']
            obj = Article.objects.get(id=id)
        except MultiValueDictKeyError as e:
            return JSONCORS(False, {'msg': 'MultiValueDictKeyError: lack ' + str(e)})
        except ObjectDoesNotExist as e:
            return JSONCORS(False, {'msg': 'ObjectDoesNotExist: ' + str(e), 'id': id})
        if obj.author != req.user and (not req.user.is_superuser):
            return HttpResponseForbidden('You do not have permission to delete this article.')
        for tag in obj.tag_name.all():
            tag.update_number_with_this(-1)
        Category.objects.get(name=obj.category_name.name).update_number_with_this(-1)
        author = obj.author
        obj.delete()
        return JSONCORS(True, {'msg': 'successfully deleted', 'id': id, 'author': str(author)})


class ArticleUpdateView(View):
    def post(self, req: HttpRequest):
        try:
            id = req.POST['id']
            obj = Article.objects.get(id=id)
        except MultiValueDictKeyError as e:
            return JSONCORS(False, {'msg': 'MultiValueDictKeyError: lack ' + str(e)})
        except ObjectDoesNotExist as e:
            return JSONCORS(False, {'msg': 'ObjectDoesNotExist: ' + str(e), 'id': id})
        if obj.author != req.user:
            return HttpResponseForbidden('You are not the author of this article')
        now = timezone.now()
        dic = {}
        field = ['title', 'content', 'is_public','category_name', 'tag_name']
        for f in field:
            parms = req.POST.get(f)
            if parms is not None:
                dic[f] = parms
        if dic=={}:
            return JSONCORS(False,{'msg':'no fields'})
        try:
            if 'category_name' in dic.keys():
                old_category = obj.category_name
                new_category = Category.objects.get(name=dic['category_name'])
                obj.category_name = new_category
                obj.save()
                Category.objects.get(name=new_category.name).update_number_with_this(1)
                Category.objects.get(name=old_category.name).update_number_with_this(-1)
            if 'tag_name' in dic.keys():
                old_tags_name = []
                for tag in obj.tag_name.all():
                    old_tags_name.append(tag.name)
                old_tags = Tag.objects.filter(name__in=tuple(old_tags_name))
                new_tags = Tag.objects.filter(name__in=tuple(dic['tag_name'].split(';')))
                obj.tag_name.set(new_tags)
                for i in range(len(new_tags)):
                    new_tags[i].update_number_with_this(1)
                for i in range(len(old_tags)):
                    old_tags[i].update_number_with_this(-1)
        except ObjectDoesNotExist as e:
            return JSONCORS(False, {'msg': str(e) + " Please check whether the tag and category exist"})
        if 'title' in dic.keys():
            obj.title =dic['title']
        if 'content' in dic.keys():
            obj.content = dic['content']
        if 'is_public' in dic.keys():
            obj.is_public = dic['is_public']
        obj.update_time=now
        obj.save()
        return JSONCORS(True,{'time':now})

def get_ip_address(request:HttpRequest):
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        ip = request.META.get("HTTP_X_FORWARDED_FOR")
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

class ArticleBrowseView(View):
    def get(self,req:HttpRequest):
        now = timezone.now()
        id=req.GET.get('id')
        try:
            article=Article.objects.filter(id=id)
            if not article:
                return JSONCORS(False,{'msg':'no result'})
        except ValueError as e:
            return JSONCORS(False, {'msg': 'ValueError: ' + str(e)})
        if req.user.is_authenticated:
            user=req.user
        else:
            user=None
        if int(article[0].is_public)!=1 and article[0].author!=user and not user.is_superuser:
            return JSONCORS(True,{'data':'','msg':'作者设置了仅自己可见'})
        BrowseRecord.objects.create(user=user,ip=get_ip_address(req),article=article[0],time=now)
        article[0].page_view+=1
        article[0].save()
        return JSONCORS(True,{'data':json.loads(serializers.serialize("json", article))})

class Auther_ArticleQueryView(View):
    def get(self,req:HttpRequest):
        author=req.GET.get('author')
        if author is None:
            return JSONCORS(False,{'msg':'author field is None'})
        author=tuple(author.split(';'))
        try:
            authors=BlogUser.objects.filter(username__in=author)
        except ValueError as e:
            return JSONCORS(False, {'msg': 'ValueError: ' + str(e)})
        res= {}
        for author in authors:
            articles_author=res[author.username]=[]
            for article in author.article_set.all():
                articles_author.append(article.pk)
        return JSONCORS(True,{'article_id':res})

class LastestArticlesView(View):
    def get(self,req:HttpRequest):
        num=req.GET.get('num')
        try:
            num=int(num)
        except ValueError:
            return JSONCORS(False,{'msg':'Invalid parameter "num" for int() with base 10'})
        if req.GET.get('author') is None:
            articles = Article.objects.raw \
                ('select id from article_article order by id desc limit {};'.format(num))
        else:
            try:
                author=BlogUser.objects.get(username=req.GET.get('author'))
            except ObjectDoesNotExist as e:
                return JSONCORS(False, {'msg': 'author does not exist'})
            articles=Article.objects.raw\
                ('select id from article_article where author_id={} order by id desc limit {};'.format(author.id,num))
        res=[]
        for a in articles:
            res.append(a.id)
        return JSONCORS(True,{'article_id':res})

class SearchArticlesView(View):
    def get(self,req:HttpRequest):
        q = req.GET.get('q')
        if not q:
            return JSONCORS(False,{'msg':'请输入搜索关键词'})
        objs=Article.objects.values('id','is_public','author').filter(djQ(title__icontains=q)|djQ(content__icontains=q))
        res=[]
        for obj in objs:
            if int(obj['is_public'])!=1 and req.user.id!=obj['author'] and not req.user.is_superuser:
                continue
            res.append(obj['id'])
        return JSONCORS(True, {'data':res})

class CommentCreate(View):
    def post(self,req:HttpRequest):
        article_id=req.POST.get('article_id')
        content=req.POST.get('content')
        now=timezone.now()
        reply_to=req.POST.get('reply_to')
        user=req.user
        try:
            article=Article.objects.get(id=article_id)
        except ObjectDoesNotExist as e:
            return JSONCORS(False,{'msg':str(e)})
        com=Comment.objects.create(article=article,content=content,date=now,reply_to=reply_to,username=user)
        return JSONCORS(True,{'data':{'article_id':article_id,'comment_id':com.id}})


