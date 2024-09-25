from django.shortcuts import render, get_object_or_404
from .forms import CatalogadaForm, DocumentoForm
from .models import Catalogada, Documento
from django.utils import timezone
from django.shortcuts import redirect
import xml.etree.ElementTree as xml
import re


def home(request):
    return render(request, 'app/home.html')


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


def descricao(request, pk):
    catalogada = get_object_or_404(Catalogada, pk=pk)
    catalogada_form = CatalogadaForm(instance=catalogada)
    #responsavel_catalogacao = catalogada.processamento.filter(
        #catalogada__pk=catalogada.pk).first().responsavel_catalogacao
    #print(responsavel_catalogacao)
    return render(request, 'app/descricao.html', {'catalogada_form': catalogada_form, 'catalogada': catalogada})


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

def pesquisar(request, pk):
    catalogada = get_object_or_404(Catalogada, pk=pk)
    return render(request, 'app/resultado.html', {'catalogada': catalogada})


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


def gerar_xml(request, pk):
    catalogada = get_object_or_404(Catalogada, pk=pk)
    print("gerar xml")

    root = xml.Element("root")
    ct = xml.Element("catalogada")
    root.append(ct)
    name = xml.SubElement(ct, "Nome")
    name.text = catalogada.nome_modernizado

    codigo = xml.SubElement(ct, "Codigo")
    codigo.text = catalogada.codigo

    nome = catalogada.nome_modernizado + ".xml"

    tree = xml.ElementTree(root)
    with open(nome, "wb") as files:
        tree.write(files)
    print("Xml salvo")

    return redirect('catalogadas')
