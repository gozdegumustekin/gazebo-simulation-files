import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class KirmiziKutuTespit(Node):
    def __init__(self):
        super().__init__('kirmizi_kutu_tespit')
        
        # Robotun kamera konusuna abone oluyoruz
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw', 
            self.image_callback,
            10)
        
        self.bridge = CvBridge()
        self.get_logger().info('Kamera Tespiti Başladı! Kırmızı kutu aranıyor...')

    def image_callback(self, msg):
        try:
            # 1. ROS mesajını OpenCV görüntüsüne çevir
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # 2. Görüntüyü HSV formatına çevir (Renk tespiti için en iyisi)
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            
            # 3. Kırmızı Renk Aralığını Belirle
            # Alt Kırmızı (0-10 arası)
            lower_red1 = np.array([0, 120, 70])
            upper_red1 = np.array([10, 255, 255])
            
            # Üst Kırmızı (170-180 arası)
            lower_red2 = np.array([170, 120, 70])
            upper_red2 = np.array([180, 255, 255])
            
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            
            mask = mask1 + mask2
            
            # 4. Gürültüleri temizle
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            # 5. Kontürleri (Çerçeveleri) Bul
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 500: # Yeterince büyükse
                    x, y, w, h = cv2.boundingRect(cnt)
                    # Yeşil Çerçeve Çiz
                    cv2.rectangle(cv_image, (x, y), (x + w, y + h), (0, 255, 0), 3)
                    cv2.putText(cv_image, "Kutu Bulundu", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # 6. Sonucu Göster
            cv2.imshow("Robot Kamerasi", cv_image)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f'Hata: {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    node = KirmiziKutuTespit()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
