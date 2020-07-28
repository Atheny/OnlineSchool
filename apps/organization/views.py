from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponse
from .models import CityDict, CourseOrg, Teacher
from .forms import UserAskForm
from operation.models import UserFavorite
from course.models import Course
from django.db.models import Q, F

from pure_pagination import PageNotAnInteger, Paginator, EmptyPage


class OrgView(View):
    '''课程机构'''
    def get(self, request):
        # current_page
        current_page = 'org'

        # 取出所有课程机构
        all_orgs = CourseOrg.objects.all()

        # 取出所有城市
        all_citys = CityDict.objects.all()

        # 增加搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))


        # 按城市筛选
        city_id = request.GET.get('city', '')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        # 按类别筛选
        category = request.GET.get('ct', '')
        if category:
            all_orgs = all_orgs.filter(category=category)

        # 课程机构排名筛选
        # 按点击量排名，只取前三个
        hot_orgs = all_orgs.order_by('-click_nums')[:3] if len(all_orgs) > 3 else all_orgs.order_by('-click_nums')

        # 学习人数和课程数筛选
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_orgs = all_orgs.order_by('-students')
            elif sort == 'courses':
                all_orgs = all_orgs.order_by('-course_nums')


        # 计算机构个数
        org_onums = all_orgs.count()

        # 指定每页显示10个
        p = Paginator(all_orgs, 10, request=request)

        # 对课程机构进行分页
        # 尝试获取前台get请求传递过来的page参数
        # 如果是不合法的配置参数默认返回第一页
        try:
            page = request.GET.get('page', 1)
            orgs = p.page(page)
        except PageNotAnInteger:
            page = 1
        except EmptyPage:
            page = 1

        orgs = p.page(page)

        return render(request, 'org-list.html', {
            'all_orgs': orgs,
            'all_citys': all_citys,
            'org_onums': org_onums,
            'city_id': city_id,
            'category': category,
            'hot_orgs': hot_orgs,
            'sort': sort,
            'search_keywords': search_keywords,
            'current_page': current_page,
        })




class AddUserAskView(View):
    '''用户添加咨询'''
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse('{"status": "fail", "msg": "添加出错"}', content_type='application/json')


