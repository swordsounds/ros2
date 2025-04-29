#include <chrono>
#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "turtlesim/msg/pose.hpp"
using std::placeholders::_1;
using namespace std::chrono_literals;
class ControllerNode : public rclcpp::Node{
    public:
        ControllerNode() : Node("controller_node"){
            ControlPublisher = this->create_publisher<geometry_msgs::msg::Twist>("/turtle1/cmd_vel", 5);
            PoseSubscriber = this->create_subscription<turtlesim::msg::Pose>(
                "/turtle1/pose",
                rclcpp::SensorDataQoS(),
                std::bind(&ControllerNode::SensorCallback,this,_1)
                );

            timerObject = this->create_wall_timer(
                20ms,
                std::bind(&ControllerNode::ControlFunction,this)
                );

            controlVel.linear.x = 0;
            controlVel.linear.y = 0;
            controlVel.linear.z = 0;

            controlVel.angular.x = 0;
            controlVel.angular.y = 0;
            controlVel.angular.z = 0;
            
            initialTime = now();
        }
        void SensorCallback(turtlesim::msg::Pose receivedMsg)
        {
            lastReceivedMsg = receivedMsg;

            lastReceivedMsgTime = now();
        }

        void ControlFunction(){
            controlVel.linear.x = 2;
            controlVel.linear.y = 0;
            controlVel.linear.z = 0;
            controlVel.angular.x = 0;
            controlVel.angular.y = 0;
            controlVel.angular.z = 0.8;
            std::cout << "Sending the control command" << std::endl;

            ControlPublisher->publish(controlVel);
            
            std::cout << "Received pose" << std::endl;
            std::cout << "Time:" << (lastReceivedMsgTime.seconds() - initialTime.seconds()) << ",x " << lastReceivedMsg.x << ",y: " << lastReceivedMsg.y << ",theta: " << lastReceivedMsg.theta;
            std::cout << ",lin vel: " << lastReceivedMsg.linear_velocity << ", ang vel: " << lastReceivedMsg.angular_velocity << std::endl;
        }

    private:
    turtlesim::msg::Pose lastReceivedMsg;
    rclcpp::Time initialTime;
    rclcpp::Time lastReceivedMsgTime;
    geometry_msgs::msg::Twist controlVel;
    rclcpp::TimerBase::SharedPtr timerObject;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr ControlPublisher;
    rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr PoseSubscriber;
};

int main(int argc, char *argv[]){
    rclcpp::init(argc, argv);
    auto TestNode = std::make_shared<ControllerNode>();
    rclcpp::spin(TestNode);
    rclcpp::shutdown();
    return 0;
};