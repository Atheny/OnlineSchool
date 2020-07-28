"""MxOnline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
import xadmin

from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.views.static import serve
from OnlineSchool.settings.common import MEDIA_ROOT, STATIC_ROOT
from users.views import LoginView, RegisterView, ActiveUserView, ForgetPwdView, ResetView, ModifyPwdView
from course.views import IndexView
from django.conf.urls import url


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('xadmin/', xadmin.site.urls),
    # path('', TemplateView.as_view(template_name='index.html', extra_context={'current_page': 'index'}), name='index'),
    path('', IndexView.as_view(), name='index'),
    # path('login/', views.user_login, name='login'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('captcha/', include('captcha.urls')),
    # 处理图片显示的url,使用Django自带serve,传入参数告诉它去哪个路径找，我们有配置好的路径MEDIAROOT
    re_path(r'^media/(?P<path>.*)', serve, {"document_root": MEDIA_ROOT}),
    # 添加邮件激活的url
    # re_path('active/(?P<active_code>[\w\d]+)/(?P<pk>\d+)/', ActiveUserView.as_view(), name='user_active'),
    path('active/<str:active_code>/<int:pk>/', ActiveUserView.as_view(), name='user_active'),
    path('forget/', ForgetPwdView.as_view(), name='forget_pwd'),
    # 重置密码激活邮箱的url
    path('reset/<str:active_code>/<int:pk>/', ResetView.as_view(), name='reset_pwd'),
    # 修改密码
    path('modify_pwd/', ModifyPwdView.as_view(), name='modify_pwd'),
    path('org/', include('organization.urls', namespace='org')),
    path('course/', include('course.urls', namespace='course')),
    # 个人信息
    path('users/', include('users.urls', namespace='users')),

    url(r'^static/(?P<path>.*)$', serve, {"document_root": STATIC_ROOT}, name='static'),
    # 增加富文本编辑器url
    path('ueditor/', include('DjangoUeditor.urls')),


]

# 全局404页面配置
handler404 = 'users.views.page_not_found'
# 全局500页面配置
handler500 = 'users.views.page_error'
# 全局403页面配置
handler403 = 'users.views.page_permissiondenied'
