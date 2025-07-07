from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', views.signup, name='signup'),

    # LICENSE ROUTES
    path('licenses/', views.view_licenses, name='view_licenses'),
    path('licenses/upload/', views.upload_license, name='upload_license'),
    path('delete/<int:license_id>/', views.delete_license, name='delete_license'),

    # CME ROUTES
    path('licenses/cme/upload/', views.upload_cme, name='upload_cme'),
    path('licenses/cme/list/', views.view_cme, name='view_cme'),
    path('cme/delete/<int:cme_id>/', views.delete_cme, name='delete_cme'),
    path('cme/upload/pdf/', views.upload_pdf_cme, name='upload_pdf_cme'),
    path('cme/view/<int:cme_id>/', views.view_cme_pdf, name='view_cme_pdf'),

    # AUTH
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)