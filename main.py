import datetime
from database import MercadoRepositorio

repo = MercadoRepositorio()

def popular_banco_inicial():
    if not repo.listar_produtos():
        print("\nBanco de dados vazio. Adicionando produtos iniciais...")
        repo.adicionar_produto({'nome': 'Água Mineral 500ml', 'preco': 2.50, 'estoque': 50})
        repo.adicionar_produto({'nome': 'Biscoito Recheado', 'preco': 4.00, 'estoque': 30})
        repo.adicionar_produto({'nome': 'Salgadinho 50g', 'preco': 5.50, 'estoque': 40})
        repo.adicionar_produto({'nome': 'Suco de Laranja 1L', 'preco': 7.00, 'estoque': 20})
        repo.adicionar_produto({'nome': 'Refrigerante Lata 350ml', 'preco': 4.50, 'estoque': 60})
        print("Produtos iniciais cadastrados!")

def adicionar_novo_produto():
    print("\n--- Adicionar Novo Produto ---")
    try:
        nome = input("Nome do produto: ")
        preco = float(input("Preço (ex: 5.50): "))
        estoque = int(input("Quantidade em estoque: "))

        novo_produto = {
            "nome": nome,
            "preco": preco,
            "estoque": estoque
        }
        repo.adicionar_produto(novo_produto)
        print("\nProduto adicionado com sucesso!")
    except ValueError:
        print("\nErro: Preço ou estoque em formato inválido. Use números.")

def listar_produtos():
    print("\n--- Lista de Produtos em Estoque ---")
    produtos = repo.listar_produtos()

    if not produtos:
        print("Nenhum produto cadastrado.")
        return

    print(f"{'ID':<5} | {'Nome':<25} | {'Preço':<10} | {'Estoque'}")
    print("-" * 55)
    
    for p in produtos:
        print(f"{p.doc_id:<5} | {p['nome']:<25} | R$ {p['preco']:.2f}{'':<4} | {p['estoque']}")

def registrar_venda():
    print("\n--- Registrar Nova Venda ---")
    listar_produtos()
    
    carrinho = []
    total_venda = 0.0

    while True:
        try:
            id_input = input("\nDigite o ID do produto para adicionar (ou 'fim' para finalizar): ")
            if id_input.lower() == 'fim':
                break

            produto_id = int(id_input)
            produto = repo.buscar_produto_por_id(produto_id)

            if not produto:
                print("Produto não encontrado.")
                continue

            quantidade = int(input(f"Quantidade de '{produto['nome']}': "))
            
            if quantidade <= 0:
                print("Quantidade deve ser positiva.")
                continue

            if produto['estoque'] < quantidade:
                print(f"Estoque insuficiente. Disponível: {produto['estoque']}")
                continue
            
            item_venda = {
                'produto_id': produto_id,
                'nome_produto': produto['nome'],
                'quantidade': quantidade,
                'preco_unitario': produto['preco']
            }
            carrinho.append(item_venda)

            subtotal = produto['preco'] * quantidade
            total_venda += subtotal
            print(f"Item adicionado! Subtotal do carrinho: R$ {total_venda:.2f}")

        except ValueError:
            print("ID ou quantidade inválida. Por favor, insira um número.")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")

    if carrinho:
        print("\n--- Finalizando Venda ---")
        print(f"Total da venda: R$ {total_venda:.2f}")
        confirmar = input("Confirmar venda? (s/n): ").lower()
        
        if confirmar == 's':
            for item in carrinho:
                repo.atualizar_estoque(item['produto_id'], item['quantidade'])

            venda_final = {
                'data_venda': datetime.datetime.now().isoformat(),
                'itens': carrinho,
                'total_venda': total_venda
            }
            repo.registrar_venda(venda_final)
            print("\nVenda registrada com sucesso!")
        else:
            print("\nVenda cancelada.")

def main():
    print("======================================")
    print("============ Mercadinho ==============")
    print("======================================")

    popular_banco_inicial()

    while True:
        print("\nEscolha uma opção:")
        print("1. Registrar Venda")
        print("2. Adicionar Novo Produto")
        print("3. Listar Todos os Produtos (Estoque)")
        print("4. Sair")
        
        opcao = input("Opção: ")

        if opcao == '1':
            registrar_venda()
        elif opcao == '2':
            adicionar_novo_produto()
        elif opcao == '3':
            listar_produtos()
        elif opcao == '4':
            break
        else:
            print("Opção inválida. Tente novamente.")
            
    print("\nObrigado por usar o sistema!")

if __name__ == "__main__":
    main()