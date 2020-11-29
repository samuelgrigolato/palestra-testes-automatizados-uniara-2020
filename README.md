# Testes automatizados

Código-fonte construído durante a apresentação da palestra "Testes automatizados - O que são e um exemplo prático com Python, Flask e Pytest".

Link p/ o vídeo completo: https://www.youtube.com/watch?v=pkpSKoq09cU

Link p/ a apresentação: https://docs.google.com/presentation/d/1j_obQoPOe7Zb41CHttoIrmP4oqYKYCGK8Y9RcMa8eVQ/edit?usp=sharing

## Passo a passo da parte prática

Siga as instruções abaixo em um diretório vazio para replicar a parte prática da palestra. Note que o roteiro assume que algumas coisas estão disponíveis no seu sistema operacional, sendo elas:

- Python 3 (incluindo a ferramenta de gestão de pacotes `pip`).
- Cliente de linha de comando `sqlite3` para interface com o banco de dados.
- Node.js (incluindo a ferramenta de gestão de pacotes `npm`).
- Navegador Firefox usado nos testes E2E.
- Utilitário `geckodriver` usado pela biblioteca Selenium para controle remoto do navegador Firefox.
- Utilitário de linha de comando `curl` para execução de requisições HTTP.

Acesse o site das respectivas ferramentas para instruções de instalação compatíveis com o seu sistema operacional. Todos os exemplos assumem um terminal Bash à disposição, portanto será necessário adaptá-los para funcionar em outros ambientes.

### Descrição do que será desenvolvido

O escopo desta prática é uma página de produtos, mostrando nome do produto e o valor de venda. O valor de venda pode sofrer desconto seguindo as regras abaixo:

- 10% de desconto se o valor for maior ou igual a R$ 5,00.
- 5% de desconto se o usuário estiver acessando o site entre terça e quinta (inclusive).

Note que as regras de desconto são acumulativas.

O foco do desenvolvimento está na cobertura das partes com testes unitários e de integração/E2E.

O trabalho será dividido em 3 grandes fases:

1. Back end (API usando Python, Flask e Pytest)
2. Front end (usando React)
3. E2E (usando script Bash e Selenium)

Execute os passos em um diretório vazio.

### Back end

Comece criando um diretório chamado `back`:

```
mkdir back
```

Acesse o diretório e prepare um ambiente virtual isolado usando o módulo `venv` do Python 3:

```
cd back
python -m venv venv
source venv/bin/activate
```

Nota: se você sair do terminal ou abrir outro, terá que repetir o comando `source venv/bin/activate` para voltar a trabalhar dentro do ambiente virtual.

Instale agora o micro web framework `flask`:

```
pip install flask flask-cors
```

Abra o diretório `back` no editor de sua preferência, e crie um arquivo chamado `app.py` com o seguinte conteúdo:

```python
from flask import Flask, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


@app.route('/ping', methods=['GET'])
def ping():
  return '', 204


@app.route('/produtos', methods=['GET'])
def produtos():
  return jsonify([
    {
      "id": 1,
      "nome": "Lápis",
      "valor": 4.5,
      "desconto": 0
    }
  ])
```

Execute o servidor no modo de desenvolvimento utilizando o seguinte comando:

```
python -m flask run
```

Em um outro terminal, execute as seguintes chamadas `curl` para verificar se deu tudo certo:

```
$ curl -v http://localhost:5000/ping
[...]
< HTTP/1.0 204 NO CONTENT
[...]

$ curl http://localhost:5000/produtos | jq
[...]
[
  {
    "desconto": 0,
    "id": 1,
    "nome": "Lápis",
    "valor": 4.5
  }
]
```

Nota: não é obrigatório o uso do utilitário `jq`, mas com ele a saída vem formatada resultando em uma visualização mais agradável.

Ainda no arquivo `app.py`, dinamize a saída usando uma base de dados `sqlite3`. Comece adicionando um evento responsável por inicializar a base com a tabela de produtos antes da primeira requisição servida pela API:

