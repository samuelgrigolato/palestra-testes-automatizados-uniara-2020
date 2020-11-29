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
