from django.views.generic import TemplateView


class TitleScreen(TemplateView):
    template_name = 'moviemon/title_screen.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['btn_enable'] = {
            'left': False,
            'right': False,
            'up': False,
            'down': False,
            'select': False,
            'a': True,
            'b': True
        }
        return context
