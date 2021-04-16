from django.shortcuts import render
from django.views.generic import View


class AbstractPublicView(View):

    def context(self, context=dict()):
        context['active_navigation'] = context.get('active_navigation', "accueil")
        return context


class IndexPublicView(AbstractPublicView):

    def get(self, req):

        return render(
            req,
            "cla_public/index.html",
            self.context({

            })
        )
