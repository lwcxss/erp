# Sistema de Mercadinho com Banco de Dados Não Relacional

## Visão Geral do Projeto

Este projeto foi desenvolvido para a disciplina de **Aspectos de Implementação de Banco de Dados**. O objetivo é apresentar uma demonstração prática de um sistema de Ponto de Venda (PDV) que utiliza um banco de dados não relacional (NoSQL) para gerenciar as operações de um pequeno mercado.

A aplicação foi construída em Python, com uma interface web interativa desenvolvida com a biblioteca Streamlit.

## O Banco de Dados Não Relacional: TinyDB

A escolha central do projeto foi utilizar um banco de dados não relacional para a persistência dos dados. Para isso, empregamos o **TinyDB**, um banco de dados NoSQL leve e serverless que armazena as informações em um único arquivo JSON.

O TinyDB opera com base em conceitos muito similares aos de bancos de dados de documentos mais robustos, como o **MongoDB**:

* **Coleções:** Os dados são organizados em "tabelas" chamadas de coleções. Neste projeto, temos uma coleção para `produtos` e outra para `vendas`.
* **Documentos:** Cada registro é um "documento" (um objeto JSON), o que nos oferece grande flexibilidade de esquema. Por exemplo, um documento de `venda` pode conter uma lista aninhada de produtos, representando um carrinho de compras de forma natural e intuitiva.

Essa abordagem é ideal para o nosso caso de uso, pois o formato de documento se alinha perfeitamente com os objetos que manipulamos na aplicação, simplificando as operações de leitura e escrita sem a necessidade de joins complexos.

## Funcionalidades do Sistema

O sistema de mercadinho oferece as seguintes utilidades:

* 🛒 **Ponto de Venda (PDV):** Uma interface web para selecionar produtos, adicionar a um carrinho e registrar uma nova venda.
* 📦 **Controle de Estoque:** O sistema atualiza o estoque de um produto automaticamente após a conclusão de uma venda. É possível visualizar o estoque de todos os itens.
* ➕ **Cadastro de Produtos:** Um formulário simples para adicionar novos produtos ao catálogo do mercado.
* 📊 **Persistência de Dados:** Todas as informações de produtos e vendas são salvas no arquivo `db.json`, garantindo que os dados não sejam perdidos ao fechar a aplicação.

## Tecnologias Utilizadas

* **Linguagem:** Python
* **Interface Web:** Streamlit
* **Banco de Dados:** TinyDB (NoSQL, baseado em documentos)

## Como Executar a Aplicação

Para rodar o projeto, siga os passos abaixo:

**1. Clone o Repositório**
```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd <NOME_DA_PASTA>
```

**2. Crie e Ative um Ambiente Virtual**
```bash
# Cria o ambiente
python -m venv venv

# Ativa o ambiente (Windows)
.\venv\Scripts\activate

# Ativa o ambiente (macOS/Linux)
source venv/bin/activate
```

**3. Instale as Dependências**
```bash
pip install -r requirements.txt
```

**4. Execute a Aplicação Web**
```bash
streamlit run app.py
```
Após executar este comando, uma aba será aberta no seu navegador com a aplicação funcionando.