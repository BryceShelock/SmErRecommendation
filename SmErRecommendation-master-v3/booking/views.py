from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ScriptRoom, Booking, Store, User
from .serializers import ScriptRoomSerializer, BookingSerializer, StoreSerializer
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json

from .serializers import ReviewSerializer, FavouriteSerializer
from rest_framework.decorators import api_view, permission_classes
from .models import PostImage, CommunityPost, Review, Favourite, Comment
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def convert_category(category):
        for key, value in CommunityPost.CATEGORY_CHOICES:
            if key == category:
                return value
        return category


def index(request):
    # 获取所有剧本房间
    script_rooms = ScriptRoom.objects.all()
    
    # 搜索功能
    search_query = request.GET.get('search', '')
    if search_query:
        script_rooms = script_rooms.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # 筛选功能
    difficulty = request.GET.get('difficulty', '')
    if difficulty:
        script_rooms = script_rooms.filter(difficulty=difficulty)
    
    player_count = request.GET.get('player_count', '')
    if player_count:
        script_rooms = script_rooms.filter(max_players__gte=player_count)
    
    context = {
        'script_rooms': script_rooms,
        'search_query': search_query,
        'difficulty': difficulty,
        'player_count': player_count,
    }
    return render(request, 'booking/index.html', context)


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'redirect': '/',  # 登录成功后重定向到首页
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'gender': user.gender,
                        'user_type': user.user_type,
                        'avatar': user.avatar.url if user.avatar else None,
                        'points': user.points,
                        'total_bookings': user.total_bookings
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': '用户名或密码错误'
                })
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '无效的请求数据'
            })
    
    # GET请求返回登录页面
    return render(request, 'login.html')


