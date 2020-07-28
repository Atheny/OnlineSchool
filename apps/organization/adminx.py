import xadmin
from .models import CityDict, CourseOrg, Teacher


class CourseOrgAdmin(object):
    '''
    注册课程机构
    '''
    list_display = ['name', 'desc', 'click_nums', 'fav_nums', 'add_time', 'get_teacher_nums']
    search_fields = ['name', 'desc', 'click_nums', 'fav_nums']
    list_filter = ['name', 'desc', 'click_nums', 'fav_nums', 'city__name', 'address', 'add_time']
    model_icon = 'fa fa-sitemap'
    ordering = ['-click_nums', '-students', '-fav_nums']
    readonly_fields = ['click_nums', 'students', 'fav_nums']



class CityDictAdmin(object):
    '''
    注册城市
    '''
    list_display = ['name', 'desc', 'add_time']
    search_fields = ['name', 'desc']
    list_filter = ['name', 'desc', 'add_time']
    model_icon = 'fa fa-map-marker'



class TeacherAdmin(object):
    '''
    注册教师
    '''
    list_display = ['name', 'org', 'work_years', 'work_company', 'work_position', 'click_nums', 'fav_nums', 'add_time', 'get_course_nums']
    search_fields = ['org__name', 'name', 'work_years', 'work_company', 'work_position']
    list_filter = ['org__name', 'name', 'work_years', 'work_company', 'work_position', 'click_nums', 'fav_nums', 'add_time']
    model_icon = 'fa fa-star'
    ordering = ['-click_nums', '-fav_nums']
    readonly_fields = ['click_nums', 'fav_nums']


xadmin.site.register(CourseOrg, CourseOrgAdmin)
xadmin.site.register(CityDict, CityDictAdmin)
xadmin.site.register(Teacher, TeacherAdmin)