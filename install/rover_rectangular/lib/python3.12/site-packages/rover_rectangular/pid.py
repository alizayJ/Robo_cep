#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
import tf2_ros


class RectanglePIDTF(Node):

    def __init__(self):
        super().__init__('rectangle_pid_tf')

        self.get_logger().info('Closed-loop rectangle controller started')

        # Publisher
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # TF2 Buffer + Listener
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Rectangle dimensions (meters)
        self.length = 2.0
        self.width = 1.0

        # Waypoints in odom frame
        self.waypoints = [
            (0.0, 0.0),
            (self.length, 0.0),
            (self.length, self.width),
            (0.0, self.width),
            (0.0, 0.0)
        ]

        self.current_target = 1

        # PID Gains
        self.kp_linear = 0.8
        self.kp_angular = 2.0

        # Limits
        self.max_linear = 0.35
        self.max_angular = 1.0

        # Control loop timer
        self.timer = self.create_timer(0.05, self.control_loop)

    # -------------------------------------------------
    # Quaternion -> Yaw using TF2 transform data
    # -------------------------------------------------
    def quaternion_to_yaw(self, q):
        x = q.x
        y = q.y
        z = q.z
        w = q.w

        siny_cosp = 2.0 * (w * z + x * y)
        cosy_cosp = 1.0 - 2.0 * (y * y + z * z)

        return math.atan2(siny_cosp, cosy_cosp)

    # -------------------------------------------------
    # Normalize angle to [-pi, pi]
    # -------------------------------------------------
    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    # -------------------------------------------------
    # Stop robot
    # -------------------------------------------------
    def stop_robot(self):
        self.cmd_pub.publish(Twist())

    # -------------------------------------------------
    # Main Controller
    # -------------------------------------------------
    def control_loop(self):

        # Finished rectangle
        if self.current_target >= len(self.waypoints):
            self.stop_robot()
            self.get_logger().info('Rectangle completed')
            return

        try:
            transform = self.tf_buffer.lookup_transform(
                'odom',
                'base_link',
                rclpy.time.Time()
            )

        except Exception as e:
            self.get_logger().warn(f'TF unavailable: {str(e)}')
            return

        # Current robot pose
        x = transform.transform.translation.x
        y = transform.transform.translation.y
        yaw = self.quaternion_to_yaw(transform.transform.rotation)

        # Target point
        tx, ty = self.waypoints[self.current_target]

        dx = tx - x
        dy = ty - y

        distance_error = math.sqrt(dx**2 + dy**2)

        target_heading = math.atan2(dy, dx)
        heading_error = self.normalize_angle(target_heading - yaw)

        cmd = Twist()

        # Reached waypoint
        if distance_error < 0.05:
            self.get_logger().info(
                f'Reached waypoint {self.current_target}'
            )
            self.current_target += 1
            self.stop_robot()
            return

        # Angular PID (P only)
        cmd.angular.z = self.kp_angular * heading_error

        # Move only if facing target
        if abs(heading_error) < 0.25:
            cmd.linear.x = self.kp_linear * distance_error
        else:
            cmd.linear.x = 0.0

        # Saturation
        cmd.linear.x = min(cmd.linear.x, self.max_linear)

        if cmd.angular.z > self.max_angular:
            cmd.angular.z = self.max_angular
        elif cmd.angular.z < -self.max_angular:
            cmd.angular.z = -self.max_angular

        self.cmd_pub.publish(cmd)


# -------------------------------------------------
# Main
# -------------------------------------------------
def main(args=None):
    rclpy.init(args=args)

    node = RectanglePIDTF()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down...')
    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()