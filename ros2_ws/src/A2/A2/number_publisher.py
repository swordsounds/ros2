#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from example_interfaces.msg import Int64

class Publisher(Node):
    def __init__(self):
        super().__init__("number_publisher")

        self.declare_parameter("number", 2)
        self.declare_parameter("timer_period", 1.0)

        self.publisher = self.create_publisher(Int64, "number", 10)

        self.timer_period = self.get_parameter("timer_period").value
        self.count = self.get_parameter("number").value
        self.timer = self.create_timer(
            self.timer_period, 
            self.callback_publisher
            )
    
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

# ros2 run A2 counter_pub --ros-args -p number:=5 -p timer_period:=0.5