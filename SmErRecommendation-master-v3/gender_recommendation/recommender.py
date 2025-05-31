from booking.models import ScriptRoom
from users.models import User

def recommend_script_rooms_by_gender(user):
    gender = user.gender
    if gender:
        # 这里简单假设不同性别有不同的推荐剧本杀列表
        if gender == 'M':
            # 男性推荐的剧本杀列表
            return ScriptRoom.objects.filter(tags__contains=['male_friendly'])
        elif gender == 'F':
            # 女性推荐的剧本杀列表
            return ScriptRoom.objects.filter(tags__contains=['female_friendly'])
    return ScriptRoom.objects.all()