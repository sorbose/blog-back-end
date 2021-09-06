import os
import random
import traceback
from queue import Queue

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError
from django.db.models import Q as djQ
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.views import View
from django.core import serializers
from django.utils.decorators import method_decorator
from django.db import transaction
import json
from django.db.models import QuerySet
from rest_framework import generics

import article
from .models import *
from account.models import BlogUser
from django.http.request import HttpRequest
from django.http.response import HttpResponseForbidden, HttpResponse


# Create your views here.

def JSONCORS(success: bool, data: dict):
    data['success'] = success
    return JsonResponse(data=data, headers={'Access-Control-Allow-Origin': '*',
                                            'Access-Control-Allow-Headers': '*',
                                            'Access-Control-Allow-Credentials': 'true'})


def checkLogin(func):
    def wrapper(request, *args, **kwargs):
        is_login = request.user.is_authenticated
        if is_login:
            return func(request, *args, **kwargs)
        else:
            return HttpResponse('not logged in', status=401)

    return wrapper


def checkAdmin(func):
    def wrapper(request, *args, **kwargs):
        is_admin = request.user.is_superuser
        if is_admin:
            return func(request, *args, **kwargs)
        else:
            return HttpResponse("You're not a super user", status=403)

    return wrapper


class TagCreateView(View):
    @method_decorator(checkLogin)
    def get(self, req: HttpRequest):
        try:
            Tag.objects.create(name=req.GET.get('name'), describe=req.GET.get('desc'))
        except IntegrityError as e:
            return JSONCORS(False, {'msg': str(e)})
        return JSONCORS(True, {'tag_name': req.GET.get('name')})


class TagDeleteView(View):
    @method_decorator(checkAdmin)
    def get(self, req: HttpRequest):
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
    @method_decorator(checkAdmin)
    def get(self, req: HttpRequest):
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
    @method_decorator(checkLogin)
    def get(self, req: HttpRequest):
        try:
            Category.objects.create(name=req.GET.get('name'), describe=req.GET.get('desc'))
        except IntegrityError as e:
            return JSONCORS(False, {'msg': str(e)})
        return JSONCORS(True, {'tag_name': req.GET.get('name')})


class CategoryDeleteView(View):
    @method_decorator(checkAdmin)
    def get(self, req: HttpRequest):
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
    @method_decorator(checkAdmin)
    def get(self, req: HttpRequest):
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
    @transaction.atomic
    def post(self, req: HttpRequest):
        now = timezone.now()
        is_public = req.POST.get('is_public')
        if is_public == None:
            is_public = 1
        try:
            tags_name = tuple(req.POST['tag'].split(';'))
            title = req.POST['title']
            category = req.POST['category']
        except MultiValueDictKeyError as e:
            return JSONCORS(False, {'msg': 'MultiValueDictKeyError' + str(e)})

        Category.objects.get_or_create(name=category)
        category = Category.objects.get(name=category)

        for t in tags_name:
            Tag.objects.get_or_create(name=t)
        tags = Tag.objects.filter(name__in=tags_name)

        article = Article.objects.create(title=title, author=req.user,
                                         summary=req.POST.get('summary'), content_HTML=req.POST.get('content_HTML'),
                                         content=req.POST.get('content'), create_time=now,
                                         category_name=category,
                                         is_public=is_public)
        article.tag_name.set(tags)
        for i in range(len(tags)):
            tags[i].update_number_with_this(1)
        category.update_number_with_this(1)
        return JSONCORS(True, {'id': article.id, 'title': article.title, 'time': now})


class ArticleDeleteView(View):
    @transaction.atomic
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
        year = obj.create_time.year
        month = obj.create_time.month
        ac = ArticleArchive.objects.get(year=year, month=month)
        ac.count -= 1
        ac.save()
        obj.delete()
        return JSONCORS(True, {'msg': 'successfully deleted', 'id': id, 'author': str(author)})


