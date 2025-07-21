import streamlit as st
import pandas as pd
from database import MercadoRepositorio
import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA E REPOSITÓRIO ---

st.set_page_config(page_title="Mercadinho PDV", page_icon="🛒", layout="wide")

repo = MercadoRepositorio()

# --- GERENCIAMENTO DE ESTADO (CARRINHO E DADOS) ---

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
        if produto_selecionado_nome:
            produto_id = nomes_produtos[produto_selecionado_nome]
            produto_obj = repo.buscar_produto_por_id(produto_id)
            st.info(f"Estoque disponível de {produto_obj['nome']}: **{produto_obj['estoque']}**")
            max_estoque = int(produto_obj.get('estoque', 0))
            if max_estoque > 0:
                quantidade = st.number_input("Quantidade", min_value=1, max_value=max_estoque, value=1, step=1)
                if st.button("➕ Adicionar ao Carrinho"):
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
                st.error("Produto sem estoque.")

    with col2:
        st.header("Carrinho")
        if not st.session_state.carrinho:
            st.info("O carrinho está vazio.")
        else:
            for i, item in enumerate(st.session_state.carrinho):
                col_item, col_botao = st.columns([4, 1])
                with col_item:
                    st.text(f"{item['nome_produto']} (x{item['quantidade']})")
                    st.caption(f"Subtotal: R$ {item['subtotal']:.2f}")
                with col_botao:
                    if st.button("➖", key=f"remover_{i}", help="Remover item", use_container_width=True):
                        item_removido = st.session_state.carrinho.pop(i)
                        st.session_state.total_venda -= item_removido['subtotal']
                        st.rerun()
            
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
                st.balloons()
                
                st.session_state.carrinho = []
                st.session_state.total_venda = 0.0
                
                time.sleep(2)
                st.rerun()


def pagina_estoque():
    st.title("📦 Produtos e Estoque")
    produtos = repo.listar_produtos()
    
    if not produtos:
        st.warning("Nenhum produto cadastrado para exibir.")
        return

    df = pd.DataFrame(produtos)
    df['id'] = [p.doc_id for p in produtos]
    df = df[['id', 'nome', 'preco', 'estoque']]

    st.subheader("Filtros")
    col1, col2 = st.columns(2)

    with col1:
        precos = df['preco'].dropna()
        min_preco, max_preco = (float(precos.min()), float(precos.max())) if not precos.empty else (0.0, 100.0)
        
        filtro_preco = st.slider(
            "Filtrar por preço (R$):",
            min_value=min_preco,
            max_value=max_preco,
            value=(min_preco, max_preco)
        )
        df = df[(df['preco'] >= filtro_preco[0]) & (df['preco'] <= filtro_preco[1])]

    with col2:
        st.write("")
        st.write("")
        apenas_com_estoque = st.checkbox("Mostrar apenas produtos com estoque", value=True)
        if apenas_com_estoque:
            df = df[df['estoque'] > 0]

    st.dataframe(df, hide_index=True, use_container_width=True)
    
    if df.empty:
        st.info("Nenhum produto encontrado com os filtros aplicados.")


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

def pagina_db_control():
    st.title("⚙️ DB Control")
    
    # --- Seção de Produtos ---
    st.header("Gerenciador de Produtos")
    st.info("Adicione, edite ou remova produtos diretamente na tabela. Clique em 'Salvar' para aplicar as mudanças.")
    produtos = repo.listar_produtos()
    if produtos:
        df_produtos = pd.DataFrame(produtos)
        df_produtos['doc_id'] = [p.doc_id for p in produtos]
    else:
        df_produtos = pd.DataFrame(columns=['nome', 'preco', 'estoque', 'doc_id'])
    if 'df_original' not in st.session_state:
        st.session_state.df_original = df_produtos.copy()
    df_editado = st.data_editor(
        df_produtos,
        column_config={
            "doc_id": st.column_config.NumberColumn("ID do DB", disabled=True),
            "nome": st.column_config.TextColumn("Nome", required=True),
            "preco": st.column_config.NumberColumn("Preço (R$)", format="%.2f", required=True),
            "estoque": st.column_config.NumberColumn("Estoque", required=True)
        },
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic",
        key="data_editor"
    )
    if st.button("Salvar Alterações nos Produtos", type="primary"):
        original_ids = set(st.session_state.df_original['doc_id'].dropna())
        editado_ids = set(df_editado['doc_id'].dropna())
        ids_deletados = original_ids - editado_ids
        for doc_id in ids_deletados:
            repo.deletar_produto(int(doc_id))
        for record in df_editado.to_dict('records'):
            doc_id = record.get('doc_id')
            produto_data = {'nome': record.get('nome'), 'preco': record.get('preco'), 'estoque': record.get('estoque')}
            if pd.notna(doc_id):
                repo.atualizar_produto(int(doc_id), produto_data)
            else:
                repo.adicionar_produto(produto_data)
        st.success("Banco de dados de produtos atualizado!")
        del st.session_state.df_original
        time.sleep(1)
        st.rerun()

    st.divider()

    # --- Seção de Vendas ---
    st.header("Histórico de Vendas")
    vendas = repo.listar_vendas()
    if not vendas:
        st.info("Nenhum registro de venda encontrado.")
    else:
        vendas_ordenadas = sorted(vendas, key=lambda v: v.get('data_venda', ''), reverse=True)
        for venda in vendas_ordenadas:
            data_venda_dt = datetime.datetime.fromisoformat(venda['data_venda'])
            data_formatada = data_venda_dt.strftime("%d/%m/%Y às %H:%M:%S")
            total_venda = venda.get('total_venda', 0.0)

            with st.expander(f"Venda de {data_formatada} - Total: R$ {total_venda:.2f}"):
                itens_df_data = {
                    "Produto": [item['nome_produto'] for item in venda['itens']],
                    "Qtd.": [item['quantidade'] for item in venda['itens']],
                    "Preço Unit.": [f"R$ {item['preco_unitario']:.2f}" for item in venda['itens']],
                    "Subtotal": [f"R$ {item.get('subtotal', item['quantidade'] * item['preco_unitario']):.2f}" for item in venda['itens']]
                }
                itens_df = pd.DataFrame(itens_df_data)
                st.dataframe(itens_df, hide_index=True, use_container_width=True)

# --- NAVEGAÇÃO PRINCIPAL (SIDEBAR) ---
st.sidebar.title("Navegação")
pagina_selecionada = st.sidebar.radio(
    "Escolha uma página", 
    ["Ponto de Venda", "Produtos e Estoque", "Adicionar Produto", "DB Control"]
)
if pagina_selecionada == "Ponto de Venda":
    pagina_pdv()
elif pagina_selecionada == "Produtos e Estoque":
    pagina_estoque()
elif pagina_selecionada == "Adicionar Produto":
    pagina_adicionar_produto()
elif pagina_selecionada == "DB Control":
    pagina_db_control()
