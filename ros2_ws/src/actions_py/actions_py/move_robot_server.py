#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.action.server import ServerGoalHandle, GoalResponse, CancelResponse

from my_robot_interfaces.action import MoveRobot
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
import threading 
import time

class MoveRobotServerNode(Node): 
    def __init__(self):
        super().__init__("move_robot_server") 
        self.goal_lock = threading.Lock()
        self.goal_handle: ServerGoalHandle = None
        self.robot_position = 50
        self.move_robot_server = ActionServer(
            self,
            MoveRobot,
            "move_robot",
            goal_callback=self.goal_callback,
            execute_callback=self.execute_callback,
            cancel_callback=self.cancel_callback,
            callback_group=ReentrantCallbackGroup()
            )
        self.get_logger().info("Action started has been started.")
        self.get_logger().info(f"Robot position: {self.robot_position}")

    def goal_callback(self, goal_request: MoveRobot.Goal):
        self.get_logger().info("Recieved a new goal.")

        if goal_request.position not in range(0,100) or goal_request.velocity <=0:
            self.get_logger().info("Invalid position or velocity, rejected")
            return GoalResponse.REJECT
        
        # new goal is valid, abort prev accept new
        if self.goal_handle is not None and self.goal_handle.is_active:
            self.goal_handle.abort()

        self.get_logger().info("Accepted goal")
        return GoalResponse.ACCEPT
    
    def cancel_callback(self, goal_handle: ServerGoalHandle):
        self.get_logger().info("Received a cancel request")
        return CancelResponse.ACCEPT
    
    def execute_callback(self, goal_handle: ServerGoalHandle):
        with self.goal_lock:
            self.goal_handle  = goal_handle # Update goal_handle

        goal_position = goal_handle.request.position
        velocity = goal_handle.request.velocity

        result =  MoveRobot.Result()
        feedback = MoveRobot.Feedback()

        self.get_logger().info("Execute goal.")
        while rclpy.ok(): # True when Node is running
            if not goal_handle.is_active:
                result.position = self.robot_position
                result.message = "Preemted by another goal"
                return result
            
            if goal_handle.is_cancel_requested:
                result.position = self.robot_position
                if goal_position == self.robot_position:
                    result.message = "Success"
                    goal_handle.succeed()
                else:
                    result.message = "Canceled"
                    goal_handle.canceled()
                return result
            
            diff = goal_position - self.robot_position

            if diff == 0:
                result.position = self.robot_position
                result.message = "Success"
                goal_handle.succeed()
                return result
            
            elif diff > 0:
                if diff >= velocity:
                    self.robot_position += velocity
                else:
                    self.robot_position += diff
                
            else:
                if abs(diff) >= velocity:
                    self.robot_position -= velocity
                else:
                    self.robot_position -= abs(diff)

            self.get_logger().info(f"Robot position: {self.robot_position}")
            feedback.current_position = self.robot_position
            goal_handle.publish_feedback(feedback=feedback)

            time.sleep(1.0)
    
def main(args=None):
    rclpy.init(args=args)
    node = MoveRobotServerNode()
    rclpy.spin(node, MultiThreadedExecutor())
    rclpy.shutdown()


if __name__ == "__main__":
    main()
