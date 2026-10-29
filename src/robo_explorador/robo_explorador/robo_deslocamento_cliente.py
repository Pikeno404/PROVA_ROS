#!/usr/bin/env python3
import sys
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from robo_interfaces.action import Deslocamento


class RoboDeslocamentoCliente(Node):
    """Cliente padrao para envio de meta de navegacao e recepcao de feedback continuo."""

    def __init__(self):
        super().__init__('robo_deslocamento_cliente')
        self._action_client = ActionClient(self, Deslocamento, 'deslocamento')

    def enviar_objetivo(self, lat: float, lon: float, vlat: float, vlon: float):
        self.get_logger().info('Aguardando conexao com o servidor de deslocamento...')
        self._action_client.wait_for_server()

        meta = Deslocamento.Goal()
        meta.latitude = float(lat)
        meta.longitude = float(lon)
        meta.vel_latitude = float(vlat)
        meta.vel_longitude = float(vlon)

        self.get_logger().info(
            f'Enviando meta -> Alvo: ({lat:.2f}, {lon:.2f}) | Velocidades: ({vlat:.2f}, {vlon:.2f})'
        )

        envio_future = self._action_client.send_goal_async(
            meta,
            feedback_callback=self.feedback_callback
        )
        envio_future.add_done_callback(self.meta_resposta_callback)

    def meta_resposta_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Meta foi rejeitada pelo servidor!')
            rclpy.shutdown()
            return

        self.get_logger().info('Meta ACEITA pelo servidor. Acompanhando navegacao...')
        resultado_future = goal_handle.get_result_async()
        resultado_future.add_done_callback(self.resultado_callback)

    def feedback_callback(self, feedback_msg):
        fb = feedback_msg.feedback
        self.get_logger().info(
            f'[FEEDBACK RECEBIDO] Posicao atual do robo: ({fb.latitude_atual:.2f}, {fb.longitude_atual:.2f})'
        )

    def resultado_callback(self, future):
        res = future.result().result
        self.get_logger().info(
            f'>>> Missao Concluida! Distancia total percorrida: {res.distancia_percorrida:.2f} m <<<'
        )
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)

    # Argumentos opcionais: lat, lon, vlat, vlon
    parametros = [float(arg) for arg in sys.argv[1:5] if arg.replace('.', '', 1).replace('-', '', 1).isdigit()]
    padrao = [6.0, 8.0, 1.0, 1.0]
    lat, lon, vlat, vlon = parametros + padrao[len(parametros):]

    node = RoboDeslocamentoCliente()
    node.enviar_objetivo(lat, lon, vlat, vlon)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
