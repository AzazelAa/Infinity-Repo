import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os
import re

# Configuração da página Web
st.set_page_config(page_title="Gerador - Infinity Elétrica", layout="wide")

# Inicializa a lista de itens na memória do navegador
if 'lista_itens' not in st.session_state:
    st.session_state.lista_itens = []

st.title("Gerador de Orçamentos - Infinity Elétrica")

# Divide a tela em duas colunas
col1, col2 = st.columns(2)

with col1:
    st.header("Dados do Cliente e Projeto")
    numero_orc = st.text_input("Nº do Orçamento (Ex: 038/2026)")
    cliente = st.text_input("Nome da Empresa (Ex: Vuteq do Brasil)")
    cnpj = st.text_input("CNPJ da Empresa")
    endereco = st.text_input("Endereço da Empresa")
    projeto = st.text_input("Nome / Local do Projeto")
    contato_nome = st.text_input("Nome do Contato")
    setor = st.text_input("Setor do Contato (Ex: TI, Manutenção)")
    contato_tel = st.text_input("Telefone do Contato")
    ddl_pagamento = st.text_input("Condição de Pagamento (Ex: 30 DDL)")
    prazo = st.text_input("Prazo de Execução (Ex: 15 dias úteis)")

with col2:
    st.header("Adicionar Itens")
    
    # Organizando Tipo e Quantidade lado a lado
    col_tipo, col_qtd = st.columns([2, 1])
    with col_tipo:
        tipo = st.selectbox("Tipo de Item", ["Serviço", "Material", "Equipamento"])
    with col_qtd:
        qtd_item = st.number_input("Quantidade", min_value=1, value=1, step=1)
        
    nome_item = st.text_input("Nome do Item")
    desc_item = st.text_area("Descrição / Detalhes")
    valor_item = st.text_input("Valor Unitário (Ex: 1500,00)")
    
    if st.button("Adicionar à Lista", type="primary"):
        if nome_item and desc_item and valor_item:
            st.session_state.lista_itens.append({
                "tipo": tipo, "qtd": qtd_item, "nome": nome_item, "desc": desc_item, "valor": valor_item
            })
            st.success("Item adicionado!")
        else:
            st.warning("Preencha todos os campos do item (Nome, Descrição e Valor)!")
            
    st.subheader("Itens no Orçamento:")
    for i, item in enumerate(st.session_state.lista_itens):
        st.write(f"- **[{item['tipo']}]** {item['qtd']}x {item['nome']} | {item['desc']} : R$ {item['valor']} (Unitário)")
        
    if st.button("Limpar Lista"):
        st.session_state.lista_itens = []
        st.rerun()

st.divider()