```python
import sqlite3

# ...

@app.before_first_request
def init_db():
  arquivo_db = app.config.get('ARQUIVO_BD', 'app.db')
  conexao = sqlite3.connect(arquivo_db)
  conexao.execute('''
    create table if not exists produtos (
      id integer primary key,
      nome text not null,
      valor_em_centavos integer not null
    );
  ''')

# ...
```

Reinicie o servidor e teste novamente uma das chamadas `curl`. Um arquivo `app.db` deve aparecer na pasta `back` e nenhum erro deve acontecer.

Utilizando o utilitário `sqlite3` insira alguns produtos na tabela criada:

```
$ sqlite3 app.db
SQLite version 3.33.0 2020-08-14 13:23:32
Enter ".help" for usage hints.
sqlite> insert into produtos (id, nome, valor_em_centavos) values (1, 'Lápis', 350);
sqlite> insert into produtos (id, nome, valor_em_centavos) values (2, 'Mesa', 70000);
```

Volte no app.py e finalize a implementação do método `produtos`:

```python
# ...

def abrir_conexao():
  arquivo_db = app.config.get('ARQUIVO_BD', 'app.db')
  return sqlite3.connect(arquivo_db)


@app.before_first_request
def init_db():
  conexao = abrir_conexao()
  conexao.execute('''
    create table if not exists produtos (
      id integer primary key,
      nome text not null,
      valor_em_centavos integer not null
    );
  ''')

# ...

@app.route('/produtos', methods=['GET'])
def produtos():
  conexao = abrir_conexao()

  produtos = conexao.execute('''
    select id, nome, valor_em_centavos
    from produtos
    order by nome
  ''')

  return jsonify([
    {
      "id": produto[0],
      "nome": produto[1],
      "valor": produto[2] / 100,
      "desconto": 0
    }
    for produto in produtos
  ])
```

Execute novamente o `curl` de busca de produtos.

O próximo passo é implementar o cálculo de desconto:

```python
# ...

def calcular_desconto(valor_em_centavos):
  porcentagem = 0
  if valor_em_centavos >= 500:
    porcentagem = 0.1
  hoje = date.today()
  dia_da_semana = hoje.weekday()
  if dia_da_semana >= 1 and dia_da_semana <= 3:
    porcentagem += 0.05
  return valor_em_centavos * porcentagem


@app.route('/produtos', methods=['GET'])
def produtos():
  conexao = abrir_conexao()

  produtos = conexao.execute('''
    select id, nome, valor_em_centavos
    from produtos
    order by nome
  ''')

  return jsonify([
    {
      "id": produto[0],
      "nome": produto[1],
      "valor": produto[2] / 100,
      "desconto": calcular_desconto(produto[2]) / 100
    }
    for produto in produtos
  ])
```

Agora é possível começar a cobrir este código com testes. Dê uma olhada no método `calcular_desconto`. Ele possui muitas regras de negócio, então é um bom candidato para começarmos. Instale a biblioteca `pytest`:

```
pip install pytest
```

Crie um arquivo `app_test.py` com o seguinte código:

```python
from app import calcular_desconto


def test_calcular_desconto_valor_200():
  desconto = calcular_desconto(200)
  assert desconto == 0.0 # ou 0.0 dependendo do dia :(
```

Teste com o comando `pytest` no terminal.

Obviamente não é aceitável uma automatização que só funciona em dias específicos da semana. Como resolver? O problema é que o conceito de dia atual é um efeito colateral da função `calcular_desconto`, que hoje não é pura. O jeito mais fácil e recomendado de resolver é transformar o dia de referência um parâmetro da função. Comece alterando no arquivo `app.py`:

```python
# ...

def calcular_desconto(valor_em_centavos, dia_referencia):
  porcentagem = 0
  if valor_em_centavos >= 500:
    porcentagem = 0.1
  dia_da_semana = dia_referencia.weekday()
  if dia_da_semana >= 1 and dia_da_semana <= 3:
    porcentagem += 0.05
  return valor_em_centavos * porcentagem

# ...
  return jsonify([
    {
      "id": produto[0],
      "nome": produto[1],
      "valor": produto[2] / 100,
      "desconto": calcular_desconto(produto[2], date.today()) / 100
    }
    for produto in produtos
  ])
# ...
```

