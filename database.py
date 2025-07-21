from tinydb import TinyDB, Query

class MercadoRepositorio:
    def __init__(self, db_path='db.json'):
        self.db = TinyDB(db_path, indent=4, ensure_ascii=False)
        self.tabela_produtos = self.db.table('produtos')
        self.tabela_vendas = self.db.table('vendas')

    # METODOS DO REPO

    def adicionar_produto(self, produto_dict):
        produto_limpo = {k: v for k, v in produto_dict.items() if v is not None and k != 'doc_id'}
        if produto_limpo.get('nome'):
            return self.tabela_produtos.insert(produto_limpo)
        return None

    def listar_produtos(self):
        return self.tabela_produtos.all()

    def buscar_produto_por_id(self, doc_id):
        produto = self.tabela_produtos.get(doc_id=doc_id)
        if produto:
            produto['doc_id'] = doc_id
        return produto

    def atualizar_estoque(self, doc_id, quantidade_comprada):
        produto = self.buscar_produto_por_id(doc_id)
        if produto and produto.get('estoque', 0) >= quantidade_comprada:
            novo_estoque = produto['estoque'] - quantidade_comprada
            self.tabela_produtos.update({'estoque': novo_estoque}, doc_ids=[doc_id])
            return True
        return False
    
    def atualizar_produto(self, doc_id, data):
        self.tabela_produtos.update(data, doc_ids=[doc_id])

    def deletar_produto(self, doc_id):
        self.tabela_produtos.remove(doc_ids=[doc_id])

    def registrar_venda(self, venda_dict):
        self.tabela_vendas.insert(venda_dict)

    def listar_vendas(self):
        """ Retorna todas as vendas registradas. """
        return self.tabela_vendas.all()
