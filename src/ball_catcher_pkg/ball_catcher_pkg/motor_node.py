import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from geometry_msgs.msg import Twist
import RPi.GPIO as GPIO

class MotorNode(Node):
    def __init__(self):
        super().__init__('motor_node')
        
        # GPIO Pin Definitions (BCM numbering)
        self.IN1, self.IN2, self.IN3, self.IN4 = 17, 27, 22, 23
        self.IN5, self.IN6, self.IN7, self.IN8 = 24, 25, 5, 6
        self.RPWM, self.REN = 12, 16  # BTS7960 launcher control
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        for pin in [self.IN1, self.IN2, self.IN3, self.IN4, 
                    self.IN5, self.IN6, self.IN7, self.IN8, self.REN]:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
            
        GPIO.setup(self.RPWM, GPIO.OUT)
        self.launcher_pwm = GPIO.PWM(self.RPWM, 1000) # 1kHz PWM
        self.launcher_pwm.start(0)
        GPIO.output(self.REN, GPIO.HIGH) # Enable launcher driver
        
        # ROS 2 Subscriptions
        self.subscription_cmd = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_callback, 10)
        self.subscription_launcher = self.create_subscription(
            Bool, '/launcher_cmd', self.launcher_callback, 10)
            
        self.get_logger().info("Motor Node Initialized & Ready.")

    def cmd_callback(self, msg):
        linear_x = msg.linear.x
        if linear_x > 0:
            GPIO.output(self.IN1, GPIO.HIGH); GPIO.output(self.IN2, GPIO.LOW)
            GPIO.output(self.IN3, GPIO.HIGH); GPIO.output(self.IN4, GPIO.LOW)
        else:
            GPIO.output(self.IN1, GPIO.LOW); GPIO.output(self.IN2, GPIO.LOW)
            GPIO.output(self.IN3, GPIO.LOW); GPIO.output(self.IN4, GPIO.LOW)

    def launcher_callback(self, msg):
        if msg.data:
            self.get_logger().info("Firing Launcher Flywheels!")
            self.launcher_pwm.ChangeDutyCycle(80)
        else:
            self.launcher_pwm.ChangeDutyCycle(0)

    def destroy_node(self):
        self.launcher_pwm.stop()
        GPIO.cleanup()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = MotorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()