from django.db import models
from django.utils import timezone
# Create your models here.
from django.db.models import UniqueConstraint


class Tag(models.Model):
    name = models.CharField(max_length=10, primary_key=True)
    describe = models.TextField(null=True)
    number_with_this = models.IntegerField(null=False,default=0)
    def update_number_with_this(self,change):
        self.number_with_this+=change
        self.save()
    def reset_number_with_this(self):
        self.number_with_this=Article.objects.filter(tag_name=self.name).count()
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=15, primary_key=True)
    describe = models.TextField(null=True)
    number_with_this = models.IntegerField(null=False,default=0)
    def update_number_with_this(self,change):
        self.number_with_this+=change
        self.save()
    def reset_number_with_this(self):
        self.number_with_this=Article.objects.filter(category_name=self.name).count()
        self.save()

class ArticleManager(models.Manager):
    def create(self,**kwargs):
        create_time=kwargs.get('create_time')
        if not create_time:
            create_time = timezone.now()
        aa = ArticleArchive.objects.get_or_create(year=create_time.year, month=create_time.month)[0]
        aa.count+=1
        aa.save()
        print()
        return super(ArticleManager, self).create(**kwargs)
    def delete(self,**kwargs):
        print(self.pk)
        return super(ArticleManager, self).delete(**kwargs)

class Article(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey('account.BlogUser', on_delete=models.RESTRICT)
    summary = models.TextField(null=True)
    content = models.TextField(null=True)
    content_HTML = models.TextField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(null=True,auto_now=True)
    category_name = models.ForeignKey('Category', on_delete=models.RESTRICT)
    tag_name = models.ManyToManyField('Tag')
    repost_num = models.IntegerField(default=0)
    page_view=models.IntegerField(default=0)
    is_public = models.SmallIntegerField(default=1)
    comment_num = models.IntegerField(default=0)
    objects=ArticleManager()

    # def save(self):
    #     super(Article,self).save()
    #     aa=ArticleArchive.objects.get_or_create(year=self.create_time.year,month=self.create_time.month)
    #     aa.count+=1
    #     aa.save()
    #     self.save()


class CommentManager(models.Manager):
    def create(self,**kwargs):
        article = kwargs.get('article',None)
        if article:
            article.comment_num += 1
            article.save()
            print("文章评论数量++")
        return super(CommentManager, self).create(**kwargs)

    def delete(self,**kwargs):
        article = kwargs.get('article', None)
        if article:
            article.comment_num -= 1
            article.save()
        return super(CommentManager, self).delete(**kwargs)


class Comment(models.Model):
    article = models.ForeignKey('Article', on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField()
    reply_to = models.ForeignKey('Comment', null=True,on_delete=models.CASCADE)
    username = models.ForeignKey('account.BlogUser', on_delete=models.RESTRICT)
    level = models.IntegerField(default=0)
    toUser = models.ForeignKey('account.BlogUser', on_delete=models.RESTRICT,related_name='toUser',null=True)
    objects = CommentManager()


class BrowseRecord(models.Model):
    user=models.ForeignKey('account.BlogUser',on_delete=models.RESTRICT)
    ip=models.GenericIPAddressField()
    article=models.ForeignKey('Article',on_delete=models.CASCADE)
    time=models.DateTimeField()

class ArticleArchiveManager(models.Manager):
    def get_or_create(self,**kwargs):
        aa,created=super(ArticleArchiveManager, self).get_or_create(**kwargs)
        count = Article.objects.filter(create_time__year=aa.year,create_time__month=aa.month).count()
        aa.count=count
        aa.save()
        return aa,created

class ArticleArchive(models.Model):
    year=models.SmallIntegerField()
    month=models.SmallIntegerField()
    count=models.IntegerField(default=0)
    objects=ArticleArchiveManager()

    # def save(self):
    #     super(ArticleArchive,self).save()
    #     count=Article.objects.filter(create_time__year=self.year,create_time__month=self.month).count()
    #     self.count=count
    #     self.save()


