from django.db import models


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


class Article(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey('account.BlogUser', on_delete=models.RESTRICT)
    summary = models.TextField(null=True)
    content = models.TextField(null=True)
    content_HTML = models.TextField(null=True)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField(null=True,default=None)
    category_name = models.ForeignKey('Category', on_delete=models.RESTRICT)
    tag_name = models.ManyToManyField('Tag')
    repost_num = models.IntegerField(default=0)
    page_view=models.IntegerField(default=0)
    is_public = models.SmallIntegerField(default=1)
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using,
             update_fields=update_fields)
        print(self.author)


class Comment(models.Model):
    article = models.ForeignKey('Article', on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField()
    reply_to = models.ForeignKey('Comment', null=True,on_delete=models.CASCADE)
    username = models.ForeignKey('account.BlogUser', on_delete=models.RESTRICT)

class BrowseRecord(models.Model):
    user=models.ForeignKey('account.BlogUser',on_delete=models.RESTRICT)
    ip=models.GenericIPAddressField()
    article=models.ForeignKey('Article',on_delete=models.RESTRICT)
    time=models.DateTimeField()
