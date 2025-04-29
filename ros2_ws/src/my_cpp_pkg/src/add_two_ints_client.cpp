#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"

using namespace std::chrono_literals;

class AddTwoIntsClientNode : public rclcpp::Node
{
public:
    AddTwoIntsClientNode() : Node("add_two_ints_client")
    {
        client = this->create_client<example_interfaces::srv::AddTwoInts>("add_two_ints");
    }

    void callAddTwoInts(int a, int b)
    {   
        while (!client->wait_for_service(1s))
        {
            RCLCPP_WARN(this->get_logger(), "Waiting for Server");
        };
        auto request = std::make_shared<example_interfaces::srv::AddTwoInts::Request>();
        request->a = a;
        request->b = b;

        client->async_send_request(request, std::bind(&AddTwoIntsClientNode::callbackCallAddTwoInts, this, std::placeholders::_1));
    }

private:
    void callbackCallAddTwoInts(rclcpp::Client<example_interfaces::srv::AddTwoInts>::SharedFuture future)
    {
        auto response = future.get();
        RCLCPP_INFO(this->get_logger(), "Sum: %d", (int)response->sum);
    }
    rclcpp::Client<example_interfaces::srv::AddTwoInts>::SharedPtr client;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<AddTwoIntsClientNode>();
    node->callAddTwoInts(10, 5);
    node->callAddTwoInts(100, 5);
    node->callAddTwoInts(1, 1);
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
};
