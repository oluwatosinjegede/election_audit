from django.shortcuts import render
from django.http import HttpResponse
from .forms import AuditUploadForm
from .utils import run_audit
import csv


# =========================
# MAIN UPLOAD VIEW
# =========================
def upload_files(request):
    form = AuditUploadForm()
    error = None

    if request.method == 'POST':
        form = AuditUploadForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                voters_file = request.FILES['voters_register']
                votes_file = request.FILES['vote_cast']

                result = run_audit(voters_file, votes_file)

                # STORE RESULTS IN SESSION (for downloads)
                request.session["invalid"] = result.get("invalid", [])
                request.session["duplicates"] = result.get("duplicates", [])
                request.session["fuzzy_matches"] = result.get("fuzzy_matches", [])

                request.session.modified = True  # ensure save

                return render(request, 'audit_app/result.html', {
                    'result': result
                })

            except Exception as e:
                error = str(e)

    return render(request, 'audit_app/upload.html', {
        'form': form,
        'error': error
    })


# =========================
#  GENERIC CSV EXPORT
# =========================
def export_csv(data, filename, header):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([header])

    for item in data:
        if isinstance(item, dict):
            # For fuzzy matches
            writer.writerow([item.get("input"), item.get("matched")])
        else:
            writer.writerow([item])

    return response


# =========================
#  EXPORT VIEWS
# =========================
def export_invalid(request):
    data = request.session.get("invalid", [])
    return export_csv(data, "invalid_voters.csv", "Invalid Names")


def export_duplicates(request):
    data = request.session.get("duplicates", [])
    return export_csv(data, "duplicate_voters.csv", "Duplicate Names")


def export_fuzzy(request):
    data = request.session.get("fuzzy_matches", [])
    return export_csv(data, "fuzzy_matches.csv", "Entered Name,Matched Name")