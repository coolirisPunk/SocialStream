from django.shortcuts import render

from socialhub import SocialHub as SocialHubClass


def home(request):
    socialhub = SocialHubClass('punkemkt', 'punkemkt', "punkemkt", '212242748')
    posts = socialhub.GetPosts()
    print len(posts)
    return render(request, 'home.html', {"posts": posts})
