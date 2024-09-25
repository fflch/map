from django.urls import path
from .import views

urlpatterns = [
    path('', views.home, name='inicio'),
    path('new_catalog/', views.catalogar, name='catalogo'),
    path('catalog_detail/', views.catalog_detail, name='catalogadas'),
    path('descricao/<int:pk>/', views.descricao, name='descricao'),
    path('catalogada/<int:pk>/edit/', views.editar, name='editar'),
    path('resultado/', views.pesquisar, name='pesquisar'),
    path('documento/', views.inserirDocumento, name='inserir_documento'),
    path('resultado_documento/', views.resultado_documento, name='resultado_documentos'),
    path('descricao_documento/<int:pk>/', views.descricao_documento, name='descricao_documento'),
    path('documento/<int:pk>/edit/', views.editar_documento, name='editar_documento'),
    path('catalogada/<int:pk>/xml/', views.gerar_xml, name='gerar_xml'),
]