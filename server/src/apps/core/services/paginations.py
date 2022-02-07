from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    # page_size_query_param = 'per_page'

    def offer_list_response(self, groups, data):
        return {
            "success": True,
            "code": 0,
            "message": "OK",
            "groups": groups,
            "results": data,
            "count": self.page.paginator.count,
            "page": self.page.number,
            "last_page": self.page.paginator.num_pages,
            # "per_page": self.page.paginator.per_page
        }

    def paginated_response(self, data):
        return {
            "success": True,
            "code": 0,
            "message": "OK",
            "results": data,
            "count": self.page.paginator.count,
            "page": self.page.number,
            "last_page": self.page.paginator.num_pages,
            # "per_page": self.page.paginator.per_page
        }

    def paginated_queryset(self, qs, request):
        return super(CustomPagination, self).paginate_queryset(qs, request)