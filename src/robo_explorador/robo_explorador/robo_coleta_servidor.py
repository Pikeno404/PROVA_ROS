#!/usr/bin/env python3
import random
import rclpy
from rclpy.node import Node
from robo_interfaces.srv import ColetaAmostra


class RoboColetaServidor(Node):
    """Servidor ROS 2 responsavel por processar o pedido de coleta de amostra de solo."""

    def __init__(self):
        super().__init__('robo_coleta_servidor')
        self.servico = self.create_service(
            ColetaAmostra,
            'coleta_material',
            self.processar_coleta_callback
        )
        self.get_logger().info('Servidor de coleta pronto no servico /coleta_material.')

    def processar_coleta_callback(self, request, response):
        self.get_logger().info(
            f'Requisicao recebida para perfuracao em profundidade: {request.profundidade:.2f} m'
        )

        # Regra de negocio: 70% de probabilidade de sucesso na operacao de perfuracao
        sorteio = random.random()
        response.sucesso = (sorteio <= 0.70)

        if response.sucesso:
            self.get_logger().info('Status: Operacao de coleta realizada com SUCESSO.')
        else:
            self.get_logger().warn('Status: Falha na coleta do material geologico.')

        return response


def main(args=None):
    rclpy.init(args=args)
    node = RoboColetaServidor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
