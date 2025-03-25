from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .forms import CatalogadaForm, DocumentoForm
from .models import Catalogada, Documento
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import xml.etree.ElementTree as ET
import re
import os
import lxml.etree as LET
import csv
import io
import zipfile

########################### IMPORTANTE ###################################
# A intenção do projeto M.A.P. era que a plataforma fosse uma espécie de #
# plataforma de aprendizado para todas as pessoas do projeto.            #
# Devido a esse fato, algumas partes precisam ser otimizadas por terem   #
# sido desenvolvidas de forma mais "intuitiva" para quem está aprendendo #
# a programar.                                                           #
##########################################################################

def home(request):
    catalogadas = Catalogada.objects.all()
    documentos = Documento.objects.all()
    return render(request, 'app/home.html', {'catalogada': catalogadas, 'documentos': documentos} )

@login_required()
def catalogar(request):
    if request.method == "POST":
        catalogada_form = CatalogadaForm(request.POST)
        print('Post')
        if request.POST.get('user') != "":
            if catalogada_form.is_valid():
                catalogada = catalogada_form.save(commit=False)
                catalogada.responsavel_catalogacao = request.POST.get('user')
                catalogada.data_catalogacao = timezone.now()
                catalogada.total_filhs = catalogada.total_filhas + catalogada.total_filhos

                # extraindo o código da catalogada = número da PK + todas as iniciais
                espaco = ""
                iniciais = re.compile(r"\b[a-zA-Z]")
                iniciais = iniciais.findall(catalogada.nome_modernizado)
                iniciais = espaco.join(iniciais)

                if Catalogada.objects.count() != 0:
                    numero = Catalogada.objects.filter().last().pk + 1  # recebe a última PK e acrescenta 1

                else:
                    numero = 1

                catalogada.codigo = (str(numero) + iniciais).upper()

                catalogada.save()  # salvando a catalogada
                # inserindo as informações de processamento
                #Processamento.objects.create(catalogada=catalogada, responsavel_catalogacao=request.POST.get('user'),
                                             #data_catalogacao=timezone.now())
                print('Salvo')
                return redirect('catalogadas')
            else:
                print(catalogada_form.errors)
        else:
            print('Não tem responsável catalogação: ', request.POST.get('user'))
    else:
        catalogada_form = CatalogadaForm()
        print('Não post')
    return render(request, 'app/catalogo.html', {'catalogada_form': catalogada_form})

@login_required()
def catalog_detail(request):
    # catalogada = Catalogada.objects.filter(published_date__lte=timezone.now()).order_by('id')
    if request.method == "POST":
        chave = request.POST.get('search_box', None)
        catalogada = Catalogada.objects.filter(nome_modernizado=chave)
        return render(request, 'app/resultado.html', {'catalogada': catalogada})

    else:
        catalogadas = Catalogada.objects.all()
        #id = []
        #processamento = Processamento.objects.all()

        #for cat in processamento:
            # catalogadas.append(cat)
            #if cat.catalogada_id in id:
                #pass
            #else:
                #id.append(cat.catalogada_id)
                #catalogadas.append(cat)
                # print(id)
        return render(request, 'app/catalog_detail.html', {'catalogada': catalogadas})

@login_required()
def descricao(request, pk):
    catalogada = get_object_or_404(Catalogada, pk=pk)
    catalogada_form = CatalogadaForm(instance=catalogada)
    #responsavel_catalogacao = catalogada.processamento.filter(
        #catalogada__pk=catalogada.pk).first().responsavel_catalogacao
    #print(responsavel_catalogacao)
    return render(request, 'app/descricao.html', {'catalogada_form': catalogada_form, 'catalogada': catalogada})

@login_required()
def editar(request, pk):
    catalogada = get_object_or_404(Catalogada, pk=pk)
    if request.method == "POST":
        catalogada_form = CatalogadaForm(request.POST, instance=catalogada)
        if catalogada_form.is_valid():
            #processamento = Processamento.objects.filter(catalogada__codigo=catalogada.codigo)
            catalogada = catalogada_form.save(commit=False)
            if request.POST.get('user') == "":
                pass
            else:
               catalogada.responsavel_catalogacao = request.POST.get('user')

            catalogada.total_filhs = catalogada.total_filhas + catalogada.total_filhos
            catalogada.data_revisao_catalogacao=timezone.now()
            catalogada.save()
            #catalogada.informacoes_internas = request.POST.get('informacoes_internas')
            #processamento.update(data_revisao_catalogacao=timezone.now())
            return redirect('catalogadas')
    else:
        catalogada_form = CatalogadaForm(instance=catalogada)
        catalogada = get_object_or_404(Catalogada, pk=pk)

        #responsavel_catalogacao = catalogada.processamento.filter(
            #catalogada__pk=catalogada.pk).first().responsavel_catalogacao
        #informacao = catalogada.informacoes_internas
    return render(request, 'app/editar.html',
                  {'catalogada_form': catalogada_form, 'catalogada': catalogada})

@login_required()
def pesquisar(request, pk):
    catalogada = get_object_or_404(Catalogada, pk=pk)
    return render(request, 'app/resultado.html', {'catalogada': catalogada})

@login_required()
def inserirDocumento(request):
    catalogadas = Catalogada.objects.all
    if request.method == "POST":
        documento_form = DocumentoForm(request.POST)
        if request.POST.get('user') != "" and request.POST.get('catalogada') != "":
            if documento_form.is_valid():

                # EXTRAINDO O CODIGO (ISSO DAQUI PRECISA SER MODIFICADO NO FUTURO)
                codigo_par = request.POST.get('catalogada')
                codigo = re.compile(r"\(\S*\)")
                codigo = codigo.findall(codigo_par)
                codigo = re.sub(r'[()]', '', codigo[0])


                documento = documento_form.save(commit=False)
                documento.data_documento = timezone.now()
                documento.responsavel_documento = request.POST.get('user')
                documento.save()
                catalogada = get_object_or_404(Catalogada, codigo=codigo)
                catalogada.documentos.add(documento)
                #processamento = Processamento.objects.filter(documento_id=documento.id)
                #processamento.update(data_documento=timezone.now())
                return redirect('catalogadas')
            else:
                print("form inválido")
                # print(documento_form.catalogadas)
                print(documento_form.errors)
        else:
            print("Falta a pessoa responsável pelo documento ou catalogada")
    else:
        documento_form = DocumentoForm()

    return render(request, 'app/documento.html', {'documento_form': documento_form, "lista_catalogadas": catalogadas})

@login_required()
def resultado_documento(request):
    if request.method == "POST":
        chave = request.POST.get('search_box', None)
        catalogada = Catalogada.objects.filter(nome_original=chave)
        return render(request, 'app/resultado.html', {'catalogada': catalogada})

    else:
        documentos = Documento.objects.all()
        #processamento = Processamento.objects.all()

        return render(request, 'app/resultado_documento.html',
                      {'documentos': documentos})

@login_required()
def descricao_documento(request, pk):
    documento = get_object_or_404(Documento, pk=pk)
    documento_form = DocumentoForm(instance=documento)
    #responsavel_documento = documento.processamento.filter(
        #documento__pk=documento.pk).first().responsavel_documento
    informacoes_internas = documento.informacoes_internas
    catalogada = documento.catalogadas.first()
    return render(request, 'app/descricao_documento.html', {'documento_form': documento_form, 'documento': documento,
                                                            #'responsavel_documento': responsavel_documento,
                                                            'informacoes_internas': informacoes_internas,
                                                            'catalogaga': catalogada})

