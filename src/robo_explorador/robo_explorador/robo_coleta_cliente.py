#!/usr/bin/env python3
import random
import sys
import rclpy
from rclpy.node import Node
from robo_interfaces.srv import ColetaAmostra


class RoboColetaCliente(Node):
    """Cliente ROS 2 para requisicao de perfuracao e coleta geologica."""

    def __init__(self):
        super().__init__('robo_coleta_cliente')
        self.client = self.create_client(ColetaAmostra, 'coleta_material')

        while not self.client.wait_for_service(timeout_sec=2.0):
            self.get_logger().info('Aguardando disponibilidade do servico /coleta_material...')

        self.get_logger().info('Conexao estabelecida com o servidor de coleta.')

    def enviar_requisicao(self, profundidade: float):
        req = ColetaAmostra.Request()
        req.profundidade = float(profundidade)
        self.get_logger().info(f'Enviando comando de coleta para profundidade={req.profundidade:.2f} m')
        return self.client.call_async(req)


def main(args=None):
    rclpy.init(args=args)
    node = RoboColetaCliente()

    # Define a profundidade aleatoria entre 0.1 e 0.5 metros, conforme especificacao
    if len(sys.argv) > 1:
        try:
            profundidade = float(sys.argv[1])
        except ValueError:
            profundidade = round(random.uniform(0.1, 0.5), 2)
    else:
        profundidade = round(random.uniform(0.1, 0.5), 2)

    future = node.enviar_requisicao(profundidade)
    rclpy.spin_until_future_complete(node, future)

    try:
        response = future.result()
        if response.sucesso:
            node.get_logger().info('>>> Resposta do Servidor: SUCESSO na extracao da amostra! <<<')
        else:
            node.get_logger().warn('>>> Resposta do Servidor: FALHA na operacao de amostragem. <<<')
    except Exception as e:
        node.get_logger().error(f'Erro na chamada do servico: {e}')

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
