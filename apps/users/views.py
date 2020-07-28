from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from .models import UserProfile, EmailVerifyRecord
from django.db.models import Q
from django.views.generic.base import View
from .forms import LoginForm, RegisterForm, ForgetPwdForm, ModifyPwdForm, UploadImageForm, UserInfoForm
from django.contrib.auth.hashers import make_password
from operation.models import UserCourse, UserFavorite, Course, UserMessage
from course.models import CourseOrg, Teacher
from .utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin
from django.http import HttpResponse
import json
from pure_pagination import Paginator, EmptyPage, InvalidPage, PageNotAnInteger



# 使用名称或邮箱登录
# 基础ModelBackend类，因为它有authenticate方法
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 不希望用户存在两个，get只能有一个。两个是get失败的一种原因 Q为使用并集查询
            user = UserProfile.objects.get(Q(email=username)|Q(username=username))
            # django的后台中密码加密：所以不能password==password
            # UserProfile继承的AbstractUser中有def check_password(self, raw_password):
            if user.check_password(password):
                return user
        except Exception as e:
            return None




# def user_login(request):
#     '''
#     用户登录
#     '''
#     if request.method == 'POST':
#         # 获取用户提交的用户名和密码
#         user_name = request.POST.get('username', None)
#         pass_word = request.POST.get('password', None)
#         # 成功返回user对象，失败None
#         user = authenticate(username=user_name, password=pass_word)
#         # 如果不是None说明验证成功
#         if user is not None:
#             # 登录
#             login(request, user)
#             return redirect('index')
#             # return render(request, 'index.html')
#         else:
#             return render(request, 'login.html', context={'msg': '用户名或密码错误'})
#
#     elif request.method == 'GET':
#         return render(request, 'login.html')


class LoginView(View):
    '''用户登录'''
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        else:
            next = request.GET.get('next', '/')
            return render(request, 'login.html', {'next': next})

    def post(self, request):
        # 实例化
        login_form = LoginForm(request.POST)
        next = request.POST.get('next', '/')
        if login_form.is_valid():
            # 获取用户提交的用户名和密码
            user_name = request.POST.get('username', None)
            pass_word = request.POST.get('password', None)
            # 成功返回user对象，失败None
            user = authenticate(username=user_name, password=pass_word)
            # 如果不是None说明验证成功
            if user is not None:
                # 只有注册激活才能登录
                if user.is_active:
                    # 登录
                    login(request, user)
                    return redirect(next)
                    # return redirect('index')
                    # return render(request, 'index.html')
                else:
                    return render(request, 'login.html', context={'msg': '注册邮箱尚未激活', 'login_form': login_form, 'next': next})
            else:
                return render(request, 'login.html', context={'msg': '用户名或密码错误', 'login_form': login_form, 'next': next})
        else:
            return render(request, 'login.html', {'login_form': login_form, 'next': next})



class LogoutView(LoginRequiredMixin, View):
    '''用户退出'''
    def get(self, request):
        logout(request)
        return redirect('index')


