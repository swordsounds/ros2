#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from example_interfaces.msg import Int64
from example_interfaces.srv import SetBool

class NumberSubscriberNode(Node):
    def __init__(self):
        super().__init__("number_counter")
        self.subscriber = self.create_subscription(Int64, "number", self.callback_subscriber, 10)
        self.publisher = self.create_publisher(Int64, "number_count", 10)
        self.count = 0
        self.get_logger().info("Subscriber Started.")
        self.reset_counter_service = self.create_service(
            SetBool, 
            "reset_counter", 
            callback=self.callback_reset
            ) # make srv_name a verb example turn_led_on
        self.get_logger().info("Server has been started.")
        
    def callback_reset(self, request: SetBool.Request, response: SetBool.Response):
        if request.data:
            self.count = 0
            response.success = True
            response.message = "Counter Resetted"
        else:
            response.success = False
            response.message = "Counter Not Resetted"
            
        return response # do not forget return
    
    def callback_subscriber(self, msg: Int64):
        self.count += msg.data
        new_msg = Int64()
        new_msg.data = self.count
        self.publisher.publish(new_msg)

def main(args=None):
    rclpy.init(args=args)
    node = NumberSubscriberNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()