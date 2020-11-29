import { useEffect, useState } from 'react';
import Produtos from './Produtos';


function App() {
  const [ produtos, setProdutos ] = useState([]);

  useEffect(() => {
    (async () => {
      const resposta = await fetch('http://localhost:5000/produtos');
      const produtos = await resposta.json();
      setProdutos(produtos);
      // trate os erros pfv :(
    })();
  }, []);

  return (
    <Produtos produtos={produtos} />
  );
}

export default App;