@login_required()
def editar_documento(request, pk):
    documento = get_object_or_404(Documento, pk=pk)
    catalogadas = Catalogada.objects.all
    if request.method == "POST":
        documento_form = DocumentoForm(request.POST, instance=documento)
        if documento_form.is_valid():
            documento = documento_form.save(commit=False)
            documento.data_edicao_documento = timezone.now()

            #Alterando a catalogada do documento e a pessoa responsável - Modificar
            if request.POST.get('user') != "" and request.POST.get('catalogada') != "":
                # EXTRAINDO O CODIGO (ISSO DAQUI PRECISA SER MODIFICADO NO FUTURO)
                codigo_par = request.POST.get('catalogada')
                codigo = re.compile(r"\(\S*\)")
                codigo = codigo.findall(codigo_par)
                codigo = re.sub(r'[()]', '', codigo[0])

            # Alterando a catalogada do documento
                print('Codigo request: ', request.POST.get('codigo'))
                catalogada = get_object_or_404(Catalogada, codigo=request.POST.get('codigo'))
                catalogada.documentos.remove(documento)

                print('Codigo regex: ', codigo)
                catalogada = get_object_or_404(Catalogada, codigo=codigo)
                catalogada.documentos.add(documento)

            # Alterando a pessoa responsável pelo documento
                documento.responsavel_documento = request.POST.get('user')
                documento.save()

            # Alterando a pessoa responsável pelo documento
            elif request.POST.get('user') != "":
                documento.responsavel_documento = request.POST.get('user')
                documento.save()


                #processamento = Processamento.objects.filter(id=documento.id)
                #print('processamento: ', processamento.values())
                #print('documento: ', catalogada.documentos.values())

            # Alterando a catalogada do documento
            elif request.POST.get('catalogada') != "":
                #EXTRAINDO O CODIGO (ISSO DAQUI PRECISA SER MODIFICADO NO FUTURO)
                codigo_par = request.POST.get('catalogada')
                codigo = re.compile(r"\(\S*\)")
                codigo = codigo.findall(codigo_par)
                codigo = re.sub(r'[()]', '', codigo[0])
                documento.save()

                print('Codigo request: ', request.POST.get('codigo'))
                catalogada = get_object_or_404(Catalogada, codigo=request.POST.get('codigo'))
                catalogada.documentos.remove(documento)

                print('Codigo regex: ', codigo)
                catalogada = get_object_or_404(Catalogada, codigo=codigo)
                catalogada.documentos.add(documento)
            elif request.POST.get('user') == "" and request.POST.get('catalogada') == "":
                documento.save()


            #processamento = Processamento.objects.filter(documento_id=documento.id)
            #processamento.update(data_edicao_documento=timezone.now())
            return redirect('resultado_documentos')
        else:
            print("form inválido")
            # print(documento_form.catalogadas)
            print(documento_form.errors)


    else:
        documento = get_object_or_404(Documento, pk=pk)
        documento_form = DocumentoForm(instance=documento)
        catalogada = documento.catalogadas.first()
        #responsavel_documento = documento.processamento.filter(
           # documento__pk=documento.pk).first().responsavel_documento


    return render(request, 'app/editar_documento.html',
                  {'documento_form': documento_form, "lista_catalogadas": catalogadas,
                   "catalogada": catalogada,
                   "documento": documento})

#Gera um XML único para a catalogada selecionada no padrão M.A.P.
#Sem os documentos
@login_required()
def gerar_xml(request, pk):
    catalogada = get_object_or_404(Catalogada, pk=pk)
    print("gerar xml")

    root = LET.Element("catalogada")

    LET.SubElement(root, "codigo").text = catalogada.codigo
    LET.SubElement(root, "nome_modernizado").text = catalogada.nome_modernizado
    LET.SubElement(root, "grafia_conservadora").text = catalogada.grafia_conservadora
    LET.SubElement(root, "trecho_nomeacao").text = catalogada.trecho_nomeacao
    LET.SubElement(root, "trecho_voz").text = catalogada.trecho_voz
    LET.SubElement(root, "detalhamento_perfil").text = catalogada.detalhamento_perfil
    LET.SubElement(root, "unidade_menor_nascimento").text = catalogada.unidade_menor_nascimento
    LET.SubElement(root, "conservadora_menor_nascimento").text = catalogada.conservadora_menor_nascimento
    LET.SubElement(root, "unidade_intermediaria_nascimento").text = catalogada.unidade_intermediaria_nascimento
    LET.SubElement(root, "conservadora_intermediaria_nascimento").text = catalogada.conservadora_intermediaria_nascimento
    LET.SubElement(root, "unidade_maior_nascimento").text = catalogada.unidade_maior_nascimento
    LET.SubElement(root, "conservadora_maior_nascimento").text = catalogada.conservadora_maior_nascimento
    LET.SubElement(root, "point_nascimento").text = catalogada.point_nascimento
    LET.SubElement(root, "total_filhs").text = str(catalogada.total_filhs)
    LET.SubElement(root, "total_filhas").text = str(catalogada.total_filhas)
    LET.SubElement(root, "total_filhos").text = str(catalogada.total_filhos)
    LET.SubElement(root, "nome_filhs_modernizado").text = catalogada.nome_filhs_modernizado
    LET.SubElement(root, "referencia_dmb").text = catalogada.referencia_dmb
    LET.SubElement(root, "trecho_bibliografia").text = catalogada.trecho_bibliografia
    LET.SubElement(root, "fonte_bibliografia").text = catalogada.fonte_bibliografia
    LET.SubElement(root, "responsavel_catalogacao").text = catalogada.responsavel_catalogacao
    LET.SubElement(root, "informacoes_internas").text = catalogada.informacoes_internas
    LET.SubElement(root, "data_catalogacao").text = str(catalogada.data_catalogacao)
    LET.SubElement(root, "responsavel_revisao_catalogacao").text = catalogada.responsavel_revisao_catalogacao
    LET.SubElement(root, "data_edicao").text = str(catalogada.data_edicao)
    LET.SubElement(root, "data_revisao_catalogacao").text = str(catalogada.data_revisao_catalogacao)
    LET.SubElement(root, "publicar").text = str(catalogada.publicar)
    LET.SubElement(root, "perfil_documental").text = catalogada.perfil_documental

    nome_arquivo = catalogada.nome_modernizado+catalogada.codigo+ ".xml"

    # Gerar XML como bytes
    xml_bytes = LET.tostring(root, pretty_print=True, encoding="utf-8", xml_declaration=True)

    response = HttpResponse(xml_bytes, content_type="application/xml")
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
    return response

# NÃO ESTÁ SENDO UTILIZADA NO MOMENTO
# gera o catálogo completo de catalogadas em XML no padrão M.A.P.
@login_required()
def gerar_xml_catalogadas(request):
    catalogadas = Catalogada.objects.all()

    print("gerar xml total")
    root = LET.Element("registro")

    for catalogada in catalogadas:
        catalogo = LET.SubElement(root, "catalogada")
        LET.SubElement(catalogo, "codigo").text = catalogada.codigo
        LET.SubElement(catalogo, "nome_modernizado").text = catalogada.nome_modernizado
        LET.SubElement(catalogo, "grafia_conservadora").text = catalogada.grafia_conservadora
        LET.SubElement(catalogo, "trecho_nomeacao").text = catalogada.trecho_nomeacao
        LET.SubElement(catalogo, "trecho_voz").text = catalogada.trecho_voz
        LET.SubElement(catalogo, "detalhamento_perfil").text = catalogada.detalhamento_perfil
        LET.SubElement(catalogo, "unidade_menor_nascimento").text = catalogada.unidade_menor_nascimento
        LET.SubElement(catalogo, "conservadora_menor_nascimento").text = catalogada.conservadora_menor_nascimento
        LET.SubElement(catalogo, "unidade_intermediaria_nascimento").text = catalogada.unidade_intermediaria_nascimento
        LET.SubElement(catalogo, "conservadora_intermediaria_nascimento").text = catalogada.conservadora_intermediaria_nascimento
        LET.SubElement(catalogo, "unidade_maior_nascimento").text = catalogada.unidade_maior_nascimento
        LET.SubElement(catalogo, "conservadora_maior_nascimento").text = catalogada.conservadora_maior_nascimento
        LET.SubElement(catalogo, "point_nascimento").text = catalogada.point_nascimento
        LET.SubElement(catalogo, "total_filhs").text = str(catalogada.total_filhs)
        LET.SubElement(catalogo, "total_filhas").text = str(catalogada.total_filhas)
        LET.SubElement(catalogo, "total_filhos").text = str(catalogada.total_filhos)
        LET.SubElement(catalogo, "nome_filhs_modernizado").text = catalogada.nome_filhs_modernizado
        LET.SubElement(catalogo, "referencia_dmb").text = catalogada.referencia_dmb
        LET.SubElement(catalogo, "trecho_bibliografia").text = catalogada.trecho_bibliografia
        LET.SubElement(catalogo, "fonte_bibliografia").text = catalogada.fonte_bibliografia
        LET.SubElement(catalogo, "responsavel_catalogacao").text = catalogada.responsavel_catalogacao
        LET.SubElement(catalogo, "informacoes_internas").text = catalogada.informacoes_internas
        LET.SubElement(catalogo, "data_catalogacao").text = str(catalogada.data_catalogacao)
        LET.SubElement(catalogo, "responsavel_revisao_catalogacao").text = catalogada.responsavel_revisao_catalogacao
        LET.SubElement(catalogo, "data_edicao").text = str(catalogada.data_edicao)
        LET.SubElement(catalogo, "data_revisao_catalogacao").text = str(catalogada.data_revisao_catalogacao)
        LET.SubElement(catalogo, "publicar").text = str(catalogada.publicar)
        LET.SubElement(catalogo, "perfil_documental").text = catalogada.perfil_documental

    tree = LET.ElementTree(root)

    nome_arquivo = "catalogadas.xml"

    # Gerar XML como bytes
    xml_bytes = LET.tostring(root, pretty_print=True, encoding="utf-8", xml_declaration=True)

    response = HttpResponse(xml_bytes, content_type="application/xml")
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
    return response

