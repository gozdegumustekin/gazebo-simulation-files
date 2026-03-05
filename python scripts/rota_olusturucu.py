import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped
import csv
import os

class RotaKaydedici(Node):
    def __init__(self):
        super().__init__('rota_kaydedici')
        
        # RViz'den gelen tıklamaları dinle
        self.subscription = self.create_subscription(
            PointStamped,
            '/clicked_point',
            self.point_callback,
            10)
        
        self.points = []
        self.get_logger().info('Rota Kaydedici Başlatıldı! RViz üzerinden "Publish Point" ile noktaları seçin.')
        self.get_logger().info('Bitirmek ve kaydetmek için terminalde Ctrl+C yapın.')

    def point_callback(self, msg):
        x = msg.point.x
        y = msg.point.y
        # Z eksenini sıfırlıyoruz (yerde gidiyoruz)
        z = 0.0
        
        self.points.append([x, y, z])
        self.get_logger().info(f'Nokta Eklendi: X={x:.2f}, Y={y:.2f}')

    def save_to_file(self):
        # Dosyayı ev dizinine kaydet
        file_path = os.path.expanduser('~/xyz_noktalari.csv')
        
        if not self.points:
            self.get_logger().warn('Hiç nokta seçilmedi, dosya kaydedilmiyor.')
            return

        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            # Başlık satırı (opsiyonel, biz direkt veri yazalım)
            # writer.writerow(["x", "y", "z"]) 
            writer.writerows(self.points)
            
        self.get_logger().info(f'BAŞARILI: {len(self.points)} nokta şuraya kaydedildi: {file_path}')

def main(args=None):
    rclpy.init(args=args)
    node = RotaKaydedici()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.save_to_file()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