class ArticleUpdateView(View):
    @transaction.atomic
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
        field = ['title', 'summary', 'content', 'content_HTML', 'is_public', 'category', 'tag']
        for f in field:
            parms = req.POST.get(f)
            if parms is not None:
                dic[f] = parms
        if dic == {}:
            return JSONCORS(False, {'msg': 'no fields'})
        try:
            if 'category' in dic.keys():
                old_category = obj.category_name
                new_category, success = Category.objects.get_or_create(name=dic['category'])
                obj.category_name = new_category
                obj.save()
                Category.objects.get(name=new_category.name).update_number_with_this(1)
                Category.objects.get(name=old_category.name).update_number_with_this(-1)
            if 'tag' in dic.keys():
                old_tags_name = []

                for tag in obj.tag_name.all():
                    old_tags_name.append(tag.name)
                old_tags = Tag.objects.filter(name__in=tuple(old_tags_name))
                for new_tag in tuple(dic['tag'].split(';')):
                    Tag.objects.get_or_create(name=new_tag)
                new_tags = Tag.objects.filter(name__in=tuple(dic['tag'].split(';')))
                obj.tag_name.set(new_tags)
                for i in range(len(new_tags)):
                    new_tags[i].update_number_with_this(1)
                for i in range(len(old_tags)):
                    old_tags[i].update_number_with_this(-1)
        except ObjectDoesNotExist as e:
            return JSONCORS(False, {'msg': str(e) + " Please check whether the tag and category exist"})
        if 'title' in dic.keys():
            obj.title = dic['title']
        if 'summary' in dic.keys():
            obj.summary = dic['summary']
        if 'content' in dic.keys():
            obj.content = dic['content']
        if 'content_HTML' in dic.keys():
            obj.content_HTML = dic['content_HTML']
        if 'is_public' in dic.keys():
            obj.is_public = dic['is_public']
        obj.update_time = now
        obj.save()
        return JSONCORS(True, {'time': now})


def get_ip_address(request: HttpRequest):
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        ip = request.META.get("HTTP_X_FORWARDED_FOR")
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class ArticleBrowseView(View):
    def get(self, req: HttpRequest):
        now = timezone.now()
        id = req.GET.get('id')
        try:
            article = Article.objects.filter(id=id)
            if not article:
                return JSONCORS(False, {'msg': 'no result'})
        except ValueError as e:
            return JSONCORS(False, {'msg': 'ValueError: ' + str(e)})
        if req.user.is_authenticated:
            user = req.user
        else:
            user = None
        if int(article[0].is_public) != 1 and article[0].author != user and not user.is_superuser:
            return JSONCORS(True, {'data': '', 'msg': '作者设置了仅自己可见'})
        BrowseRecord.objects.create(user=user, ip=get_ip_address(req), article=article[0], time=now)
        article[0].page_view += 1
        article[0].save()
        return JSONCORS(True, {'data': json.loads(
            serializers.serialize("json", article, use_natural_foreign_keys=True, use_natural_primary_keys=True))})


class Auther_ArticleQueryView(View):
    def get(self, req: HttpRequest):
        author = req.GET.get('author')
        if author is None:
            return JSONCORS(False, {'msg': 'author field is None'})
        author = tuple(author.split(';'))
        try:
            authors = BlogUser.objects.filter(username__in=author)
        except ValueError as e:
            return JSONCORS(False, {'msg': 'ValueError: ' + str(e)})
        res = {}
        for author in authors:
            articles_author = res[author.username] = []
            for article in author.article_set.all():
                articles_author.append(article.pk)
        return JSONCORS(True, {'article_id': res})


class LastestArticlesView(View):
    def get(self, req: HttpRequest):
        num = req.GET.get('num')
        try:
            num = int(num)
        except ValueError:
            return JSONCORS(False, {'msg': 'Invalid parameter "num" for int() with base 10'})
        if req.GET.get('author') is None:
            articles = Article.objects.raw \
                ('select id from article_article order by id desc limit {};'.format(num))
        else:
            try:
                author = BlogUser.objects.get(username=req.GET.get('author'))
            except ObjectDoesNotExist as e:
                return JSONCORS(False, {'msg': 'author does not exist'})
            articles = Article.objects.raw \
                ('select id from article_article where author_id={} order by id desc limit {};'.format(author.id, num))
        res = []
        for a in articles:
            res.append(a.id)
        return JSONCORS(True, {'article_id': res})


