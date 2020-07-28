import xadmin
from .models import UserAsk, UserMessage, CourseComments, UserCourse, UserFavorite


class CourseCommentsAdmin(object):
    '''
    注册用户评论
    '''
    list_display = ['user', 'course', 'comments', 'add_time']
    search_fields = ['user__username', 'course__name', 'comments']
    list_filter = ['user__username', 'course__name', 'comments', 'add_time']
    model_icon = 'fa fa-pencil-square-o'


class UserAskAdmin(object):
    '''
    注册用户咨询
    '''
    list_display = ['name', 'mobile', 'course_name', 'add_time']
    search_fields = ['name', 'mobile', 'course_name']
    list_filter = ['name', 'mobile', 'course_name', 'add_time']
    model_icon = 'fa fa-question-circle'


class UserMessageAdmin(object):
    '''
    注册用户消息
    '''
    list_display = ['user', 'message', 'has_red', 'add_time']
    search_fields = ['user', 'message', 'has_red']
    list_filter = ['user', 'message', 'has_red', 'add_time']
    model_icon = 'fa fa-comments-o'


class UserCourseAdmin(object):
    '''
    注册用户学习的课程
    '''
    list_display = ['user', 'course', 'add_time']
    search_fields = ['user__username', 'course__name']
    list_filter = ['user__username', 'course__name', 'add_time']
    model_icon = 'fa fa-book'


class UserFavoriteAdmin(object):
    '''
    注册用户收藏
    '''
    list_display = ['user', 'fav_id', 'fav_type', 'add_time']
    search_fields = ['user__username', 'fav_id', 'fav_type']
    list_filter = ['user__username', 'fav_id', 'fav_type', 'add_time']
    model_icon = 'fa fa-bookmark'


xadmin.site.register(UserFavorite, UserFavoriteAdmin)
xadmin.site.register(UserCourse, UserCourseAdmin)
xadmin.site.register(UserAsk, UserAskAdmin)
xadmin.site.register(CourseComments, CourseCommentsAdmin)
xadmin.site.register(UserMessage, UserMessageAdmin)
