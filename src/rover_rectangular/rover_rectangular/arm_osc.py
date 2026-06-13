#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from sensor_msgs.msg import LaserScan  # common for Gazebo ultrasonic/lidar

class ArmController(Node):

    def __init__(self):
        super().__init__('arm_controller')

        # ---------------- JOINT PUBLISHERS ----------------
        self.joint1_pub = self.create_publisher(
            Float64,
            '/model/manipulator/joint/joint_1/cmd_pos',
            10
        )

        self.joint2_pub = self.create_publisher(
            Float64,
            '/model/manipulator/joint/joint_2/cmd_pos',
            10
        )

        # ---------------- STATE ----------------
        self.obstacle_detected = False
        self.joint1_position = 0.0

        # ---------------- SENSOR SUBSCRIBER ----------------
        self.create_subscription(
            LaserScan,
            '/arm/scan',   
            self.sensor_callback,
            10
        )

        # ---------------- STARTUP ACTION ----------------
        self.send_joint2_once()
        self.send_joint2_once()
        self.send_joint2_once()


        # ---------------- CONTROL LOOP ----------------
        self.timer = self.create_timer(6.0, self.control_loop)

        self.get_logger().info("Robot Controller Started")

    # =====================================================
    # Joint 2 moves once
    # =====================================================
    def send_joint2_once(self):
        msg = Float64()
        msg.data = 1.57
        self.joint2_pub.publish(msg)
        self.get_logger().info("Joint2 moved once to 1.57 rad")

    # =====================================================
    # SENSOR CALLBACK
    # =====================================================
    def sensor_callback(self, msg: LaserScan):

        # take minimum distance in range
        min_dist = min(msg.ranges)

        # threshold (adjust based on your sensor)
        if min_dist < 0.5:
            self.obstacle_detected = True
        else:
            self.obstacle_detected = False

    # =====================================================
    # CONTROL LOGIC
    # =====================================================
    def control_loop(self):

        msg = Float64()

        if self.obstacle_detected:

            # move joint 1 to 90 degrees
            if self.joint1_position == 0.0:
                self.joint1_position = 1.57
                self.get_logger().info("Obstacle detected → Joint1 to 1.57")

            else:
                # return back after some time
                self.joint1_position = 0.0
                self.get_logger().info("Returning Joint1 to 0")

        else:
            # idle state
            self.joint1_position = 0.0

        msg.data = self.joint1_position
        self.joint1_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ArmController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()