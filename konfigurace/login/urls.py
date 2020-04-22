from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('set-version', views.login, name='set-version'),
    path('tree', views.tree, name='tree'),
    path('loyalty/step-1', views.loyalty, name="loyalty/step-1"),
    path('loyalty/step-2', views.loyalty_proceed_1_step, name='loyalty/step-2'),
    path('loyalty/step-3', views.loyalty_proceed_2_step, name='loyalty/step-3'),
    path('step-2', views.loyalty_proceed_1_step, name='step-2'),
    path('success', views.success, name='success'),
    path('back', views.back_to_tree, name='back'),
]