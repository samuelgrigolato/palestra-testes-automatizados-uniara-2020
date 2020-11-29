from datetime import date
from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)


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


@app.route('/ping', methods=['GET'])
def ping():
  return '', 204


def calcular_desconto(valor_em_centavos, dia_referencia):
  porcentagem = 0
  if valor_em_centavos >= 500:
    porcentagem = 0.1
  dia_da_semana = dia_referencia.weekday()
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
      "desconto": calcular_desconto(produto[2], date.today()) / 100
    }
    for produto in produtos
  ])
