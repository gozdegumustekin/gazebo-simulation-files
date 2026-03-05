import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import FollowPath
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
import csv
import os
import math

class RotaTakip(Node):
    def __init__(self):
        super().__init__('rota_takip_node')
        self._action_client = ActionClient(self, FollowPath, 'follow_path')
        self.get_logger().info('Rota Takipçisi Hazır! CSV dosyası okunuyor...')
        
        # 1. Rotayı Oku
        self.path_msg = self.read_csv_and_create_path()
        
        # 2. Nav2'ye Gönder
        if self.path_msg:
            self.send_goal()

    def read_csv_and_create_path(self):
        path = Path()
        path.header.frame_id = 'map'
        path.header.stamp = self.get_clock().now().to_msg()
        
        file_path = os.path.expanduser('~/benim_rotam.csv')
        
        if not os.path.exists(file_path):
            self.get_logger().error(f'Dosya bulunamadı: {file_path}')
            return None

        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            points = list(reader)
            
            # Basit bir Interpolation (Nokta Sıkılaştırma) yapalım
            # Noktalar arası çok açıksa robot sapıtır.
            # Şimdilik sadece CSV'deki ham noktaları kullanıyoruz.
            
            for row in points:
                if not row: continue
                pose = PoseStamped()
                pose.header.frame_id = 'map'
                pose.pose.position.x = float(row[0])
                pose.pose.position.y = float(row[1])
                pose.pose.position.z = 0.0
                
                # Yönelim (Orientation) hesabı şu an yok, Nav2 bunu
                # bir sonraki noktaya bakarak kendi halledecek.
                pose.pose.orientation.w = 1.0 
                
                path.poses.append(pose)
                
        self.get_logger().info(f'{len(path.poses)} adet nokta yüklendi.')
        return path

    def send_goal(self):
        self.get_logger().info('Nav2 Action Server bekleniyor...')
        self._action_client.wait_for_server()
        
        goal_msg = FollowPath.Goal()
        goal_msg.path = self.path_msg
        goal_msg.controller_id = 'FollowPath' # nav2_params.yaml içindeki ID
        goal_msg.goal_checker_id = 'general_goal_checker'

        self.get_logger().info('Rota Nav2 ye gönderiliyor...')
        self._send_goal_future = self._action_client.send_goal_async(goal_msg)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Nav2 rotayı REDDETTİ!')
            return

        self.get_logger().info('Nav2 rotayı kabul etti, Sürüş Başlıyor!')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info('Rota Tamamlandı!')
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = RotaTakip()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
