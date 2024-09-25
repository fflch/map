from django import forms
from .models import *


class CatalogadaForm(forms.ModelForm):

    class Meta:
        model = Catalogada
        fields = ('nome_modernizado', 'grafia_conservadora', 'trecho_nomeacao', 'trecho_voz',
                  'perfil_documental', 'detalhamento_perfil','unidade_menor_nascimento',
                  'conservadora_menor_nascimento', 'unidade_intermediaria_nascimento',
                  'conservadora_intermediaria_nascimento','unidade_maior_nascimento', 'conservadora_maior_nascimento',
                  'point_nascimento', 'total_filhas', 'total_filhos', 'nome_filhs_modernizado',
                  'referencia_dmb', 'trecho_bibliografia', 'fonte_bibliografia', 'informacoes_internas',
                  'publicar')


class DocumentoForm(forms.ModelForm):

    class Meta:
        model = Documento
        fields = ('tipo_documento', 'subtipo_documento', 'ano_escrita', 'ano_inferencia',
                  'datacao_cronologica_inicial', 'cronologica_inicial_inferencia', 'datacao_cronologica_final',
                  'cronologica_final_inferencia', 'descricao_conteudo_documento', 'descricao_materia_documento',
                  'rede_documental', 'unidade_menor_escrita', 'autoria_documento',
                  'autoria_institucional', 'autoria_material', 'arquivo_guarda', 'chave_pesquisa',
                  'condicao_documento', 'indexador_fonte', 'url_fonte', 'idade_catalogada_documento',
                  'estado_civil', 'qualificacao_social_documento','conservadora_menor_escrita',
                  'unidade_intermediaria_escrita', 'conservadora_intermediaria_escrita',
                  'unidade_maior_escrita', 'conservadora_maior_escrita', 'point_escrita',
                  'unidade_menor_morada', 'conservadora_menor_morada', 'unidade_intermediaria_morada',
                  'conservadora_intermediaria_morada', 'unidade_maior_morada', 'conservadora_maior_morada',
                  'point_morada', 'edicao_filologica_parcial', 'autoria_edicao_conservadora',
                  'autoria_edicao_modernizada','responsabilidade_revisao_parcial', 'data_revisao',
                  'ligacao_edicao_filologica', 'terceira_referida',
                  'trabalhos_andamento', 'trabalhos_derivados', 'tema', 'subtema',
                  'link_gdrive', 'gx_media_links', 'informacoes_internas', 'publicar')


class UserForm(forms.ModelForm):
    pass


