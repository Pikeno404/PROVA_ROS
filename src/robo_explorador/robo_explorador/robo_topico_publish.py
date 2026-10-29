#!/usr/bin/env python3
import random
import rclpy
from rclpy.node import Node
from robo_interfaces.msg import Monitoramento


class RoboMonitoramentoPublisher(Node):
    """No responsavel por simular os sensores ambientais do robo e publicar no topico."""

    def __init__(self):
        super().__init__('robo_topico_publish')
        self.publisher_ = self.create_publisher(Monitoramento, '/monitoramento', 10)
        self.timer_period = 1.0  # Publicacao a cada 1 segundo
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.get_logger().info('No publicador de monitoramento iniciado em /monitoramento.')

    def timer_callback(self):
        msg = Monitoramento()
        # Valores de telemetria simulados entre 1 e 100
        msg.oxigenio = float(random.uniform(1.0, 100.0))
        msg.temperatura = float(random.uniform(1.0, 100.0))

        self.publisher_.publish(msg)
        self.get_logger().info(
            f'Sensor Telemetria -> Oxigenio: {msg.oxigenio:.2f}% | Temperatura: {msg.temperatura:.2f}°C'
        )


def main(args=None):
    rclpy.init(args=args)
    node = RoboMonitoramentoPublisher()
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
