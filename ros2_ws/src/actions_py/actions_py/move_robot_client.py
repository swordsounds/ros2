#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from my_robot_interfaces.action import MoveRobot
from rclpy.action.client import ClientGoalHandle, GoalStatus
from example_interfaces.msg import Empty
class MoveRobotClientNode(Node):

    def __init__(self):
        super().__init__("move_robot_client")
        self.goal_handle = None
        self.move_robot_client = ActionClient(
            self,
            MoveRobot,
            "move_robot" 
        )
        self.cancel_subscriber = self.create_subscription(Empty, 
                                                          "cancel_move", 
                                                          callback=self.callback_cancel_move,
                                                          qos_profile=10)

    def send_goal(self,position, velocity):
        self.move_robot_client.wait_for_server()
        goal = MoveRobot.Goal()
        goal.position = position
        goal.velocity = velocity

        self.get_logger().info(f"Send goal with position {position} and {velocity}")
        self.move_robot_client\
            .send_goal_async(goal, feedback_callback=self.feedback_callback,)\
            .add_done_callback(callback=self.goal_response_callback)
    
    def feedback_callback(self, feedback_msg):
        position = feedback_msg.feedback.current_position
        self.get_logger().info(f"Feedback position: {position}")

    def goal_response_callback(self, future):
        self.goal_handle: ClientGoalHandle = future.result()
        if self.goal_handle.accepted:
            self.get_logger().info("Goal got accepted")
            self.goal_handle.get_result_async().\
                add_done_callback(self.goal_result_callback)
        else:
            self.get_logger().info("Goal got rejected")

    def goal_result_callback(self, future):
        status = future.result().status
        result = future.result().result
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info("Succeeded")
        elif status == GoalStatus.STATUS_ABORTED:
            self.get_logger().error("Aborted")
        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().warn("Canceled")
        self.get_logger().info(f"Position {result.position}")
        self.get_logger().info(f"Message {result.message}")

    def callback_cancel_move(self, msg):
        self.cancel_goal()

    def cancel_goal(self):
        if self.goal_handle is not None:
            self.get_logger().info("Send a cancel request")
            self.goal_handle.cancel_goal_async()

def main(args=None):
    rclpy.init(args=args)
    node = MoveRobotClientNode()
    node.send_goal(76, 1)
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()