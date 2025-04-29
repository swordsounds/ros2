#!/usr/bin/env python3 

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts
from functools import partial

class AddTwoIntsClient(Node):
    def __init__(self):
        super().__init__("add_two_ints_client")
        self.client = self.create_client(AddTwoInts, "add_two_ints")

    def call_add_two_ints(self, a: AddTwoInts.Request, b: AddTwoInts.Request):
        while not self.client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Server")
        
        request = AddTwoInts.Request()
        request.a = a
        request.b = b

        future = self.client.call_async(request)
        future.add_done_callback(partial(self.callback_call_add_two_ints, request=request)) # add partial if you want to add additional arguments
    
    def callback_call_add_two_ints(self, future, request):
        response = future.result()
        self.get_logger().info(f"Got response {str(request.a)} + {str(request.b)} = {str(response.sum)}")

def main(args=None):
    rclpy.init(args=args)
    node = AddTwoIntsClient()
    node.call_add_two_ints(8, 9)
    node.call_add_two_ints(1, 1)
    node.call_add_two_ints(8, 100)
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()