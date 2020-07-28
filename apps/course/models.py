from datetime import datetime

from django.db import models
from organization.models import CourseOrg, Teacher
from DjangoUeditor.models import UEditorField


class Course(models.Model):
    '''
    课程表
    '''
    DEGREE_CHOICES = (
        ('cj', '初级'),
        ('zj', '中级'),
        ('gj', '高级'),
    )

    name = models.CharField('课程名', max_length=50)
    # desc = models.CharField('课程描述', max_length=300)
    desc = models.TextField('课程描述', max_length=300)
    # detail = models.TextField('课程详情')
    detail = UEditorField(verbose_name=u'课程详情', width=600, height=300, imagePath='courses/ueditor/', filePath='courses/ueditor/', default='')
    degree = models.CharField('难度', choices=DEGREE_CHOICES, max_length=2)
    learn_times = models.IntegerField('学习时长(分钟数)', default=0)
    students = models.IntegerField('学习人数', default=0)
    fav_nums = models.IntegerField('收藏人数', default=0)
    image = models.ImageField('封面图', upload_to='courses/%Y/%m', max_length=100, blank=True, null=True)
    click_nums = models.IntegerField('点击数', default=0)
    add_time = models.DateTimeField('添加时间', default=datetime.now)
    course_org = models.ForeignKey(CourseOrg, on_delete=models.CASCADE, verbose_name='所属机构', null=True, blank=True, related_name='courses')
    category = models.CharField('课程类别', max_length=20, default='', blank=True)
    # 增加课程标签
    tag = models.CharField('课程标签', max_length=10, default='', blank=True)
    # 添加teacher外键
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='讲师', null=True, blank=True, related_name='courses')
    youneed_know = models.TextField('课程须知')
    teacher_tell = models.TextField('能学到什么')
    is_banner = models.BooleanField('是否轮播', default=False)


    class Meta:
        verbose_name = '课程'
        verbose_name_plural = verbose_name
        ordering = ['-add_time']


    def __str__(self):
        return self.name


    def get_degree_display(self):
        DEGREE_DICT = {
            'cj': '初级',
            'zj': '中级',
            'gj': '高级',
        }
        return DEGREE_DICT.get(self.degree, '初级')

    def get_zj_nums(self):
        '''获取课程的章节数'''
        return self.lesson_set.all().count()

    get_zj_nums.short_description = '章节数'   # 在后台显示名称

    def get_learn_users(self):
        '''获取课程的学习用户(5位)'''
        return self.usercourse_set.all()[:5] if self.usercourse_set.all().count() > 5 else self.usercourse_set.all()


    def get_course_lesson(self):
        '''获取课程的所有章节'''
        return self.lesson_set.all()


    def go_to(self):
        from django.utils.safestring import mark_safe
        # mark_safe后就不会转义
        return mark_safe('<a href="https://www.atheny.xyz/" target="__blank">跳转</a>')
    go_to.short_description = '跳转'


class Lesson(models.Model):
    '''
    章节信息表
    '''
    course = models.ForeignKey(Course, verbose_name='课程', on_delete=models.CASCADE)
    name = models.CharField('章节名', max_length=100)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        verbose_name = '章节'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '《{0}》课程的章节 >> {1}'.format(self.course, self.name)

    def get_lesson_video(self):
        '''获取章节的所有视频'''
        return self.video_set.all()



class Video(models.Model):
    '''
    视频信息
    '''
    lesson = models.ForeignKey(Lesson, verbose_name='章节', on_delete=models.CASCADE)
    name = models.CharField('视频名', max_length=100)
    url = models.CharField('访问地址', default='', max_length=200, blank=True)
    learn_times = models.IntegerField('学习时长(分钟)', default=0)
    add_time = models.DateTimeField('添加时间', default=datetime.now)
    # 增加上传视频文件
    file = models.FileField('上传视频', upload_to='course/lesson/video/%Y/%m', blank=True)

    class Meta:
        verbose_name = '视频'
        verbose_name_plural = verbose_name





class CourseResourse(models.Model):
    '''
    课程资源
    '''
    course = models.ForeignKey(Course, verbose_name='课程', on_delete=models.CASCADE)
    name = models.CharField('名称', max_length=100)
    download = models.FileField('资源文件', upload_to='course/resourse/%Y/%m', max_length=100, null=True, blank=True)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        verbose_name = '课程资源'
        verbose_name_plural = verbose_name



class BannerCourse(Course):
    '''显示轮播课程'''
    class Meta:
        verbose_name = '轮播课程'
        verbose_name_plural = verbose_name
        # 这里必须设置proxy = True, 这样就不会再生成一张表，同时还具有Model的功能
        proxy = True