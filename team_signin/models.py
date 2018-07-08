from django.db import models
from django.contrib.auth.models import User
import pytz
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.
class SlackProfile(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    user_sid=models.CharField(unique=True,max_length=255,null=True)
    team_id=models.CharField(max_length=255,null=True)
    username=models.CharField(max_length=255,null=True)
    access_token=models.CharField(max_length=255,null=True)
   
    date_created = models.DateField(auto_now=False,null=True)
    last_login = models.DateField(auto_now=False,null=True)
     #description
    last_login_date=models.CharField(max_length=255,null=True)

    def __str__(self):
        return self.user_sid
        
    @classmethod
    def is_user(cls,user_sid):
        u=cls.objects.filter(user_sid=user_sid)
        return True if u else False
        

    def update_last_login(self):
        tz=pytz.timezone('Africa/Nairobi')
        c_time=datetime.now(tz)
        self.last_login_date="{}".format(c_time.date())
        self.save()

    
    
class SignInRecords(models.Model):
    profile=models.ForeignKey(SlackProfile,on_delete=models.CASCADE)
    token=models.CharField(max_length=255,null=True)
    date_in=models.DateField(auto_now=False,null=True)
    in_time=models.DateTimeField(auto_now=False,null=True)
    date_str=models.CharField(max_length=255,null=True)
    time_description=models.CharField(max_length=255,null=True)
    is_authenticated=models.BooleanField(default=False)

    def __str__(self):
        return 'record {}'.format(self.pk)

    
        

    def set_time(self):
        tz=pytz.timezone('Africa/Nairobi')
        c_time=datetime.now(tz)
        self.time_description=str(c_time.strftime("%Y-%m-%d %H:%M"))
        self.date_str=str(c_time.strftime("%Y-%m-%d"))
        self.in_time=c_time
        self.date_in=c_time.date()

    @classmethod
    def list_authenticated_records_by_date(cls,dt=None):
        if dt:
            try:
                return cls.objects.filter(date_in=dt).order_by('-in_time')
            except:
                return None
        
        return cls.objects.all().order_by('-date_in')
   
    @classmethod
    def is_signed_in(cls,dt,profile):
        r=cls.objects.filter(date_str=dt,profile=profile)
        if r:
            return r[0].is_authenticated
        return None

    @classmethod
    def get_record_by_date_profile(cls,dt,profile):
        r=cls.objects.filter(date_str=dt,profile=profile)
        if r:
            return r[0]
        return None

class Eventmesssage(models.Model):
    client_msg_id=models.CharField(max_length=255,unique=True,null=True)
    user=models.CharField(max_length=255,null=True)
    text=models.CharField(max_length=255,null=True)
    channel=models.CharField(max_length=255,null=True)
    event_ts=models.CharField(max_length=255,null=True)

    def __str__(self):
        return '{}'.format(self.client_msg_id)

    @classmethod
    def validate_unique(cls,msg_id):
        try:
            msg=cls.objects.get(client_msg_id=msg_id)
            return False
        except ObjectDoesNotExist:
            return True

class AllowedHostsAddress(models.Model):
    ip_addrr=models.CharField(max_length=255,null=True,unique=True)


    def __str__(self):
        return '{}'.format(self.ip_addrr)

    @classmethod
    def check_if_host_is_allowed(cls,ip_addrr):
        res=cls.objects.filter(ip_addrr=ip_addrr)
        return True if res else False

