import pytest
from freezegun import freeze_time
from datetime import date
from app import calcular_desconto, abrir_conexao


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
  assert desconto == pytest.approx(75)


def test_ping(client):
  resposta = client.get('/ping')
  assert resposta.status_code == 204


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