@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            gender = data.get('gender')
            user_type = data.get('userType')
            
            # 验证用户名是否已存在
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'success': False,
                    'message': '用户名已存在'
                })
            
            # 验证邮箱是否已存在
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': '邮箱已被注册'
                })
            
            # 创建新用户，直接赋值gender和user_type
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                gender=gender,
                user_type=user_type
            )
            
            return JsonResponse({
                'success': True,
                'message': '注册成功'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    # GET请求返回注册页面
    return render(request, 'register.html')


def logout_view(request):
    auth_logout(request)
    return redirect('login')


class ScriptRoomViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ScriptRoomSerializer
    queryset = ScriptRoom.objects.all()

    @action(detail=True, methods=['post'])
    def book(self, request, pk=None):
        script_room = self.get_object()
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                user=request.user,
                script_room=script_room,
                total_price=script_room.price * serializer.validated_data['number_of_players']
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        booking = self.get_object()
        if booking.status != 'confirmed':
            return Response(
                {'error': 'Only confirmed bookings can be marked as completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'completed'
        booking.completion_time = request.data.get('completion_time')
        booking.save()
        
        # Update user points
        user = request.user
        user.points += 5  # Points for completing a booking
        user.total_bookings += 1
        user.save()
        
        return Response(BookingSerializer(booking).data)


@login_required
def store_list(request):
    # 获取所有店铺
    stores = Store.objects.all()
    
    # 搜索功能
    search_query = request.GET.get('search', '')
    if search_query:
        stores = stores.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # 区域筛选
    district = request.GET.get('district', '')
    if district:
        stores = stores.filter(district=district)
    
    # 排序方式
    sort_by = request.GET.get('sort', '')
    if sort_by == 'rating':
        stores = stores.order_by('-rating')
    elif sort_by == 'distance':
        # 这里需要根据用户位置计算距离
        pass
    elif sort_by == 'price':
        stores = stores.order_by('min_price')
    
    # 特色筛选
    feature = request.GET.get('feature', '')
    if feature:
        stores = stores.filter(features__contains=feature)
    
    # 价格区间
    price_range = request.GET.get('price_range', '')
    if price_range:
        min_price, max_price = map(int, price_range.split('-'))
        stores = stores.filter(min_price__gte=min_price, max_price__lte=max_price)
    
    # 营业时间
    business_hours = request.GET.get('business_hours', '')
    if business_hours:
        stores = stores.filter(business_hours=business_hours)

    for store in stores:
        store.feature_list = store.features.split(',') if store.features else []

    # logger.info(f"stores: {stores}")
    
    context = {
        'stores': stores,
        'search_query': search_query,
        'district': district,
        'sort_by': sort_by,
        'feature': feature,
        'price_range': price_range,
        'business_hours': business_hours,
        'range_stars': range(1, 6),
    }
    return render(request, 'stores.html', context)


class StoreViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StoreSerializer
    queryset = Store.objects.all()

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        store = self.get_object()
        reviews = store.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        # 处理表单提交
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']

        gender = request.POST.get('gender', user.gender)
        if gender in ['male', 'female']:
            user.gender = gender
        
        user.save()
        return redirect('booking:profile')
    
    context = {
        'user': user,
        'is_male': user.gender == 'male',
        'is_female': user.gender == 'female',
    }
    return render(request, 'booking/profile.html', context)


@login_required
def my_reviews(request):
    user = request.user
    reviews = Review.objects.filter(user=user).order_by('-created_at')
    context = {
        'reviews': reviews,
    }
    return render(request, 'booking/my_reviews.html', context)


@login_required
def my_bookings(request):
    user = request.user

    # Get filter and sort parameters
    status_filter = request.GET.get('status')
    sort_method = request.GET.get('sort', '-created_at')  # Default to '-created_at'
    page = request.GET.get('page', 1)

    # Filter bookings by status if specified
    bookings = Booking.objects.filter(user=user)
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    # Apply sorting
    if sort_method == 'start_time':
        bookings = bookings.order_by('date', 'time')
    elif sort_method == 'price':
        bookings = bookings.order_by('total_price')
    else:
        bookings = bookings.order_by('-created_at')

    # Paginate the results
    paginator = Paginator(bookings, 6)  # 6 bookings per page
    page_obj = paginator.get_page(page)

    # Return data as JSON response
    booking_data = [
        {
            'id': booking.id,
            'script_room': booking.script_room.name,
            'script_room_image': request.build_absolute_uri(booking.script_room.image.url) if booking.script_room.image else None,
            'date': booking.date,
            'time': booking.time,
            'player_count': booking.player_count,
            'price': booking.script_room.price,
            'status': booking.status,
        }
        for booking in page_obj
    ]

    # print(booking_data)

    return JsonResponse({
        'bookings': booking_data,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
    })


@login_required
def my_favourites(request):
    user = request.user
    favourites = Favourite.objects.filter(user=user)
    context = {
        'favourites': favourites,
    }
    return render(request, 'booking/my_favourites.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        try:
            user = request.user
            category = request.POST.get('category')
            content = request.POST.get('content')
            images = request.FILES.getlist('images')  # Use `FILES` for image uploads

            # Create the CommunityPost
            post = CommunityPost.objects.create(user=user, category=category, content=content)

            # Create associated PostImages (if any)
            for img in images[:6]:  # Limit to 6 images
                PostImage.objects.create(post=post, image=img)

            return JsonResponse({'success': True, 'message': '创建成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return render(request, 'booking/post_create.html')


@login_required
def fetch_community_posts(request):
    posts = CommunityPost.objects.prefetch_related('images').order_by('-created_at')
    data = [
        {
            'id': post.id,
            'category': convert_category(post.category),
            'content': post.content,
            'images': [image.image.url for image in post.images.all()],
            'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for post in posts
    ]
    return JsonResponse({'posts': data})


@login_required
def store_create(request):
    if request.method == 'POST':
        try:
            # Extract data from POST request
            name = request.POST.get('name')
            address = request.POST.get('address')
            district = request.POST.get('district')
            phone = request.POST.get('phone')
            business_hours = request.POST.get('business_hours')
            min_price = request.POST.get('min_price')
            max_price = request.POST.get('max_price')
            rating = request.POST.get('rating')
            features = request.POST.get('features')
            
            # Handle file upload
            image = request.FILES.get('image')

            # Create store entry
            store = Store.objects.create(
                name=name,
                address=address,
                district=district,
                phone=phone,
                business_hours=business_hours,
                min_price=min_price,
                max_price=max_price,
                rating=rating,
                features=features,
                image=image,
            )

            return JsonResponse({'success': True, 'message': '创建成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return render(request, 'booking/store_create.html')


@login_required
def store_recommendation(request):
    stores = Store.objects.order_by('-created_at')[:3]
    store_list = []
    for store in stores:
        store_data = {
            'id': store.id,
            'name': store.name,
            'address': store.address,
            'district': store.district,
            'phone': store.phone,
            'business_hours': store.business_hours,
            'min_price': store.min_price,
            'max_price': store.max_price,
            'rating': store.rating,
            'features': store.features,
            'image': request.build_absolute_uri(store.image.url) if store.image else None,
        }
        store_list.append(store_data)
    return JsonResponse({'stores': store_list})


@login_required
def script_room_create(request):
    if request.method == 'POST':
        try:
            # Extract data from POST request
            name = request.POST.get('name')
            store_id = request.POST.get('store_id')
            description = request.POST.get('description')
            difficulty = request.POST.get('difficulty')
            duration = int(request.POST.get('duration'))
            min_players = int(request.POST.get('min_players'))
            max_players = int(request.POST.get('max_players'))
            price = float(request.POST.get('price'))
            
            # Handle file upload
            image = request.FILES.get('image')

            store = get_object_or_404(Store, id=store_id)

            # Create script room entry
            script_room = ScriptRoom.objects.create(
                name=name,
                store=store,
                description=description,
                difficulty=difficulty,
                duration=duration,
                min_players=min_players,
                max_players=max_players,
                price=price,
                image=image,
            )

            return JsonResponse({'success': True, 'message': '创建成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return render(request, 'booking/script_create.html')


@login_required
def script_room_recommendation(request):
    script_rooms = ScriptRoom.objects.order_by('-created_at')[:6]
    # serializer = ScriptRoomSerializer(script_rooms, many=True)
    script_room_list = []
    
    for script_room in script_rooms:
        script_room_data = {
            'id': script_room.id,
            'name': script_room.name,
            'description': script_room.description,
            'difficulty': script_room.difficulty,
            'duration': script_room.duration,
            'min_players': script_room.min_players,
            'max_players': script_room.max_players,
            'price': script_room.price,
            'rating': script_room.store.rating,
            'image': request.build_absolute_uri(script_room.image.url) if script_room.image else None,
            'genre': '推理',
            'store_name': script_room.store.name,
            'store_id': script_room.store.id,
        }
        script_room_list.append(script_room_data)
    
    return JsonResponse({'script_rooms': script_room_list})


@login_required
def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    script_rooms = ScriptRoom.objects.filter(store=store).order_by('-created_at')
    context = {
        'store': store,
        'script_rooms': script_rooms,
    }
    return render(request, 'booking/store_detail.html', context)


@login_required
def script_detail(request, script_id):
    script_room = get_object_or_404(ScriptRoom, id=script_id)
    bookings = Booking.objects.filter(script_room=script_room).order_by('-created_at')
    reviews = Review.objects.filter(script_room=script_room).order_by('-created_at')
    is_favourited = Favourite.objects.filter(user=request.user, script_room=script_room).exists()
    context = {
        'script': script_room,
        'bookings': bookings,
        'reviews': reviews,
        'is_favourited': is_favourited,
    }
    return render(request, 'booking/script_detail.html', context)


@login_required
def booking_create(request, room_id):
    if request.method == 'POST':
        try:
            room = get_object_or_404(ScriptRoom, id=room_id)
            date_str = request.POST.get('date')
            time_str = request.POST.get('time')
            player_count_str = request.POST.get('player_count')
            notes = request.POST.get('notes')

            if not date_str:
                return JsonResponse({'success': False, 'message': 'Date is required'})
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                if date < datetime.now().date():
                    return JsonResponse({'success': False, 'message': 'Date cannot be in the past'})
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD'})

            if not time_str:
                return JsonResponse({'success': False, 'message': 'Time is required'})
            try:
                time = datetime.strptime(time_str, '%H:%M').time()
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Invalid time format. Use HH:MM'})

            if not player_count_str or not player_count_str.isdigit():
                return JsonResponse({'success': False, 'message': 'Player count must be a valid number'})
            player_count = int(player_count_str)
            if player_count < room.min_players or player_count > room.max_players:
                return JsonResponse({'success': False, 'message': f'Player count must be between {room.min_players} and {room.max_players}'})

            total_price = room.price * player_count
            
            booking = Booking.objects.create(
                user=request.user,
                script_room=room,
                date=date,
                time=time,
                player_count=player_count,
                notes=notes,
                total_price=total_price,
            )

            return JsonResponse({'success': True, 'message': '创建成功'})
        except Exception as e:
            print(f"Error creating booking: {e}")
            return JsonResponse({'success': False, 'message': str(e)})
    
    room = get_object_or_404(ScriptRoom, id=room_id)
    context = {
        'room': room,
    }
    return render(request, 'booking/booking_create.html', context)


@login_required
def review_create(request, script_id):
    script_room = get_object_or_404(ScriptRoom, id=script_id)
    if request.method == 'POST':
        try:
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')
            review = Review.objects.create(
                script_room=script_room,
                user=request.user,
                rating=rating,
                comment=comment,
            )
            return JsonResponse({'success': True, 'message': '创建成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return render(request, 'booking/review_create.html')


@login_required
def toggle_favourite(request, script_id):
    script_room = get_object_or_404(ScriptRoom, id=script_id)
    favourite = Favourite.objects.filter(user=request.user, script_room=script_room).first()

    if favourite:  # If the favorite exists, remove it
        favourite.delete()
        return JsonResponse({'favourited': False})
    else:  # If it doesn't exist, create it
        Favourite.objects.create(user=request.user, script_room=script_room)
        return JsonResponse({'favourited': True})


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    comments = post.comments.order_by('-created_at')

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(post=post, user=request.user, content=content)
            return redirect('post_detail', post_id=post.id)

    post.category = convert_category(post.category)
    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'booking/post_detail.html', context)
