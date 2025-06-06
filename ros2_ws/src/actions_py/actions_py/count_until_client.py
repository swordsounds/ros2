#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle, GoalStatus
from my_robot_interfaces.action import CountUntil



class CountUntilClientNode(Node): # MODIFY NAME
    def __init__(self):
        super().__init__("count_until_client") # MODIFY NAME
        self.count_until_client = ActionClient(self, CountUntil, "count_until")
        
    def send_goal(self, target_number, period):
        # Wait for the server
        self.count_until_client.wait_for_server()

        # Create a goal
        goal = CountUntil.Goal()
        goal.target_number = target_number
        goal.period = period

        # Send the goal
        self.get_logger().info("Sending Goal")
        self.count_until_client. \
            send_goal_async(goal, feedback_callback=self.goal_feedback_callback).\
            add_done_callback(self.goal_response_callback)

        # Send a cancel request 2 seconds later
        self.timer = self.create_timer(2.0 , self.cancel_goal)

    def cancel_goal(self):
        pass
        # self.get_logger().info("Send a cancel Request")
        # self.goal_handle.cancel_goal_async()
        # self.timer.cancel()

    def goal_response_callback(self, future): # Server responds with accepted or rejected
        self.goal_handle: ClientGoalHandle = future.result()
        if self.goal_handle.accepted:
            self.get_logger().info("Goal got accepted.")
            self.goal_handle.\
                get_result_async().\
                add_done_callback(self.goal_result_callback)
        else:
            self.get_logger().warn("Goal got rejected.")
    
    def goal_result_callback(self, future): # Server responds with result
        status = future.result().status
        result = future.result().result

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info("Success")
        elif status == GoalStatus.STATUS_ABORTED:
            self.get_logger().error("Aborted")
        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().warn("Canceled")

        self.get_logger().info(str(result.reached_number))

    def goal_feedback_callback(self, feedback_msg):
        number = feedback_msg.feedback.current_number
        self.get_logger().info(f"Got feedback: {number}")


def main(args=None):
    rclpy.init(args=args)
    node = CountUntilClientNode() # MODIFY NAME
    node.send_goal(6, 1.0)
    # node.send_goal(-1, 1.0)
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()