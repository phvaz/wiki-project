from django.shortcuts import render, redirect

from . import util

from .util import get_entry

from .util import list_entries

from .util import save_entry

import random

from django import forms

import markdown


def convert_md_to_html(markdown_content):
    html_content = markdown.markdown(markdown_content)
    return html_content


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def get_title(request, title):
    content = get_entry(title)
    if content is None:
        return render(request, 'encyclopedia/not_found.html')    # create this 
    
    html_content = convert_md_to_html(content)

    return render(request, 'encyclopedia/entry.html',
                  {'title':title, 'content': html_content})


def search(request):
    query = request.GET.get('q') 
    if query:
        entry_content = get_entry(query)
        entries = [entry for entry in list_entries() if query.lower() in entry.lower()]
        if entry_content:
            html_content = markdown.markdown(entry_content)
            return render(request, "encyclopedia/entry.html", {"title": query, "content": html_content})
        elif entries:
            return render(request, "encyclopedia/search_results.html", {"entries": entries, "query": query})
        else:
            return render(request, "encyclopedia/no_results.html")


class NewPageForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100)
    content = forms.CharField(widget=forms.Textarea, label="Content")      


def new_page(request):
    if request.method == 'POST':     # is activated in case the user wants to submit something
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            existing_entry = get_entry(title)   # checks if title passed to the form exists and if thats de case return an error
            
            if existing_entry:
                form.add_error('title', 'An entry with this title already exists.')    
            else:
                save_entry(title, content)
                return redirect('get_title', title=title)
    else:
        form = NewPageForm()     # display form in the page

    return render(request, 'encyclopedia/new_page.html', {'form': form})

def edit_page(request, title):
    entry_content = get_entry(title)
    if request.method == 'POST':
        form = NewPageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            save_entry(title, content)
            return redirect('get_title', title=title)
    else:
        form = NewPageForm(initial={'content': entry_content})
    
    return render(request, 'encyclopedia/edit_page.html', {'form': form, 'title': title})



def random_page(request):
    all_entries = util.list_entries()
    random_entry_title = random.choice(all_entries)
    random_entry_content = util.get_entry(random_entry_title)
    html_content = convert_md_to_html(random_entry_content)
    return render(request, "encyclopedia/entry.html", {
        "title": random_entry_title,
        "content": html_content
    })

    