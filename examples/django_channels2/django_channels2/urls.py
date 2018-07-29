from django.urls import path
from django.views.generic import TemplateView
from graphene_django.views import GraphQLView

urlpatterns = [
    path("", TemplateView.as_view(template_name="chat.html")),
    path("graphql/", GraphQLView.as_view(graphiql=True)),
]
