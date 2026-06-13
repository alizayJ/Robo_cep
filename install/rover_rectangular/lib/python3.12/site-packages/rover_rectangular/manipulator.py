#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float64


class ManipulatorControlNode(Node):

    def __init__(self):
        super().__init__('manipulator_node')

        # Publishers
        self.pub_j1 = self.create_publisher(
            Float64,
            '/model/manipulator/joint/joint_1/cmd_pos',
            10)

        self.pub_j2 = self.create_publisher(
            Float64,
            '/model/manipulator/joint/joint_2/cmd_pos',
            10)

        # Sensor (unused)
        self.create_subscription(
            LaserScan,
            '/arm/scan',
            self.sensor_callback,
            10)

        # State
        self.start_time = self.get_clock().now()
        self.j1_target = 0.0
        self.moved = False

        # Publish frequently (important for Gazebo)
        self.timer = self.create_timer(0.1, self.control_loop)

        # INITIAL publish (first call idea)
        self.pub_j1.publish(Float64(data=0.0))
        self.pub_j2.publish(Float64(data=1.57))

        self.get_logger().info("Manipulator Node Online")

    def sensor_callback(self, msg):
        pass

    def control_loop(self):
       
        
        now = self.get_clock().now()
        elapsed = (now - self.start_time).nanoseconds * 1e-9

        # Move joint 1 after 20 seconds
        if elapsed >= 60.0:
            self.j1_target = 0.0
        elif elapsed >= 55.0:
            self.j1_target = 1.57

        # Joint 2 fixed
        j2 = 1.57

        # Continuous publishing (required for Gazebo)
        self.pub_j1.publish(Float64(data=self.j1_target))
        self.pub_j2.publish(Float64(data=j2))


def main(args=None):
    rclpy.init(args=args)
    node = ManipulatorControlNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()