
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
