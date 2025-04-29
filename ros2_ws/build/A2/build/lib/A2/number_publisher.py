#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from example_interfaces.msg import Int64

class Publisher(Node):
    def __init__(self):
        super().__init__("number_publisher")
        self.publisher = self.create_publisher(Int64, "number", 10)
        self.timer = self.create_timer(1.0, self.callback_publisher)
        self.count = 2
        self.get_logger().info("Publisher Started.")

    def callback_publisher(self):
        msg = Int64()
        msg.data = self.count
        self.publisher.publish(msg)
        
def main(args=None):
    rclpy.init(args=args)
    node = Publisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()