E por fim no `app_test.py`:

```python
from datetime import date
from app import calcular_desconto


def test_calcular_desconto_valor_200_segunda_feira():
  desconto = calcular_desconto(200, date(2000, 1, 3))
  assert desconto == 0.0


def test_calcular_desconto_valor_200_terca_feira():
  desconto = calcular_desconto(200, date(2000, 1, 4))
  assert desconto == 10.0


def test_calcular_desconto_valor_500_segunda_feira():
  desconto = calcular_desconto(500, date(2000, 1, 3))
  assert desconto == 50.0


def test_calcular_desconto_valor_500_terca_feira():
  desconto = calcular_desconto(500, date(2000, 1, 4))
  assert desconto == 75.0
```

O problema da data atual foi resolvido, mas o último caso de teste continua não funcionando. Matemática com pontos flutuantes em computação é sempre complicada, e este é um exemplo do que pode acontecer. Via de regra não se deve verificar igualdade de ponto flutuante utilizando `==`, mas sim testando a diferença absoluta dos dois números, dessa forma:

```python
def test_calcular_desconto_valor_500_terca_feira():
  desconto = calcular_desconto(500, date(2000, 1, 4))
  assert abs(75.0 - desconto) < 0.001
```

Essa prática é tão comum que o próprio `pytest` (e qualquer framework de testes que se preze) fornece um utilitário:

```python
import pytest

# ...

def test_calcular_desconto_valor_500_terca_feira():
  desconto = calcular_desconto(500, date(2000, 1, 4))
  assert desconto == pytest.approx(75)
```

Dica: suba o servidor novamente e teste o comando `curl` antes de prosseguir.

E como testar a camada das requisições HTTP? Felizmente o Flask possui um bom suporte para testes. O primeiro passo é criar uma `fixture` do Pytest capaz de efetuar requisições à aplicação Flask. Para isso crie um arquivo `conftest.py` com o seguinte conteúdo:

```python
import pytest

from app import app


@pytest.fixture
def client():
  app.config['TESTING'] = True
  with app.test_client() as client:
    yield client
```

E adicione o seguinte caso de teste no arquivo `app_test.py`:

```python
def test_ping(client):
  resposta = client.get('/ping')
  assert resposta.status_code == 204
```

Mas e o endpoint que retorna produtos? Ele possui a complicação de depender do banco de dados. Testes automatizados só são úteis se forem fácil de executar repetidamente, e ter que preparar a base de dados manualmente antes de cada execução não é muito compatível com esse princípio.

A abordagem será outra. O pytest irá criar e inicializar uma base de dados nova para cada caso de teste. Assim cada caso de teste pode inserir os dados que precisa para a chamada que está sendo testada, e nada além disso.

Faça as seguintes alterações no arquivo `conftest.py`:

```python
import os
import tempfile
import pytest

from app import app, init_db


@pytest.fixture
def client():
  fd, caminho = tempfile.mkstemp()
  app.config['ARQUIVO_BD'] = caminho
  app.config['TESTING'] = True

  with app.test_client() as client:
    with app.app_context():
      init_db()
    yield client

  os.close(fd)
  os.unlink(caminho)
```

E escreva o seguinte caso de teste no arquivo `app_test.py`:

```python
def test_produtos(client):
  with abrir_conexao() as conexao:
    conexao.execute('''
      insert into produtos (id, nome, valor_em_centavos)
      values (1, 'Papel', 230);
    ''')
  resposta = client.get('/produtos')
  assert resposta.status_code == 200
  assert resposta.json == [
    {
      "id": 1,
      "nome": "Papel",
      "valor": 2.3,
      "desconto": pytest.approx(0.0) # depende do dia :(
    }
  ]
```

Novamente existe o problema do efeito colateral na chamada `date.today()`. Dessa vez é mais difícil resolver via passagem de parâmetros, então é necessário uma outra solução. Para este problema específico existe uma biblioteca python chamada `freezegun`, capaz de *mocar* várias funções nativas relacionadas com o horário atual do sistema. Comece instalando a biblioteca:

