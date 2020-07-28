import xadmin

from .models import Course, BannerCourse, Lesson, Video, CourseResourse


class LessonInline(object):
    model = Lesson
    extra = 0


class CourseResourseInline(object):
    model = CourseResourse
    extra = 0


class CourseAdmin(object):
    '''
    注册课程(非轮播)
    '''
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'get_zj_nums', 'go_to']  # 显示的字段
    # detail就是要显示为富文本的字段名
    style_fields = {'detail': 'ueditor'}
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']                # 搜索
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']   # 过滤
    inlines = [LessonInline, CourseResourseInline]          # 使用inlines添加章节和课程资源，在添加课程的时候，可以直接添加章节和课程资源
    model_icon = 'fa fa-book'           # 图标
    ordering = ['-click_nums', '-students', '-fav_nums']          # 按点击数倒序排序
    readonly_fields = ['click_nums', 'students', 'fav_nums']    # 只读字段，不能编辑
    # exclude = ['fav_nums']              # 不显示的字段
    list_editable = ['degree', 'desc']  # 设置在列表页可以直接编辑的字段
    refresh_times = [3, 5]  #自动刷新（里面是秒数）

    def queryset(self):
        # 重载queryset方法，来过滤出我们想要的数据的
        qs = super(CourseAdmin, self).queryset()
        # 只显示is_banner=False的课程
        qs = qs.filter(is_banner=False)
        return qs

    def save_models(self):
        # 在保存课程的时候统计课程机构的课程数
        # obj实际是一个course对象
        obj = self.new_obj
        # 如果这里不保存，新增课程，统计的课程数会少一个
        obj.save()
        # 确定课程的课程机构存在
        if obj.course_org is not None:
            # 找到添加的课程的课程机构
            course_org = obj.course_org
            # 课程机构的课程数量等于添加课程后的数量
            course_org.course_nums = Course.objects.filter(course_org=course_org).count()
            course_org.save()



class BannerCourseAdmin(object):
    '''
    注册课程(轮播)
    '''
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'get_zj_nums', 'go_to']  # 显示的字段
    # detail就是要显示为富文本的字段名
    style_fields = {'detail': 'ueditor'}
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']                # 搜索
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']   # 过滤
    inlines = [LessonInline, CourseResourseInline]          # 使用inlines添加章节和课程资源，在添加课程的时候，可以直接添加章节和课程资源
    model_icon = 'fa fa-book'           # 图标
    ordering = ['-click_nums', '-students', '-fav_nums']          # 按点击数倒序排序
    readonly_fields = ['click_nums', 'students', 'fav_nums']    # 只读字段，不能编辑
    # exclude = ['fav_nums']              # 不显示的字段
    list_editable = ['degree', 'desc']  # 设置在列表页可以直接编辑的字段

    def queryset(self):
        # 重载queryset方法，来过滤出我们想要的数据的
        qs = super(BannerCourseAdmin, self).queryset()
        # 只显示is_banner=True的课程
        qs = qs.filter(is_banner=True)
        return qs


    def save_models(self):
        # 在保存课程的时候统计课程机构的课程数
        # obj实际是一个course对象
        obj = self.new_obj
        # 如果这里不保存，新增课程，统计的课程数会少一个
        obj.save()
        # 确定课程的课程机构存在
        if obj.course_org is not None:
            # 找到添加的课程的课程机构
            course_org = obj.course_org
            # 课程机构的课程数量等于添加课程后的数量
            course_org.course_nums = Course.objects.filter(course_org=course_org).count()
            course_org.save()



class LessonAdmin(object):
    '''
    注册章节
    '''
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course__name', 'name']
    list_filter = ['course__name', 'name', 'add_time']
    model_icon = 'fa fa-columns'


class VideoAdmin(object):
    '''
    注册视频
    '''
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson__name', 'name']
    list_filter = ['lesson__name', 'name', 'add_time']
    model_icon = 'fa fa-video-camera'


class CourseResourseAdmin(object):
    '''
    注册课程资源
    '''
    list_display = ['course', 'name', 'download', 'add_time']
    search_fields = ['course__name', 'name', 'download']
    list_filter =['course__name', 'name', 'download', 'add_time']
    model_icon = 'fa fa-file-text-o'




xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResourse, CourseResourseAdmin)