from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from datetime import date
from django.contrib.auth.models import User
from django.core.mail import send_mail
import time
from django.http import FileResponse


from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw



from .models import *
from .forms import *
from .filters import *
# Create your views here.


class LoginView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            return redirect('home')
        else:
            msg=""
            return render(request,'accounts/login.html',{'msg':msg})

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        msg ="Invalid login.Check your credentials!"
        return render(request,'accounts/login.html',{'msg':msg})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('/')


class PasswordChangeView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated: 
            form = PasswordChangeForm(user=user)
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s = Staff.objects.get(user=user)
                return render(request,'accounts/password_change.html',{'s':s,'no_count':no_count,'note':note,'form':form})
            except:
                s = Student.objects.get(user=user)
                return render(request,'students/password_change.html',{'s':s,'no_count':no_count,'note':note,'form':form})
        else:
            return redirect('logout')  

    def post(self, request):
        user = request.user
        
        form = PasswordChangeForm(user=user, data=request.POST)
        note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
        no_count = note.count()
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            msg="Password Updated successfully"
            try:
                s = Staff.objects.get(user=user)
                return render(request,'accounts/okmsg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})
            except:
                s = Student.objects.get(user=user)
                return render(request,'students/msg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})
        else:
            msg="Password Updation failed"
            try:
                s = Staff.objects.get(user=user)
                return render(request,'accounts/okmsg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})
            except:
                s = Student.objects.get(user=user)
                return render(request,'students/msg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})
        

        



class HomeView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            try:
                s = Staff.objects.get(user=user)
                if s.stype == "1" :
                    return redirect('operations_dashboard')
                elif s.stype == "2" :
                    return redirect('sales_dashboard')
                elif s.stype == "3" :
                    return redirect('trainer_dashboard')
                elif s.stype == "4" :
                    return redirect('admin_view')
                else:
                    return redirect('logout')
            except:
                try:
                    return redirect('student_dashboard')
                except:
                    return redirect('logout')
        else:
            return redirect('logout')


################################################
###        Authenticated User Functions      ###
################################################
class ProfileView(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                return render(request,'accounts/profile.html',{'s':s,'no_count':no_count,'note':note})
            except:
                s= Student.objects.get(user=user)
                return render(request,'students/profile.html',{'s':s,'no_count':no_count,'note':note})
        else:
            return redirect('logout')


class ProfileUpdate(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                form = ProfileUpdateForm(instance=s)
                return render(request,'accounts/edit_profile.html',{'s':s,'form':form,'no_count':no_count,'note':note})
            except:
                s= Student.objects.get(user=user)
                form = StudentProfileUpdateForm(instance=s)
                return render(request,'students/edit_profile.html',{'s':s,'form':form,'no_count':no_count,'note':note})
        else:
            return redirect('logout')

    def post(self, request):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                form = ProfileUpdateForm(request.POST,instance=s)
                if form.is_valid():
                    form.save()
                    return redirect('home')
                else:
                    return redirect('profile_update')
            except:
                s= Student.objects.get(user=user)
                form = StudentProfileUpdateForm(request.POST,instance=s)
                if form.is_valid():
                    form.save()
                    return redirect('profile_update')
                else:
                    return redirect('profile_update')
        else:
            return redirect('logout')



class MarkAsRead(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            try:
                ###Common code
                n= Notification.objects.filter(receiver=user)
                for i in n:
                    i.status = "Read"
                    i.save()
                return redirect('home')
                ###Common code
            except:
                return redirect('home')
        else:
            return redirect('logout')


class StudentProfileView(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                student = Student.objects.get(id=id)
                scd = StudentCourseData.objects.filter(student=student)
                return render(request,'accounts/student_profile.html',{'s':s,'no_count':no_count,'note':note,'student':student,'scd':scd})
            except:
                return redirect('home')
        else:
            return redirect('logout')


class AddStudentCourseData(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                student = Student.objects.get(id=id)
                form = AddStudentCourseDataForm()
                return render(request,'accounts/add_scd.html',{'s':s,'student':student,'no_count':no_count,'note':note,'form':form})
            except:
                return redirect('home')
        else:
            return redirect('logout')


    def post(self, request,id):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                student = Student.objects.get(id=id)
                form = AddStudentCourseDataForm(request.POST)
                if form.is_valid():
                    f =form.save(commit=False)
                    f.student = student
                    f.save()
                    re = student.user
                    n = Notification(sender=user,receiver=re,content="Batch update",subject="Added to a new batch")
                    n.save()
                    return redirect('student_profile_view',id=student.id)
                else:
                    msg="Unable to add data. If you find this as an error report it to the development team. "
                    return render(request,'okmsg',{'s':s,'msg':msg,'no_count':no_count,'note':note,'msg':msg})
            except:
                return redirect('home')
        else:
            return redirect('logout')










################################################
###             Common Functions             ###
################################################
class TaskListView(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                task=Task.objects.filter(user=s).order_by('-status','created_at')
                f=TaskFilter(self.request.GET,queryset=task)
                task=f.qs
                return render(request, 'accounts/task_list.html',{'s':s,'task':task,'f':f,'no_count':no_count,'note':note})

            except:
                return redirect('home')
        else:
            return redirect('logout')

class TaskView(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="1" or s.stype =="2" or s.stype == "3"  or s.stype == "4":
                    ###Common code 
                    task = Task.objects.get(id=id)
                    return render(request,'accounts/task_details.html',{'s':s,'task':task,'no_count':no_count,'note':note})
                    ###Common code
                else:
                    return redirect('logout')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class TaskUpdate(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="1" or s.stype =="2" or s.stype == "3" or s.stype == "4":
                    ###Common code 
                    task = Task.objects.get(id=id)
                    return render(request,'accounts/task_update.html',{'s':s,'task':task,'no_count':no_count,'note':note})
                    ###Common code
                else:
                    return redirect('logout')
            except:
                return redirect('home')
        else:
            return redirect('logout')

    def post(self, request,id):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="1" or s.stype =="2" or s.stype == "3" or s.stype == "4":
                    ###Common code 
                    task = Task.objects.get(id=id)
                    ns=request.POST.get('status')
                    if ns == task.status or ns =="None":
                        return redirect('task')
                    else:
                        Task.objects.filter(id=id).update(status=ns)
                        return redirect('task')
                    ###Common code
                else:
                    return redirect('logout')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class StudentRegister(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="1" or s.stype =="2" or s.stype == "3" or s.stype == "4":
                    note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                    no_count = note.count()
                    ###Common code 
                    students=Student.objects.all()
                    f=StudentFilter(self.request.GET,queryset=students)
                    students=f.qs
                    for i in students:
                        course_data = StudentCourseData.objects.filter(student=i)
                        i.course_enrolled=[]
                        i.now_attending=[]
                        for j in course_data:
                            i.course_enrolled.append(j.batch.subject)
                            if j.batch.status == "Ongoing":
                                i.now_attending.append(j.batch.subject)
                        i.save()
                    
                    return render(request,'accounts/student_register.html',{'s':s,'f':f,'students':students,'note':note,'no_count':no_count})
                    ###Common code
                else:
                    return redirect('logout')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class ProfilePicUpdate(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                form = ProfilePicChange(instance=s)
                return render(request,'accounts/profile_pic_update.html',{'form':form,'s':s,'no_count':no_count,'note':note})
            except:
                s= Student.objects.get(user=user)
                form = StudentProfilePicChange(instance=s)
                return render(request,'students/profile_pic_update.html',{'form':form,'s':s,'no_count':no_count,'note':note})
        else:
            return redirect('logout')

    def post(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user) 
                form = ProfilePicChange(request.POST,request.FILES,instance=s)
                if form.is_valid():
                    form.save()
                    return redirect('home')
                else:
                    msg ="Failed to update profile picture"
                    return render(request,'accounts/okmsg.html',{'msg':msg,'s':s,'no_count':no_count,'note':note})
                
            except:
                s= Student.objects.get(user=user) 
                form = StudentProfilePicChange(request.POST,request.FILES,instance=s)
                if form.is_valid():
                    form.save()
                    return redirect('home')
                else:
                    msg ="Failed to update profile picture"
                    return render(request,'students/msg.html',{'msg':msg,'s':s,'no_count':no_count,'note':note})
        else:
            return redirect('logout')






                
##########################################################################################################################################


################################################
###            Sales Functions               ###
################################################

class SalesDashboard(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="2":
                    note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                    no_count = note.count()
                    new = Lead.objects.filter(status="New").filter(generator=s)
                    new_count = new.count()
                    #for i in new:
                        #days = datetime.timedelta(30)
                    pipe = Lead.objects.filter(status="In Pipeline").filter(generator=s)
                    pipe_count = pipe.count()
                    #days = datetime.timedelta(30)
                    lead = Lead.objects.filter(generator=s).filter(Q(status="In Pipeline")|Q(status="New")).order_by('-created_on')
                    closure = Lead.objects.filter(status="Converted").filter(generator=s).filter(created_on__month__gte=date.today().month-1)
                    closure_count = closure.count()
                    return render(request,'accounts/sales_dashboard.html',{'lead':lead,'closure_count':closure_count,'s':s,'no_count':no_count,'note':note,'new':new,'new_count':new_count,'pipe':pipe,'pipe_count':pipe_count})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class CreateLead(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="2":
                    form = LeadCreateForm()
                    return render(request,'accounts/create_lead.html',{'form':form,'s':s,'no_count':no_count,'note':note})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

    
    def post(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="2":
                    form = LeadCreateForm(request.POST)
                    if form.is_valid():
                        f = form.save(commit=False)
                        f.generator = s
                        f.save()
                        return redirect('home')
                    else:
                        msg ="Failed to create lead.If this issue persist please contact the technical team."
                        return render(request,'accounts/okmsg.html',{'msg':msg,'s':s,'no_count':no_count,'note':note}) 
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class MyNewLead(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="2":
                    lead = Lead.objects.filter(status="New").filter(generator=s)
                    f=LeadFilter(self.request.GET,queryset=lead)
                    lead=f.qs
                    return render(request,'accounts/my_lead.html',{'f':f,'s':s,'no_count':no_count,'note':note,'lead':lead})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class MyLeadInPipeline(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="2":
                    lead = Lead.objects.filter(status="In Pipeline").filter(generator=s)
                    f=LeadFilter(self.request.GET,queryset=lead)
                    lead=f.qs
                    return render(request,'accounts/my_lead_in_pipeline.html',{'f':f,'s':s,'no_count':no_count,'note':note,'lead':lead})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class MyClosedLead(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="2":
                    lead = Lead.objects.filter(status="Closed").filter(generator=s)
                    f=LeadFilter(self.request.GET,queryset=lead)
                    lead=f.qs
                    return render(request,'accounts/closed_lead.html',{'f':f,'s':s,'no_count':no_count,'note':note,'lead':lead})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class MyLeadRegister(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="2":
                    lead = Lead.objects.filter(generator=s)
                    f=LeadFilter(self.request.GET,queryset=lead)
                    lead=f.qs
                    return render(request,'accounts/lead_register.html',{'f':f,'s':s,'no_count':no_count,'note':note,'lead':lead})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class LeadUpdateView(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="2":
                    lead = Lead.objects.get(id=id)
                    form = LeadCreateForm(instance=lead)
                    return render(request,'accounts/lead_update.html',{'form':form,'s':s,'no_count':no_count,'note':note,'lead':lead})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

    
    def post(self, request,id):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="2":
                    lead = Lead.objects.get(id=id)
                    form = LeadCreateForm(request.POST,instance=lead)
                    if form.is_valid():
                        f = form.save(commit=False)
                        f.generator=s
                        f.save()
                        return redirect('home')
                    else:
                        msg ="Failed to update lead.If this issue persist please contact the technical team."
                        return render(request,'accounts/okmsg.html',{'msg':msg,'s':s,'no_count':no_count,'note':note}) 
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')



class CreateStudentView(View):
    def get(self, request, id):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "2":
                    ###Common code for operations
                    l =Lead.objects.get(id=id)
                    user = User.objects.create_user(l.email,l.email,l.mobile)
                    try:
                        user.save()
                        student = Student(user=user,name=l.name,email=l.email,mobile=l.mobile,sex=l.sex)
                        student.save()
                        msg="Learner account created successfully and mails have been sent."
                        l.status = "Converted"
                        l.save()
                        send_mail(
                            '[TEQSTORIES] Account Created',
                            'Hello learner, Your learner account has been created successfully.Please login to http://127.0.0.1/ with your email as username and mobile number as password.',
                            'anandubs1409@gmail.com',
                            [l.email],
                            fail_silently=False,
                        )
                    except:
                        msg="Learner account creation failed."
                    return render(request,'accounts/okmsg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})
                    ###Common code for operations
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')








##########################################################################################################################################


################################################
###          Operations Functions            ###
################################################
class OperationsDashboard(View):
   
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="1":
                    ###Common code for operations
                    ba=Batch.objects.filter(status="Ongoing")
                    ba_count = ba.count()
                    by=Batch.objects.filter(status="Yet to start")
                    by_count = by.count()
                    ta=Task.objects.filter(user=s).filter(~Q(status="Completed"))
                    ta_count = ta.count()
                    students=Student.objects.all()
                    note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                    no_count = note.count()
                    for i in students:
                        course_data = StudentCourseData.objects.filter(student=i)
                        i.course_enrolled=[]
                        i.now_attending=[]
                        for j in course_data:
                            i.course_enrolled.append(j.batch.subject)
                            if j.batch.status == "Ongoing":
                                i.now_attending.append(j.batch.subject)
                        i.save()
                    return render(request,'accounts/operations_dashboard.html',{'ba_count':ba_count,'by_count':by_count,'by':by,'ba':ba,'ta':ta,'ta_count':ta_count,'students':students,'no_count':no_count,'note':note,'s':s})
                    ###Common code for operations
                return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class AddBatchView(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "1":
                    note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                    no_count = note.count()
                    ###Common code for operations
                    t=Staff.objects.filter(stype="3")
                    c=Courses.objects.all()
                    return render(request,'accounts/batch_creation_form.html',{'t':t,'c':c,'no_count':no_count,'note':note})
                    ###Common code for operations
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

    def post(self, request):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "1":
                    ###Common code for operations
                    subject = request.POST.get('subject')
                    s=Courses.objects.get(name=subject)
                    trainer = request.POST.get('trainer')
                    if trainer!="None":
                        tra=Staff.objects.get(name=trainer)
                    mod = request.POST.get('mod')
                    status = request.POST.get('status')
                    t=request.POST.get('timing')
                    sd=request.POST.get('start_date')
                    ed=request.POST.get('end_date')
                    if trainer=="None":
                        b=Batch(subject=s,timing=t,start_date=sd,end_date=ed,mode=mod,status=status)
                    else:
                        b=Batch(subject=s,trainer=tra,timing=t,start_date=sd,end_date=ed,mode=mod,status=status)
                        re = tra.user
                        n = Notification(sender=user,receiver=re,content="Batch created",subject=b)
                        n.save()
                    b.save()
                    if status=="1":
                        return redirect('upcoming_batch_register')
                    else:
                        return redirect('active_batch_register')
                    ###Common code for operations
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')
                


        
class AllBatchView(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "1" or s.stype == "3":
                    ###Common code for operations
                    b=Batch.objects.filter(mode="1")
                    c=Batch.objects.filter(mode="2")
                    return render(request,'accounts/all_batches.html',{'s':s,'b':b,'c':c,'no_count':no_count,'note':note})
                    ###Common code for operations
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class AllActiveBatchView(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "1" or s.stype == "3" :
                    ###Common code for operations
                    b=Batch.objects.filter(status='Ongoing',mode="1")
                    c=Batch.objects.filter(status='Ongoing',mode="2")
                    return render(request,'accounts/all_active_batches.html',{'s':s,'b':b,'c':c,'no_count':no_count,'note':note})
                    ###Common code for operations
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class EditBatchView(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                b=Batch.objects.get(id=id)
                if s.stype == "1":
                    ###Common code for operations
                    form = AddBatchForm(instance=b)
                    return render(request,'accounts/batch_updation_form.html',{'s':s,'b':b,'form':form,'no_count':no_count,'note':note})
                    ###Common code for operations
                elif  s.stype == "3":
                    update = UpdateBatchForm(instance=b)
                    return render(request,'accounts/batch_updation_form.html',{'s':s,'b':b,'no_count':no_count,'note':note,'update':update})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

    def post(self, request,id):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                b=Batch.objects.get(id=id)
                if s.stype == "1" :
                    ###Common code for operations
                    form = AddBatchForm(request.POST,instance=b)
                    if form.is_valid():
                        form.save()
                        st=form.cleaned_data['status']
                        tr= form.cleaned_data['trainer']
                        if tr:
                            re = User.objects.get(username=tr.user)
                            n = Notification(sender=user,receiver=re,content="Batch updated",subject=b)
                            n.save()
                        if st == "Completed":
                            p = Project(batch=b)
                            p.save()
                        name = []
                        scd = StudentCourseData.objects.filter(batch=b)
                        for i in scd:
                            name.append(i.student)
                        stu = Student.objects.filter(name__in=name)
                        for i in stu:
                            re = i.user
                            n = Notification(sender=user,receiver=re,content="Batch ended and projects released for ",subject=b)
                            n.save()
        
                        if st =="Ongoing":
                            return redirect('active_batch_register')
                        else :
                            return redirect('batch_register')

                    else:
                        msg="Please review your edit."
                        return render(request,'accounts/okmsg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})
                    ###Common code for operations
                elif s.stype == "3":
                    update = UpdateBatchForm(request.POST,instance=b)
                    if update.is_valid():
                        update.save()
                        st=update.cleaned_data['status']
                        if st == "Completed":
                            p = Project(batch=b)
                            p.save()
                        name = []
                        scd = StudentCourseData.objects.filter(batch=b)
                        for i in scd:
                            name.append(i.student)
                        stu = Student.objects.filter(name__in=name)
                        for i in stu:
                            re = i.user
                            n = Notification(sender=user,receiver=re,content="Batch ended and projects released for ",subject=b)
                            n.save()
                        return redirect('home')
                    else:
                        msg="Please review your edit."
                        return render(request,'accounts/okmsg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})


                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class DeleteBatch(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            s= Staff.objects.get(user=user)
            try:
                if s.stype == "1":
                    ###Common code for operations
                    b=Batch.objects.get(id=id)
                    msg="Are you sure you want to delete?"
                    return render(request,'accounts/msg.html',{'b':b,'msg':msg,'no_count':no_count,'note':note})
                    ###Common code for operations
                else:
                    msg="You dont have permission to delete batches."
                    return render(request,'accounts/okmsg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})
            except:
                return redirect('home')
        else:
            return redirect('logout')

    def post(self, request,id):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "1":
                    ###Common code for operations
                    b=Batch.objects.get(id=id)
                    b.delete()
                    return redirect('operations_dashboard')
                    ###Common code for operations
                else:
                    msg="You dont have permission to delete batches."
                    return render(request,'accounts/okmsg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})
            except:
                return redirect('home')
        else:
            return redirect('logout')
        



class AllUpcomingBatchView(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "1" or s.stype == "3":
                    note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                    no_count = note.count()
                    ###Common code for operations
                    b=Batch.objects.filter(status='Yet to start',mode="1")
                    c=Batch.objects.filter(status='Yet to start',mode="2")
                    return render(request,'accounts/all_upcoming_batches.html',{'s':s,'b':b,'c':c,'no_count':no_count,'note':note})
                    ###Common code for operations
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class TrainerList(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "1":
                    note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                    no_count = note.count()
                    ###Common code for operations
                    t=Staff.objects.filter(stype="3")
                    return render(request,'accounts/all_trainer_list.html',{'s':s,'t':t,'no_count':no_count,'note':note})
                    ###Common code for operations
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class TrainerProfileView(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "1":
                    note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                    no_count = note.count()
                    ###Common code for operations
                    t=Staff.objects.get(id=id)
                    return render(request,'accounts/trainer_profile.html',{'t':t,'no_count':no_count,'note':note})
                    ###Common code for operations
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class QueryList(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "1":
                    note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                    no_count = note.count()
                    ###Common code for operations
                    q=Query.objects.filter(receiver=s).filter(status="Not replied")
                    return render(request,'accounts/read_queries.html',{'q':q,'no_count':no_count,'note':note})
                    ###Common code for operations
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class ReplyQuery(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "1":
                    note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                    no_count = note.count()
                    ###Common code for operations
                    q=Query.objects.get(id=id)
                    form = QuerySendForm(instance=q)
                    return render(request,'accounts/reply_query.html',{'form':form,'no_count':no_count,'note':note})
                    ###Common code for operations
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

    def post(self, request,id):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "1":
                    ###Common code for operations
                    q=Query.objects.get(id=id)
                    q.reply=request.POST.get('reply')
                    q.status="Replied"
                    q.save()
                    re = q.sender.user
                    n = Notification(sender=user,receiver=re,content="Re : Query",subject=q.subject)
                    n.save()
                    return redirect('query_list')
                    ###Common code for operations
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class DeactivateStaff(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "1"or s.stype == "4":
                    ###Common code for operations
                    t =Staff.objects.get(id=id)
                    t.status="Inactive"
                    t.save()
                    u =t.user
                    u.is_active = False
                    u.save()
                    return redirect(request.META['HTTP_REFERER'])
                    ###Common code for operations
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class ActivateStaff(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "1" or s.stype == "4":
                    ###Common code for operations
                    t =Staff.objects.get(id=id)
                    t.status="Active"
                    t.save()
                    u =t.user
                    u.is_active = True
                    u.save()
                    return redirect(request.META['HTTP_REFERER'])
                    ###Common code for operations
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class DeactivateStudent(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "1" or s.stype == "4":
                    ###Common code for operations
                    t =Student.objects.get(id=id)
                    t.status="Inactive"
                    t.save()
                    u =t.user
                    u.is_active = False
                    u.save()
                    return redirect(request.META['HTTP_REFERER'])
                    ###Common code for operations
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class ActivateStudent(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "1" or s.stype == "4":
                    ###Common code for operations
                    t =Student.objects.get(id=id)
                    t.status="Active"
                    t.save()
                    u =t.user
                    u.is_active = True
                    u.save()
                    return redirect(request.META['HTTP_REFERER'])
                    ###Common code for operations
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class RemoveSCD(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "1" or s.stype=="4" :
                    scd = StudentCourseData.objects.get(id=id)
                    scd.delete()
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    msg="Failed to delete Student Course Data"
                    return render(request,'accounts/okmsg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})
            except:
                return redirect('home')
        else:
            return redirect('logout')
                














#########################################################################################################################################








################################################
###            Trainer Functions             ###
################################################
class TrainerDashboard(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="3":
                    ###Common code for trainers
                    batch = Batch.objects.filter(trainer=s).filter(status="Ongoing")
                    name = []
                    scd = StudentCourseData.objects.filter(batch__in=batch)
                    for i in scd:
                        name.append(i.student.name)
                    students = Student.objects.filter(name__in=name)
                    for i in students:
                        course_data = StudentCourseData.objects.filter(student=i)
                        i.course_enrolled=[]
                        i.now_attending=[]
                        for j in course_data:
                            i.course_enrolled.append(j.batch.subject)
                            if j.batch.status == "Ongoing":
                                i.now_attending.append(j.batch.subject)
                                i.save()
                    ba = Batch.objects.filter(trainer=s).filter(status="Ongoing")
                    ba_count = ba.count()
                    by = Batch.objects.filter(trainer=s).filter(status="Yet to start")
                    by_count = by.count()
                    ta  = Task.objects.filter(user=s).filter(~Q(status="Completed"))
                    ta_count = ta.count()
                    q = Doubt.objects.filter(receiver=s).filter(status="Not replied")
                    q_count = q.count()
                    return render(request,'accounts/trainer_dashboard.html',{'q':q,'q_count':q_count,'s':s,'by':by,'ta_count':ta_count,'ta':ta,'ba':ba,'ba_count':ba_count,'by_count':by_count,'note':note, 'no_count':no_count,'students':students})
                    ###Common code for trainers
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class MyStudents(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="3":
                    batch = Batch.objects.filter(trainer=s).filter(status="Ongoing")
                    name = []
                    scd = StudentCourseData.objects.filter(batch__in=batch)
                    for i in scd:
                        name.append(i.student.name)
                    students = Student.objects.filter(name__in=name)
                    f=StudentFilter(self.request.GET,queryset=students)
                    students=f.qs
                    for i in students:
                        course_data = StudentCourseData.objects.filter(student=i)
                        i.course_enrolled=[]
                        i.now_attending=[]
                        for j in course_data:
                            i.course_enrolled.append(j.batch.subject)
                            if j.batch.status == "Ongoing":
                                i.now_attending.append(j.batch.subject)
                            i.save()
                    return render(request,'accounts/my_student_register.html',{'s':s,'f':f,'students':students,'note':note,'no_count':no_count})
                    ###Common code
                else:
                    return redirect('logout')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class UpcomingBatchView(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "3":
                    ###Common code for trainers
                    b=Batch.objects.filter(status='Yet to start',mode="1",trainer=s)
                    c=Batch.objects.filter(status='Yet to start',mode="2",trainer=s)
                    return render(request,'accounts/upcoming_batches.html',{'s':s,'b':b,'c':c,'no_count':no_count,'note':note})
                    ###Common code for trainers
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class ActiveBatchView(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "3" :
                    ###Common code for trainers
                    b=Batch.objects.filter(status='Ongoing',mode="1",trainer=s)
                    c=Batch.objects.filter(status='Ongoing',mode="2",trainer=s)
                    return render(request,'accounts/active_batches.html',{'s':s,'b':b,'c':c,'no_count':no_count,'note':note})
                    ###Common code for trainers
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class ViewQueries(View):
    def get(self, request): 
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s = Staff.objects.get(user=user)
                if s.stype == "3":
                    q= Doubt.objects.filter(receiver=s).order_by('-datetime')
                    return render(request,'accounts/queries.html',{'s':s,'no_count':no_count,'note':note,'q':q})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        return redirect('logout')


class DetailedViewQuery(View):
    def get(self, request,id): 
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s = Staff.objects.get(user=user)
                q= Doubt.objects.filter(receiver=s).get(id=id)
                if s.stype == "3":
                    form = SolutionSendForm(instance=q)
                    return render(request,'accounts/send_solution.html',{'form': form,'s':s,'no_count':no_count,'note':note,'q':q})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        return redirect('logout')
    
    def post(self, request,id): 
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s = Staff.objects.get(user=user)
                q= Doubt.objects.get(id=id)
                form = SolutionSendForm(request.POST,instance=q)
                re = q.sender.user
                subject=q.subject
                if form.is_valid():
                    form.save()
                    q.status ="Replied"
                    q.save()
                    n = Notification(sender=user,receiver=re,content="Re : Doubt",subject=subject)
                    n.save()
                    msg="Reply send Successfully!."
                    return render(request,'accounts/okmsg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})
                else:
                    msg="Encountered an error.Feel free to contact the developers in case this error persist."
                    return render(request,'accounts/okmsg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})
            except:
                return redirect('home')
        else:
            return redirect('logout')

class ActiveBatchList(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s = Staff.objects.get(user=user)
                batch = Batch.objects.filter(trainer=s).filter(status="Ongoing")
                if s.stype == "3":
                    return render(request,'accounts/activebatch.html',{'s':s,'batch':batch,'no_count':no_count,'note':note})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class BatchContent(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s = Staff.objects.get(user=user)
                if s.stype == "3":
                    batch = Batch.objects.get(id=id)
                    batch_data = BatchData(batch=batch)
                    form = AddBatchData(instance=batch_data)
                    return render(request,'accounts/add_video.html',{'form':form,'s':s,'no_count':no_count,'note':note,'batch':batch})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

    def post(self, request,id):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s = Staff.objects.get(user=user)
                if s.stype == "3":
                    batch = Batch.objects.get(id=id)
                    batch_data = BatchData(batch=batch)
                    form = AddBatchData(request.POST,instance=batch_data)
                    if form.is_valid():
                        link=form.cleaned_data['link']
                        string ="https://transcripts.gotomeeting.com"
                        if string in link:
                            bd = form.save(commit=False)
                            bd.batch = batch
                            bd.save()
                        else:
                            link = link[:-16]+"preview"
                            bd = form.save(commit=False)
                            bd.link = link
                            bd.batch = batch
                            bd.save()
                        
                        scd = StudentCourseData.objects.filter(batch=batch)
                        name = []
                        for i in scd:
                            name.append(i.student)
                        students = Student.objects.filter(name__in=name)
                        for i in students:
                            re = i.user
                            
                            n = Notification(sender=user,receiver=re,content="Batch Video Uploaded",subject=batch)
                            n.save()
                        msg="Course video added and notifications send"
                        return render(request,'accounts/okmsg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})
                    else:
                        msg="Course video adding failed"
                        return render(request,'accounts/okmsg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class BatchContentList(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s = Staff.objects.get(user=user)
                if s.stype == "3":
                    batch = Batch.objects.get(id=id)
                    batch_data = BatchData.objects.filter(batch=batch)
                    return render(request,'accounts/video_list.html',{'batch_data':batch_data,'no_count':no_count,'note':note,'batch':batch,'s':s})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')






class TrainerRegistrationView(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "3":
                    ###Common code for trainers
                    form =StaffCreationForm()
                    return render(request,'accounts/staff_registration.html',{'form':form})
                    ###Common code for trainers
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

    def post(self, request):
        user=request.user
        if user.is_authenticated:
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "3":
                    ###Common code for trainers
                    form =StaffCreationForm(request.POST)
                    if form.is_valid():
                        user = form.save()
                        name = request.POST.get('name')
                        mobile = request.POST.get('mobile')
                        city = request.POST.get('city')
                        stype=3
                        s = Staff(user=user, name=name,mobile=mobile, city=city, stype=stype)
                        s.save()
                        return HttpResponse("Done")
                    else:
                        return HttpResponse("Failed")
                    ###Common code for trainers
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class AddAssignment(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "3":
                    ###Common code for trainers
                    form = AddAssignmentForm()
                    return render(request,'accounts/add_assignment.html',{'form':form,'s':s,'no_count':no_count,'note':note})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

    def post(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "3":
                    ###Common code for trainers
                    form = AddAssignmentForm(request.POST)
                    try:
                        link = request.POST['link']
                        if link == "":
                            f = form.save(commit=False)
                            f.link = "N/A"
                            f.save()
                        else:
                            f = form.save(commit=False)
                            f.link = link
                            f.save()
                        batch = form.cleaned_data['batch']
                        scd = StudentCourseData.objects.filter(batch=batch)
                        name = []
                        for i in scd:
                            name.append(i.student)
                        students = Student.objects.filter(name__in=name)
                        for i in students:
                            re = i.user
                            n = Notification(sender=user,receiver=re,content="Assignment Uploaded for",subject=batch)
                            n.save()
                        msg="Assignment added successfully and notifications send."
                        return render(request,'accounts/okmsg.html',{'msg':msg,'no_count':no_count,'note':note,'s':s})
                    except:
                        msg="Assignment adding failed.Please contact tech team for more information."
                        return render(request,'accounts/okmsg.html',{'msg':msg,'no_count':no_count,'note':note,'s':s})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')



class ViewAssignments(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "3":
                    ###Common code for trainers
                    batch = Batch.objects.filter(trainer=s).filter(status="Ongoing")
                    assi = Assignment.objects.filter(batch__in=batch).order_by('-datecreated')
                    return render(request,'accounts/assignment_list.html',{'assi':assi,'no_count':no_count,'note':note,'s':s})
                    ###Common code for trainers                
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class ViewSubmissions(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "3":
                    ###Common code for trainers
                    assi = Assignment.objects.get(id=id)
                    sad = StudentAssignmentData.objects.filter(assignment=assi)
                    return render(request,'accounts/submissions.html',{'assi':assi,'no_count':no_count,'note':note,'s':s,'sad':sad})
                    ###Common code for trainers                
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class ViewProjectSubmissions(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "3":
                    ###Common code for trainers
                    batch = Batch.objects.filter(trainer=s).filter(status="Completed")
                    project = Project.objects.filter(batch__in=batch)
                    spd =StudentProjectData.objects.filter(project__in=project).filter(status="Waiting for approval")
                    print(spd)
                    form = ProjectApproval()
                    return render(request,'accounts/project_submissions.html',{'s':s,'no_count':no_count,'note':note,'spd':spd,'form':form})
                    ###Common code for trainers                
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

class UpdateSPD(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "3":
                    ###Common code for trainers
                    spd = StudentProjectData.objects.get(id=id)
                    form = ProjectApproval(instance=spd)
                    return render(request,'accounts/edit_spd.html',{'form':form,'s':s,'no_count':no_count,'note':note,'spd':spd})
                    ###Common code for trainers                
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

    def post(self, request,id):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype == "3":
                    ###Common code for trainers
                    spd = StudentProjectData.objects.get(id=id)
                    form = ProjectApproval(request.POST,instance=spd)
                    if form.is_valid():
                        f = form.save(commit=False)
                        f.verified_on = datetime.datetime.now()
                        if form.cleaned_data['status']=="Approved":
                            epoch = time.time()
                            spd_id = "TS" # this could be incremental or even a uuid
                            f.certificate_id = "%s_%d" % (spd_id, epoch)
                            template = CertificateTemplate.objects.get(name="sample")
                            c_id = str(f.certificate_id)
                            date = str(datetime.datetime.now().date())
    ############################################################################################################################
                            img = Image.open(template.certificate)
                            draw = ImageDraw.Draw(img)
                            file_name = str("certificates/"+f.certificate_id+".pdf")
                            selectFont = ImageFont.truetype("arialbd.ttf", size = 150)
                            courseFont = ImageFont.truetype("arialbd.ttf", size = 100)
                            codeFont = ImageFont.truetype("arialbd.ttf", size = 80)
                            draw.text( (1750,980), spd.student.name, (1,91,153),anchor="ma",font=selectFont,align ="center")
                            draw.text( (1750,1430), spd.project.batch.subject.name, (1,1,1),anchor="ma",font=courseFont,align ="center")
                            draw.text( (746,1960),c_id, (1,1,1),anchor="ma",font=codeFont,align ="center")
                            draw.text( (1786,1960), date, (1,1,1),anchor="ma",font=codeFont,align ="center")
                            img.save( file_name, "PDF", resolution=70.0)
###########################################################################################################################
                        f.save()
                        re = spd.student.user
                        n = Notification(sender=user,receiver=re,content="Project approved ",subject=spd.project)
                        n.save()
                        generate()
                        return redirect('project_submissions')
                    else:
                        msg="Failed to update the project status."
                        return render(request,'accounts/okmsg.html',{'msg':msg,'no_count':no_count,'note':note,'s':s})
                    ###Common code for trainers                
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')





















#########################################################################################################################################




################################################
###            Student Functions             ###
################################################

class StudentDashboard(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s = Student.objects.get(user=user)
                ###Common code for students
                scd = StudentCourseData.objects.filter(student=s).filter(~Q(batch__status="Yet to start"))
                scd_count = scd.count()
                c = Courses.objects.all()
                q=Query.objects.filter(sender=s,status="Not replied")
                q_count = q.count()
                d=Doubt.objects.filter(sender=s,status="Not replied")
                d_count = d.count()
                return render(request,'students/dashboard.html',{'s':s,'scd':scd,'scd_count':scd_count,'q_count':q_count,'no_count':no_count,'note':note,'d_count':d_count})
                ###Common code for students
            except:
                return redirect('home')
        return redirect('logout')


class MyCourses(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                scd = StudentCourseData.objects.filter(student=s).filter(batch__status="Ongoing")
                return render(request,'students/my_courses.html',{'s':s,'scd':scd,'no_count':no_count,'note':note})
                ###Common code for students
            except:
                return redirect('home')
        return redirect('logout')

class MyCourseList(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                scd = StudentCourseData.objects.filter(student=s).filter(~Q(batch__status="Yet to start"))
                scd_count = scd.count()
                c = Courses.objects.all()
                return render(request,'students/active_course_list.html',{'s':s,'scd':scd,'scd_count':scd_count,'no_count':no_count,'note':note})
                ###Common code for students
            except:
                return redirect('home')
        return redirect('logout')

class VideoList(View):
    def get(self, request,id): #id of batch is passed as parameter
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                batch = Batch.objects.get(id=id)
                scd = StudentCourseData.objects.filter(student=s).filter(batch=batch)
                if scd:
                    batch_data = BatchData.objects.filter(batch=batch)
                    return render(request,'students/video_list.html',{'batch_data':batch_data,'batch':batch,'no_count':no_count,'note':note})
                else:
                    msg = "You are not authorized to access this play list"
                    return render(request,'student/msg.html',{'msg':msg,'no_count':no_count,'note':note})
                ###Common code for students
            except:
                return redirect('home')
        return redirect('logout')

class PlayVideo(View):
    def get(self, request,id): 
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s = Student.objects.get(user=user)
                ###Common code for students
                batch_data = BatchData.objects.get(id=id)
                scd = StudentCourseData.objects.get(student=s,batch=batch_data.batch)
                if scd.payment =="Full" or scd.optional =="Yes":
                    return render(request,'students/videoplayer.html',{'batch_data':batch_data,'no_count':no_count,'note':note})
                else:
                    msg="Please contact you representative to access this course videos!"
                    return render(request,'students/msg.html',{'msg':msg,'no_count':no_count,'note':note})
                ###Common code for students
            except:
                s = Staff.objects.get(user=user)
                if s.stype == "3":
                    batch_data = BatchData.objects.get(id=id)
                    return render(request,'accounts/videoplayer.html',{'batch_data':batch_data,'no_count':no_count,'note':note})
                else:
                    return redirect('home')
        return redirect('logout')

class SendQuery(View):
    def get(self, request): 
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                form = QuerySendForm()
                st=Staff.objects.filter(stype="1")
                return render(request,'students/send_query.html',{'s':s,'form':form,'st':st,'no_count':no_count,'note':note})
                ###Common code for students
            except:
                return redirect('home')
        return redirect('logout')


    def post(self, request): 
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                form = QuerySendForm(request.POST)
                if form.is_valid():
                    f=form.save(commit=False)
                    f.sender=s
                    f.save()
                    receiver=form.cleaned_data['receiver']
                    subject=form.cleaned_data['subject']
                    r=Staff.objects.get(name=receiver)
                    re=r.user
                    n = Notification(sender=user,receiver=re,content="Issue",subject=subject)
                    n.save()
                    msg="Issue Raised"
                    return render(request,'students/msg.html',{'msg':msg,'no_count':no_count,'note':note})
                else:
                    msg="Failed to raise issue. Try again and mention all fields."
                    return render(request,'students/msg.html',{'msg':msg,'no_count':no_count,'note':note})
                ###Common code for students
            except:
                return redirect('home')
        return redirect('logout')


class ViewQueryReply(View):
    def get(self, request): 
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                q= Query.objects.filter(sender=s).order_by('-datetime')
                return render(request,'students/responses.html',{'s':s,'no_count':no_count,'note':note,'q':q})
                ###Common code for students
            except:
                return redirect('home')
        return redirect('logout')

class ViewQReply(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                q=Query.objects.get(id=id)
                form = QuerySendForm(instance=q)
                return render(request,'students/reply.html',{'s':s,'no_count':no_count,'note':note,'form':form})
                ###Common code for students
            except:
                return redirect('home')
        return redirect('logout')



class SendDoubt(View):
    def get(self, request): 
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                form = DoubtSendForm()
                st=Staff.objects.filter(stype="3")
                return render(request,'students/send_doubt.html',{'s':s,'form':form,'st':st,'no_count':no_count,'note':note})
                ###Common code for students
            except:
                return redirect('home')
        return redirect('logout')

    def post(self, request): 
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                form = DoubtSendForm(request.POST,request.FILES)
                if form.is_valid():
                    f=form.save(commit=False)
                    f.sender=s
                    f.save()
                    receiver=form.cleaned_data['receiver']
                    subject=form.cleaned_data['subject']
                    r=Staff.objects.get(name=receiver)
                    re=r.user
                    n = Notification(sender=user,receiver=re,content="Doubt",subject=subject)
                    n.save()
                    msg="Doubt send.Your trainer will get back to you soon."
                    return render(request,'students/msg.html',{'msg':msg,'no_count':no_count,'note':note})
                else:
                    msg="Failed to send doubt. Try again or report it as Issue."
                    return render(request,'students/msg.html',{'msg':msg,'no_count':no_count,'note':note})
                ###Common code for students
            except:
                return redirect('home')
        return redirect('logout')

class ViewDoubtReply(View):
    def get(self, request): 
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                d= Doubt.objects.filter(sender=s).order_by('-datetime')
                return render(request,'students/dresponses.html',{'s':s,'no_count':no_count,'note':note,'d':d})
                ###Common code for students
            except:
                return redirect('home')
        return redirect('logout')

class ViewDReply(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                d=Doubt.objects.get(id=id)
                form = DoubtSendForm(instance=d)
                return render(request,'students/dreply.html',{'s':s,'no_count':no_count,'note':note,'form':form,'d':d})
                ###Common code for students
            except:
                return redirect('home')
        return redirect('logout')

class ListAssignments(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                scd = StudentCourseData.objects.filter(student=s)
                batch = []
                for i in scd:
                    batch.append(i.batch)
                assi = Assignment.objects.filter(batch__in=batch).order_by('-datecreated')
                return render(request,'students/assignment_list.html',{'assi':assi,'s':s,'no_count':no_count,'note':note})
            except:
                return redirect('home')
        else:
            return redirect('logout')

class ViewAssignment(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                assi = Assignment.objects.get(id=id)
                print(assi)
                sad = StudentAssignmentData.objects.filter(student=s).filter(assignment=assi)
                print(sad)
                if sad:
                    b = "Y"
                else:
                    b = "N"
                print(b)
                return render(request,'students/assignment_details.html',{'assi':assi,'no_count':no_count,'note':note,'s':s,'b':b})
                ###Common code for students
            except:
                return redirect('home')
        else:
            return redirect('logout')

class SubmitAssignment(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                assi = Assignment.objects.get(id=id)
                print(assi)
                return render(request,'students/submit_assignment.html',{'assi':assi,'no_count':no_count,'note':note})
                ###Common code for students
            except:
                return redirect('home')
        else:
            return redirect('logout')

    def post(self, request,id):
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                assi = Assignment.objects.get(id=id)
                link = request.POST['link']
                sad = StudentAssignmentData(student=s,assignment=assi,link=link)
                sad.save()
                return redirect('assignment_list')
                ###Common code for students
            except:
                return redirect('home')
        else:
            return redirect('logout')

class ListProjects(View):
    def get(self, request):    
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                scd = StudentCourseData.objects.filter(student=s)
                batch = []
                for i in scd:
                    batch.append(i.batch)
                projects = Project.objects.filter(batch__in = batch)
                return render(request,'students/available_projects.html',{'s':s,'no_count':no_count,'note':note,'projects':projects})
                ###Common code for students
            except:
                return redirect('home')
        else:
            return redirect('logout')

class SubmitProject(View):
    def get(self, request,id):    
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                project = Project.objects.get(id=id)
                spd = StudentProjectData.objects.filter(student=s).filter(project=project)
                if spd:
                    msg="You have already uploaded once.Please contact tech team if this is an error."
                    return render(request,'students/msg.html',{'msg':msg,'no_count':no_count,'note':note})
                else:
                    return render(request,'students/submit_project.html',{'project':project,'no_count':no_count,'note':note})
                ###Common code for students
            except:
                return redirect('home')
        else:
            return redirect('logout')

    def post(self, request,id):    
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                project = Project.objects.get(id=id)
                link = request.POST['link']
                try:
                    spd = StudentProjectData(student=s,project=project,link=link)
                    print(spd)
                    spd.save()
                    msg="Project uploaded successfully.You will be notified when your project is approved and certificate is generated."
                    return render(request,'students/msg.html',{'msg':msg,'no_count':no_count,'note':note})
                except:
                    msg="Failed to upload project. Try again or report it as Issue."
                    return render(request,'students/msg.html',{'msg':msg,'no_count':no_count,'note':note})
                ###Common code for students
            except:
                return redirect('home')
        else:
            return redirect('logout')

class GetCertificates(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
                no_count = note.count()
                ###Common code for students
                spd = StudentProjectData.objects.filter(student=s).filter(status="Approved")
                print(spd)
                return render(request,'students/certificates.html',{'s':s,'spd':spd,'no_count':no_count,'note':note})
                ###Common code for students
            except:
                return redirect('home')
        else:
            return redirect('logout')

class GetFile(View):
    def get(self, request,id):
        user=request.user
        if user.is_authenticated:
            try:
                s = Student.objects.get(user=user)
                ###Common code for students
                id = id
                string = str("certificates/"+id+".pdf")
                certificate = open(string,'rb')
                response = FileResponse(certificate)
                return response
                ###Common code for students
            except:
                return redirect('home')
        else:
            return redirect('logout')






            




















##########################################################################################################################################


################################################
###            Admin Functions               ###
################################################

class AdminDashboardView(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="4":
                    ###Common code for trainers
                    leads = Lead.objects.filter(Q(status="New")|Q(status="In Pipeline"))
                    leads_count = leads.count()
                    new_lead_count = Lead.objects.filter(status="New").count()
                    pipeline_lead_count = Lead.objects.filter(status="In Pipeline").count()
                    closure = Lead.objects.filter(status="Converted").filter(created_on__month__gte=date.today().month-1)
                    closure_count = closure.count()
                    active_trainers = Staff.objects.filter(stype="3")
                    active_trainers_count = 0
                    for trainer in active_trainers:
                        if trainer.user.is_active:
                            active_trainers_count = active_trainers_count + 1
                    active_staff = Staff.objects.all()
                    active_staff_count = 0
                    for staff in active_staff:
                        if staff.user.is_active:
                            active_staff_count = active_staff_count + 1
                    active_batches = Batch.objects.filter(status="Ongoing")
                    active_batches_count = active_batches.count()
                    upcoming_batches = Batch.objects.filter(status="Yet to start")
                    upcoming_batches_count = upcoming_batches.count()
                    staff_pending_task = Task.objects.filter(~Q(status="Completed"))
                    staff_pending_task_count = staff_pending_task.count()
                    return render(request,'accounts/admin_dashboard.html',{'new_lead_count':new_lead_count,'pipeline_lead_count':pipeline_lead_count,'s':s,'note':note, 'no_count':no_count,'leads':leads,'leads_count':leads_count,'closure':closure,'closure_count':closure_count,'active_trainers':active_trainers,'active_trainers_count':active_trainers_count,'active_batches':active_batches,'upcoming_batches':upcoming_batches,'staff_pending_task_count':staff_pending_task_count,'staff_pending_task':staff_pending_task,'active_staff_count':active_staff_count,'active_batches_count':active_batches_count,'upcoming_batches_count':upcoming_batches_count})
                    ###Common code for trainers
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class OperationsRegisterView(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="4":
                    staff = Staff.objects.filter(stype="1")
                    f=StaffFilter(self.request.GET,queryset=staff)
                    staff=f.qs
                    return render(request,'accounts/operations_register.html',{'staff':staff,'no_count':no_count,'note':note,'s':s,'f':f})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class SalesRegisterView(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="4":
                    staff = Staff.objects.filter(stype="2")
                    f=StaffFilter(self.request.GET,queryset=staff)
                    staff=f.qs
                    return render(request,'accounts/sales_register.html',{'staff':staff,'no_count':no_count,'note':note,'s':s,'f':f})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class TrainerRegisterView(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="4":
                    staff = Staff.objects.filter(stype="3")
                    f=StaffFilter(self.request.GET,queryset=staff)
                    staff=f.qs
                    return render(request,'accounts/trainer_register.html',{'staff':staff,'no_count':no_count,'note':note,'s':s,'f':f})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


class RegisterNewStaff(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="4":
                    form = NewStaffRegisterForm()
                    return render(request,'accounts/staff_creation_form.html',{'form':form,'s':s,'no_count':no_count,'note':note})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')


    def post(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="4":
                    form = NewStaffRegisterForm(request.POST)
                    name=form.cleaned_data['name']
                    email=form.cleaned_data['email']
                    mobile=form.cleaned_data['mobile']
                    nuser = User.objects.create_user(email,email,mobile)
                    nuser.first_name = name
                    try:
                        user.save()
                        f = form.save(commit=False)
                        f.user = nuser
                        f.save()
                        send_mail(
                            '[TEQSTORIES] Account Created',
                            'Hello team, Your staff account has been created successfully.Please login to http://127.0.0.1/ with your email as username and mobile number as password.',
                            'anandubs1409@gmail.com',
                            [email],
                            fail_silently=False,
                        )
                        msg="Staff account created successfully and mails have been sent."
                        return render(request,'accounts/okmsg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})
                    except:
                        msg="Learner account creation failed."
                        return render(request,'accounts/okmsg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})

                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')
                

class AssignTask(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="4":
                    form = TaskAllocationForm()
                    return render(request,'accounts/task_assign_form.html',{'form':form,'note':note,'no_count':no_count,'s':s})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')

    def post(self, request):
        user=request.user
        if user.is_authenticated:
            note = Notification.objects.filter(receiver=user).filter(status="Not Read").order_by('-datetime')
            no_count = note.count()
            try:
                s= Staff.objects.get(user=user)
                if s.stype =="4":
                    form = TaskAllocationForm(request.POST)
                    if form.is_valid():
                        t = form.save(commit=False)
                        t.assigned_by = s
                        t.save()
                        r = form.cleaned_data['user']
                        re = r.user
                        n = Notification(sender=user,receiver=re,content="Task allocated",subject=t)
                        n.save()
                        msg = "Task has been successfully allocated"
                        return render(request,'accounts/okmsg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})
                    else:
                        msg = "Task allocation failed!."
                        return render(request,'accounts/okmsg.html',{'s':s,'msg':msg,'no_count':no_count,'note':note})
                else:
                    return redirect('home')
            except:
                return redirect('home')
        else:
            return redirect('logout')







