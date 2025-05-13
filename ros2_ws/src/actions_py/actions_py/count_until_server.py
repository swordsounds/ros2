#!/usr/bin/env python3
import rclpy
import time
import threading

from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.action.server import ServerGoalHandle

from my_robot_interfaces.action import CountUntil
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

class CountUntilServerNode(Node):
    def __init__(self):
        super().__init__("count_until_server")
        self.goal_handle: ServerGoalHandle = None
        self.goal_lock = threading.Lock()
        self.goal_queue = []
        self.count_until_server = ActionServer(self, 
                                               CountUntil, 
                                               "count_until", 
                                               goal_callback=self.goal_callback,
                                               handle_accepted_callback=self.handle_accepting_callback, # Queueing
                                               cancel_callback=self.cancel_callback,
                                               execute_callback=self.execute_callback,
                                               callback_group=ReentrantCallbackGroup())
        self.get_logger().info("Action server has been started.")

    def goal_callback(self, goal_request: CountUntil.Goal): #All callbacks run in a thread themselves
        self.get_logger().info("Recieved a goal.")

        # Policy: refuse new goal if current goal is still active
        # with self.goal_lock:
        #     if self.goal_handle is not None and self.goal_handle.is_active:
        #         self.get_logger().info("Goal in progress")
        #         return GoalResponse.REJECT
        

        # Validate the goal request
        if goal_request.target_number <= 0:
            return GoalResponse.REJECT
        
        # Policy: preempt existing goal when new recieved
        # with self.goal_lock:
        #     if self.goal_handle is not None and self.goal_handle.is_active:
        #         self.get_logger().info("Abort current goal and accept new goal")
        #         self.goal_handle.abort()

        self.get_logger().info("Accepting the goal.")
        return GoalResponse.ACCEPT
    


    def execute_callback(self, goal_handle: ServerGoalHandle): #All callbacks run in a thread themselves
        with self.goal_lock:
            self.goal_handle = goal_handle

        # Get request from goal
        target_number = goal_handle.request.target_number
        period = goal_handle.request.period

        # Execute the action (send feedback here)
        self.get_logger().info("Executing the goal.")
        feedback = CountUntil.Feedback()
        result = CountUntil.Result()
        counter = 0
        for i in range(target_number):

            # Returns aborted/completed result
            if not goal_handle.is_active:
                result.reached_number = counter
                self.process_next_goal_in_queue()
                return result
            
            if goal_handle.is_cancel_requested:
                self.get_logger().info("Canceling the goal")
                goal_handle.canceled()
                result.reached_number = counter
                self.process_next_goal_in_queue()
                return result
            
            counter += 1

            feedback.current_number = counter
            goal_handle.publish_feedback(feedback)

            self.get_logger().info(str(counter))
            time.sleep(period)

        # Once done, set goal final state
        goal_handle.succeed()

        # And send the result
        result.reached_number = counter
        self.process_next_goal_in_queue()
        return result
    

    def handle_accepting_callback(self, goal_handle: ServerGoalHandle):
        with self.goal_lock:
            if self.goal_handle is not None: #current goal_handle
                self.goal_queue.append(goal_handle)
            else:
                goal_handle.execute()

    def cancel_callback(self, goalhandle: ServerGoalHandle): #All callbacks run in a thread themselves
        self.get_logger().info("received a cancel request")
        return CancelResponse.ACCEPT # or REJECT
    
    def process_next_goal_in_queue(self):
        with self.goal_lock:
            if len(self.goal_queue) > 0:
                self.goal_queue.pop(0).execute()
            else:
                self.goal_handle = None

def main(args=None):
    rclpy.init(args=args)
    node = CountUntilServerNode()
    rclpy.spin(node, MultiThreadedExecutor())
    rclpy.shutdown()


if __name__ == "__main__":
    main()