class SearchArticlesView(View):
    def get(self, req: HttpRequest):
        q = req.GET.get('q')
        if not q:
            return JSONCORS(False, {'msg': '请输入搜索关键词'})
        objs = Article.objects.values('id', 'is_public', 'author').filter(
            djQ(title__icontains=q) | djQ(content__icontains=q))
        res = []
        for obj in objs:
            if int(obj['is_public']) != 1 and req.user.id != obj['author'] and not req.user.is_superuser:
                continue
            res.append(obj['id'])
        return JSONCORS(True, {'data': res})


class AdvancedSearchArticlesView(View):
    @method_decorator(checkLogin)
    def get(self, req: HttpRequest):
        conditions = {}
        disabled_field = ['browserecord', 'page', 'num', 'sort']
        for field in req.GET:
            if field in disabled_field:
                continue
            conditions[field] = req.GET[field]
        sort_fields = tuple(req.GET.get('sort', '').split(';'))
        objs = Article.objects.filter(**conditions).filter(djQ(is_public=1) | djQ(author=req.user))
        if sort_fields[0] != '':
            objs = objs.order_by(*sort_fields)

        page = int(req.GET.get('page', 1))
        num = int(req.GET.get('num', 5))
        paginator = Paginator(objs, num)
        try:
            res = paginator.page(page)  # 获取当前页码的记录
        except PageNotAnInteger:
            res = paginator.page(1)
        except (EmptyPage, InvalidPage):
            res = {}
        return JSONCORS(True, {'data': json.loads(serializers.serialize("json", res))})


class ArticleArchiveView(View):
    def get(self, req: HttpRequest):
        aas = ArticleArchive.objects.all()
        return JSONCORS(True, {'data': json.loads(serializers.serialize("json", aas))})


class CommentCreate(View):
    @method_decorator(checkLogin)
    def post(self, req: HttpRequest):
        article_id = req.POST.get('article_id')
        content = req.POST.get('content')
        now = timezone.now()
        reply_to_id = req.POST.get('reply_to')
        user = req.user
        level = req.POST.get('level')
        toUser = req.POST.get('toUser')
        if toUser:
            toUser = BlogUser.objects.get(id=toUser)
        try:
            article = Article.objects.get(id=article_id)
            reply_to = Comment.objects.get(id=reply_to_id)
        except ObjectDoesNotExist as e:
            reply_to = None
            # return JSONCORS(False, {'msg': str(e)})
        try:
            com = Comment.objects.create(article=article, content=content, date=now, reply_to=reply_to, username=user,
                                         level=level, toUser=toUser)
        except IntegrityError as e:
            return JSONCORS(False, {'msg': str(e)})
        return JSONCORS(True, {'data': {'article_id': article_id, 'comment_id': com.id}})


class CommentDelete(View):
    @method_decorator(checkLogin)
    def post(self, req: HttpRequest):
        comment_id = req.POST.get('comment_id')
        try:
            comment = Comment.objects.get(id=comment_id)
        except ObjectDoesNotExist as e:
            return JSONCORS(False, {'msg': str(e)})
        user = req.user
        if user != comment.username and user != comment.article.author and not user.is_superuser \
                and comment.reply_to is not None and user != comment.reply_to.username:
            return JSONCORS(False, {'msg': 'No permission to delete'})
        comment.delete()
        return JSONCORS(True, {})


