from datetime import datetime

from django.db import models


# Create your models here.


class CityDict(models.Model):
    '''
    城市信息
    '''
    name = models.CharField('城市', max_length=20)
    desc = models.CharField('描述', max_length=200)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        verbose_name = '城市'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name



class CourseOrg(models.Model):
    '''
    课程机构基本信息
    '''

    # 机构类别
    ORG_CHOICES = (
        ('pxjg', '培训机构'),
        ('gx', '高校'),
        ('gr', '个人'),
    )

    name = models.CharField('机构名称', max_length=100)
    desc = models.TextField('机构描述')
    category = models.CharField(max_length=20, choices=ORG_CHOICES, verbose_name='机构类别', default='pxjg')
    click_nums = models.IntegerField('点击数', default=0)
    fav_nums = models.IntegerField('收藏数', default=0)
    image = models.ImageField('logo', upload_to='org/%Y/%m', max_length=100, blank=True)
    address = models.CharField('机构地址', max_length=150)
    city = models.ForeignKey(CityDict, verbose_name='所在城市', on_delete=models.CASCADE)
    add_time = models.DateTimeField('添加时间', default=datetime.now)
    # 新增学习人数和课程数两个字段
    students = models.IntegerField('学习人数', default=0)
    course_nums = models.IntegerField('课程数', default=0)
    tag = models.CharField('机构标签', max_length=10, default='全国知名')

    class Meta:
        verbose_name = '课程机构'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    # 获取教师数量
    def get_teacher_nums(self):
        return self.teacher_set.all().count()

    get_teacher_nums.short_description = '教师数'


    def get_classify_course(self):
        courses = self.courses.all()
        courses = courses[:2] if courses.count() > 2 else courses
        return courses




class Teacher(models.Model):
    '''
    教师信息
    '''
    org = models.ForeignKey(CourseOrg, verbose_name='所属机构', on_delete=models.CASCADE)
    name = models.CharField('教师名', max_length=50)
    work_years = models.IntegerField('工作年限', default=0)
    work_company = models.CharField('就职公司', max_length=50)
    work_position = models.CharField('公司职位', max_length=50)
    points = models.CharField('教学特点', max_length=50)
    click_nums = models.IntegerField('点击数', default=0)
    fav_nums = models.IntegerField('收藏数', default=0)
    add_time = models.DateTimeField('添加时间', default=datetime.now)
    image = models.ImageField(default='', upload_to='teacher/%Y/%m', verbose_name='头像', max_length=100, blank=True)
    teacher_age = models.IntegerField('年龄', default=25)

    class Meta:
        verbose_name = '教师'
        verbose_name_plural = verbose_name


    def get_course_nums(self):
        return self.courses.all().count()

    get_course_nums.short_description = '课程数'


    def get_first_course(self):
        courses = self.courses.all()
        courses = courses[0:1] if courses.count() > 1 else courses
        return courses



    def __str__(self):
        return '[{0}]的教师：{1}'.format(self.org, self.name)
