#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time
import math


class LShapeNode(Node):

    def __init__(self):

        super().__init__("l_shape_node")

        self.get_logger().info("L Shape Node Started")

        self.publisher_ = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Parameters
        self.linear_speed = 0.5      # m/s
        self.angular_speed = 0.5     # rad/s

        self.first_length = 2.0      # First line
        self.second_length = 4.0     # Second line

        self.timer = self.create_timer(
            1.0,
            self.run_logic
        )

        self.already_running = False

    def run_logic(self):

        if self.already_running:
            return

        self.already_running = True

        self.get_logger().info("Starting L Shape Motion")

        self.move_l_shape()

    def publish_velocity(self, lin, ang):

        msg = Twist()

        msg.linear.x = float(lin)
        msg.angular.z = float(ang)

        self.publisher_.publish(msg)

    def stop_robot(self):

        self.publish_velocity(0.0, 0.0)

    def move_straight(self, distance):

        duration = distance / self.linear_speed

        self.get_logger().info(
            f"Moving straight for {duration:.2f} seconds"
        )

        start = self.get_clock().now()

        while (
            (self.get_clock().now() - start).nanoseconds / 1e9
            < duration
        ):

            if not rclpy.ok():
                break

            self.publish_velocity(
                self.linear_speed,
                0.0
            )

            time.sleep(0.1)

        self.stop_robot()

        time.sleep(1)

    def turn_90(self):

        angle = math.pi 

        duration = angle / self.angular_speed

        self.get_logger().info(
            f"Turning for {duration:.2f} seconds"
        )

        start = self.get_clock().now()

        while (
            (self.get_clock().now() - start).nanoseconds / 1e9
            < duration
        ):

            if not rclpy.ok():
                break

            self.publish_velocity(
                0.0,
                self.angular_speed
            )

            time.sleep(0.1)

        self.stop_robot()

        time.sleep(1)

    def move_l_shape(self):

        # First segment
        self.move_straight(self.first_length)

        # 90 degree turn
        self.turn_90()

        # Second segment
        self.move_straight(self.second_length)

        # Final stop
        self.stop_robot()

        self.get_logger().info("L Shape Completed")


def main(args=None):

    rclpy.init(args=args)

    node = LShapeNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:

        node.get_logger().info("Shutting down...")

    finally:

        node.destroy_node()

        rclpy.shutdown()


if __name__ == '__main__':
    main()