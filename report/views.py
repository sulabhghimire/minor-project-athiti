from django.shortcuts import redirect
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib import messages
from .models import Report
from .forms import ReportForm

def CreateReport(request, pk):
    url     = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        form        = ReportForm(request.POST)
        if form.is_valid():
            data                = Report()
            data.message        = form.cleaned_data['message']
            data.report_by      = request.user
            data.reported_to    = User.objects.get(id=pk)
            data.save()
            messages.success(request, "Thank you! Your rport have been submitted.")
            return redirect(url)
        else:
            messages.info(request, "The form is not valid.")
            return redirect(url)
