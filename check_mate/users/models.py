from django.db import models
from django_resized import ResizedImageField
import json
import os

#funtion for saving image path in os
def course_picture_upload_path(instance, filename):
    # Generate file path dynamically
    return os.path.join('Courses', f'{str(instance.course_code)}','cover_picture', filename)
def question_picture_upload_path(instance, filename):
    # Generate file path dynamically
    return os.path.join('Courses', f'{str(instance.questions_of.section.course_id.course_code)}',f'{str(instance.questions_of.section.section_number)}',f'{str(instance.questions_of.exam_type)}_{str(instance.questions_of.exam_title)}','questions', filename)

def answer_picture_upload_path(instance, filename):
    # Generate file path dynamically
    return os.path.join('Courses', f'{str(instance.answer_of.questions_of.section.course_id.course_code)}',f'{str(instance.answer_of.questions_of.section.section_number)}',f'{str(instance.answer_of.questions_of.exam_type)}_{str(instance.answer_of.questions_of.exam_title)}','answers',{str(instance.uploaded_by)}, filename)

def file_upload_path(instance, filename):
    # Generate file path dynamically
    return os.path.join('Courses', f'{str(instance.exam_of.section.course_id.course_code)}',f'{str(instance.exam_of.section.section_number)}',f'{str(instance.exam_of.exam_type.exam_type)}_{str(instance.exam_of.exam_title)}','answers',{str(instance.student)}, filename)
# Create your models here.

class Session(models.Model):

    session_name = models.CharField(max_length = 50,default = "")
    session_id = models.IntegerField(default = 0)
    current = models.BooleanField(default = False)
    year = models.IntegerField(default = 0)

    def __str__(self) -> str:
        return str(self.session_name)
    
    class Meta:
        verbose_name = "Session"

class Roles(models.Model):

    '''This model will save the type of user our system will have apart from Admin'''
    #only for Instructor, and Student (Instructor id is 1 and Student is 2)

    role_id = models.IntegerField(null=False,blank=False,default = 0,unique = True)
    role_name = models.CharField(max_length = 30, null = False, blank = False)

    #This function will return the name of the role object when called.
    def __str__(self) -> str:
        return str(self.role_name)
    
    class Meta:
        #verbose name shows the name of the table according to the given one, otherwise
        #would have shown the name of the class on Admin panel. I gave both the name same.
        verbose_name = "Roles"
        #It will store the entities in the table in descending order
        ordering = ['-role_id']

class School_Users(models.Model):

    '''This model will hold all the users of our system other than admins'''
    #only for  Instructor and Student (Student can be TA)

    user_id = models.CharField(max_length = 20,null=False,blank=False,unique = True)
    user_role = models.ManyToManyField(Roles)  
    user_first_name = models.CharField(max_length = 50,null=True,blank=True)
    user_middle_name = models.CharField(max_length = 50,null=True,blank=True)
    user_last_name = models.CharField(max_length = 50,null=True,blank=True)
    user_email = models.EmailField(null = True,blank = True)
    user_phone_number = models.CharField(null=True,blank=True,max_length=16)
    user_profile_picture=ResizedImageField(null=True,blank=True,upload_to='School_User/user_profile_pictures/')
    user_otp_verified = models.BooleanField(null=True,blank=True,default = False)

    #This function will return the id of the user object when called.
    def __str__(self) -> str:
        return str(self.user_id)
    
    class Meta:

        #gave a different name on the admin panel rather then setting class name on admin
        #as default
        verbose_name = "Registered Members"


class Course(models.Model):

    '''This model will hold the course details'''

    course_code = models.CharField(max_length = 50,null=True,blank=True,default="")
    course_name = models.CharField(max_length = 200,null=True,blank=True,default="")
    course_picture = ResizedImageField(size=[500, 300], upload_to=course_picture_upload_path, blank=True, null=True)
    course_description = models.TextField(null=True,blank=True,default="")

    def __str__(self) -> str:
        return str(self.course_code)
    
    class Meta:

        verbose_name = "Courses"

class Student(models.Model):
    
    student_id = models.ForeignKey(School_Users,on_delete=models.CASCADE)
    courses = models.ForeignKey(Course,on_delete=models.CASCADE,blank=True,null=True)
    semester = models.ForeignKey(Session,on_delete = models.CASCADE)
    year = models.IntegerField(default = 0)
    section = models.IntegerField(default = 1)
    
    def __str__(self) -> str:
        return str(self.student_id)
    
    class Meta:

        verbose_name = "Student Courses"

class Instructor(models.Model):

    instructor_id = models.ForeignKey(School_Users,on_delete=models.CASCADE)
    courses = models.ForeignKey(Course,on_delete=models.CASCADE,blank=True,null=True)
    semester = models.ForeignKey(Session,on_delete = models.CASCADE)
    year = models.IntegerField(default = 0)
    section = models.IntegerField(default = 1)

    def __str__(self) -> str:
        return str(self.instructor_id.user_id)
    
    class Meta:

        verbose_name = "Instructor Courses"

