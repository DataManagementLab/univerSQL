from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from api import views

urlpatterns = [
    path('translate', views.Translate.as_view()),
    path('translate/logs', views.TranslateLogList.as_view()),
    path('translate/logs/<int:n>', views.TranslateLogList.as_view()),
    path('translate/log_item/<int:pk>', views.TranslationLogDetail.as_view()),
    path('interaction', views.StartInteraction.as_view()),
    path('interaction/<int:int_id>', views.TranslateInteraction.as_view(), name="interaction"),
    path('interaction/logs', views.InteractionLogList.as_view()),
    path('interaction/logs/<int:n>', views.InteractionLogList.as_view()),
    path('interaction/log_item/<int:int_id>', views.InteractionLogDetail.as_view()),
    path('translators', views.TranslatorList.as_view()),
    path('schemas', views.SchemaList.as_view()),
    path('schemas/<str:schema_name>', views.SchemaDetail.as_view()),
]

#urlpatterns = format_suffix_patterns(urlpatterns)