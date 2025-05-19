from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render, get_object_or_404

from django.db.models import F
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from django.http import Http404

from .models import Question, Choice, Task
from django.views.generic import ListView
from django.shortcuts import redirect

# Create your views here.
class IndexView(ListView):
    template_name = "blog/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = Task.objects.order_by('-created_at')
        return context

    def post(self, request, *args, **kwargs):
        task_name = request.POST.get('task_name')
        if task_name:
            Task.objects.create(name=task_name)
        return redirect('blog:index')

class DetailView(generic.DetailView):
    model = Question
    template_name = "blog/detail.html"
    
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone())

class ResultsView(generic.DetailView):
    model = Question
    template_name = "blog/results.html"

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "blog/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("blog:results", args=(question.id,)))


