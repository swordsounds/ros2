#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from my_robot_interfaces.msg import LedStateArray
from my_robot_interfaces.srv import LedToggle

class LedServerNode(Node):
    def __init__(self):
        super().__init__("led_node")
        self.led_states = [0, 0, 0]
        self.publisher = self.create_publisher(LedStateArray, "led_panel_state", 10)
        self.timer = self.create_timer(5.0, self.callback_publish_led_states)
        self.set_led_service = self.create_service(LedToggle, "set_led", self.callback_set_led)
        self.get_logger().info("LED panel node has been started.")

    def callback_publish_led_states(self):

        msg = LedStateArray()
        msg.led_states = self.led_states

        self.publisher.publish(msg)

    def callback_set_led(self, request: LedToggle.Request, response: LedToggle.Response):
        led_number = request.led_number
        state = request.state
        
        if led_number >= len(self.led_states) or led_number < 0:
            response.success_flag = False
            return response

        if state not in [0, 1] :
            response.success_flag = False
            return response

        self.led_states[led_number] = state
        self.callback_publish_led_states()
        response.success_flag = True
        return response
    
def main(args=None):
    rclpy.init(args=args)
    node = LedServerNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()