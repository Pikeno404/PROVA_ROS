#!/usr/bin/env python3
import math
import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from robo_interfaces.action import Deslocamento


class RoboDeslocamentoServidor(Node):
    """Servidor de Acao para navegacao e deslocamento do robo explorador."""

    def __init__(self):
        super().__init__('robo_deslocamento_servidor')
        self.pos_lat = 0.0
        self.pos_lon = 0.0
        self.callback_group = ReentrantCallbackGroup()

        self._action_server = ActionServer(
            self,
            Deslocamento,
            'deslocamento',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group,
        )
        self.get_logger().info('Servidor de Acao de deslocamento inicializado na posicao (0.0, 0.0).')

    def goal_callback(self, goal_request):
        self.get_logger().info(
            f'Nova meta recebida -> Destino: Lat {goal_request.latitude:.2f}, Lon {goal_request.longitude:.2f} '
            f'| Velocidade: Lat {goal_request.vel_latitude:.2f}, Lon {goal_request.vel_longitude:.2f}'
        )
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().warn('Solicitacao de cancelamento recebida pelo servidor!')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        meta = goal_handle.request
        resultado = Deslocamento.Result()
        feedback = Deslocamento.Feedback()

        vel_lat = abs(meta.vel_latitude)
        vel_lon = abs(meta.vel_longitude)
        delta_lat = meta.latitude - self.pos_lat
        delta_lon = meta.longitude - self.pos_lon

        # Validacao de destino
        if delta_lat == 0.0 and delta_lon == 0.0:
            self.get_logger().warn('Robo ja se encontra na coordenada de destino.')
            goal_handle.abort()
            resultado.distancia_percorrida = 0.0
            return resultado

        # Validacao de velocidade
        if (delta_lat != 0.0 and vel_lat == 0.0) or (delta_lon != 0.0 and vel_lon == 0.0):
            self.get_logger().error('Velocidade nula para eixo com deslocamento obrigatorio. Abortando acao.')
            goal_handle.abort()
            resultado.distancia_percorrida = 0.0
            return resultado

        distancia_acumulada = 0.0
        self.get_logger().info('Iniciando movimentacao do robo...')

        while rclpy.ok():
            time.sleep(1.0)

            # Verificacao de interrupcao / cancelamento
            if goal_handle.is_cancel_requested:
                resultado.distancia_percorrida = distancia_acumulada
                goal_handle.canceled()
                self.get_logger().warn(
                    f'Deslocamento CANCELADO. Distancia parcial percorrida: {distancia_acumulada:.2f} m'
                )
                return resultado

            dist_lat = meta.latitude - self.pos_lat
            dist_lon = meta.longitude - self.pos_lon
            lat_anterior, lon_anterior = self.pos_lat, self.pos_lon

            # Avanco linear no eixo de latitude
            if abs(dist_lat) <= vel_lat:
                self.pos_lat = meta.latitude
            else:
                self.pos_lat += math.copysign(vel_lat, dist_lat)

            # Avanco linear no eixo de longitude
            if abs(dist_lon) <= vel_lon:
                self.pos_lon = meta.longitude
            else:
                self.pos_lon += math.copysign(vel_lon, dist_lon)

            # Calculo do deslocamento percorrido na iteracao
            deslocamento_passo = math.hypot(self.pos_lat - lat_anterior, self.pos_lon - lon_anterior)
            distancia_acumulada += deslocamento_passo

            # Publicacao de feedback
            feedback.latitude_atual = self.pos_lat
            feedback.longitude_atual = self.pos_lon
            goal_handle.publish_feedback(feedback)

            self.get_logger().info(
                f'Feedback de Posicao -> Atual: ({self.pos_lat:.2f}, {self.pos_lon:.2f}) '
                f'| Distancia Total: {distancia_acumulada:.2f} m'
            )

            # Condicao de chegada
            if self.pos_lat == meta.latitude and self.pos_lon == meta.longitude:
                self.get_logger().info('Coordenada alvo alcancada com sucesso!')
                break

        resultado.distancia_percorrida = distancia_acumulada
        goal_handle.succeed()
        return resultado


def main(args=None):
    rclpy.init(args=args)
    node = RoboDeslocamentoServidor()
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
