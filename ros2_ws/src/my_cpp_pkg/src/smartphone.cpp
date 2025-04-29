#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/msg/string.hpp"

class SmartphoneNode : public rclcpp::Node
{
public:
    SmartphoneNode() : Node("smartphone")
    {
        subscriber = this->create_subscription<example_interfaces::msg::String>(
            "robot_news", 
            10, 
            std::bind(&SmartphoneNode::callback_robot_news, this, std::placeholders::_1));
        RCLCPP_INFO(this->get_logger(), "Smartphone has ben started.");
    }
private:
    void callback_robot_news(const example_interfaces::msg::String::SharedPtr msg)
    {
        RCLCPP_INFO(this->get_logger(), "%s", msg->data.c_str());
    }
    rclcpp::Subscription<example_interfaces::msg::String>::SharedPtr subscriber;

};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<SmartphoneNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}