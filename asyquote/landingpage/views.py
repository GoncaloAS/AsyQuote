from django.views.generic import TemplateView


class HomeListView(TemplateView):
    template_name = "components/homepage/homepage.html"
