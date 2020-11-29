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
