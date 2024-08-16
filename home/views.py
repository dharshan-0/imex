from django.shortcuts import render, redirect
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_delete
from django.contrib.sessions.models import Session
from django.http import HttpResponse

from pathlib import Path
from .forms import DocumentForm
from .models import Document
from .util import ImageExtractor, ZipCreator
import os

SESSION_EXPIRY = 3600 # 2hr

@receiver(pre_delete, sender=Session)
def file_cleanup(instance, **kwargs):
    doc = Document.objects.filter(session = instance.session_key)
    if len(doc) > 0:
        doc = doc[0]
        doc.delete()

def delete_zip(path):
    base_dir = os.path.dirname(path)
    file_name = Path(path).stem
    zip_path = os.path.join(base_dir, f'{file_name}-images.zip')
    os.remove(zip_path)

@receiver(post_delete, sender=Document)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    document = instance.document

    if Path(document.path).is_file():
        os.remove(document.path)
        delete_zip(document.path)

def create_session(request):
    request.session.set_expiry(SESSION_EXPIRY)

    if not request.session.exists(request.session.session_key):
        request.session.create()    

def index_page(request):
    request.session.clear_expired()

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            create_session(request)

            session = Session.objects.filter(session_key = request.session.session_key)[0]
            instance.session = session

            instance.save()
            form.save()

            return redirect('homeapp:download_page')
    else:
        form = DocumentForm()

    ctx = {'form': form}
    return render(request, 'pages/index.html', ctx)


def download_page(request):
    if request.method == 'GET':
        return render(request, 'pages/download.html', {})

    doc = Document.objects.filter(session = request.session.session_key)
    if len(doc) == 0:
        return redirect('homeapp:index_page')
    doc = doc[0]

    images = ImageExtractor(doc.document.path)
    images.save_image()

    zipf = ZipCreator(images.imgDirPath)
    zipf.create_zip()
    zipf.delete_used_folder()
    
    with open(zipf.ZIP_PATH, 'rb') as f:
        response = HttpResponse(f.read(), content_type="application/zip")
        response['Content-Disposition'] = 'inline; filename=' + zipf.FILE_NAME + '.zip'
        request.session.set_expiry(1)
    return response

def disclaimer_contact_page(request):
    return render(request, 'pages/disclaimer-contact.html', {})