
from django.shortcuts import render , get_object_or_404
from django.http import HttpResponse , HttpResponseRedirect
from applications.academic_information.models import Meeting
from .models import Constants,hostel_allotment,Budget
from applications.gymkhana.models import Club_budget,Club_info
from applications.globals.models import *
import json
from django.contrib.auth.decorators import login_required

"""
    Default view for Dean Students Module
    All models are Loaded from respective Tables in Database and passed to default template
    List of Concerned Models :
    S.no. Model             |  Load Variables  |  Usage
    
    1.    Club_budget       |  budget_app      |  Budget reuests where status is open
                            |  past_budget     |  Past budget requests
                            |  approved_budgets|  Budget requests marked as approved
    2.    Meeting           |  minutes         |  Meeting entries where minutes file is not present
                            |  final_minutes   |  Meeting entries where minute file is present
    3.    hostel_allotment  |  hall_allotment  |  All entries
    4.    Club_info         |  clubNew         |  Clubs which are not approved/rejected
                            |  club            |  Clubs which are approved/rejected
                            |  budgets         |  Clubs which are approved
    5.    HoldsDesignation  |  designation     |  Designation of the active user
"""
@login_required
def officeOfDeanStudents(request):
    budget_app = Club_budget.objects.all().filter(status='open')
    past_budget = Club_budget.objects.all().exclude(status='open')
    minutes = Meeting.objects.all().filter(minutes_file="")
    final_minutes = Meeting.objects.all().exclude(minutes_file="")
    hall_allotment = hostel_allotment.objects.all()
    clubNew = Club_info.objects.all().filter(status='open')
    club = Club_info.objects.all().exclude(status='open')
    budgets = Club_info.objects.all().filter(status='confirmed')
    approved_budgets = Club_budget.objects.all().filter(status='confirmed')
    budget_allotment = Club_info.objects.all().filter(status='confirmed')
    budget_alloted = Club_info.objects.all().exclude(alloted_budget=0)
    designation = HoldsDesignation.objects.all().filter(working=request.user)

    """getting roll and designation(s) of the active user in roll_"""
    desig = list(HoldsDesignation.objects.all().filter(working = request.user).values_list('designation'))
    b = [i for sub in desig for i in sub]
    roll_=[]
    for i in b :
        name_ = get_object_or_404(Designation, id = i)
        roll_.append(str(name_.name))

    HALL_NO = (('HALL-1','hall-1'),('HALL-3','hall-3'),('HALL-4','hall-4'))
    hall=[]
    for i in HALL_NO:
        if(str(i[1])):
            hall.append(str(i[1]))

    context = {'meetingMinutes': minutes,
                'final_minutes': final_minutes,
                'hall': hall,
                'hall_allotment': hall_allotment,
                'budget_app': budget_app,
                'p_budget': past_budget,
                'clubNew': clubNew,
                'club': club,
                'budgets': budgets,
                'approved_budgets': approved_budgets,
                'budget_allotment': budget_allotment,
                'budget_alloted': budget_alloted,
                'all_designation': roll_,
              }
    return render(request, "officeModule/officeOfDeanStudents/officeOfDeanStudents.html", context)

@login_required
def holdingMeeting(request):
    """title= request.POST.get('title')"""
    date = request.POST.get('date')
    Time = request.POST.get('time')
    Venue = request.POST.get('venue')
    Agenda = request.POST.get('agenda')
    Minutes_File = request.POST.get('minutes_file')
   # print(Venue," ",date," ", Time," ",Agenda)
    p=Meeting(venue=Venue,date=date,time=Time,agenda=Agenda,minutes_file= Minutes_File)

    p.save()
    return HttpResponse('ll')

@login_required
def meetingMinutes(request):
    file=request.FILES['minutes_file']
    id=request.POST.get('id')
    b=Meeting.objects.get(pk=id)
    b.minutes_file=file
    b.save()
    #return HttpResponseRedirect('/office/officeOfDeanStudents/first')
    return render(request, "officeModule/officeModule/officeOfDeanStudents/holdingMeetings.html", context)

@login_required
def hostelRoomAllotment(request):
    file=request.FILES['hostel_file']
    hall_no=request.POST.get('hall_no')
    p=hostel_allotment(allotment_file=file,hall_no=hall_no)
    p.save()
    return HttpResponseRedirect('/office/officeOfDeanStudents')

@login_required
def budgetApproval(request):
    id_r=request.POST.getlist('check')
    remark=request.POST.getlist('remark')
    for i in range(len(id_r)):
        a=Club_budget.objects.get(id=id_r[i])
        a.status='confirmed'
        a.remarks=request.POST.get(id_r[i])
        budget= request.POST.get('amount '+ id_r[i])
        spentBudget=a.club.spent_budget
        availBudget= a.club.avail_budget
        b=Club_info.objects.get(club_name = a.club.club_name )
        b.spent_budget= (spentBudget+int(budget))
        b.avail_budget= (availBudget- int(budget))
        a.save()
        b.save()
    return HttpResponseRedirect('/office/officeOfDeanStudents')

@login_required
def budgetRejection(request):
    id_r=request.POST.getlist('check')
    remark=request.POST.getlist('remark')
    for i in range(len(id_r)):
        a=Club_budget.objects.get(id=id_r[i]);
        a.status='rejected'
        a.remarks=request.POST.get(id_r[i])
        a.save()
    return HttpResponseRedirect('/office/officeOfDeanStudents')


@login_required
def clubApproval(request):
    id_r=request.POST.getlist('check')
    for i in range(len(id_r)):
        a=Club_info.objects.get(pk=id_r[i])
        co_ordinator= a.co_ordinator.id.user
        co_co = a.co_coordinator.id.user
        a.status='confirmed'
        a.save()
        designation = get_object_or_404(Designation, name="co-ordinator")
        designation1 = get_object_or_404(Designation, name="co co-ordinator")
        HoldsDesig= HoldsDesignation(user=co_ordinator,working=co_ordinator,designation=designation)
        HoldsDesig.save()
        HoldsDesig = HoldsDesignation( user= co_co, working= co_co, designation=designation1)
        HoldsDesig.save()
    return HttpResponseRedirect('/office/officeOfDeanStudents')
    return render(request, "officeModule/officeModule / officeOfDeanStudents / newClubApprovals.html", context)

@login_required
def clubRejection(request):
    id_r=request.POST.getlist('check')
    for i in range(len(id_r)):
        a=Club_info.objects.get(pk=id_r[i]);
        a.status='rejected'
        a.save()
    return HttpResponseRedirect('/office/officeOfDeanStudents')

@login_required
def budgetAllot(request):
    id_r=request.POST.get('id')
    budget= request.POST.get('budget')
    a= Club_info.objects.get(pk=id_r)
    a.alloted_budget=int(budget)
    a.avail_budget= int(budget)
    a.save()
    return HttpResponseRedirect('/office/officeOfDeanStudents')

@login_required
def budgetAllotEdit(request):
    id_r=request.POST.get('id')
    budget= request.POST.get('budget')
    a= Club_info.objects.get(pk=id_r)
    a.alloted_budget=int(budget)
    a.avail_budget= int(budget)
    a.spent_budget= int(0)
    a.save()
    return HttpResponseRedirect('/office/officeOfDeanStudents')
