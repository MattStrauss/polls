from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth import login
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from .models import Choice, Question


def welcome(request):
    return render(request, 'welcome.html')


def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)

        if form.is_valid():
            user = form.save()
            login(response, user)

            return redirect("/polls")

    else:
        form = RegisterForm()

    return render(response, "registration/register.html", {"form": form})


@method_decorator(login_required, name='dispatch')
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published polls (not including those set to be
        published in the future).
        """
        from django.db.models import Sum
        Question.objects.annotate(total_votes=Sum('choice__votes'))

        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).annotate(total_votes=Sum('choice__votes')).order_by('total_votes')[:5]


@method_decorator(login_required, name='dispatch')
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


@method_decorator(login_required, name='dispatch')
class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


@login_required()
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
