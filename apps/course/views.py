from django.shortcuts import render
from django.views import View
from .models import Course, CourseResourse, Video
from users.models import Banner
from organization.models import CourseOrg
from operation.models import UserFavorite, CourseComments, UserCourse
from pure_pagination import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.db.models import F, Q
from django.http import HttpResponse
from utils.mixin_utils import LoginRequiredMixin


class IndexView(View):
    '''首页'''
    def get(self, request):
        # 轮播图
        all_banners = Banner.objects.all().order_by('index')
        # 非轮播课程
        courses = Course.objects.filter(is_banner=False)
        courses = courses[:6] if courses.count() > 6 else courses
        # 轮播课程
        banner_courses = Course.objects.filter(is_banner=True)
        banner_courses = banner_courses[:3] if banner_courses.count() > 3 else banner_courses
        # 课程机构
        course_orgs = CourseOrg.objects.all()
        course_orgs = course_orgs[:15] if course_orgs.count() > 15 else course_orgs
        return render(request, 'index.html', {
            'all_banners': all_banners,
            'courses': courses,
            'banner_courses': banner_courses,
            'course_orgs': course_orgs,
        })




class CourseListView(View):
    '''课程列表'''
    def get(self, request):
        current_page = 'course'

        # 默认按时间排序
        all_courses = Course.objects.all().order_by('-add_time')

        # 增加搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            # 在name字段进行操作,做like语句的操作。i代表不区分大小写
            # or操作使用Q
            all_courses = all_courses.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords) | Q(
                detail__icontains=search_keywords))


        # 热门课程推荐
        hot_courses = Course.objects.all().order_by('-click_nums', '-add_time')[:3] if Course.objects.all().count() > 3 else Course.objects.all()

        # 排序
        sort = request.GET.get('sort', '')
        if sort:
            # 按参与人数排序
            if sort == 'students':
                all_courses = all_courses.order_by('-students', '-add_time')
            # 按热门排序
            elif sort == 'hot':
                all_courses = all_courses.order_by('-click_nums', '-add_time')

        # 翻页
        # 每页指定6个
        p = Paginator(all_courses, 6, request=request)
        page = request.GET.get('page', 1)

        try:
            courses = p.page(page)
        except PageNotAnInteger:
            courses = p.page(1)
        except EmptyPage:
            courses = p.page(1)
        except InvalidPage:
            courses = p.page(1)
        finally:
            return render(request, 'course-list.html', {
                'all_courses': courses,
                'sort': sort,
                'hot_courses': hot_courses,
                'search_keywords': search_keywords,
                'current_page': current_page,
            })


class CourseDetailView(View):
    '''课程详情'''
    def get(self, request, course_id):
        current_page = 'course'

        course = Course.objects.get(id=int(course_id))
        # 课程点击数+1
        course.click_nums = F('click_nums') + 1
        course.save()

        # 课程收藏和机构收藏
        # 定义收藏类型和状态
        has_fav_course = False
        has_fav_org = False

        # 用户已登录才做判断
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        # 课程标签
        # 通过课程标签，查找数据库中的课程，相关推荐
        tag = course.tag
        if tag:
            # 需要用exclude过滤掉当前课程，不然会推荐自己
            relates = Course.objects.exclude(id=course.id).filter(tag=tag).order_by('-click_nums', '-students', '-fav_nums', '-add_time')
            relate_courses = relates[:3] if relates.count() > 3 else relates
        else:
            relate_courses = []


        return render(request, 'course-detail.html', {
            'course': course,
            'relate_courses': relate_courses,
            'current_page': current_page,
            'has_fav_course': has_fav_course,
            'has_fav_org': has_fav_org,
        })