#Gera um XML único para a catalogada selecionada no padrão eDictor
#Sem os documentos
@login_required()
def gerar_xml_edictor(request, pk):
    catalogada = get_object_or_404(Catalogada, pk=pk)
    print("gerar xml edictor")

    root = LET.Element("metadata", generation="MAP")
    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "codigo"
    LET.SubElement(meta, "v").text = catalogada.codigo

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "nome_modernizado"
    LET.SubElement(meta, "v").text = catalogada.nome_modernizado

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "grafia_conservadora"
    LET.SubElement(meta, "v").text = catalogada.grafia_conservadora

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "trecho_nomeacao"
    LET.SubElement(meta, "v").text = catalogada.trecho_nomeacao

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "trecho_voz"
    LET.SubElement(meta, "v").text = catalogada.trecho_voz

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "detalhamento_perfil"
    LET.SubElement(meta, "v").text = catalogada.detalhamento_perfil

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "unidade_menor_nascimento"
    LET.SubElement(meta, "v").text = catalogada.unidade_menor_nascimento

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "conservadora_menor_nascimento"
    LET.SubElement(meta, "v").text = catalogada.conservadora_menor_nascimento

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "unidade_intermediaria_nascimento"
    LET.SubElement(meta, "v").text = catalogada.unidade_intermediaria_nascimento

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "conservadora_intermediaria_nascimento"
    LET.SubElement(meta, "v").text = catalogada.conservadora_intermediaria_nascimento

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "unidade_maior_nascimento"
    LET.SubElement(meta, "v").text = catalogada.unidade_maior_nascimento

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "conservadora_maior_nascimento"
    LET.SubElement(meta, "v").text = catalogada.conservadora_maior_nascimento

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "point_nascimento"
    LET.SubElement(meta, "v").text = str(catalogada.point_nascimento)

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "total_filhs"
    LET.SubElement(meta, "v").text = str(catalogada.total_filhs)

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "total_filhas"
    LET.SubElement(meta, "v").text = str(catalogada.total_filhas)

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "total_filhos"
    LET.SubElement(meta, "v").text = str(catalogada.total_filhos)

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "nome_filhs_modernizado"
    LET.SubElement(meta, "v").text = str(catalogada.nome_filhs_modernizado)

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "referencia_dmb"
    LET.SubElement(meta, "v").text = catalogada.referencia_dmb

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "trecho_bibliografia"
    LET.SubElement(meta, "v").text = catalogada.trecho_bibliografia

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "fonte_bibliografia"
    LET.SubElement(meta, "v").text = catalogada.fonte_bibliografia

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "responsavel_catalogacao"
    LET.SubElement(meta, "v").text = catalogada.responsavel_catalogacao

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "informacoes_internas"
    LET.SubElement(meta, "v").text = catalogada.informacoes_internas

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "data_catalogacao"
    LET.SubElement(meta, "v").text = str(catalogada.data_catalogacao)

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "responsavel_revisao_catalogacao"
    LET.SubElement(meta, "v").text = catalogada.responsavel_revisao_catalogacao

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "data_edicao"
    LET.SubElement(meta, "v").text = str(catalogada.data_edicao)

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "data_revisao_catalogacao"
    LET.SubElement(meta, "v").text = str(catalogada.data_revisao_catalogacao)

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "publicar"
    LET.SubElement(meta, "v").text = str(catalogada.publicar)

    meta = LET.SubElement(root, "meta")
    LET.SubElement(meta, "n").text = "perfil_documental"
    LET.SubElement(meta, "v").text = catalogada.perfil_documental


    nome_arquivo = catalogada.nome_modernizado+catalogada.codigo+ ".xml"

    # Gerar XML como bytes
    xml_bytes = LET.tostring(root, pretty_print=True, encoding="utf-8", xml_declaration=True)

    response = HttpResponse(xml_bytes, content_type="application/xml")
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
    return response


# NÃO ESTÁ SENDO UTILIZADA NO MOMENTO
# gera o catálogo completo de catalogadas em XML no padrão eDictor
@login_required()
def gerar_xml_catalogadas_edictor(request):
    catalogadas = Catalogada.objects.all()

    print("gerar xml total eDictor")

    root = LET.Element("registros")


    for catalogada in catalogadas:
        metadata_map = LET.SubElement(root, "metadata", generation="MAP")

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "codigo"
        LET.SubElement(meta, "v").text = catalogada.codigo

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "nome_modernizado"
        LET.SubElement(meta, "v").text = catalogada.nome_modernizado

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "grafia_conservadora"
        LET.SubElement(meta, "v").text = catalogada.grafia_conservadora

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "trecho_nomeacao"
        LET.SubElement(meta, "v").text = catalogada.trecho_nomeacao

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "trecho_voz"
        LET.SubElement(meta, "v").text = catalogada.trecho_voz

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "detalhamento_perfil"
        LET.SubElement(meta, "v").text = catalogada.detalhamento_perfil

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "unidade_menor_nascimento"
        LET.SubElement(meta, "v").text = catalogada.unidade_menor_nascimento

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "conservadora_menor_nascimento"
        LET.SubElement(meta, "v").text = catalogada.conservadora_menor_nascimento

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "unidade_intermediaria_nascimento"
        LET.SubElement(meta, "v").text = catalogada.unidade_intermediaria_nascimento

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "conservadora_intermediaria_nascimento"
        LET.SubElement(meta, "v").text = catalogada.conservadora_intermediaria_nascimento

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "unidade_maior_nascimento"
        LET.SubElement(meta, "v").text = catalogada.unidade_maior_nascimento

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "conservadora_maior_nascimento"
        LET.SubElement(meta, "v").text = catalogada.conservadora_maior_nascimento

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "point_nascimento"
        LET.SubElement(meta, "v").text = str(catalogada.point_nascimento)

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "total_filhs"
        LET.SubElement(meta, "v").text = str(catalogada.total_filhs)

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "total_filhas"
        LET.SubElement(meta, "v").text = str(catalogada.total_filhas)

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "total_filhos"
        LET.SubElement(meta, "v").text = str(catalogada.total_filhos)

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "nome_filhs_modernizado"
        LET.SubElement(meta, "v").text = str(catalogada.nome_filhs_modernizado)

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "referencia_dmb"
        LET.SubElement(meta, "v").text = catalogada.referencia_dmb

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "trecho_bibliografia"
        LET.SubElement(meta, "v").text = catalogada.trecho_bibliografia

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "fonte_bibliografia"
        LET.SubElement(meta, "v").text = catalogada.fonte_bibliografia

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "responsavel_catalogacao"
        LET.SubElement(meta, "v").text = catalogada.responsavel_catalogacao

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "informacoes_internas"
        LET.SubElement(meta, "v").text = catalogada.informacoes_internas

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "data_catalogacao"
        LET.SubElement(meta, "v").text = str(catalogada.data_catalogacao)

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "responsavel_revisao_catalogacao"
        LET.SubElement(meta, "v").text = catalogada.responsavel_revisao_catalogacao

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "data_edicao"
        LET.SubElement(meta, "v").text = str(catalogada.data_edicao)

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "data_revisao_catalogacao"
        LET.SubElement(meta, "v").text = str(catalogada.data_revisao_catalogacao)

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "publicar"
        LET.SubElement(meta, "v").text = str(catalogada.publicar)

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "perfil_documental"
        LET.SubElement(meta, "v").text = catalogada.perfil_documental


    nome_arquivo = "catalogadas_edictor.xml"

    # Gerar XML como bytes
    xml_bytes = LET.tostring(root, pretty_print=True, encoding="utf-8", xml_declaration=True)

    response = HttpResponse(xml_bytes, content_type="application/xml")
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
    return response

