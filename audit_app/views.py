from django.shortcuts import render
from .forms import AuditUploadForm
from .utils import run_audit

def upload_files(request):
    if request.method == 'POST':
        form = AuditUploadForm(request.POST, request.FILES)
        if form.is_valid():
            voters_file = request.FILES['voters_register']
            votes_file = request.FILES['vote_cast']

            result = run_audit(voters_file, votes_file)

            # 👉 SEND RESULT TO result.html
            return render(request, 'audit_app/result.html', {
                'result': result
            })
    else:
        form = AuditUploadForm()

    return render(request, 'audit_app/upload.html', {
        'form': form
    })