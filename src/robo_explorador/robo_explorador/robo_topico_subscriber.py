#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from robo_interfaces.msg import Monitoramento


class RoboMonitoramentoSubscriber(Node):
    """No assinante responsavel por avaliar as condicoes ambientais recebidas."""

    def __init__(self):
        super().__init__('robo_topico_subscriber')
        self.subscription = self.create_subscription(
            Monitoramento,
            '/monitoramento',
            self.monitoramento_callback,
            10
        )
        self.get_logger().info('Assinante de telemetria ativo no topico /monitoramento.')

    def monitoramento_callback(self, msg: Monitoramento):
        # Criterio da avaliacao:
        # Safe: temperatura entre 10 e 40 °C (inclusive) e oxigenio superior a 80
        # Not Safe: caso qualquer condicao nao seja satisfeita
        temperatura_valida = 10.0 <= msg.temperatura <= 40.0
        oxigenio_valido = msg.oxigenio > 80.0

        if temperatura_valida and oxigenio_valido:
            estado = "Safe"
        else:
            estado = "Not Safe"

        self.get_logger().info(
            f'Dados Recebidos [O2: {msg.oxigenio:.2f}%, Temp: {msg.temperatura:.2f}°C] -> CLASSIFICACAO: {estado}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = RoboMonitoramentoSubscriber()
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
