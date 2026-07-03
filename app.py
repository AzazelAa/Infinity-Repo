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

# Divide a tela em duas colunas (Esquerda = Cliente / Direita = Itens)
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
    tipo = st.selectbox("Tipo de Item", ["Serviço", "Material", "Equipamento"])
    nome_item = st.text_input("Nome do Item")
    desc_item = st.text_area("Descrição / Detalhes")
    valor_item = st.text_input("Valor (Ex: 1500,00)")
    
    if st.button("Adicionar à Lista", type="primary"):
        if nome_item and desc_item and valor_item:
            st.session_state.lista_itens.append({
                "tipo": tipo, "nome": nome_item, "desc": desc_item, "valor": valor_item
            })
            st.success("Item adicionado!")
        else:
            st.warning("Preencha todos os campos do item (Nome, Descrição e Valor)!")
            
    st.subheader("Itens no Orçamento:")
    for i, item in enumerate(st.session_state.lista_itens):
        st.write(f"- **[{item['tipo']}]** {item['nome']} | {item['desc']} : R$ {item['valor']}")
        
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
    
    # Tabela de Itens
    pdf.ln(12)
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(r_azul, g_azul, b_azul)
    pdf.cell(25, 10, txt="TIPO", border='B', align='C')
    pdf.cell(45, 10, txt="NOME", border='B', align='C')
    pdf.cell(80, 10, txt="DESCRIÇÃO", border='B', align='C')
    pdf.cell(30, 10, txt="VALOR", border='B', align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(0, 0, 0)
    
    total_orcamento = 0.0
    for item in st.session_state.lista_itens:
        try:
            valor_calc = float(item["valor"].replace(".", "").replace(",", "."))
            total_orcamento += valor_calc
        except ValueError:
            pass 
        
        nome_curto = (item["nome"][:25] + '...') if len(item["nome"]) > 28 else item["nome"]
        desc_curta = (item["desc"][:45] + '...') if len(item["desc"]) > 48 else item["desc"]
        
        pdf.cell(25, 10, txt=item["tipo"], border='B', align='C')
        pdf.cell(45, 10, txt=nome_curto, border='B', align='C')
        pdf.cell(80, 10, txt=desc_curta, border='B', align='C')
        pdf.cell(30, 10, txt=f"R$ {item['valor']}", border='B', align='C')
        pdf.ln(10)
    
    # Total
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
    
    # Salva em memória (não no disco) para o download na web
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