class Teaching_Assistant(models.Model):

    teaching_id = models.ForeignKey(School_Users,on_delete=models.CASCADE)
    courses = models.ForeignKey(Course,on_delete=models.CASCADE,blank=True,null=True)
    semester = models.ForeignKey(Session,on_delete = models.CASCADE)
    year = models.IntegerField(default = 0)
    section = models.IntegerField(default = 1)

    def __str__(self) -> str:
        return str(self.teaching_id.user_id)
    
    class Meta:

        verbose_name = "Teaching Assistant Courses"

class Course_Section(models.Model):

    course_id = models.ForeignKey(Course,on_delete=models.CASCADE)
    section_number = models.IntegerField(default=1)
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, blank=True)
    students = models.ManyToManyField(Student)
    teaching_assistant = models.ManyToManyField(Teaching_Assistant)
    semester = models.ForeignKey(Session,on_delete = models.CASCADE)
    year = models.IntegerField(default = 0)

    def __str__(self) -> str:
        return str(self.course_id)
    
    class Meta:

        verbose_name = "Course Section"
        ordering = ['-section_number']

class Exam_Type(models.Model):

    type_id = models.IntegerField(default = 0)
    exam_type = models.CharField(max_length=50,default="",null=True,blank=True)

    def __str__(self) -> str:
        return str(self.exam_type)
    
    class Meta:

        verbose_name = "Exam Type"
    
class Exam_Mode(models.Model):

    mode_id = models.IntegerField(default = 0)
    mode = models.CharField(max_length = 50,null=True,blank=True,default="")

    def __str__(self) -> str:
        return str(self.mode)
    
    class Meta:

        verbose_name = "Exam Mode"

class Section_Exam(models.Model):

    section = models.ForeignKey(Course_Section,on_delete = models.CASCADE)
    exam_title = models.CharField(max_length = 200,null=True,blank=True)
    exam_description = models.TextField(null=True,blank=True,default="")
    exam_type = models.ForeignKey(Exam_Type,on_delete = models.CASCADE)
    exam_mode = models.ForeignKey(Exam_Mode,on_delete = models.CASCADE)
    exam_date = models.DateField(null=True,blank=True)
    exam_time = models.CharField(max_length = 50,null=True,blank=True)
    exam_set = models.IntegerField(default = 0)
    ta_available = models.BooleanField(default=False)
    is_started = models.BooleanField(default= False)
    is_stopped = models.BooleanField(default = False)
    is_completed = models.BooleanField(default = False)
    is_checked = models.BooleanField(default  = False)

    def __str__(self) -> str:
        return str(self.section)
    
    class Meta:

        verbose_name = "Section Exam"
class Students_Score(models.Model):

    exam_of = models.ForeignKey(Section_Exam,on_delete = models.CASCADE)
    student = models.ForeignKey(School_Users,on_delete = models.CASCADE)
    score = models.IntegerField(default = 0)
    total_marks = models.IntegerField(default = 0)
    exam_type= models.ForeignKey(Exam_Type,on_delete = models.CASCADE)


    def __str__(self) -> str:
        return str(self.exam_of)
    
    class Meta:
        verbose_name = "Student Score"
class Exam_Submitted(models.Model):

    exam_of = models.ForeignKey(Section_Exam,on_delete=models.CASCADE)
    student = models.ForeignKey(School_Users,on_delete=models.CASCADE)
    is_uploaded  = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.exam_of)
    
    class Meta:

        verbose_name = "Exam Submitted"

class Question(models.Model):

    questions_of = models.ForeignKey(Section_Exam,on_delete=models.CASCADE)
    question_number = models.IntegerField(null=True,blank=True,default=1)
    question = models.TextField(null=True,blank=True)
    answer_field_length = models.CharField(max_length=100,null=True,blank=True)#short,medium,long
    answer_field_length_number = models.IntegerField(default = 0)
    marks = models.IntegerField(default = 0)
    question_set = models.CharField(max_length=10,null=True,blank=True)
    question_image =  ResizedImageField(size=[500, 300], upload_to=question_picture_upload_path, blank=True, null=True)

    def __str__(self) -> str:
        return str(self.questions_of)
      
    class Meta:

        verbose_name = "Questions"

class Answer(models.Model):

    answer_of = models.ForeignKey(Question,on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(School_Users,on_delete=models.CASCADE,null=True)
    answer_textfield = models.TextField(blank=True,null=True)
    answer_image = ResizedImageField(size=[500, 300], upload_to=answer_picture_upload_path, blank=True, null=True)
    marks_obtained = models.IntegerField(default = 0)
    comment = models.TextField(null=True,blank=True)


    def __str__(self) -> str:
        return str(self.answer_of)
    
    class Meta:

        verbose_name = "Answers"

class Shuffled_Papers(models.Model):

    student = models.ForeignKey(Student,on_delete = models.CASCADE)
    course_id = models.ForeignKey(Course_Section,on_delete=models.CASCADE,null=True)
    set_name = models.CharField(max_length=10,null=True,blank=True,default="A")

    def __str__(self) -> str:
        return str(self.student)
    
    class Meta:

        verbose_name = "Shuffled Papers Student Info"