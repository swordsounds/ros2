#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from my_robot_interfaces.msg import HardwareStatus

class HardwareStatusPublisherNode(Node):
    def __init__(self):
        super().__init__("hardware_status_publisher")
        self.publisher = self.create_publisher(HardwareStatus, "hardware_status", 10)
        self.timer = self.create_timer(1.0, self.callback_hardware_status)
        self.get_logger().info("HW Status publisher has been started.")

    def callback_hardware_status(self):
        msg = HardwareStatus()
        msg.tempurature = 47.0
        msg.are_motors_ready = True
        msg.debug_message = "Nothing broke"
        self.publisher.publish(msg)
        
def main(args=None):
    rclpy.init(args=args)
    node = HardwareStatusPublisherNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()