#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time
import math

class RectangularNode(Node): 
    def __init__(self):
        super().__init__("Rectangular_node")
        self.get_logger().info("Rectangular node has started")
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)

        # Parameters
        self.linear_speed = 0.5    # m/s 
        self.angular_speed = 0.5   # rad/s 
        self.length = 2.0      # meters  First
        self.width = 5.0          # meters second 

        # Create a timer to start the logic AFTER the node is fully initialized
        self.timer = self.create_timer(1.0, self.run_logic)
        self.already_running = False

    def run_logic(self):
        # Ensure we only start the loop once
        if self.already_running:
            return
        self.already_running = True
        
        self.get_logger().info("Starting Rectangle Loop")
        self.move_rectangle()

    def publish_velocity(self, lin, ang):
        msg = Twist()
        msg.linear.x = float(lin) # Ensure it's a float
        msg.angular.z = float(ang)
        self.publisher_.publish(msg)

    def stop_robot(self):
        self.publish_velocity(0.0, 0.0)

    def move_straight(self, distance):
        duration = distance / self.linear_speed
        self.get_logger().info(f"Moving straight for {duration:.2f}s")
        start = self.get_clock().now() # Use ROS Clock instead of time.time()

        # Use the node's clock for better Gazebo compatibility
        while (self.get_clock().now() - start).nanoseconds / 1e9 < duration:
            if not rclpy.ok(): break
            self.publish_velocity(self.linear_speed, 0.0)
            time.sleep(0.1)

        self.stop_robot()
        time.sleep(1)

    def turn_90(self):
        angle = 1.5*math.pi 
        duration = angle / self.angular_speed
        self.get_logger().info(f"Turning for {duration:.2f}s")
        start = self.get_clock().now()

        while (self.get_clock().now() - start).nanoseconds / 1e9 < duration:
            if not rclpy.ok(): break
            self.publish_velocity(0.0, self.angular_speed)
            time.sleep(0.1)

        self.stop_robot()
        time.sleep(1)

    def move_rectangle(self):
        while rclpy.ok():
            self.move_straight(self.length)
            self.turn_90()
            self.move_straight(self.width)
            self.turn_90()
           
def main(args=None):
    rclpy.init(args=args)
    node = RectangularNode()    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()