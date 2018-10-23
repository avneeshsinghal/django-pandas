import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import pandas as pd
from pandas import ExcelWriter
from django.http import HttpResponse, FileResponse
import urllib

from uploads.core.models import Document
from uploads.core.forms import DocumentForm

global globvar

def home(request):
    documents = Document.objects.all()
    return render(request, 'core/home.html', { 'documents': documents })


def simple_upload(request):
    global globvar
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)

        uploaded_file_url = fs.url(filename)
        globvar = urllib.parse.unquote(uploaded_file_url)
        return render(request, 'core/simple_upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'core/simple_upload.html')


def model_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = DocumentForm()
    return render(request, 'core/model_form_upload.html', {
        'form': form
    })


def add_roundoff(request):
    global globvar
    if request.method == 'GET':
        df = pd.read_excel("/home/avneesh/Desktop/simple-file-upload"+globvar)
        xa = "/home/avneesh/Desktop/simple-file-upload"+globvar[:-5]+"_2"+".xlsx"
        ew = ExcelWriter(xa)
        df['Retention Time Roundoff'] =list(map(int, df['Retention time (min)'].round()))
        df.insert(3, 'Retention Time Roundoff(in mins)', df['Retention Time Roundoff'])
        df.to_excel(ew)
        ew.save()

        file_full_path = xa
        with open(file_full_path, 'rb') as f:
            data = f.read()
        response = HttpResponse(data, content_type='application/msexcel')
        response['Content-Disposition'] = "attachment; filename=file2.xlsx".format(file_full_path)
        response['Content-Length'] = os.path.getsize(file_full_path)
        return response
    return render(request, 'core/simple_upload.html')

def remove_groupby(request):
    global globvar
    if request.method == 'GET':
        df = pd.read_excel("/home/avneesh/Desktop/simple-file-upload"+globvar)
        xa = "/home/avneesh/Desktop/simple-file-upload"+globvar[:-5]+"_3"+".xlsx"
        ew = ExcelWriter(xa)
        df['Retention Time Roundoff'] = list(map(int, df['Retention time (min)'].round()))
        df.insert(3, 'Retention Time Roundoff(in mins)', df['Retention Time Roundoff'])
        df1=df.drop(columns=['m/z', 'Accepted Compound ID', 'Retention time (min)'])
        df2 = df1.groupby('Retention Time Roundoff(in mins)').mean()
        df2.to_excel(ew)
        ew.save()
        file_full_path = xa
        with open(file_full_path, 'rb') as f:
            data = f.read()
        response = HttpResponse(data, content_type='application/msexcel')
        response['Content-Disposition'] = "attachment; filename=file3.xlsx".format(file_full_path)
        response['Content-Length'] = os.path.getsize(file_full_path)
        return response
    return render(request, 'core/simple_upload.html')

def filter_compound(request):
    global globvar
    if request.method == 'GET':
        strlist = ['PC', 'LPC', 'plasmalogen']
        df = pd.read_excel("/home/avneesh/Desktop/simple-file-upload"+globvar)
        xa = "/home/avneesh/Desktop/simple-file-upload"+globvar[:-5]+"_1"+".xlsx"
        ew = ExcelWriter(xa)
        for item in strlist:
            df1 = df[df['Accepted Compound ID'].str.contains(' '+item+'$') == True]
            df1.to_excel(ew,item)
        ew.save()
        file_full_path = xa
        with open(file_full_path, 'rb') as f:
            data = f.read()
        response = HttpResponse(data, content_type='application/msexcel')
        response['Content-Disposition'] = "attachment; filename=file1.xlsx".format(file_full_path)
        response['Content-Length'] = os.path.getsize(file_full_path)
        return response
    return render(request, 'core/simple_upload.html')