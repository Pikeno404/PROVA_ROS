#!/usr/bin/env python3
import sys
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from robo_interfaces.action import Deslocamento


class RoboDeslocamentoCancela(Node):
    """Cliente de Acao projetado para solicitar cancelamento da meta apos 5 segundos de operacao."""

    def __init__(self):
        super().__init__('robo_deslocamento_cancela')
        self._action_client = ActionClient(self, Deslocamento, 'deslocamento')
        self.goal_handle = None
        self.timer_cancelamento = None

    def enviar_objetivo(self, lat: float, lon: float, vlat: float, vlon: float):
        self.get_logger().info('Aguardando servidor de deslocamento para teste de cancelamento...')
        self._action_client.wait_for_server()

        meta = Deslocamento.Goal()
        meta.latitude = float(lat)
        meta.longitude = float(lon)
        meta.vel_latitude = float(vlat)
        meta.vel_longitude = float(vlon)

        self.get_logger().info(
            f'Enviando meta de longa duracao -> ({lat:.2f}, {lon:.2f}) | Cancelamento programado para T+5.0s'
        )

        envio_future = self._action_client.send_goal_async(
            meta,
            feedback_callback=self.feedback_callback
        )
        envio_future.add_done_callback(self.meta_resposta_callback)

    def meta_resposta_callback(self, future):
        self.goal_handle = future.result()
        if not self.goal_handle.accepted:
            self.get_logger().error('A meta foi recusada pelo servidor!')
            rclpy.shutdown()
            return

        self.get_logger().info('Meta ACEITA. Temporizador de 5 segundos disparado.')

        resultado_future = self.goal_handle.get_result_async()
        resultado_future.add_done_callback(self.resultado_callback)

        # Configura timer de 5 segundos para requisitar o cancelamento
        self.timer_cancelamento = self.create_timer(5.0, self.solicitar_cancelamento)

    def feedback_callback(self, feedback_msg):
        fb = feedback_msg.feedback
        self.get_logger().info(
            f'[Telemetria de Movimento] Lat: {fb.latitude_atual:.2f}, Lon: {fb.longitude_atual:.2f}'
        )

    def solicitar_cancelamento(self):
        self.timer_cancelamento.cancel()
        self.get_logger().warn('Tempo limite de 5.0 segundos alcancado! Enviando comando de CANCELAMENTO...')

        cancel_future = self.goal_handle.cancel_goal_async()
        cancel_future.add_done_callback(self.cancelamento_resposta_callback)

    def cancelamento_resposta_callback(self, future):
        cancel_response = future.result()
        if len(cancel_response.goals_canceling) > 0:
            self.get_logger().info('Cancelamento aceito e confirmado pelo servidor.')
        else:
            self.get_logger().warn('Falha na solicitacao de cancelamento.')

    def resultado_callback(self, future):
        status = future.result().status
        res = future.result().result
        self.get_logger().info(
            f'>>> Status Final: {status} | Distancia percorrida antes da parada: {res.distancia_percorrida:.2f} m <<<'
        )
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)

    # Parametros para trajeto longo que exceda 5 segundos (ex: lat=15.0, lon=15.0, vel=1.0)
    parametros = [float(arg) for arg in sys.argv[1:5] if arg.replace('.', '', 1).replace('-', '', 1).isdigit()]
    padrao = [12.0, 12.0, 1.0, 1.0]
    lat, lon, vlat, vlon = parametros + padrao[len(parametros):]

    node = RoboDeslocamentoCancela()
    node.enviar_objetivo(lat, lon, vlat, vlon)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
