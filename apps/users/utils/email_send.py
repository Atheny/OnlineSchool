from random import Random
from users.models import EmailVerifyRecord
from django.core.mail import send_mail
from OnlineSchool.settings.common import EMAIL_FROM


# 生成随机字符串
def random_str(random_length=8):
    str = ''
    # 生成字符串的可选字符串
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(random_length):
        str += chars[random.randint(0, length)]
    return str


# 发送注册邮件
def send_register_email(email, send_type='register'):
    # 发送之前先保存到数据库，到时候查询链接是否存在
    # 实例化一个EmailVerifyRecord对象
    email_record = EmailVerifyRecord()
    # 生成随机的code放入链接
    if send_type == 'update_email':
        code = random_str(6)
    else:
        code = random_str(16)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()
    pk = email_record.pk

    # 定义邮件内容:
    email_title = ''
    email_body = ''

    if send_type == 'register':
        email_title = 'Atheny在线教育注册激活链接'
        email_body = '请点击下面的链接激活你的账号: http://www.atheny.xyz/active/{0}/{1}/'.format(code, pk)
        # 使用Django内置函数完成邮件发送。四个参数：主题，邮件内容，发件人邮箱地址，收件人（是一个字符串列表）
        try:
            send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        except Exception as e:
            EmailVerifyRecord.objects.filter(pk=pk).delete()
            return False
        else:
            return True

    elif send_type == 'forget':
        email_title = 'Atheny在线教育找回密码链接'
        email_body = '请点击下面的链接找回你的密码: http://www.atheny.xyz/reset/{0}/{1}/'.format(code, pk)
        try:
            send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        except Exception as e:
            EmailVerifyRecord.objects.filter(pk=pk).delete()
            return False
        else:
            return True
    elif send_type == 'update_email':
        email_title = 'Atheny在线教育修改密码验证码'
        email_body = '你的邮箱验证码为{0}'.format(code)
        try:
            send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        except Exception as e:
            EmailVerifyRecord.objects.filter(pk=pk).delete()
            return False
        else:
            return True


