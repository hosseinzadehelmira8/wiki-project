from django.shortcuts import render, redirect
from django import forms
import markdown2
from . import util
import random


def random_page(request):
    entries = util.list_entries()
    if entries:
        title = random.choice(entries)
        return redirect("entry", title=title)
    else:
        return render(
            request, "encyclopedia/error.html", {"message": "No pages available 😢"}
        )


def index(request):
    entries = util.list_entries()
    return render(request, "encyclopedia/index.html", {"entries": entries})


def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(
            request,
            "encyclopedia/error.html",
            {"message": "The requested page was not found 😢"},
        )
    html_content = markdown2.markdown(content)
    return render(
        request, "encyclopedia/entry.html", {"title": title, "content": html_content}
    )


def search(request):
    query = request.GET.get("q", "")
    entries = util.list_entries()
    matched = [entry for entry in entries if query.lower() in entry.lower()]

    if query in entries:
        return redirect("entry", title=query)

    return render(
        request, "encyclopedia/search.html", {"query": query, "entries": matched}
    )


class NewPageForm(forms.Form):
    title = forms.CharField(label="Page Title")
    content = forms.CharField(widget=forms.Textarea, label="Content")


def create_page(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if util.get_entry(title):
                return render(
                    request,
                    "encyclopedia/create_page.html",
                    {"form": form, "error": "A page with this title already exists 😢"},
                )
            util.save_entry(title, content)
            return redirect("entry", title=title)
    else:
        form = NewPageForm()

    return render(request, "encyclopedia/create_page.html", {"form": form})


class EditPageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, label="Content")


def edit_page(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(
            request,
            "encyclopedia/error.html",
            {"message": "The requested page was not found 😢"},
        )

    if request.method == "POST":
        form = EditPageForm(request.POST)
        if form.is_valid():
            updated_content = form.cleaned_data["content"]
            util.save_entry(title, updated_content)
            return redirect("entry", title=title)
    else:
        form = EditPageForm(initial={"content": content})

    return render(
        request, "encyclopedia/edit_page.html", {"form": form, "title": title}
    )
