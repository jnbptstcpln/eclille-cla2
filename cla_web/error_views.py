from django.shortcuts import render


def error_400(request, exception=None):
    return render(
        request,
        "error/error-400.html",
        status=400
    )


def error_403(request, exception=None):
    return render(
        request,
        "error/error-403.html",
        status=403
    )


def error_404(request, exception=None):
    return render(
        request,
        "error/error-404.html",
        status=404
    )


def error_500(request):

    return render(
        request,
        "error/error-500.html",
        status=500,
    )