class CommentQuery(View):
    def get_a_comment_by_id(self, req: HttpRequest):
        comment_id = req.GET.get('comment_id')
        try:
            comment = Comment.objects.filter(id=comment_id)
        except ObjectDoesNotExist as e:
            return JSONCORS(False, {'msg': str(e)})
        return JSONCORS(True, {'data': json.loads(serializers.serialize("json", comment))})

    def get_comments_by_article(self, req: HttpRequest):
        article_id = req.GET.get('article_id')
        try:
            article = Article.objects.get(id=article_id)
        except ObjectDoesNotExist as e:
            return JSONCORS(False, {'msg': str(e)})
        if req.GET.get('only_id') is not None:
            res = []
            for comment in article.comment_set.all():
                res.append(comment.pk)
            return JSONCORS(True, {'data': res})
        else:
            res = []
            comments = Comment.objects.filter(article__id=article_id).order_by('-date')
            for comment in comments:
                if comment.level != 0:
                    continue
                obj = {
                    'author': {
                        'id': str(comment.username.id),
                        'nickname': str(comment.username.username),
                        'avatar': str(comment.username.avatar.url)
                    },
                    'content': str(comment.content),
                    'createDate': str(comment.date),
                    'id': comment.id,
                    'level': comment.level,
                    'childrens': []
                }
                res.append(obj)
            for comment in comments:
                if comment.level == 0:
                    continue
                obj = {
                    'author': {
                        'id': str(comment.username.id),
                        'nickname': str(comment.username.username)
                    },
                    'content': str(comment.content),
                    'createDate': str(comment.date),
                    'id': comment.id,
                    'level': comment.level,
                    'childrens': []
                }
                for i in res:
                    if i['id'] == comment.reply_to.id:
                        if comment.level == 2:
                            obj['toUser'] = {
                                'id': str(comment.toUser.id),
                                'nickname': str(comment.toUser.username)
                            }
                        i['childrens'].append(obj)
                        break
            return JSONCORS(True, {'data': res})

    def get_comments_reply_to(self, req: HttpRequest):
        comment_id = req.GET.get('comment_id')  # 该字段为None时查询的是reply_to为null的评论
        article_id = req.GET.get('article_id')
        if req.GET.get('only_id') is not None:
            comments = Comment.objects.values('id').filter(article__id=article_id, reply_to__id=comment_id)
            res = []
            for c in comments:
                res.append(c['id'])
            return JSONCORS(True, {'data': {'id': res}})
        else:
            res = []
            comments = Comment.objects.filter(article__id=article_id, reply_to__id=comment_id).order_by('date')
            return JSONCORS(True, {'data': res})

    def get(self, req: HttpRequest):
        type = req.GET.get('type')
        if type == 'get_a_comment_by_id':
            return self.get_a_comment_by_id(req)
        elif type == 'get_comments_by_article':
            return self.get_comments_by_article(req)
        elif type == 'get_comments_reply_to':
            return self.get_comments_reply_to(req)
        return JSONCORS(False, {'msg': '没有查询type字段'})


class BrowseRecordQuery(View):
    @method_decorator(checkAdmin)
    def get(self, req: HttpRequest):
        conditions = {}
        for field in req.GET:
            conditions[field] = req.GET[field]
        brs = BrowseRecord.objects.filter(**conditions)
        return JSONCORS(True, {'data': json.loads(serializers.serialize("json", brs))})


def generate_random_str(randomlength=8):
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


@transaction.atomic
def upload_file(request: HttpRequest):
    if request.method == "POST":
        myFile = request.FILES.get("image", None)

        path = os.path.join("static/media/article_img", generate_random_str() + '_' + myFile.name)
        destination = open(path, 'wb+')  # 打开特定的文件进行二进制的写操作
        for chunk in myFile.chunks():
            destination.write(chunk)
        destination.close()
        return JSONCORS(True, {'path': path})


from .serializers import ArticleListSerializer, ArticleDetailSerializer
from .pagination import ArticleListPagination
from .filter import ArticleFilter
from blog_admin.views import Success
from rest_framework import permissions


class ArticleList(generics.ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleListSerializer
    filter_class = ArticleFilter
    search_fields = ('title', 'content', 'author__username', 'tag_name__name')
    ordering_fields = ('create_time', 'page_view')
    pagination_class = ArticleListPagination

    def get(self, request, *args, **kwargs):
        author=request.user
        if author.id==self.request.user.id:
            self.queryset = Article.objects.all()
        else:
            self.queryset = Article.objects.filter(is_public=1)
        return Success(super(ArticleList, self).get(request, *args, **kwargs))


class ArticleCreate(generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return super(ArticleCreate, self).post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
