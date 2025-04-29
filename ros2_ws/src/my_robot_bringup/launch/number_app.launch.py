from launch import LaunchDescription
from launch_ros.actions import Node



def generate_launch_description():
    ld = LaunchDescription()

    number_publisher = Node(
        package="A2",
        executable="counter_pub"
    )

    number_subscriber = Node(
        package="A2",
        executable="counter_sub"
    )

    ld.add_action(number_publisher)
    ld.add_action(number_subscriber)
    return ld