from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views import defaults as default_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from chatbot_commerce.stores.views import successfuly_email, email_is_active, testing
# from rest_framework.documentation import include_docs_urls
# from db_python import product_list

schema_view = get_schema_view(
    openapi.Info(
        title="TodoViernes 😎 commerce chatbot API",
        default_version='v1',
        description="Commerce chatbot API endpoints documentation",
    ),
    public=True,
)

urlpatterns = [
    # Django Admin
    path(settings.ADMIN_URL, admin.site.urls),
    path("api/", include("config.api_router")),
    # path('docs/', include_docs_urls(title='Todo Viernes', public=False)),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('confirm/email/<uidb64>/<token>/', email_is_active, name='email-activate'),
    path('successfuly/email/', successfuly_email, name='email-successfuly'),
    path('test/', testing)
    # path('prueba/', product_list)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