class RegisterView(View):
    '''用户注册'''
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        else:
            register_form = RegisterForm()
            return render(request, 'register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get('email', None)
            # 如果用户已存在,则提示错误信息
            if UserProfile.objects.filter(email=user_name):
                return render(request, 'register.html', {'register_form': register_form, 'msg': '用户已存在'})

            pass_word = request.POST.get('password', None)
            pass_word_2 = request.POST.get('password_2', None)

            # 如果两次密码一致
            if pass_word == pass_word_2:
                # 实例化一个user_profile对象
                user_profile = UserProfile()
                user_profile.username = user_name
                user_profile.email = user_name
                user_profile.is_active = False
                # 对保存到数据库中的密码加密
                user_profile.password = make_password(pass_word)
                user_profile.save()

                send_status = send_register_email(user_name, 'register')
                if send_status:
                    return render(request, 'send_success.html')
                else:
                    return render(request, 'send_fail.html')


            else:
                # 两次密码不一致
                return render(request, 'register.html', {'register_form': register_form, 'msg': '两次密码不一致'})
        else:
            return render(request, 'register.html', {'register_form': register_form})


class ActiveUserView(View):
    '''激活用户'''
    def get(self, request, active_code, pk):
        # 查询邮箱验证记录是否存在
        record = EmailVerifyRecord.objects.filter(Q(pk=pk) & Q(code=active_code))

        if record:
            # 获取到对应的邮箱
            email = record[0].email
            # 查找到邮箱对应的user
            user = UserProfile.objects.get(email=email)
            user.is_active = True
            user.save()
            # 激活成功后跳转到激活成功页面
            return render(request, 'active_succ.html')

        # 验证码不对的时候跳转到激活失败页面
        else:
            return render(request, 'active_fail.html')


class ForgetPwdView(View):
    '''找回密码'''
    def get(self, request):
        forget_form = ForgetPwdForm()
        return render(request, 'forgetpwd.html', context={'forget_form': forget_form})

    def post(self, request):
        forget_form = ForgetPwdForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email', None)
            user = UserProfile.objects.filter(email=email)
            # 如果邮箱不存在
            if not user:
                return render(request, 'forgetpwd.html', context={'forget_form': forget_form, 'msg': '邮箱不存在'})

            # # 如果邮箱未激活
            # if not user[0].is_active:
            #     return render(request, 'forgetpwd.html', context={'forget_form': forget_form, 'msg': '邮箱未激活'})

            # 若邮箱存在且已激活，则发送密码重置邮件, 并跳转到提醒成功发送页面。
            send_status = send_register_email(email, 'forget')
            if send_status:
                return render(request, 'send_success.html')
            else:
                return render(request, 'send_fail.html')
        else:
            return render(request, 'forgetpwd.html', {'forget_form': forget_form})


class ResetView(View):
    '''重置密码并激活'''
    def get(self, request, active_code, pk):
        record = EmailVerifyRecord.objects.filter(Q(pk=pk) & Q(code=active_code))
        if record:
            email = record[0].email
            user = UserProfile.objects.get(email=email)
            user.is_active = True
            user.save()
            return render(request, 'password_reset.html', context={"email": email, 'pk': pk, 'active_code': active_code})
        else:
            return render(request, 'active_fail.html')


class ModifyPwdView(View):
    '''修改密码'''
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            email = request.POST.get('email', '')
            pk = request.POST.get('pk', 0)
            active_code = request.POST.get('active_code', '')

            if pwd1 != pwd2:
                return render(request, 'password_reset.html', {'email': email, 'msg': '密码不一致!', 'pk': pk, 'active_code': active_code})

            record = EmailVerifyRecord.objects.filter(Q(pk=pk) & Q(code=active_code))
            if record:
                email = record[0].email
                user = UserProfile.objects.get(email=email)
                user.password = make_password(pwd2)
                user.save()
                return render(request, 'reset_succ.html')
            else:
                return render(request, 'reset_fail.html')
        else:
            email = request.POST.get('email', '')
            pk = request.POST.get('pk', 0)
            active_code = request.POST.get('active_code', '')
            return render(request, 'password_reset.html', {'email': email, 'modify_form': modify_form, 'pk': pk, 'active_code': active_code})



class UserinfoView(LoginRequiredMixin, View):
    '''用户个人信息'''
    def get(self, request):
        return render(request, 'usercenter-info.html', {})

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dump(user_info_form.errors), content_type='application/json')




class UploadImageView(LoginRequiredMixin, View):
    '''用户图像修改'''
    def post(self, request):
        # 上传的文件都在request.FILES里面获取，所以这里要多传一个这个参数
        image_form = UploadImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            image = image_form.cleaned_data['image']
            request.user.image = image
            request.user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


class UpdatePwdView(LoginRequiredMixin, View):
    '''个人中心修改密码'''
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                return HttpResponse('{"status":"fail","msg":"密码不一致"}', content_type='application/json')
            user = request.user
            user.password = make_password(pwd2)
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


class SendEmailCodeView(LoginRequiredMixin, View):
    '''发送邮箱修改验证码'''
    def get(self, request):
        email = request.GET.get('email', '')
        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"邮箱已存在"}', content_type='application/json')

        send_status = send_register_email(email, send_type='update_email')
        if send_status:
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"email":"发送失败，请重新填写正确的邮箱地址"}', content_type='application/json')


class UpdateEmailView(LoginRequiredMixin, View):
    '''修改邮箱'''
    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')
        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"email":"验证码无效"}', content_type='application/json')



class MyCourseView(LoginRequiredMixin, View):
    '''我的课程'''
    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, "usercenter-mycourse.html", {
            'user_courses': user_courses,
        })


class MyFavOrgView(LoginRequiredMixin, View):
    '''我收藏的课程机构'''
    def get(self, request):
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request, 'usercenter-fav-org.html', {
            'org_list': org_list,
        })


class MyFavTeacherView(LoginRequiredMixin, View):
    '''我收藏的授课教师'''
    def get(self, request):
        teacher_list = []
        fav_tearchers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_tearcher in fav_tearchers:
            teacher_id = fav_tearcher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, 'usercenter-fav-teacher.html', {
            'teacher_list': teacher_list,
        })


class MyFavCourseView(LoginRequiredMixin, View):
    '''我收藏的公开课程'''
    def get(self, request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request, 'usercenter-fav-course.html', {
            'course_list': course_list,
        })


class MyMessageView(LoginRequiredMixin, View):
    '''我的消息'''
    def get(self, request):
        all_message = UserMessage.objects.filter(user=request.user.id)

        # 翻页
        page = request.GET.get('page', 1)
        p = Paginator(all_message, 5, request=request)

        try:
            messages = p.page(page)
        except PageNotAnInteger:
            messages = p.page(1)
        except EmptyPage:
            messages = p.page(1)
        except InvalidPage:
            messages = p.page(1)
        finally:
            return render(request, 'usercenter-message.html', {
                'messages': messages,
            })



def page_not_found(request, exception):
    '''全局404处理函数'''
    return render(request, '404.html', status=404)


def page_error(request):
    '''全局500处理函数'''
    return render(request, '500.html', status=500)


def page_permissiondenied(request, exception):
    '''全局403处理函数'''
    return render(request, '403.html', status=403)