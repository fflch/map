from django.urls import path, include
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
    path('catalogada', views.gerar_xml_catalogadas, name='gerar_xml_catalogadas'),
    path('catalogada/<int:pk>/xmledictor/', views.gerar_xml_edictor, name='gerar_xml_edictor'),
    path('catalogada/', views.gerar_xml_catalogadas_edictor, name='gerar_xml_catalogadas_edictor'),
    path('documeneto/importar', views.importar_documentos, name='importar_documentos'),
    path('catalogada/xmldoc', views.gerar_arquivos_xml_documentos, name='gerar_arquivos_xml_documentos'),
    path('catalogada/xmldocunico', views.gerar_arquivos_xml_documentos_unico, name='gerar_arquivos_xml_documentos_unico'),
    path('catalogada/xmledi', views.gerar_xml_documentos_edictor, name='gerar_xml_documentos_edictor'),
    path('catalogada/xmlediu', views.gerar_xml_documentos_edictor_uni, name='gerar_xml_documentos_edictor_uni'),
    path('importar_csv/', views.importar_csv, name='importar_csv'),
    path('importar_documentos_csv/', views.importar_documentos_csv, name='importar_documentos_csv'),

]