@login_required()
def gerar_arquivos_xml_documentos(request):
    catalogadas = Catalogada.objects.all()
    documentos = Documento.objects.all()

    buffer = io.BytesIO()

    print("gerar xml documentos")

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for documento in documentos:
            root = LET.Element("registros")

            catalogada = get_object_or_404(Catalogada, codigo_antes=documento.codigo_antes)

            catalogadaXML = LET.SubElement(root, "catalogada")

            LET.SubElement(catalogadaXML, "codigo_antes").text = catalogada.codigo_antes
            LET.SubElement(catalogadaXML, "codigo").text = catalogada.codigo
            LET.SubElement(catalogadaXML, "nome_modernizado").text = catalogada.nome_modernizado
            LET.SubElement(catalogadaXML, "grafia_conservadora").text = catalogada.grafia_conservadora
            LET.SubElement(catalogadaXML, "trecho_nomeacao").text = catalogada.trecho_nomeacao
            LET.SubElement(catalogadaXML, "trecho_voz").text = catalogada.trecho_voz
            LET.SubElement(catalogadaXML, "detalhamento_perfil").text = catalogada.detalhamento_perfil
            LET.SubElement(catalogadaXML, "unidade_menor_nascimento").text = catalogada.unidade_menor_nascimento
            LET.SubElement(catalogadaXML, "conservadora_menor_nascimento").text = catalogada.conservadora_menor_nascimento
            LET.SubElement(catalogadaXML, "unidade_intermediaria_nascimento").text = catalogada.unidade_intermediaria_nascimento
            LET.SubElement(catalogadaXML, "conservadora_intermediaria_nascimento").text = catalogada.conservadora_intermediaria_nascimento
            LET.SubElement(catalogadaXML, "unidade_maior_nascimento").text = catalogada.unidade_maior_nascimento
            LET.SubElement(catalogadaXML, "conservadora_maior_nascimento").text = catalogada.conservadora_maior_nascimento
            LET.SubElement(catalogadaXML, "point_nascimento").text = catalogada.point_nascimento
            LET.SubElement(catalogadaXML, "total_filhs").text = str(catalogada.total_filhs)
            LET.SubElement(catalogadaXML, "total_filhas").text = str(catalogada.total_filhas)
            LET.SubElement(catalogadaXML, "total_filhos").text = str(catalogada.total_filhos)
            LET.SubElement(catalogadaXML, "nome_filhs_modernizado").text = catalogada.nome_filhs_modernizado
            LET.SubElement(catalogadaXML, "referencia_dmb").text = catalogada.referencia_dmb
            LET.SubElement(catalogadaXML, "trecho_bibliografia").text = catalogada.trecho_bibliografia
            LET.SubElement(catalogadaXML, "fonte_bibliografia").text = catalogada.fonte_bibliografia
            LET.SubElement(catalogadaXML, "responsavel_catalogacao").text = catalogada.responsavel_catalogacao
            LET.SubElement(catalogadaXML, "informacoes_internas").text = catalogada.informacoes_internas
            LET.SubElement(catalogadaXML, "data_catalogacao").text = str(catalogada.data_catalogacao)
            LET.SubElement(catalogadaXML, "responsavel_revisao_catalogacao").text = catalogada.responsavel_revisao_catalogacao
            LET.SubElement(catalogadaXML, "data_edicao").text = str(catalogada.data_edicao)
            LET.SubElement(catalogadaXML, "data_revisao_catalogacao").text = str(catalogada.data_revisao_catalogacao)
            LET.SubElement(catalogadaXML, "publicar").text = str(catalogada.publicar)
            LET.SubElement(catalogadaXML, "perfil_documental").text = catalogada.perfil_documental


            documentoXML = LET.SubElement(root, "documento")
            LET.SubElement(documentoXML, "codigo_antes").text = documento.codigo_antes
            LET.SubElement(documentoXML, "ano_escrita").text = str(documento.ano_escrita)
            LET.SubElement(documentoXML, "datacao_cronologica_inicial").text = documento.datacao_cronologica_inicial
            LET.SubElement(documentoXML, "datacao_cronologica_final").text = str(documento.datacao_cronologica_final)
            LET.SubElement(documentoXML, "descricao_conteudo_documento").text = documento.descricao_conteudo_documento
            LET.SubElement(documentoXML, "descricao_materia_documento").text = str(documento.descricao_materia_documento)
            LET.SubElement(documentoXML, "autoria_institucional").text = documento.autoria_institucional
            LET.SubElement(documentoXML, "autoria_material").text = str(documento.autoria_material)
            LET.SubElement(documentoXML, "chave_pesquisa").text = documento.chave_pesquisa
            LET.SubElement(documentoXML, "condicao_documento").text = str(documento.condicao_documento)
            LET.SubElement(documentoXML, "indexador_fonte").text = documento.indexador_fonte
            LET.SubElement(documentoXML, "url_fonte").text = str(documento.url_fonte)
            LET.SubElement(documentoXML, "idade_catalogada_documento").text = str(documento.idade_catalogada_documento)
            LET.SubElement(documentoXML, "qualificacao_social_documento").text = str(documento.qualificacao_social_documento)
            LET.SubElement(documentoXML, "unidade_menor_escrita").text = documento.unidade_menor_escrita
            LET.SubElement(documentoXML, "conservadora_menor_escrita").text = str(documento.conservadora_menor_escrita)
            LET.SubElement(documentoXML, "unidade_intermediaria_escrita").text = documento.unidade_intermediaria_escrita
            LET.SubElement(documentoXML, "conservadora_intermediaria_escrita").text = str(documento.conservadora_intermediaria_escrita)
            LET.SubElement(documentoXML, "unidade_maior_escrita").text = documento.unidade_maior_escrita
            LET.SubElement(documentoXML, "conservadora_maior_escrita").text = str(documento.conservadora_maior_escrita)
            LET.SubElement(documentoXML, "point_escrita").text = documento.point_escrita
            LET.SubElement(documentoXML, "unidade_menor_morada").text = str(documento.unidade_menor_morada)
            LET.SubElement(documentoXML, "conservadora_menor_morada").text = documento.conservadora_menor_morada
            LET.SubElement(documentoXML, "unidade_intermediaria_morada").text = str(documento.unidade_intermediaria_morada)
            LET.SubElement(documentoXML, "conservadora_intermediaria_morada").text = documento.conservadora_intermediaria_morada
            LET.SubElement(documentoXML, "unidade_maior_morada").text = str(documento.unidade_maior_morada)
            LET.SubElement(documentoXML, "conservadora_maior_morada").text = documento.conservadora_maior_morada
            LET.SubElement(documentoXML, "point_morada").text = str(documento.point_morada)
            LET.SubElement(documentoXML, "edicao_filologica_parcial").text = documento.edicao_filologica_parcial
            LET.SubElement(documentoXML, "autoria_edicao_conservadora").text = str(documento.autoria_edicao_conservadora)
            LET.SubElement(documentoXML, "autoria_edicao_modernizada").text = documento.autoria_edicao_modernizada
            LET.SubElement(documentoXML, "responsabilidade_revisao_parcial").text = str(documento.responsabilidade_revisao_parcial)
            LET.SubElement(documentoXML, "ligacao_edicao_filologica").text = documento.ligacao_edicao_filologica
            LET.SubElement(documentoXML, "rede_documental").text = str(documento.rede_documental)
            LET.SubElement(documentoXML, "terceira_referida").text = documento.terceira_referida
            LET.SubElement(documentoXML, "trabalhos_andamento").text = str(documento.trabalhos_andamento)
            LET.SubElement(documentoXML, "trabalhos_derivados").text = documento.trabalhos_derivados
            LET.SubElement(documentoXML, "tema").text = str(documento.tema)
            LET.SubElement(documentoXML, "subtema").text = documento.subtema
            LET.SubElement(documentoXML, "informacoes_internas").text = str(documento.informacoes_internas)
            LET.SubElement(documentoXML, "link_gdrive").text = documento.link_gdrive
            LET.SubElement(documentoXML, "gx_media_links").text = str(documento.gx_media_links)
            LET.SubElement(documentoXML, "colaboracao").text = documento.colaboracao
            LET.SubElement(documentoXML, "creditos_imagem").text = str(documento.creditos_imagem)
            LET.SubElement(documentoXML, "responsavel_documento").text = documento.responsavel_documento
            LET.SubElement(documentoXML, "data_edicao_documento").text = str(documento.data_edicao_documento)
            LET.SubElement(documentoXML, "publicar").text = documento.publicar
            LET.SubElement(documentoXML, "tipo_documento").text = str(documento.tipo_documento)
            LET.SubElement(documentoXML, "subtipo_documento").text = str(documento.subtipo_documento)
            LET.SubElement(documentoXML, "ano_inferencia").text = str(documento.ano_inferencia)
            LET.SubElement(documentoXML, "cronologica_inicial_inferencia").text = str(documento.cronologica_inicial_inferencia)
            LET.SubElement(documentoXML, "cronologica_final_inferencia").text = str(documento.cronologica_final_inferencia)
            LET.SubElement(documentoXML, "perfil_documental").text = str(documento.perfil_documental)
            LET.SubElement(documentoXML, "arquivo_guarda").text = str(documento.arquivo_guarda)
            LET.SubElement(documentoXML, "estado_civil").text = str(documento.estado_civil)



            nome_arquivo = '['+catalogada.codigo_antes+']'+'_'+catalogada.codigo+'_'+catalogada.nome_modernizado+ ".xml"

            # Gerar XML como bytes
            xml_bytes = LET.tostring(root, pretty_print=True, encoding="utf-8", xml_declaration=True)

            # Adicionar o arquivo ao ZIP
            zip_file.writestr(nome_arquivo, xml_bytes)



    #move o ponteiro para o início do buffer após o fechamento do zip
    buffer.seek(0)
    #prepara resposta HTTP com o conteúdo do ZIP
    response = HttpResponse(buffer.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="catalogadas_map_lote.zip"'

    return response


@login_required()
def gerar_arquivos_xml_documentos_unico(request):
    catalogadas = Catalogada.objects.all()
    documentos = Documento.objects.all()

    root = LET.Element("registros")
    n_conjunto = 1
    print("gerar xml documentos unico")
    for documento in documentos:

        catalogada = get_object_or_404(Catalogada, codigo_antes=documento.codigo_antes)

        conjunto = LET.SubElement(root, "conjunto" + '_' +str(n_conjunto), numero=str(n_conjunto))

        catalogadaXML = LET.SubElement(conjunto, "catalogada")

        LET.SubElement(catalogadaXML, "codigo_antes").text = catalogada.codigo_antes
        LET.SubElement(catalogadaXML, "codigo").text = catalogada.codigo
        LET.SubElement(catalogadaXML, "nome_modernizado").text = catalogada.nome_modernizado
        LET.SubElement(catalogadaXML, "grafia_conservadora").text = catalogada.grafia_conservadora
        LET.SubElement(catalogadaXML, "trecho_nomeacao").text = catalogada.trecho_nomeacao
        LET.SubElement(catalogadaXML, "trecho_voz").text = catalogada.trecho_voz
        LET.SubElement(catalogadaXML, "detalhamento_perfil").text = catalogada.detalhamento_perfil
        LET.SubElement(catalogadaXML, "unidade_menor_nascimento").text = catalogada.unidade_menor_nascimento
        LET.SubElement(catalogadaXML, "conservadora_menor_nascimento").text = catalogada.conservadora_menor_nascimento
        LET.SubElement(catalogadaXML, "unidade_intermediaria_nascimento").text = catalogada.unidade_intermediaria_nascimento
        LET.SubElement(catalogadaXML, "conservadora_intermediaria_nascimento").text = catalogada.conservadora_intermediaria_nascimento
        LET.SubElement(catalogadaXML, "unidade_maior_nascimento").text = catalogada.unidade_maior_nascimento
        LET.SubElement(catalogadaXML, "conservadora_maior_nascimento").text = catalogada.conservadora_maior_nascimento
        LET.SubElement(catalogadaXML, "point_nascimento").text = catalogada.point_nascimento
        LET.SubElement(catalogadaXML, "total_filhs").text = str(catalogada.total_filhs)
        LET.SubElement(catalogadaXML, "total_filhas").text = str(catalogada.total_filhas)
        LET.SubElement(catalogadaXML, "total_filhos").text = str(catalogada.total_filhos)
        LET.SubElement(catalogadaXML, "nome_filhs_modernizado").text = catalogada.nome_filhs_modernizado
        LET.SubElement(catalogadaXML, "referencia_dmb").text = catalogada.referencia_dmb
        LET.SubElement(catalogadaXML, "trecho_bibliografia").text = catalogada.trecho_bibliografia
        LET.SubElement(catalogadaXML, "fonte_bibliografia").text = catalogada.fonte_bibliografia
        LET.SubElement(catalogadaXML, "responsavel_catalogacao").text = catalogada.responsavel_catalogacao
        LET.SubElement(catalogadaXML, "informacoes_internas").text = catalogada.informacoes_internas
        LET.SubElement(catalogadaXML, "data_catalogacao").text = str(catalogada.data_catalogacao)
        LET.SubElement(catalogadaXML, "responsavel_revisao_catalogacao").text = catalogada.responsavel_revisao_catalogacao
        LET.SubElement(catalogadaXML, "data_edicao").text = str(catalogada.data_edicao)
        LET.SubElement(catalogadaXML, "data_revisao_catalogacao").text = str(catalogada.data_revisao_catalogacao)
        LET.SubElement(catalogadaXML, "publicar").text = str(catalogada.publicar)
        LET.SubElement(catalogadaXML, "perfil_documental").text = catalogada.perfil_documental


        documentoXML = LET.SubElement(conjunto, "documento")
        LET.SubElement(documentoXML, "codigo_antes").text = documento.codigo_antes
        LET.SubElement(documentoXML, "ano_escrita").text = str(documento.ano_escrita)
        LET.SubElement(documentoXML, "datacao_cronologica_inicial").text = documento.datacao_cronologica_inicial
        LET.SubElement(documentoXML, "datacao_cronologica_final").text = str(documento.datacao_cronologica_final)
        LET.SubElement(documentoXML, "descricao_conteudo_documento").text = documento.descricao_conteudo_documento
        LET.SubElement(documentoXML, "descricao_materia_documento").text = str(documento.descricao_materia_documento)
        LET.SubElement(documentoXML, "autoria_institucional").text = documento.autoria_institucional
        LET.SubElement(documentoXML, "autoria_material").text = str(documento.autoria_material)
        LET.SubElement(documentoXML, "chave_pesquisa").text = documento.chave_pesquisa
        LET.SubElement(documentoXML, "condicao_documento").text = str(documento.condicao_documento)
        LET.SubElement(documentoXML, "indexador_fonte").text = documento.indexador_fonte
        LET.SubElement(documentoXML, "url_fonte").text = str(documento.url_fonte)
        LET.SubElement(documentoXML, "idade_catalogada_documento").text = str(documento.idade_catalogada_documento)
        LET.SubElement(documentoXML, "qualificacao_social_documento").text = str(documento.qualificacao_social_documento)
        LET.SubElement(documentoXML, "unidade_menor_escrita").text = documento.unidade_menor_escrita
        LET.SubElement(documentoXML, "conservadora_menor_escrita").text = str(documento.conservadora_menor_escrita)
        LET.SubElement(documentoXML, "unidade_intermediaria_escrita").text = documento.unidade_intermediaria_escrita
        LET.SubElement(documentoXML, "conservadora_intermediaria_escrita").text = str(documento.conservadora_intermediaria_escrita)
        LET.SubElement(documentoXML, "unidade_maior_escrita").text = documento.unidade_maior_escrita
        LET.SubElement(documentoXML, "conservadora_maior_escrita").text = str(documento.conservadora_maior_escrita)
        LET.SubElement(documentoXML, "point_escrita").text = documento.point_escrita
        LET.SubElement(documentoXML, "unidade_menor_morada").text = str(documento.unidade_menor_morada)
        LET.SubElement(documentoXML, "conservadora_menor_morada").text = documento.conservadora_menor_morada
        LET.SubElement(documentoXML, "unidade_intermediaria_morada").text = str(documento.unidade_intermediaria_morada)
        LET.SubElement(documentoXML, "conservadora_intermediaria_morada").text = documento.conservadora_intermediaria_morada
        LET.SubElement(documentoXML, "unidade_maior_morada").text = str(documento.unidade_maior_morada)
        LET.SubElement(documentoXML, "conservadora_maior_morada").text = documento.conservadora_maior_morada
        LET.SubElement(documentoXML, "point_morada").text = str(documento.point_morada)
        LET.SubElement(documentoXML, "edicao_filologica_parcial").text = documento.edicao_filologica_parcial
        LET.SubElement(documentoXML, "autoria_edicao_conservadora").text = str(documento.autoria_edicao_conservadora)
        LET.SubElement(documentoXML, "autoria_edicao_modernizada").text = documento.autoria_edicao_modernizada
        LET.SubElement(documentoXML, "responsabilidade_revisao_parcial").text = str(documento.responsabilidade_revisao_parcial)
        LET.SubElement(documentoXML, "ligacao_edicao_filologica").text = documento.ligacao_edicao_filologica
        LET.SubElement(documentoXML, "rede_documental").text = str(documento.rede_documental)
        LET.SubElement(documentoXML, "terceira_referida").text = documento.terceira_referida
        LET.SubElement(documentoXML, "trabalhos_andamento").text = str(documento.trabalhos_andamento)
        LET.SubElement(documentoXML, "trabalhos_derivados").text = documento.trabalhos_derivados
        LET.SubElement(documentoXML, "tema").text = str(documento.tema)
        LET.SubElement(documentoXML, "subtema").text = documento.subtema
        LET.SubElement(documentoXML, "informacoes_internas").text = str(documento.informacoes_internas)
        LET.SubElement(documentoXML, "link_gdrive").text = documento.link_gdrive
        LET.SubElement(documentoXML, "gx_media_links").text = str(documento.gx_media_links)
        LET.SubElement(documentoXML, "colaboracao").text = documento.colaboracao
        LET.SubElement(documentoXML, "creditos_imagem").text = str(documento.creditos_imagem)
        LET.SubElement(documentoXML, "responsavel_documento").text = documento.responsavel_documento
        LET.SubElement(documentoXML, "data_edicao_documento").text = str(documento.data_edicao_documento)
        LET.SubElement(documentoXML, "publicar").text = documento.publicar
        LET.SubElement(documentoXML, "tipo_documento").text = str(documento.tipo_documento)
        LET.SubElement(documentoXML, "subtipo_documento").text = str(documento.subtipo_documento)
        LET.SubElement(documentoXML, "ano_inferencia").text = str(documento.ano_inferencia)
        LET.SubElement(documentoXML, "cronologica_inicial_inferencia").text = str(documento.cronologica_inicial_inferencia)
        LET.SubElement(documentoXML, "cronologica_final_inferencia").text = str(documento.cronologica_final_inferencia)
        LET.SubElement(documentoXML, "perfil_documental").text = str(documento.perfil_documental)
        LET.SubElement(documentoXML, "arquivo_guarda").text = str(documento.arquivo_guarda)
        LET.SubElement(documentoXML, "estado_civil").text = str(documento.estado_civil)

        n_conjunto = n_conjunto + 1


    nome_arquivo = "padrao_map_unico.xml"

    # Gerar XML como bytes
    xml_bytes = LET.tostring(root, pretty_print=True, encoding="utf-8", xml_declaration=True)

    # Criar e retornar a resposta HTTP
    response = HttpResponse(xml_bytes, content_type="application/xml")
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
    return response


@login_required()
def gerar_xml_documentos_edictor(request):
    catalogadas = Catalogada.objects.all()
    documentos = Documento.objects.all()

    # Usar BytesIO para armazenar o ZIP em memória
    buffer = io.BytesIO()

    print("gerar xml documentos edictor")
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        for documento in documentos:
            root = LET.Element("metadata", generation="MAP")

            catalogada = get_object_or_404(Catalogada, codigo_antes=documento.codigo_antes)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "codigo_antes"
            LET.SubElement(meta, "v").text = catalogada.codigo_antes

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "codigo"
            LET.SubElement(meta, "v").text = catalogada.codigo

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "nome_modernizado"
            LET.SubElement(meta, "v").text = catalogada.nome_modernizado

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "grafia_conservadora"
            LET.SubElement(meta, "v").text = catalogada.grafia_conservadora

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "trecho_nomeacao"
            LET.SubElement(meta, "v").text = catalogada.trecho_nomeacao

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "trecho_voz"
            LET.SubElement(meta, "v").text = catalogada.trecho_voz

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "detalhamento_perfil"
            LET.SubElement(meta, "v").text = catalogada.detalhamento_perfil

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "unidade_menor_nascimento"
            LET.SubElement(meta, "v").text = catalogada.unidade_menor_nascimento

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "conservadora_menor_nascimento"
            LET.SubElement(meta, "v").text = catalogada.conservadora_menor_nascimento

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "unidade_intermediaria_nascimento"
            LET.SubElement(meta, "v").text = catalogada.unidade_intermediaria_nascimento

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "conservadora_intermediaria_nascimento"
            LET.SubElement(meta, "v").text = catalogada.conservadora_intermediaria_nascimento

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "unidade_maior_nascimento"
            LET.SubElement(meta, "v").text = catalogada.unidade_maior_nascimento

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "conservadora_maior_nascimento"
            LET.SubElement(meta, "v").text = catalogada.conservadora_maior_nascimento

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "point_nascimento"
            LET.SubElement(meta, "v").text = str(catalogada.point_nascimento)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "total_filhs"
            LET.SubElement(meta, "v").text = str(catalogada.total_filhs)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "total_filhas"
            LET.SubElement(meta, "v").text = str(catalogada.total_filhas)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "total_filhos"
            LET.SubElement(meta, "v").text = str(catalogada.total_filhos)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "nome_filhs_modernizado"
            LET.SubElement(meta, "v").text = str(catalogada.nome_filhs_modernizado)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "referencia_dmb"
            LET.SubElement(meta, "v").text = catalogada.referencia_dmb

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "trecho_bibliografia"
            LET.SubElement(meta, "v").text = catalogada.trecho_bibliografia

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "fonte_bibliografia"
            LET.SubElement(meta, "v").text = catalogada.fonte_bibliografia

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "responsavel_catalogacao"
            LET.SubElement(meta, "v").text = catalogada.responsavel_catalogacao

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "informacoes_internas"
            LET.SubElement(meta, "v").text = catalogada.informacoes_internas

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "data_catalogacao"
            LET.SubElement(meta, "v").text = str(catalogada.data_catalogacao)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "responsavel_revisao_catalogacao"
            LET.SubElement(meta, "v").text = catalogada.responsavel_revisao_catalogacao

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "data_edicao"
            LET.SubElement(meta, "v").text = str(catalogada.data_edicao)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "data_revisao_catalogacao"
            LET.SubElement(meta, "v").text = str(catalogada.data_revisao_catalogacao)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "publicar"
            LET.SubElement(meta, "v").text = str(catalogada.publicar)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "perfil_documental"
            LET.SubElement(meta, "v").text = catalogada.perfil_documental



            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "ano_escrita"
            LET.SubElement(meta, "v").text = str(documento.ano_escrita)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "datacao_cronologica_inicial"
            LET.SubElement(meta, "v").text = str(documento.datacao_cronologica_inicial)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "datacao_cronologica_final"
            LET.SubElement(meta, "v").text = str(documento.datacao_cronologica_final)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "descricao_conteudo_documento"
            LET.SubElement(meta, "v").text = str(documento.descricao_conteudo_documento)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "descricao_materia_documento"
            LET.SubElement(meta, "v").text = str(documento.descricao_materia_documento)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "autoria_institucional"
            LET.SubElement(meta, "v").text = str(documento.autoria_institucional)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "autoria_material"
            LET.SubElement(meta, "v").text = str(documento.autoria_material)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "chave_pesquisa"
            LET.SubElement(meta, "v").text = str(documento.chave_pesquisa)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "condicao_documento"
            LET.SubElement(meta, "v").text = str(documento.condicao_documento)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "indexador_fonte"
            LET.SubElement(meta, "v").text = str(documento.indexador_fonte)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "url_fonte"
            LET.SubElement(meta, "v").text = str(documento.url_fonte)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "idade_catalogada_documento"
            LET.SubElement(meta, "v").text = str(documento.idade_catalogada_documento)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "qualificacao_social_documento"
            LET.SubElement(meta, "v").text = str(documento.qualificacao_social_documento)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "unidade_menor_escrita"
            LET.SubElement(meta, "v").text = str(documento.unidade_menor_escrita)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "conservadora_menor_escrita"
            LET.SubElement(meta, "v").text = str(documento.conservadora_menor_escrita)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "unidade_intermediaria_escrita"
            LET.SubElement(meta, "v").text = str(documento.unidade_intermediaria_escrita)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "conservadora_intermediaria_escrita"
            LET.SubElement(meta, "v").text = str(documento.conservadora_intermediaria_escrita)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "unidade_maior_escrita"
            LET.SubElement(meta, "v").text = str(documento.unidade_maior_escrita)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "conservadora_maior_escrita"
            LET.SubElement(meta, "v").text = str(documento.conservadora_maior_escrita)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "point_escrita"
            LET.SubElement(meta, "v").text = str(documento.point_escrita)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "unidade_menor_morada"
            LET.SubElement(meta, "v").text = str(documento.unidade_menor_morada)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "conservadora_menor_morada"
            LET.SubElement(meta, "v").text = str(documento.conservadora_menor_morada)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "unidade_intermediaria_morada"
            LET.SubElement(meta, "v").text = str(documento.unidade_intermediaria_morada)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "conservadora_intermediaria_morada"
            LET.SubElement(meta, "v").text = str(documento.conservadora_intermediaria_morada)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "unidade_maior_morada"
            LET.SubElement(meta, "v").text = str(documento.unidade_maior_morada)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "conservadora_maior_morada"
            LET.SubElement(meta, "v").text = str(documento.conservadora_maior_morada)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "point_morada"
            LET.SubElement(meta, "v").text = str(documento.point_morada)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "edicao_filologica_parcial"
            LET.SubElement(meta, "v").text = str(documento.edicao_filologica_parcial)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "autoria_edicao_conservadora"
            LET.SubElement(meta, "v").text = str(documento.autoria_edicao_conservadora)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "autoria_edicao_modernizada"
            LET.SubElement(meta, "v").text = str(documento.autoria_edicao_modernizada)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "responsabilidade_revisao_parcial"
            LET.SubElement(meta, "v").text = str(documento.responsabilidade_revisao_parcial)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "ligacao_edicao_filologica"
            LET.SubElement(meta, "v").text = str(documento.ligacao_edicao_filologica)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "rede_documental"
            LET.SubElement(meta, "v").text = str(documento.rede_documental)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "terceira_referida"
            LET.SubElement(meta, "v").text = str(documento.terceira_referida)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "trabalhos_andamento"
            LET.SubElement(meta, "v").text = str(documento.trabalhos_andamento)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "trabalhos_derivados"
            LET.SubElement(meta, "v").text = str(documento.trabalhos_derivados)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "tema"
            LET.SubElement(meta, "v").text = str(documento.tema)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "subtema"
            LET.SubElement(meta, "v").text = str(documento.subtema)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "informacoes_internas"
            LET.SubElement(meta, "v").text = str(documento.informacoes_internas)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "link_gdrive"
            LET.SubElement(meta, "v").text = str(documento.link_gdrive)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "gx_media_links"
            LET.SubElement(meta, "v").text = str(documento.gx_media_links)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "colaboracao"
            LET.SubElement(meta, "v").text = str(documento.colaboracao)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "creditos_imagem"
            LET.SubElement(meta, "v").text = str(documento.creditos_imagem)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "responsavel_documento"
            LET.SubElement(meta, "v").text = str(documento.responsavel_documento)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "data_edicao_documento"
            LET.SubElement(meta, "v").text = str(documento.data_edicao_documento)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "publicar"
            LET.SubElement(meta, "v").text = str(documento.publicar)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "tipo_documento"
            LET.SubElement(meta, "v").text = str(documento.tipo_documento)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "subtipo_documento"
            LET.SubElement(meta, "v").text = str(documento.subtipo_documento)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "ano_inferencia"
            LET.SubElement(meta, "v").text = str(documento.ano_inferencia)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "cronologica_inicial_inferencia"
            LET.SubElement(meta, "v").text = str(documento.cronologica_inicial_inferencia)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "cronologica_final_inferencia"
            LET.SubElement(meta, "v").text = str(documento.cronologica_final_inferencia)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "perfil_documental"
            LET.SubElement(meta, "v").text = str(documento.perfil_documental)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "perfil_documental"
            LET.SubElement(meta, "v").text = str(documento.perfil_documental)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "arquivo_guarda"
            LET.SubElement(meta, "v").text = str(documento.arquivo_guarda)

            meta = LET.SubElement(root, "meta")
            LET.SubElement(meta, "n").text = "estado_civil"
            LET.SubElement(meta, "v").text = str(documento.estado_civil)


            nome_arquivo = '['+catalogada.codigo_antes+']'+'_'+catalogada.codigo+'_'+catalogada.nome_modernizado+ ".xml"

            # Gerar XML como bytes
            xml_bytes = LET.tostring(root, pretty_print=True, encoding="utf-8", xml_declaration=True)

            # Adicionar ao zip
            zip_file.writestr(nome_arquivo, xml_bytes)

    #move o ponteiro para o início do buffer após o fechamento do zip
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="catalogadas_edictor_lote.zip"'

    return response



@login_required()
def gerar_xml_documentos_edictor_uni(request):
    catalogadas = Catalogada.objects.all()
    documentos = Documento.objects.all()


    root = LET.Element("registros")

    print("gerar xml documentos edictor unico")
    for documento in documentos:
        metadata_map = LET.SubElement(root, "metadata", generation="MAP")

        catalogada = get_object_or_404(Catalogada, codigo_antes=documento.codigo_antes)

        meta = LET.SubElement(metadata_map, "meta")
        LET.SubElement(meta, "n").text = "codigo_antes"
        LET.SubElement(meta, "v").text = catalogada.codigo_antes

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "codigo"
        LET.SubElement(meta, "v").text = catalogada.codigo

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "nome_modernizado"
        LET.SubElement(meta, "v").text = catalogada.nome_modernizado

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "grafia_conservadora"
        LET.SubElement(meta, "v").text = catalogada.grafia_conservadora

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "trecho_nomeacao"
        LET.SubElement(meta, "v").text = catalogada.trecho_nomeacao

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "trecho_voz"
        LET.SubElement(meta, "v").text = catalogada.trecho_voz

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "detalhamento_perfil"
        LET.SubElement(meta, "v").text = catalogada.detalhamento_perfil

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "unidade_menor_nascimento"
        LET.SubElement(meta, "v").text = catalogada.unidade_menor_nascimento

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "conservadora_menor_nascimento"
        LET.SubElement(meta, "v").text = catalogada.conservadora_menor_nascimento

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "unidade_intermediaria_nascimento"
        LET.SubElement(meta, "v").text = catalogada.unidade_intermediaria_nascimento

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "conservadora_intermediaria_nascimento"
        LET.SubElement(meta, "v").text = catalogada.conservadora_intermediaria_nascimento

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "unidade_maior_nascimento"
        LET.SubElement(meta, "v").text = catalogada.unidade_maior_nascimento

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "conservadora_maior_nascimento"
        LET.SubElement(meta, "v").text = catalogada.conservadora_maior_nascimento

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "point_nascimento"
        LET.SubElement(meta, "v").text = str(catalogada.point_nascimento)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "total_filhs"
        LET.SubElement(meta, "v").text = str(catalogada.total_filhs)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "total_filhas"
        LET.SubElement(meta, "v").text = str(catalogada.total_filhas)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "total_filhos"
        LET.SubElement(meta, "v").text = str(catalogada.total_filhos)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "nome_filhs_modernizado"
        LET.SubElement(meta, "v").text = str(catalogada.nome_filhs_modernizado)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "referencia_dmb"
        LET.SubElement(meta, "v").text = catalogada.referencia_dmb

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "trecho_bibliografia"
        LET.SubElement(meta, "v").text = catalogada.trecho_bibliografia

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "fonte_bibliografia"
        LET.SubElement(meta, "v").text = catalogada.fonte_bibliografia

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "responsavel_catalogacao"
        LET.SubElement(meta, "v").text = catalogada.responsavel_catalogacao

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "informacoes_internas"
        LET.SubElement(meta, "v").text = catalogada.informacoes_internas

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "data_catalogacao"
        LET.SubElement(meta, "v").text = str(catalogada.data_catalogacao)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "responsavel_revisao_catalogacao"
        LET.SubElement(meta, "v").text = catalogada.responsavel_revisao_catalogacao

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "data_edicao"
        LET.SubElement(meta, "v").text = str(catalogada.data_edicao)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "data_revisao_catalogacao"
        LET.SubElement(meta, "v").text = str(catalogada.data_revisao_catalogacao)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "publicar"
        LET.SubElement(meta, "v").text = str(catalogada.publicar)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "perfil_documental"
        LET.SubElement(meta, "v").text = catalogada.perfil_documental



        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "ano_escrita"
        LET.SubElement(meta, "v").text = str(documento.ano_escrita)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "datacao_cronologica_inicial"
        LET.SubElement(meta, "v").text = str(documento.datacao_cronologica_inicial)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "datacao_cronologica_final"
        LET.SubElement(meta, "v").text = str(documento.datacao_cronologica_final)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "descricao_conteudo_documento"
        LET.SubElement(meta, "v").text = str(documento.descricao_conteudo_documento)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "descricao_materia_documento"
        LET.SubElement(meta, "v").text = str(documento.descricao_materia_documento)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "autoria_institucional"
        LET.SubElement(meta, "v").text = str(documento.autoria_institucional)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "autoria_material"
        LET.SubElement(meta, "v").text = str(documento.autoria_material)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "chave_pesquisa"
        LET.SubElement(meta, "v").text = str(documento.chave_pesquisa)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "condicao_documento"
        LET.SubElement(meta, "v").text = str(documento.condicao_documento)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "indexador_fonte"
        LET.SubElement(meta, "v").text = str(documento.indexador_fonte)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "url_fonte"
        LET.SubElement(meta, "v").text = str(documento.url_fonte)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "idade_catalogada_documento"
        LET.SubElement(meta, "v").text = str(documento.idade_catalogada_documento)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "qualificacao_social_documento"
        LET.SubElement(meta, "v").text = str(documento.qualificacao_social_documento)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "unidade_menor_escrita"
        LET.SubElement(meta, "v").text = str(documento.unidade_menor_escrita)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "conservadora_menor_escrita"
        LET.SubElement(meta, "v").text = str(documento.conservadora_menor_escrita)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "unidade_intermediaria_escrita"
        LET.SubElement(meta, "v").text = str(documento.unidade_intermediaria_escrita)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "conservadora_intermediaria_escrita"
        LET.SubElement(meta, "v").text = str(documento.conservadora_intermediaria_escrita)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "unidade_maior_escrita"
        LET.SubElement(meta, "v").text = str(documento.unidade_maior_escrita)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "conservadora_maior_escrita"
        LET.SubElement(meta, "v").text = str(documento.conservadora_maior_escrita)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "point_escrita"
        LET.SubElement(meta, "v").text = str(documento.point_escrita)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "unidade_menor_morada"
        LET.SubElement(meta, "v").text = str(documento.unidade_menor_morada)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "conservadora_menor_morada"
        LET.SubElement(meta, "v").text = str(documento.conservadora_menor_morada)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "unidade_intermediaria_morada"
        LET.SubElement(meta, "v").text = str(documento.unidade_intermediaria_morada)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "conservadora_intermediaria_morada"
        LET.SubElement(meta, "v").text = str(documento.conservadora_intermediaria_morada)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "unidade_maior_morada"
        LET.SubElement(meta, "v").text = str(documento.unidade_maior_morada)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "conservadora_maior_morada"
        LET.SubElement(meta, "v").text = str(documento.conservadora_maior_morada)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "point_morada"
        LET.SubElement(meta, "v").text = str(documento.point_morada)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "edicao_filologica_parcial"
        LET.SubElement(meta, "v").text = str(documento.edicao_filologica_parcial)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "autoria_edicao_conservadora"
        LET.SubElement(meta, "v").text = str(documento.autoria_edicao_conservadora)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "autoria_edicao_modernizada"
        LET.SubElement(meta, "v").text = str(documento.autoria_edicao_modernizada)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "responsabilidade_revisao_parcial"
        LET.SubElement(meta, "v").text = str(documento.responsabilidade_revisao_parcial)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "ligacao_edicao_filologica"
        LET.SubElement(meta, "v").text = str(documento.ligacao_edicao_filologica)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "rede_documental"
        LET.SubElement(meta, "v").text = str(documento.rede_documental)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "terceira_referida"
        LET.SubElement(meta, "v").text = str(documento.terceira_referida)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "trabalhos_andamento"
        LET.SubElement(meta, "v").text = str(documento.trabalhos_andamento)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "trabalhos_derivados"
        LET.SubElement(meta, "v").text = str(documento.trabalhos_derivados)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "tema"
        LET.SubElement(meta, "v").text = str(documento.tema)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "subtema"
        LET.SubElement(meta, "v").text = str(documento.subtema)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "informacoes_internas"
        LET.SubElement(meta, "v").text = str(documento.informacoes_internas)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "link_gdrive"
        LET.SubElement(meta, "v").text = str(documento.link_gdrive)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "gx_media_links"
        LET.SubElement(meta, "v").text = str(documento.gx_media_links)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "colaboracao"
        LET.SubElement(meta, "v").text = str(documento.colaboracao)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "creditos_imagem"
        LET.SubElement(meta, "v").text = str(documento.creditos_imagem)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "responsavel_documento"
        LET.SubElement(meta, "v").text = str(documento.responsavel_documento)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "data_edicao_documento"
        LET.SubElement(meta, "v").text = str(documento.data_edicao_documento)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "publicar"
        LET.SubElement(meta, "v").text = str(documento.publicar)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "tipo_documento"
        LET.SubElement(meta, "v").text = str(documento.tipo_documento)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "subtipo_documento"
        LET.SubElement(meta, "v").text = str(documento.subtipo_documento)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "ano_inferencia"
        LET.SubElement(meta, "v").text = str(documento.ano_inferencia)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "cronologica_inicial_inferencia"
        LET.SubElement(meta, "v").text = str(documento.cronologica_inicial_inferencia)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "cronologica_final_inferencia"
        LET.SubElement(meta, "v").text = str(documento.cronologica_final_inferencia)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "perfil_documental"
        LET.SubElement(meta, "v").text = str(documento.perfil_documental)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "perfil_documental"
        LET.SubElement(meta, "v").text = str(documento.perfil_documental)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "arquivo_guarda"
        LET.SubElement(meta, "v").text = str(documento.arquivo_guarda)

        meta = LET.SubElement(root, "meta")
        LET.SubElement(meta, "n").text = "estado_civil"
        LET.SubElement(meta, "v").text = str(documento.estado_civil)



    nome_arquivo = "padrao_edictor_unico.xml"

    # Gerar XML como bytes
    xml_bytes = LET.tostring(root, pretty_print=True, encoding="utf-8", xml_declaration=True)

    # Criar e retornar a resposta HTTP
    response = HttpResponse(xml_bytes, content_type="application/xml")
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
    return response


@login_required()
def importar_documentos(request):
    catalogadas = Catalogada.objects.all()
    documentos = Documento.objects.all()

    for documento in documentos:
        catalogada = get_object_or_404(Catalogada, codigo_antes=documento.codigo_antes)
        catalogada.documentos.add(documento)

    return redirect('resultado_documentos')


@login_required()
def importar_csv(request):

    if request.method == "POST" and request.FILES.get("csv_file"):

        arquivo = request.FILES["csv_file"]
        decoded_file = io.TextIOWrapper(arquivo.file)
        leitor_csv = csv.DictReader(decoded_file, delimiter=";")

        nomes_importados = []

        for linha in leitor_csv:
            Catalogada.objects.create(

                codigo_antes=linha.get("codigo_antes"),
                codigo=linha.get("codigo"),
                nome_modernizado=linha.get("nome_modernizado"),
                grafia_conservadora=linha.get("grafia_conservadora"),
                trecho_nomeacao=linha.get("trecho_nomeacao"),
                trecho_voz=linha.get("trecho_voz"),
                detalhamento_perfil=linha.get("detalhamento_perfil"),
                unidade_menor_nascimento=linha.get("unidade_menor_nascimento"),
                conservadora_menor_nascimento=linha.get("conservadora_menor_nascimento"),
                unidade_intermediaria_nascimento=linha.get("unidade_intermediaria_nascimento"),
                conservadora_intermediaria_nascimento=linha.get("conservadora_intermediaria_nascimento"),
                unidade_maior_nascimento=linha.get("unidade_maior_nascimento"),
                conservadora_maior_nascimento=linha.get("conservadora_maior_nascimento"),
                point_nascimento=linha.get("point_nascimento"),
                total_filhs=int(linha.get("total_filhs")),
                total_filhas=int(linha.get("total_filhas")),
                total_filhos=int(linha.get("total_filhos")),
                nome_filhs_modernizado=linha.get("nome_filhs_modernizado"),
                referencia_dmb=linha.get("referencia_dmb"),
                trecho_bibliografia=linha.get("trecho_bibliografia"),
                fonte_bibliografia=linha.get("fonte_bibliografia"),
                responsavel_catalogacao=linha.get("responsavel_catalogacao"),
                informacoes_internas=linha.get("informacoes_internas"),
                data_catalogacao=linha.get("data_catalogacao"),
                responsavel_revisao_catalogacao=linha.get("responsavel_revisao_catalogacao"),
                data_edicao=linha.get("data_edicao"),
                data_revisao_catalogacao=linha.get("data_revisao_catalogacao"),
                publicar=linha.get("publicar"),
                perfil_documental=linha.get("perfil_documental")
            )

        catalogadas = Catalogada.objects.all()
        for catalogada in catalogadas:
            nomes_importados.append(f" {catalogada.id} {catalogada.nome_modernizado} {catalogada.codigo}")

        texto = str("As seguintes catalogadas foram importadas:\n\n" + "\n".join(nomes_importados))
        messages.success(request, texto)

        return redirect("importar_csv")
        print("catalogadas importadas")

    return render(request, 'app/importar_csv.html')

def importar_documentos_csv(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        arquivo = request.FILES["csv_file"]
        decoded_file = io.TextIOWrapper(arquivo.file)
        leitor_csv = csv.DictReader(decoded_file, delimiter=";")

        nomes_importados = []

        for linha in leitor_csv:
            Documento.objects.create(

               codigo_antes = linha.get("codigo_antes"),
               ano_escrita = linha.get("ano_escrita"),
               datacao_cronologica_inicial = linha.get("datacao_cronologica_inicial"),
               datacao_cronologica_final = linha.get("datacao_cronologica_final"),
               descricao_conteudo_documento = linha.get("descricao_conteudo_documento"),
               descricao_materia_documento = linha.get("descricao_materia_documento"),
               autoria_institucional = linha.get("autoria_institucional"),
               autoria_material = linha.get("autoria_material"),
               chave_pesquisa = linha.get("chave_pesquisa"),
               condicao_documento = linha.get("condicao_documento"),
               indexador_fonte = linha.get("indexador_fonte"),
               url_fonte = linha.get("url_fonte"),
               idade_catalogada_documento = linha.get("idade_catalogada_documento"),
               qualificacao_social_documento = linha.get("qualificacao_social_documento"),
               unidade_menor_escrita = linha.get("unidade_menor_escrita"),
               conservadora_menor_escrita = linha.get("conservadora_menor_escrita"),
               unidade_intermediaria_escrita = linha.get("unidade_intermediaria_escrita"),
               conservadora_intermediaria_escrita = linha.get("conservadora_intermediaria_escrita"),
               unidade_maior_escrita = linha.get("unidade_maior_escrita"),
               conservadora_maior_escrita = linha.get("conservadora_maior_escrita"),
               point_escrita = linha.get("point_escrita"),
               unidade_menor_morada = linha.get("unidade_menor_morada"),
               conservadora_menor_morada = linha.get("conservadora_menor_morada"),
               unidade_intermediaria_morada = linha.get("unidade_intermediaria_morada"),
               conservadora_intermediaria_morada = linha.get("conservadora_intermediaria_morada"),
               unidade_maior_morada = linha.get("unidade_maior_morada"),
               conservadora_maior_morada = linha.get("conservadora_maior_morada"),
               point_morada = linha.get("point_morada"),
               edicao_filologica_parcial = linha.get("edicao_filologica_parcial"),
               autoria_edicao_conservadora = linha.get("autoria_edicao_conservadora"),
               autoria_edicao_modernizada = linha.get("autoria_edicao_modernizada"),
               responsabilidade_revisao_parcial = linha.get("responsabilidade_revisao_parcial"),
               ligacao_edicao_filologica = linha.get("ligacao_edicao_filologica"),
               rede_documental = linha.get("rede_documental"),
               terceira_referida = linha.get("terceira_referida"),
               trabalhos_andamento = linha.get("trabalhos_andamento"),
               trabalhos_derivados = linha.get("trabalhos_derivados"),
               tema = linha.get("tema"),
               subtema = linha.get("subtema"),
               informacoes_internas = linha.get("informacoes_internas"),
               link_gdrive = linha.get("link_gdrive"),
               gx_media_links = linha.get("gx_media_links"),
               colaboracao = linha.get("colaboracao"),
               creditos_imagem = linha.get("creditos_imagem"),
               responsavel_documento = linha.get("responsavel_documento"),
               data_edicao_documento = linha.get("data_edicao_documento"),
               publicar = linha.get("publicar"),
               tipo_documento = linha.get("tipo_documento"),
               subtipo_documento = linha.get("subtipo_documento"),
               ano_inferencia = linha.get("ano_inferencia"),
               cronologica_inicial_inferencia = linha.get("cronologica_inicial_inferencia"),
               cronologica_final_inferencia = linha.get("cronologica_final_inferencia"),
               perfil_documental = linha.get("perfil_documental"),
               arquivo_guarda = linha.get("arquivo_guarda"),
               estado_civil = linha.get("estado_civil"),
            )

        documentos = Documento.objects.all()
        for documento in documentos:
            nomes_importados.append(f" {documento.id} {documento.codigo_antes}")

        texto = str("Os seguintes documentos foram importadas:\n\n" + "\n".join(nomes_importados))
        messages.success(request, texto)


    return render(request, 'app/importar_documentos_csv.html')