from .common import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.atheny.xyz']
ALLOWED_HOSTS = ['atheny.xyz', 'www.atheny.xyz']

# 改为线上环境的MySQL数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'onlineschool_online',
        'USER': 'root',
        'PASSWORD': os.environ['MYSQL_PASSWORD_ONLINE'],
        'HOST': os.environ['MYSQL_HOST_ONLINE'],
        'PORT': '3306',
        # 'OPTIONS':
        #     {
        #         'init_command': 'SET sql_mode="traditional",default_storage_engine=INNODB;',  # 设置数据库为INNODB，为第三方数据库登录用
        #         "unix_socket": "/tmp/mysql.sock",
        #     },
    }
}