# --- LÓGICA DE GERAÇÃO DO PDF ---
def gerar_pdf_bytes():
    data_atual = datetime.now().strftime("%d/%m/%Y")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    r_azul, g_azul, b_azul = 10, 50, 150
    
    # Cabeçalho
    if os.path.exists("logo.jpeg"):
        pdf.image("logo.jpeg", x=15, y=15, w=45)
        
    pdf.set_font("Arial", "", 11)
    pdf.set_xy(100, 18)
    pdf.cell(95, 6, txt="(19) 99801-4456", ln=True, align='R')
    pdf.set_x(100)
    pdf.cell(95, 6, txt="edmilson.martins01@gmail.com", ln=True, align='R')
    pdf.set_x(100)
    pdf.cell(95, 6, txt="CNPJ: 62.634.914/0001-61", ln=True, align='R')
    
    # Título
    pdf.set_y(65)
    pdf.set_font("Arial", "B", 24)
    pdf.set_text_color(r_azul, g_azul, b_azul)
    titulo_texto = f"ORÇAMENTO Nº {numero_orc}" if numero_orc else "ORÇAMENTO"
    pdf.cell(0, 10, txt=titulo_texto, ln=True)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 6, txt=f"Data: {data_atual}", ln=True)
    
    # Dados Cliente
    pdf.ln(8)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 8, txt="A/C:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, txt=f"Empresa: {cliente}", ln=True)
    pdf.cell(0, 6, txt=f"CNPJ: {cnpj}", ln=True)
    if endereco:
        pdf.cell(0, 6, txt=f"Endereço: {endereco}", ln=True)
    texto_contato = f"Contato: {contato_nome} (Setor: {setor})" if setor else f"Contato: {contato_nome}"
    pdf.cell(0, 6, txt=texto_contato, ln=True)
    pdf.cell(0, 6, txt=f"Telefone: {contato_tel}", ln=True)
    if projeto:
        pdf.ln(2)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 6, txt=f"Projeto / Local: {projeto}", ln=True)
    
    # Tabela de Itens (Cabeçalho Redesenhado com QTD)
    pdf.ln(12)
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(r_azul, g_azul, b_azul)
    
    y_linha = pdf.get_y()
    pdf.set_xy(15, y_linha)
    pdf.cell(20, 10, txt="TIPO", align='C')
    pdf.set_xy(35, y_linha)
    pdf.cell(10, 10, txt="QTD", align='C')
    pdf.set_xy(45, y_linha)
    pdf.cell(40, 10, txt="NOME", align='C')
    pdf.set_xy(85, y_linha)
    pdf.cell(75, 10, txt="DESCRIÇÃO", align='C')
    pdf.set_xy(160, y_linha)
    pdf.cell(35, 10, txt="VALOR TOTAL", align='C')
    
    # Desenha a linha inferior do cabeçalho
    pdf.line(15, y_linha + 10, 195, y_linha + 10)
    pdf.set_y(y_linha + 12)
    
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(0, 0, 0)
    
    total_orcamento = 0.0
    for item in st.session_state.lista_itens:
        # Prevenção de erro caso o item antigo não tenha QTD na memória
        qtd = int(item.get("qtd", 1))
        valor_total_item = 0.0
        
        try:
            valor_unit_calc = float(item["valor"].replace(".", "").replace(",", "."))
            valor_total_item = valor_unit_calc * qtd
            total_orcamento += valor_total_item
        except ValueError:
            pass 
        
        # Formata o valor total do item específico para exibir na linha
        valor_total_str = f"R$ {valor_total_item:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        # Se a linha for passar da página, cria uma nova folha
        if pdf.get_y() > 250:
            pdf.add_page()
            
        y_linha = pdf.get_y()
        
        # TIPO
        pdf.set_xy(15, y_linha)
        pdf.cell(20, 6, txt=item["tipo"], align='C')
        
        # QTD
        pdf.set_xy(35, y_linha)
        pdf.cell(10, 6, txt=str(qtd), align='C')
        
        # NOME (Quebra de linha)
        pdf.set_xy(45, y_linha)
        pdf.multi_cell(40, 6, txt=item["nome"], align='C')
        y_nome = pdf.get_y()
        
        # DESCRIÇÃO (Quebra de linha)
        pdf.set_xy(85, y_linha)
        pdf.multi_cell(75, 6, txt=item["desc"], align='L')
        y_desc = pdf.get_y()
        
        # VALOR TOTAL DO ITEM (Qtd * Valor Unitário)
        pdf.set_xy(160, y_linha)
        pdf.cell(35, 6, txt=valor_total_str, align='C')
        
        # Descobre qual foi o bloco de texto mais longo para desenhar a linha divisória abaixo dele
        y_maximo = max(y_linha + 6, y_nome, y_desc)
        
        # Linha inferior do item
        pdf.line(15, y_maximo + 2, 195, y_maximo + 2)
        pdf.set_y(y_maximo + 4)
    
    # Total Final
    pdf.ln(5)
    pdf.set_x(105) 
    pdf.set_fill_color(r_azul, g_azul, b_azul) 
    pdf.set_text_color(255, 255, 255) 
    pdf.set_font("Arial", "B", 14)
    total_formatado = f"{total_orcamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    pdf.cell(90, 12, txt=f"TOTAL: R$ {total_formatado}", fill=True, align='C', ln=True) 
    
    # Prazos e Condições
    pdf.ln(15)
    pdf.set_text_color(r_azul, g_azul, b_azul)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, txt="CONDIÇÕES COMERCIAIS", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 10)
    texto_pagamento = f"Forma de Pagamento: Boleto bancário - {ddl_pagamento}" if ddl_pagamento else "Forma de Pagamento: Boleto bancário (a combinar)"
    pdf.cell(0, 6, txt=texto_pagamento, ln=True)
    texto_prazo = f"Prazo de Execução: {prazo}" if prazo else "Prazo de Execução: A definir junto ao cliente."
    pdf.cell(0, 6, txt=texto_prazo, ln=True)
    pdf.cell(0, 6, txt="Validade: Este orçamento é válido por 30 dias.", ln=True)
    pdf.ln(3)
    pdf.set_font("Arial", "I", 9)
    pdf.multi_cell(0, 5, txt="Observação: O prazo poderá ser alterado caso surjam problemas não previstos durante a implementação ou necessidade de materiais não especificados.")
    
    # Rodapé
    pdf.ln(15)
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, txt="Gerado por Infinity", align='C', ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# Botão de Download Web
if len(st.session_state.lista_itens) > 0:
    pdf_bytes = gerar_pdf_bytes()
    
    cliente_seguro = re.sub(r'[^A-Za-z0-9 ]+', '', cliente).strip()
    cliente_seguro = cliente_seguro if cliente_seguro else "Cliente"
    numero_seguro = numero_orc.replace("/", "-").strip() if numero_orc else "S-N"
    nome_arquivo = f"Orcamento_{cliente_seguro}_{numero_seguro}.pdf".replace(" ", "_")
    
    st.download_button(
        label="Gerar e Baixar PDF Profissional",
        data=pdf_bytes,
        file_name=nome_arquivo,
        mime="application/pdf",
        type="primary"
    )
else:
    st.info("Adicione pelo menos um item na lista para poder gerar o PDF.")
