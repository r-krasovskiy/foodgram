from django.http import HttpResponse


def placeholder_view(request):
    """Временная заглушка при разработке."""
    return HttpResponse("Страница в разработке.")
