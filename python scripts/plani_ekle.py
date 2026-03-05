import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
import csv
import os
import time

class PlanAppender(Node):
    def __init__(self):
        super().__init__('plan_appender_node')
        
        self.subscription = self.create_subscription(
            Path,
            '/plan',
            self.plan_callback,
            10)
        
        self.dosya_yolu = os.path.expanduser('~/benim_rotam.csv')
        # Başlangıçta dosyanın içini temizleyelim mi? 
        # Eğer 'w' yaparsan her açışta siler. 'a' yaparsan öncekilerin üstüne ekler.
        # Biz her çalıştırdığımızda sıfırdan başlasın diye 'w' ile açıp hemen kapatıyoruz.
        with open(self.dosya_yolu, 'w') as f:
            pass 

        self.last_save_time = 0
        self.get_logger().info('=== ÇOKLU ROTA KAYDEDİCİ ===')
        self.get_logger().info(f'Dosya sıfırlandı: {self.dosya_yolu}')
        self.get_logger().info('Sıradaki işlem:')
        self.get_logger().info('1. Robotu başlangıca koy (2D Pose Estimate)')
        self.get_logger().info('2. Hedefe tıkla (Nav2 Goal)')
        self.get_logger().info('3. Tekrarla...')

    def plan_callback(self, msg):
        # Nav2 saniyede çok kez yayın yapar, spam'i önlemek için 2 saniye bekleme koyalım
        current_time = time.time()
        if current_time - self.last_save_time < 2.0:
            return

        point_count = len(msg.poses)
        if point_count == 0: return

        self.get_logger().info(f'YENİ ROTA ALGILANDI! ({point_count} nokta)')
        
        # Dosyayı 'a' (append/ekle) modunda açıyoruz
        with open(self.dosya_yolu, 'a', newline='') as file:
            writer = csv.writer(file)
            for pose in msg.poses:
                x = pose.pose.position.x
                y = pose.pose.position.y
                z = 0.0
                writer.writerow([x, y, z])
                
        self.get_logger().info(f'✓ Eklendi! Toplam dosya boyutu büyüyor...')
        self.get_logger().info('Bir sonraki parça için robotu ucuna taşıyın (2D Pose Estimate).')
        
        self.last_save_time = current_time

def main(args=None):
    rclpy.init(args=args)
    node = PlanAppender()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
