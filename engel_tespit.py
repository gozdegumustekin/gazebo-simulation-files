import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

class EngelTespit(Node):
    def __init__(self):
        super().__init__('engel_tespit_dugumu')
        
        # /scan topiğine abone oluyoruz
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)
            
        self.tehlike_mesafesi = 0.5  # Metre cinsinden (50 cm)

    def scan_callback(self, msg):
        # 0. indeks robotun tam önündeki mesafeyi verir
        on_mesafe = msg.ranges[0]
        
        # Lidar bazen ölçemediği yerler için 'inf' (sonsuz) veya 0 değerini döndürür.
        # Bunu filtrelemek için basit bir kontrol:
        if on_mesafe == float('inf') or on_mesafe == 0.0:
            on_mesafe = 99.0  # Güvenli, uzak bir değer atıyoruz

        # Mesafeyi kontrol et
        if on_mesafe < self.tehlike_mesafesi:
            self.get_logger().warn(f'DİKKAT! Önde engel var. Mesafe: {on_mesafe:.2f} metre')
        else:
            self.get_logger().info(f'Yol açık. Ön mesafe: {on_mesafe:.2f} metre')

def main(args=None):
    rclpy.init(args=args)
    dugum = EngelTespit()
    
    try:
        rclpy.spin(dugum) # Düğümü sürekli çalışır halde tutar
    except KeyboardInterrupt:
        pass
        
    dugum.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
