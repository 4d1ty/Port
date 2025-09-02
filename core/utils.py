from django.core.paginator import Paginator


def paginate(request, qs):
    paginated_qs = Paginator(qs, min(request.GET.get("per_page", 10), 100))
    page_no = request.GET.get("page")
    return paginated_qs.get_page(page_no)
