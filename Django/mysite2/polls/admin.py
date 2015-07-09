from django.contrib import admin
from .models import Choice,Question

class QuestionAdmin(admin.ModelAdmin):
    fields=[
    (None,{'fields':['question_text']}),
    ('Date information',{'fields':['pub_date'],'classes':['collapse']}),
    ]


admin.site.register(Choice)
#admin.site.register(Question,QuestionAdmin)
# Register your models here.
