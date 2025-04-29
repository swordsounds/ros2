#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from my_robot_interfaces.srv import LedToggle

class BatteryClientNode(Node):
    def __init__(self):
        super().__init__("battery_client_node")
        self.last_time_battery_state_changed = self.get_current_time_seconds()
        self.battery_state = "full"
        self.client = self.create_client(LedToggle, "set_led")
        self.timer = self.create_timer(0.1, self.callback_timer)
        self.get_logger().info("Battery Client started.")
    
    def get_current_time_seconds(self):
        seconds, nanoseconds = self.get_clock().now().seconds_nanoseconds()
        return seconds + nanoseconds / 1000000000.0
    
    def callback_timer(self):
        time_now = self.get_current_time_seconds()

        if self.battery_state == "full":
            if time_now - self.last_time_battery_state_changed > 4.0:
                self.battery_state = "empty"
                self.get_logger().info("Battery is empty, charging...")
                self.call_led(2, 1)
                self.last_time_battery_state_changed = time_now
        elif self.battery_state == "empty":
            if time_now - self.last_time_battery_state_changed > 6.0:
                self.battery_state = "full"
                self.get_logger().info("Battery is now full.")
                self.call_led(2, 0)
                self.last_time_battery_state_changed = time_now

    def call_led(self, led_number: LedToggle.Request, state: LedToggle.Request):
        while not self.client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for server.")

        request = LedToggle.Request()
        request.led_number = led_number
        request.state = state

        future = self.client.call_async(request)
        future.add_done_callback(self.callback_call_led)
        
    def callback_call_led(self, future):
        response: LedToggle.Response =  future.result()
        if response.success_flag:
            self.get_logger().info("LED Turned on.")
        else:
            self.get_logger().info("LED Not Changed.")

def main(args=None):
    rclpy.init(args=args)
    node = BatteryClientNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()