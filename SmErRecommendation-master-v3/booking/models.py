from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
    )
    
    USER_TYPE_CHOICES = (
        ('player', '玩家'),
        ('store', '商家'),
    )
    
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male', verbose_name='性别')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='player', verbose_name='用户类型')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    points = models.IntegerField(default=0, verbose_name='积分')
    total_bookings = models.IntegerField(default=0, verbose_name='总预约次数')
    
    # 添加related_name来解决冲突
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='booking_user_set',
        related_query_name='booking_user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='booking_user_set',
        related_query_name='booking_user'
    )
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.username


class Store(models.Model):
    name = models.CharField(max_length=100, verbose_name='店铺名称')
    address = models.CharField(max_length=200, verbose_name='地址', default='')
    district = models.CharField(max_length=50, verbose_name='区域', null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name='联系电话')
    business_hours = models.CharField(max_length=100, verbose_name='营业时间', null=True, blank=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='最低价格', null=True, blank=True)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='最高价格', null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0, verbose_name='评分')
    features = models.CharField(max_length=200, blank=True, null=True, verbose_name='特色')
    image = models.ImageField(upload_to='stores/', blank=True, null=True, verbose_name='店铺图片')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '店铺'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.name


class ScriptRoom(models.Model):
    name = models.CharField(max_length=100, verbose_name='剧本名称')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='店铺')
    description = models.TextField(verbose_name='剧本描述')
    difficulty = models.CharField(max_length=20, verbose_name='难度')
    duration = models.IntegerField(verbose_name='时长(分钟)')
    min_players = models.IntegerField(verbose_name='最少人数')
    max_players = models.IntegerField(verbose_name='最多人数')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    image = models.ImageField(upload_to='script_rooms/', blank=True, null=True, verbose_name='剧本图片')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '剧本房间'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', '待确认'),
        ('confirmed', '已确认'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    script_room = models.ForeignKey(ScriptRoom, on_delete=models.CASCADE, verbose_name='剧本房间')
    date = models.DateField(verbose_name='预约日期', null=True, blank=True)
    time = models.TimeField(verbose_name='预约时间', null=True, blank=True)
    player_count = models.IntegerField(verbose_name='玩家数量', null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总价')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    notes = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '预约'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return f"{self.user.username} - {self.script_room.name}"


# 用户评价模型
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    script_room = models.ForeignKey(ScriptRoom, on_delete=models.CASCADE, related_name='my_reviews')
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} 对 {self.script_room.name} 的评价"


# 用户收藏模型
class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    script_room = models.ForeignKey(ScriptRoom, on_delete=models.CASCADE, related_name='my_favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.script_room.name}"


class CommunityPost(models.Model):
    CATEGORY_CHOICES = [
    ('Experence', '经验分享'),
    ('QA', '求助问答'),
    ('Recommendation', '剧本推荐'),
    ('Reviews', '店铺点评'),
    ('MakeFriends', '组队交友'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.content[:30]}"


class PostImage(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')


class Comment(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    content = models.TextField(verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"