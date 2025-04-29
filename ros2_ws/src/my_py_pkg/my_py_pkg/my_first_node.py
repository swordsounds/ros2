#!/usr/bin/env python3

import rclpy

from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__("py_test")
        self.count = 0
        self.get_logger().info('Hello World')
        self.create_timer(1.0, callback=self.timer_callback)

    def timer_callback(self):
        self.count += 1
        self.get_logger().info(str(self.count))

def main(args=None):
    rclpy.init(args=args) # inits rclpy
    
    node = MyNode() # Creates a node object
    rclpy.spin(node=node) # Runs until keyboard interrupt
    rclpy.shutdown() # Shutdown

if __name__ == "__main__":
    main()

# ros2 pkg create <pkg_name> --build-type ament_python --dependencies rclpy
# chmod +x my_first_node.py

# never build in the src file