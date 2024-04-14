from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.admin import TokenAdmin
from rest_framework.authtoken.models import Token

# Register the User model with the custom UserAdmin class
admin.site.register(User, UserAdmin)

# Register the Token model with TokenAdmin
admin.site.register(Token)

# Optionally, customize the TokenAdmin if needed
admin.site.unregister(Token)
admin.site.register(Token, TokenAdmin)


from django.contrib import admin
from .models import User, Animals, Plants, Images, Videos, Articles, Feedback

# Register your models here.
admin.site.register(User)
admin.site.register(Animals)
admin.site.register(Plants)
admin.site.register(Images)
admin.site.register(Videos)
admin.site.register(Articles)
admin.site.register(Feedback)
