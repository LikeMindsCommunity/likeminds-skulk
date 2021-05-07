from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from payments.forms import PlanForm
from .plans_impl import PlansImpl

class CreatePlanView(View):

    template_name = 'plan_form.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreatePlanView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        form = PlanForm()

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):

        form = PlanForm(request.POST)

        if form.is_valid():
            plans_manager = PlansImpl()
            plan_instance = plans_manager.create_plan(form.cleaned_data)

            return render(request, self.template_name, {'form': form, 'plan': plan_instance})