class OrgHomeView(View):
    '''机构首页'''
    def get(self, request, org_id):
        current_page = 'home'
        # 根据id找到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums = F('click_nums') + 1
        course_org.save()

        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        # 反向查询到课程机构的所有课程和老师
        all_courses = course_org.courses.all()[:4] if len(course_org.courses.all()) > 4 else course_org.courses.all()
        all_teacher = course_org.teacher_set.all()[:2] if len(course_org.teacher_set.all()) > 2 else course_org.teacher_set.all()
        return render(request, 'org-detail-homepage.html', {
            'course_org': course_org,
            'all_courses': all_courses,
            'all_teacher': all_teacher,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgCourseView(View):
    '''机构课程列表页'''
    def get(self, request, org_id):
        current_page = 'course'
        # 根据id取到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))


        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        # 通过课程机构找到课程。内建的变量，找到指向这个字段的外键引用
        all_courses = course_org.courses.all()
        return render(request, 'org-detail-course.html', {
            'all_courses': all_courses,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgDescView(View):
    '''机构介绍页'''
    def get(self, request, org_id):
        current_page = 'desc'
        course_org = CourseOrg.objects.get(id=int(org_id))

        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        return render(request, 'org-detail-desc.html', {
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgTeacherView(View):
    '''机构讲师'''
    def get(self, request, org_id):
        current_page = 'teacher'
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_teacher = course_org.teacher_set.all()

        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        return render(request, 'org-detail-teachers.html', {
            'course_org': course_org,
            'all_teacher': all_teacher,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class AddFavView(View):
    '''用户收藏和取消操作(机构)'''
    def post(self, request):
        id = request.POST.get('fav_id', 0)
        type = request.POST.get('fav_type', 0)



        if not request.user.is_authenticated:
            # 未登录时返回json提示未登录，跳转到登录页面是在ajax中做的
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        exist_record = UserFavorite.objects.filter(user=request.user, fav_id=int(id), fav_type=int(type))
        if exist_record:
            # 如果记录已经存在，表示用户取消收藏
            exist_record.delete()
            if int(type) == 1:
                course = Course.objects.get(id=int(id))
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(type) == 2:
                org = CourseOrg.objects.get(id=int(id))
                org.fav_nums -= 1
                if org.fav_nums < 0:
                    org.fav_nums = 0
                org.save()
            elif int(type) == 3:
                teacher = Teacher.objects.get(id=int(id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()
            return HttpResponse('{"status":"success", "msg":"收藏"}', content_type='application/json')
        else:
            user_fav = UserFavorite()
            if int(id) > 0 and int(type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(id)
                user_fav.fav_type = int(type)
                user_fav.save()

                if int(type) == 1:
                    course = Course.objects.get(id=int(id))
                    course.fav_nums = F('fav_nums') + 1
                    course.save()
                elif int(type) == 2:
                    org = CourseOrg.objects.get(id=int(id))
                    org.fav_nums = F('fav_nums') + 1
                    org.save()
                elif int(type) == 3:
                    teacher = Teacher.objects.get(id=int(id))
                    teacher.fav_nums = F('fav_nums') + 1
                    teacher.save()

                return HttpResponse('{"status":"success", "msg":"已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail", "msg":"收藏出错"}', content_type='application/json')



class TeacherListView(View):
    '''教师列表'''
    def get(self, request):
        current_page = 'teacher'
        all_teachers = Teacher.objects.all()

        # 增加搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_teachers = all_teachers.filter(Q(name__icontains=search_keywords))

        # 总共有多少老师使用count进行统计
        teacher_nums = all_teachers.count()

        # 按人气排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'hot':
                all_teachers = all_teachers.order_by('-click_nums')


        # 讲师排行榜
        sorted = Teacher.objects.all().order_by('-click_nums', '-fav_nums')
        sorted_teachers = sorted[:3] if sorted.count() > 3 else sorted




        # 指定每页显示10个
        p = Paginator(all_teachers, 10, request=request)

        # 对课程教师进行分页
        # 尝试获取前台get请求传递过来的page参数
        # 如果是不合法的配置参数默认返回第一页
        try:
            page = request.GET.get('page', 1)
            teachers = p.page(page)
        except PageNotAnInteger:
            page = 1
        except EmptyPage:
            page = 1

        teachers = p.page(page)


        return render(request, 'teachers-list.html', {
            'all_teachers': teachers,
            'teacher_nums': teacher_nums,
            'sort': sort,
            'sorted_teachers': sorted_teachers,
            'search_keywords': search_keywords,
            'current_page': current_page,
        })



class TeacherDetailView(View):
    '''讲师详情'''
    def get(self, request, teacher_id):
        current_page = 'teacher'

        teacher = Teacher.objects.get(id=int(teacher_id))
        teacher.click_nums = F('click_nums') + 1
        teacher.save()
        all_courses = Course.objects.filter(teacher=teacher)


        # 该讲师的经典课程
        classic_course = all_courses.order_by('-students', '-click_nums', '-fav_nums', '-add_time')
        classic_course = classic_course[0] if classic_course.count() > 0 else []

        # 讲师排行
        sorted = Teacher.objects.all().order_by('-click_nums', '-fav_nums')
        sorted_teachers = sorted[:3] if sorted.count() > 3 else sorted

        # 教师收藏和机构收藏
        has_teacher_saved = False
        has_org_saved = False
        if request.user.is_authenticated:
            # 判断是否已收藏讲师
            if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher.id):
                has_teacher_saved = True

            # 判断是否已收藏机构
            if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
                has_org_saved = True


        return render(request, 'teacher-detail.html', {
            'teacher': teacher,
            'all_courses': all_courses,
            'sorted_teachers': sorted_teachers,
            'classic_course': classic_course,
            'has_teacher_saved': has_teacher_saved,
            'has_org_saved': has_org_saved,
            'current_page': current_page,
        })