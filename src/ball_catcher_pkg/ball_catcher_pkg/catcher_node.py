import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from geometry_msgs.msg import Twist
import time

class CatcherNode(Node):
    def __init__(self):
        super().__init__('catcher_node')
        self.sub_ball = self.create_subscription(Bool, '/ball_detected', self.ball_callback, 10)
        self.pub_launcher = self.create_publisher(Bool, '/launcher_cmd', 10)
        self.pub_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info("Catcher Behavior Node Active.")

    def ball_callback(self, msg):
        if msg.data:
            self.get_logger().info("Ball caught in funnel! Triggering return launcher...")
            
            stop_twist = Twist()
            self.pub_vel.publish(stop_twist)
            
            launch_msg = Bool()
            launch_msg.data = True
            self.pub_launcher.publish(launch_msg)
            
            time.sleep(1.5)
            
            launch_msg.data = False
            self.pub_launcher.publish(launch_msg)

def main(args=None):
    rclpy.init(args=args)
    node = CatcherNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()