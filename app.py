import streamlit as st
import pandas as pd
from database import MercadoRepositorio
import datetime

# --- CONFIGURAÇÃO DA PÁGINA E REPOSITÓRIO ---

st.set_page_config(page_title="Mercadinho PDV", page_icon="🛒", layout="wide")

repo = MercadoRepositorio()

# --- GERENCIAMENTO DE ESTADO (CARRINHO) ---

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'total_venda' not in st.session_state:
    st.session_state.total_venda = 0.0

# --- FUNÇÕES DAS PÁGINAS ---

def pagina_pdv():
    st.title("🛒 Ponto de Venda")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("Adicionar produtos")
        produtos = repo.listar_produtos()
        
        if not produtos:
            st.warning("Nenhum produto cadastrado. Adicione produtos na página 'Adicionar Produto'.")
            return

        nomes_produtos = {p['nome']: p.doc_id for p in produtos}
        produto_selecionado_nome = st.selectbox("Selecione um produto", options=nomes_produtos.keys())
        
        produto_id = nomes_produtos[produto_selecionado_nome]
        produto_obj = repo.buscar_produto_por_id(produto_id)

        st.info(f"Estoque disponível de {produto_obj['nome']}: **{produto_obj['estoque']}**")
        
        quantidade = st.number_input("Quantidade", min_value=1, max_value=int(produto_obj['estoque']), value=1, step=1)

        if st.button("➕ Adicionar ao Carrinho"):
            if quantidade > 0:
                item_venda = {
                    'produto_id': produto_id,
                    'nome_produto': produto_obj['nome'],
                    'quantidade': quantidade,
                    'preco_unitario': produto_obj['preco'],
                    'subtotal': produto_obj['preco'] * quantidade
                }
                st.session_state.carrinho.append(item_venda)
                st.session_state.total_venda += item_venda['subtotal']
                st.rerun()
            else:
                st.error("A quantidade deve ser maior que zero.")

    with col2:
        st.header("Carrinho")
        if not st.session_state.carrinho:
            st.info("O carrinho está vazio.")
        else:
            df_carrinho = pd.DataFrame(st.session_state.carrinho)
            st.dataframe(df_carrinho[['nome_produto', 'quantidade', 'preco_unitario', 'subtotal']],
                         hide_index=True)
            
            st.subheader(f"Total: R$ {st.session_state.total_venda:.2f}")

            if st.button("💰 Finalizar Compra", use_container_width=True, type="primary"):
                venda_final = {
                    'data_venda': datetime.datetime.now().isoformat(),
                    'itens': st.session_state.carrinho,
                    'total_venda': st.session_state.total_venda
                }
                for item in st.session_state.carrinho:
                    repo.atualizar_estoque(item['produto_id'], item['quantidade'])
                
                repo.registrar_venda(venda_final)

                st.success("Venda registrada com sucesso!")
                
                st.session_state.carrinho = []
                st.session_state.total_venda = 0.0
                
                st.balloons()
                import time
                time.sleep(2)
                st.rerun()

def pagina_estoque():
    st.title("📦 Estoque de Produtos")
    
    produtos = repo.listar_produtos()
    if not produtos:
        st.warning("Nenhum produto cadastrado.")
        return
        
    df = pd.DataFrame(produtos)
    
    df['id'] = [p.doc_id for p in produtos]
    
    df = df[['id', 'nome', 'preco', 'estoque']]
    
    st.dataframe(df, hide_index=True, use_container_width=True)

def pagina_adicionar_produto():
    st.title("➕ Adicionar Novo Produto")

    with st.form("novo_produto_form", clear_on_submit=True):
        nome = st.text_input("Nome do Produto", placeholder="Ex: Refrigerante Lata 350ml")
        preco = st.number_input("Preço (R$)", min_value=0.01, format="%.2f")
        estoque = st.number_input("Quantidade em Estoque", min_value=0, step=1)
        
        submitted = st.form_submit_button("Cadastrar Produto")
        
        if submitted:
            if not nome:
                st.error("O nome do produto é obrigatório.")
            else:
                novo_produto = {"nome": nome, "preco": preco, "estoque": estoque}
                repo.adicionar_produto(novo_produto)
                st.success(f"Produto '{nome}' adicionado com sucesso!")

# --- NAVEGAÇÃO PRINCIPAL (SIDEBAR) ---

st.sidebar.title("Navegação")
pagina_selecionada = st.sidebar.radio("Escolha uma página", ["Ponto de Venda", "Ver Estoque", "Adicionar Produto"])

if pagina_selecionada == "Ponto de Venda":
    pagina_pdv()
elif pagina_selecionada == "Ver Estoque":
    pagina_estoque()
elif pagina_selecionada == "Adicionar Produto":
    pagina_adicionar_produto()