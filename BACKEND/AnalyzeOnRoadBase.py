import cv2
import os
import numpy as np
from datetime import datetime
from ultralytics import solutions
# Set environment variable to avoid KMP duplicate library error
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

class AnalyzeOnRoadBase:
    """Class gói gọn script xử lý tuần tự nhưng đảm bảo tính đóng gói OOP
        Attributes:
            count_car_display (int): số lượng xe oto trung bình
            speed_car_display (int): trung bình tốc độ tức thời của oto
            count_moto_display (int): số lượng xe xe máy trung bình
            speed_moto_display (int): trung bình tốc độ tức thời của xe máy
            speed_tool (solutions.SpeedEstimator()): đối tượng SpeedEstimator của YOLO
            frame_output (np.array): ảnh đã qua xử lý được vẽ hoặc không vẽ (tuỳ vào biến is_draw)\
            các thông tin được chuẩn đoán
        Examples:
            Hướng dẫn chạy xử lý 1 video đơn
            >>> analyzer = AnalyzeOnRoadBase(
            >>>     path_video=path_video,
            >>>     meter_per_pixel=meter_per_pixel,
            >>>     info_dict=info_dict,
            >>>     frame_dict=frame_dict,
            >>>     lock_info=lock_info,
            >>>     lock_frame=lock_frame,
            >>> )
            >>> analyzer.process_on_single_video()
    """
    def __init__(self, path_video, meter_per_pixel, model_path="best.pt", time_step=30,
                 is_draw=True, device='cpu', iou=0.3, conf=0.2, show=True):
        """Hàm xử lý uần tự như một Script đơn giản áp dụng YOLO và cải tiến hơn là ở việc gói gọn trong 1 class

        Args:
            path_video (str): Đường dẫn đến video
            meter_per_pixel (float): Tỉ lệ 1 mét ngoài đời với 1 pixel
            model_path (str): Đường dẫn đến model. Defaults to "best.pt".
            time_step (int): Khoảng thời gian giữa 2 lần cập nhật thông tin các phương tiện. Defaults to 30.
            is_draw (bool): Biến chỉ định có vẽ các thông tin xử lý được lên frame hay không. Defaults to True.
            device (str): Dùng GPU hoặc CPU. Defaults to 'cpu'.
            iou (float): Ngưỡng tin cậy về bounding box . Defaults to 0.3.
            conf (float): Ngưỡng tin cậy về nhãn được dự đoán. Defaults to 0.2.
            show (bool): Hiển thị video xử lý qua opencv, đặt là False khi tích làm server tránh lãng phí tài nguyên.\
            Defaults to True.
        """
        self.speed_tool = solutions.SpeedEstimator(
            model=model_path,
            verbose=False,
            show=False,
            device=device,
            iou=iou,
            conf=conf,
            meter_per_pixel=meter_per_pixel,
            max_hist=15
        )
        
        self.show = show
        self.path_video = path_video
        self.name = path_video.split('/')[-1][:-4] 
        
        self.count_car_display = 0
        self.list_count_car = []
        self.speed_car_display = 0
        self.list_speed_car = []
        
        self.count_motor_display = 0
        self.list_count_motor = []
        self.speed_motor_display = 0
        self.list_speed_motor = []
        
        self.time_pre = datetime.now()
        self.frame_output = None
        self.time_step = time_step
        self.frame_predict = None
        self.is_draw = is_draw
        self.delta_time = 0

    def convert_frame_to_base64(self, img):
        """Dành cho subclass định nghĩa, do không cần ở hiện tại"""
        pass
    def update_for_frame(self):
        """Dành cho subclass định nghĩa, do không cần ở hiện tại"""
        pass
    def update_for_vehicle(self):
        """Dành cho subclass định nghĩa, do không cần ở hiện tại"""
        pass
    def safe_avg_np(self, lst: list) -> int:
        """Hàm tính trung bình cộng các số dương

        Args:
            lst (list): list các số đầu vào (tốc độ tức thời các phương tiện)

        Returns:
            int: giá trị trung bình
        """
        arr = np.array(lst, dtype=np.int32)
        non_zero = arr[arr != 0]
        return int(non_zero.mean()) if non_zero.size > 0 else 0
    
    def update_data(self):
        """Hàm này sẽ được gọi để cập nhật dữ liệu cho frame và thông tin phương tiện sau một khoảng thời gian\
            đã thiết lập là time_step"""

        # Gọi hàm này để cập nhật dữ liệu cho frame (luôn được cập nhật đảm bảo tính realtime)
        # Cái này dành cho subclass để cập nhật frame_output 
        self.update_for_frame()
        
        # Tính toán thời gian đã trôi qua kể từ lần cập nhật trước và cập nhật thông tin các phương tiện nếu đủ thời gian đã thiết lập
        time_now = datetime.now()
        self.delta_time = (time_now - self.time_pre).total_seconds()
        
        # Khi đủ thời gian đã thiết lập, cập nhật thông tin phương tiện và reset danh sách
        if self.delta_time >= self.time_step:
            self.time_pre = time_now
            
            # Tính toán trung bình các giá trị trong danh sách
            self.count_car_display = self.safe_avg_np(self.list_count_car)
            self.speed_car_display = self.safe_avg_np(self.list_speed_car)
            self.count_motor_display = self.safe_avg_np(self.list_count_motor)
            self.speed_motor_display = self.safe_avg_np(self.list_speed_motor)
            
            # Cập nhật thông tin phương tiện vào info_dict, cái này dành cho subclass ghi đè để cập nhật thông tin phương tiện
            self.update_for_vehicle()
            
            # Reset danh sách để chuẩn bị cho lần cập nhật tiếp theo
            self.list_count_car.clear()
            self.list_count_motor.clear()
            self.list_speed_car.clear()
            self.list_speed_motor.clear()
   
    def process_single_frame(self, frame_input):
        """Hàm này xử lý từng frame một 
        Args:
            frame_input (np.array): Ảnh được đọc từ opencv
        
        >>> self.speed_tool.track_data
        Lệnh trên sẽ truy suất thông tin tracking được từ frame đầu vào
        >>> self.speeds = self.speed_tool.spd
        >>> self.ids = self.speed_tool.track_data.id.cpu().numpy().astype('int')
        >>> self.boxes = self.speed_tool.track_data.xyxy.cpu().numpy().astype('int')
        >>> self.classes = self.speed_tool.track_data.cls.cpu().numpy().astype('int')
        Tốc độ là một dict với key là id của phương tiện và value là tốc độ tương ứng
        ids là một numpy array chứa id của các phương tiện
        boxes là một numpy array chứa bounding boxes của các phương tiện
        classes là một numpy array chứa class của các phương tiện (0: ô tô, 1: xe máy)
        """
        
        try:
            # Đặt lại kích thước ảnh đầu vào đủ lớn để xử lý, copy để tránh thay đổi ảnh gốc, cắt ảnh để chỉ predict vùng cần thiết
            frame_in = cv2.resize(frame_input, (600, 400))
            self.frame_output = frame_in.copy()
            self.frame_predict = np.ascontiguousarray(frame_in[130:, 50:])
            
            # Xử lý ảnh để dự đoán tốc độ
            # Sao chép frame_predict để tránh thay đổi ảnh gốc, sau đó xử lý
            frame_predict_cp = self.frame_predict.copy()
            self.speed_tool.process(frame_predict_cp)
            self.speed_tool.region = np.array([[50, 400], [50, 280], [370, 130], [600, 130], [600, 400]], np.int32) - np.array([[50, 130]])
            
            # Lấy dữ liệu từ speed_tool như tốc độ, id, bounding boxes và class 
            self.speeds = self.speed_tool.spd
            self.ids = self.speed_tool.track_data.id.cpu().numpy().astype('int')
            self.boxes = self.speed_tool.track_data.xyxy.cpu().numpy().astype('int')
            self.classes = self.speed_tool.track_data.cls.cpu().numpy().astype('int')
            
            # Tính toán số lượng ô tô và xe máy, lưu vào danh sách            
            count_car = np.count_nonzero(self.classes == 0)
            count_motor = np.count_nonzero(self.classes == 1)
            self.list_count_car.append(count_car)
            self.list_count_motor.append(count_motor)
            
            # Lấy id của ô tô và xe máy, sau đó lấy tốc độ tương ứng từ speeds (speeds là một dict)
            car_ids = self.ids[self.classes == 0]
            motor_ids = self.ids[self.classes == 1]
            self.list_speed_car.extend([self.speeds[tid] for tid in car_ids if tid in self.speeds])
            self.list_speed_motor.extend([self.speeds[tid] for tid in motor_ids if tid in self.speeds])

            # Vẽ đè lên hình các thông tin 
            if self.is_draw:
                self.draw_info_to_frame_output()
            
            # Tính toán xong xuôi sẽ gọi hàm update_data để cập nhật data ngay lập tức
            self.update_data()
        except Exception as e:
            print(f"Lỗi khi xử lý với file {self.name}: {e}")
    def draw_info_to_frame_output(self):
        """Hàm này để vẽ các thông tin lên ảnh"""
        try:
            # Đặt vùng cần chú ý
            pts = np.array([[50, 400], [50, 265], [370, 130], [600, 130], [600, 400]], np.int32).reshape((-1, 1, 2))
            
            if self.ids is not None:
                for i, box in enumerate(self.boxes):
                    # Lấy tâm các box
                    x1, y1, x2, y2 = box
                    cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)

                    # Kiểm tra nếu không thuộc vùng quan tâm thì không hiển thị
                    result = cv2.pointPolygonTest(pts, (cx + 50, cy + 130), False)
                    if result < 0:
                        continue
                    
                    # Lấy thông tin về phương tiện
                    track_id = self.ids[i]
                    class_id = self.classes[i]
                    speed_id = self.speeds.get(track_id, 0)
                    
                    # Thiết đặt label (tốc độ) và màu sắc
                    label = f"{str(speed_id)} km/h"
                    color = (0, 0, 255) if class_id == 1 else (255, 0, 0)
                    
                    # Vẽ lên frame
                    cv2.putText(self.frame_predict, label, (cx - 50, cy - 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (51, 153, 255), 2)
                    cv2.circle(self.frame_predict, (cx, cy), 6, color, -1)

            # Gắn lại vùng được cắt để predict lại vào frame ban đầu
            self.frame_output[130:, 50:] = self.frame_predict
            
            # Cuối cùng vẽ các thông tin tổng quát
            cv2.polylines(self.frame_output, [pts], isClosed=True, color=(0, 255, 255), thickness=4)
            cv2.putText(self.frame_output, f"Xe may: {self.count_motor_display} xe, Vtb = {self.speed_motor_display} km/h", (5, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 200), 3)
            cv2.putText(self.frame_output, f"O to: {self.count_car_display} xe, Vtb = {self.speed_car_display} km/h", (5, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 0, 0), 3)
        except Exception as e:
            print(f"Lỗi khi vẽ: {e}")
    
    def process_on_single_video(self):
        """Hàm này sẽ được gọi để xử lý video bằng việc đọc từng frame và xử lý từng frame một"""
        cam = cv2.VideoCapture(self.path_video)
        
        if not cam.isOpened():
            print(f'Không thể mở video: {self.path_video}')
            return
        
        try:
            while True:
                check, cap = cam.read()
                if not check:
                    print(f'Kết thúc video: {self.path_video}')
                    # Restart video để loop
                    cam.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                # Xử lý từng frame một
                self.process_single_frame(cap)
                
                # Hiển thị frame nếu show là True            
                if self.show:
                    cv2.imshow(f'{self.name}', self.frame_output)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    
        except KeyboardInterrupt:
            print(f"Đã dừng xử lý {self.name}")
        except Exception as e:
            print(f"Lỗi khi xử lý {self.name}: {e}")
        finally:
            # Giải phóng tài nguyên
            cam.release()
            if self.show:
                cv2.destroyAllWindows()

#************************************************************************ Script for testing *******************************************************
if __name__ == "__main__":
    # Example usage
    path_video = "./video_test/Đường Láng.mp4"
    meter_per_pixel = 0.04
    
    analyzer = AnalyzeOnRoadBase(
        path_video=path_video,
        meter_per_pixel=meter_per_pixel,
        show=True
    )
    
    analyzer.process_on_single_video()