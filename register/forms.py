from django.contrib.auth.models import User
import json
from team_signin.models import *
from django import forms
class Ajax(forms.Form):
    args = []
    user = []
    def __init__(self, *args, **kwargs):
        self.args = args
        if len(args) > 1:
            self.user = args[1]
        if self.user.id == None:
            self.user = "NL"

    def error(self, message):
        return json.dumps({ "Status": "Error", "Message": message }, ensure_ascii=False)

    def success(self, message):
        return json.dumps({ "Status": "Success", "Message": message }, ensure_ascii=False)

    def items(self, json):
        return json

    def output(self):
        return self.validate()

class AjaxRecordsDate(Ajax):
    def validate(self):
        try:
            self.date_filter = self.args[0]["date"]
        except Exception as e:
            return self.error("Malformed request, did not process.")

        records=SignInRecords.objects.filter(date_str=self.date_filter)
        r=[]
        print(records)
        if records:
            for item in records:        
                r.append({ "name": item.profile.username, "email": item.profile.user.email, "time_description": item.time_description})
            return self.items(json.dumps(r))
        else:
            return self.error("No records found")

        