class CourseInfoView(LoginRequiredMixin, View):
    '''课程章节信息'''
    def get(self, request, course_id):
        current_page = 'course'
        course = Course.objects.get(id=int(course_id))

        # 查询用户是否已经学习了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            # 如果没有学习该门课程就关联起来
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

            # 课程的学习人数+1
            course.students = F('students') + 1
            course.save()


        # 相关课程推荐
        # 找到学习这门课的所有用户课程
        user_courses = UserCourse.objects.filter(course=course)

        ################################################################################################################
        # 找到学习这门课的所有用户的id
        # user_ids = [user_course.user.id for user_course in user_courses]
        #
        # # 通过所有学习这门课程的用户的id，找到这些用户学习过的课程
        # all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # # 取出所有课程id
        # course_ids = [all_user_course.course_id for all_user_course in all_user_courses]
        # # 通过所有课程的id,找到所有的课程，按点击量取五个
        # relate = Course.objects.filter(id__in=course_ids).exclude(id=int(course_id)).order_by('-click_nums', '-add_time')
        # relate_courses = relate[:5] if relate.count() > 5 else relate
        ################################################################################################################


        # 找到这些用户学习过的课程
        all_user_courses = UserCourse.objects.filter(user__in=[user_course.user for user_course in user_courses])

        # 取出所有课程
        courses = [all_user_course.course for all_user_course in all_user_courses]
        # 按点击量取五个
        relate = Course.objects.filter(id__in=[course.id for course in courses]).exclude(id=int(course_id)).order_by('-click_nums', '-add_time')
        relate_courses = relate[:5] if relate.count() > 5 else relate


        # 资源
        all_resources = CourseResourse.objects.filter(course=course)
        return render(request, 'course-video.html', {
            'course': course,
            'all_resources': all_resources,
            'relate_courses': relate_courses,
            'current_page': current_page,
        })


class CommentsView(LoginRequiredMixin, View):
    '''课程评论显示'''
    def get(self, request, course_id):
        current_page = 'course'
        course = Course.objects.get(id=int(course_id))
        all_resources = CourseResourse.objects.filter(course=course)
        all_comments = CourseComments.objects.filter(course=course).order_by('-add_time')

        # 服务端返回用户是否登录标志给前端
        if_login = False
        if request.user.is_authenticated:
            if_login = True

        # 相关课程推荐
        # 找到学习这门课的所有用户课程
        user_courses = UserCourse.objects.filter(course=course)
        # 找到这些用户学习过的课程
        all_user_courses = UserCourse.objects.filter(user__in=[user_course.user for user_course in user_courses])

        # 取出所有课程
        courses = [all_user_course.course for all_user_course in all_user_courses]
        # 按点击量取五个
        relate = Course.objects.filter(id__in=[course.id for course in courses]).exclude(id=int(course_id)).order_by(
            '-click_nums', '-add_time')
        relate_courses = relate[:5] if relate.count() > 5 else relate

        # 评论翻页
        page = request.GET.get('page', 1)
        p = Paginator(all_comments, 10, request=request)

        try:
            comments = p.page(page)
        except PageNotAnInteger:
            comments = p.page(1)
        except EmptyPage:
            comments = p.page(1)
        except InvalidPage:
            comments = p.page(1)
        finally:
            return render(request, 'course-comment.html', {
            'course': course,
            'all_resources': all_resources,
            'all_comments': comments,
            'if_login': if_login,
            'relate_courses': relate_courses,
            'current_page': current_page,
        })


class AddCommentsView(View):
    '''添加评论'''
    def post(self, request):
        if not request.user.is_authenticated:
            # 未登录时返回json提示未登录，跳转到登录页面是在ajax中做的
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        course_id = request.POST.get('course_id', 0)
        comments = request.POST.get('comments', '')
        if int(course_id) > 0 and comments:
            # 实例化一个course_comments对象
            course_comments = CourseComments()
            # 获取评论的是哪门课程
            course = Course.objects.get(id=int(course_id))
            # 分别把评论的课程、评论的内容和评论的用户保存到数据库
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            return HttpResponse('{"status":"success", "msg":"评论成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"评论失败"}', content_type='application/json')



class VideoPlayView(LoginRequiredMixin, View):
    '''课程章节视频播放页面'''
    def get(self, request, video_id):
        current_page = 'course'
        video = Video.objects.get(id=int(video_id))
        # 通过外键找到章节再找到视频对应的课程
        course = video.lesson.course

        # 查询用户是否已经学习了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            # 如果没有学习该门课程就关联起来
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

            # 课程的学习人数+1
            course.students = F('students') + 1
            course.save()

        # 相关课程推荐
        # 找到学习这门课的所有用户课程
        user_courses = UserCourse.objects.filter(course=course)
        # 找到这些用户学习过的课程
        all_user_courses = UserCourse.objects.filter(user__in=[user_course.user for user_course in user_courses])

        # 取出所有课程
        courses = [all_user_course.course for all_user_course in all_user_courses]
        # 按点击量取五个
        relate = Course.objects.filter(id__in=[course.id for course in courses]).exclude(
            id=int(course.id)).order_by(
            '-click_nums', '-add_time')
        relate_courses = relate[:5] if relate.count() > 5 else relate

        # 资源
        all_resources = CourseResourse.objects.filter(course=course)

        return render(request, 'course-play-2.html', {
            'course': course,
            'all_resources': all_resources,
            'relate_courses': relate_courses,
            'video': video,
            'current_page': current_page,
        })

