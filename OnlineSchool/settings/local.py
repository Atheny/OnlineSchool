from .common import *

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# 改为测试环境的MySQL数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'onlineschool_test',
        'USER': 'root',
        'PASSWORD': os.environ['MYSQL_PASSWORD_LOCAL'],
        'HOST': os.environ['MYSQL_HOST_LOCAL'],
        'PORT': '3306',
        # 'OPTIONS':
        #     {
        #         'init_command': 'SET sql_mode="traditional",default_storage_engine=INNODB;',  # 设置数据库为INNODB，为第三方数据库登录用
        #         "unix_socket": "/tmp/mysql.sock",
        #     },
    }
}



