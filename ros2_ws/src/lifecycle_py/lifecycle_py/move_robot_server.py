#!/usr/bin/env python3
import rclpy
# from rclpy.node import Node
from rclpy.lifecycle import LifecycleNode, LifecycleState, TransitionCallbackReturn
from rclpy.action import ActionServer
from rclpy.action.server import ServerGoalHandle, GoalResponse, CancelResponse

from my_robot_interfaces.action import MoveRobot
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
import threading 
import time

class MoveRobotServerNode(LifecycleNode): 
    def __init__(self):
        super().__init__("move_robot_server") 
        self.goal_lock = threading.Lock()
        self.goal_handle: ServerGoalHandle = None
        self.robot_position = 50
        self.server_activated = False
        self.get_logger().info(f"Robot position: {self.robot_position}")

    def on_configure(self, state: LifecycleState):
        self.declare_parameter("robot_name", rclpy.Parameter.Type.STRING)
        self.robot_name = self.get_parameter("robot_name").value
        self.move_robot_server = ActionServer(
        self,
        MoveRobot,
        "move_robot_" + self.robot_name,
        goal_callback=self.goal_callback,
        execute_callback=self.execute_callback,
        cancel_callback=self.cancel_callback,
        callback_group=ReentrantCallbackGroup()
        )
        self.get_logger().info("Action started has been started.")
        return TransitionCallbackReturn.SUCCESS
    
    def on_cleanup(self, state: LifecycleState):
        self.move_robot_server.destroy()
        self.robot_name = ""
        self.undeclare_parameter("robot_name")
        return TransitionCallbackReturn.SUCCESS
    
    def on_activate(self, state: LifecycleState):
        self.get_logger().info("Activate node")
        self.server_activated = True
        return super().on_activate(state)
    
    def on_deactivate(self, state: LifecycleState):
        self.get_logger().info("Deactivate node")
        self.server_activated = False
        with self.goal_lock:
            if self.goal_handle is not None and self.goal_handle.is_active:
                self.goal_handle.abort()
        return super().on_deactivate(state)

    def on_shutdown(self, state: LifecycleState):
        self.move_robot_server.destroy()
        self.robot_name = ""
        self.undeclare_parameter("robot_name")
        return TransitionCallbackReturn.SUCCESS



    def goal_callback(self, goal_request: MoveRobot.Goal):
        self.get_logger().info("Recieved a new goal.")

        if not self.server_activated:
            self.get_logger().warn("Node not activated yet.")
            return GoalResponse.REJECT

        if goal_request.position not in range(0,100) or goal_request.velocity <=0:
            self.get_logger().info("Invalid position or velocity, rejected")
            return GoalResponse.REJECT
        
        # new goal is valid, abort prev accept new
        with self.goal_lock:
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
                result.message = "Preemted by another goal, or node deactivated"
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

# ros2 run lifecycle_py move_robot_server --ros-args -r __node:=move_robot_server_a -p robot_name:=A