```
pip install freezegun
```

E decorando o caso de teste que precisa de data fixa:

```python
# ...
from freezegun import freeze_time

# ...
@freeze_time('2000-01-04')
def test_produtos(client):
  with abrir_conexao() as conexao:
    conexao.execute('''
      insert into produtos (id, nome, valor_em_centavos)
      values (1, 'Papel', 230);
    ''')
  resposta = client.get('/produtos')
  assert resposta.status_code == 200
  assert resposta.json == [
    {
      "id": 1,
      "nome": "Papel",
      "valor": 2.3,
      "desconto": pytest.approx(0.115)
    }
  ]
```

### Front end

Volte para a pasta inicial (saindo da pasta `back`) e crie um projeto em branco usando `create-react-app`:

```
npx create-react-app front
```

Navegue para dentro do diretório `front` e execute o seguinte comando para testar se deu certo:

```
npm start
```

A página de boas-vindas do CRA deve aparecer no seu navegador.

Execute também a suíte de teste que foi criada junto com o projeto:

```
npm test
```

Abra o diretório `front` no seu editor e abra o arquivo `src/App.test.js` e veja seu conteúdo. Abra agora o arquivo `src/App.js` e modifique-o para mostrar a lista de produtos do back end:

```js
import { useEffect, useState } from 'react';


function App() {
  const [ produtos, setProdutos ] = useState([]);

  useEffect(() => {
    (async () => {
      const resposta = await fetch('http://localhost:5000/produtos');
      const produtos = await resposta.json();
      setProdutos(produtos);
    })();
  }, []);

  return (
    <ul>
      {produtos.map(produto => (
        <li key={produto.id}>
          {produto.nome} (R$ {produto.valor - produto.desconto})
        </li>
      ))}
    </ul>
  );
}

export default App;
```

Nota: lembre-se de deixar o back end rodando antes de testar o front end.

Se você testar agora o comando `npm test` vai reparar que o teste obviamente quebrou, pois o componente `App` foi completamente modificado. Na tentativa de resolver, no entanto, você vai se deparar com um problema bem chato: como garantir a lista de produtos retornada pela API?

A resposta é que estes testes, chamados de integração/E2E, são complicados de escrever/executar e devem compor a menor parte dos esforços, sendo que a grande maioria pode ser escrita sem se preocupar com serviços externos. Neste caso é possível resolver extraindo a renderização dos produtos para um componente chamado `Produtos`. Comece criando um arquivo chamado `Produtos.js` com o seguinte conteúdo:

```js

function Produtos ({ produtos }) {
  return (
    <ul>
      {produtos.map(produto => (
        <li key={produto.id}>
          {produto.nome} (R$ {produto.valor - produto.desconto})
        </li>
      ))}
    </ul>
  );
}


export default Produtos;
```

E ajustando o `App.js`:

```js
import { useEffect, useState } from 'react';
import Produtos from './Produtos';


function App() {
  const [ produtos, setProdutos ] = useState([]);

  useEffect(() => {
    (async () => {
      const resposta = await fetch('http://localhost:5000/produtos');
      const produtos = await resposta.json();
      setProdutos(produtos);
    })();
  }, []);

  return (
    <Produtos produtos={produtos} />
  );
}

export default App;
```

Dica: antes de continuar garanta que a aplicação esteja funcionando.

O próximo passo é renomear o arquivo `App.test.js` para `Produtos.test.js` e ajustar o teste dentro dele:

```js
import { render, screen } from '@testing-library/react';
import Produtos from './Produtos';

test('renderiza um produto', () => {
  const produtos = [
    {
      "id": 1,
      "nome": "Monitor",
      "valor": 3510.99,
      "desconto": 5.00
    }
  ];
  render(<Produtos produtos={produtos} />);
  const elemento = screen.getByText('Monitor (R$ 3505.99)');
  expect(elemento).toBeInTheDocument();
});
```

O que foi feito aqui é basicamente a criação de um componente puro (Produtos) facilmente testável. Note que mais uma vez a escrita de testes promove escrita de código com maior qualidade.
