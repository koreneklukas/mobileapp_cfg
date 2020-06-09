from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('set-version', views.login, name='set-version'),
    path('tree', views.tree, name='tree'),
    path('loyalty/step-1', views.loyalty, name="loyalty/step-1"),
    path('loyalty/step-2', views.loyalty_proceed_1_step, name='loyalty/step-2'),
    path('loyalty/step-3', views.loyalty_proceed_2_step, name='loyalty/step-3'),
    path('banners-android', views.banners, name="banners-android"),
    path('banners-ios', views.ios, name="banners-ios"),
    path('images-upload', views.upload_banner_images_page, name="images-upload"),
    path('step-2', views.loyalty_proceed_1_step, name='step-2'),
    path('success', views.success, name='success'),
    path('back', views.back_to_tree, name='back'),
    path('git-push', views.git, name='git-push'),
    path('upload', views.upload, name='upload'),
    path('web-app-status', views.web_status, name='web-status')
]