from django.shortcuts import render,redirect
from signin import utils
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from team_signin.models import SlackProfile,SignInRecords,AllowedHostsAddress
from team_signin.utils import get_ctime_obj, valid_token
from .forms import Ajax,AjaxRecordsDate

@login_required(login_url='/slack/login/')
def index(request):
    user=User.objects.get(username=request.user.username)
    profile= user.slackprofile

    c_time=get_ctime_obj()
    if '{}'.format(profile.last_login) != '{}'.format(c_time.date()):
        profile.update_last_login()
        profile.last_login=c_time.date()
        profile.save()
        return redirect('register:logout')
    
    ip=utils.get_client_ip(request)
    day_record= SignInRecords.get_record_by_date_profile(c_time.date(),profile)
    
    context={"ip":ip,
            "day_record":day_record,
        }
    return render(request,'sign-in-bot/index.html',context)

def error_cache(request):
    return render(request,'error/session_expired.html')

@login_required(login_url='/slack/login/')
def table_records(request):
    user=User.objects.get(username=request.user.username)
    profile= user.slackprofile
    table_headers=["name","email","time in"]
    records=SignInRecords.objects.all()
    context={"table_headers":table_headers,
            "records":records}
    return render(request,'sign-in-bot/roll_table.html',context) 
    

@login_required(login_url='/slack/login/')
def authenticate_token(request,token):
    user=User.objects.get(username=request.user.username)
    profile= user.slackprofile
    c_time=get_ctime_obj()
    
    r=valid_token(profile,token)
    host_ip=utils.get_client_ip(request)
    ip_check=AllowedHostsAddress.check_if_host_is_allowed(host_ip)

    if not ip_check:
        context={"user":user,"warn":"invalid request IP address"}
        return render(request,'sign-in-bot/authenticate.html',context)

    if not r:
        context={"user":user,"warn":"invalid token"}
        return render(request,'sign-in-bot/authenticate.html',context)

    r=r[0]

    if r.is_authenticated:
        context={"user":user,"warn":"Already authenticated"}
        return render(request,'sign-in-bot/authenticate.html',context)
        
    r.is_authenticated=True

    r.set_time()
    r.save()
    context={"user":user,"warn":"Authenticated"}
    return render(request,'sign-in-bot/authenticate.html',context)
    

    

    
def ajax_records_date(request):
    ajax = AjaxRecordsDate(request.GET, request.user)
    context = { 'ajax_output': ajax.output() }
    return render(request, 'ajax.html', context)
    

