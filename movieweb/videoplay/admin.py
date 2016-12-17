from django.contrib import admin
from videoplay.models import Movie, User, UserComment, MoviePay
# Register your models here.

admin.site.register(Movie)
admin.site.register(User)
admin.site.register(UserComment)
admin.site.register(MoviePay)
