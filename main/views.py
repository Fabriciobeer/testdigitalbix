from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='/auth?next=/')
def render_index(request):
    
    breadcrumb = [["/","Home"]]

    return render(request, 'main/index.html', {"breadcrumb": breadcrumb})