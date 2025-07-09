import cv2
import os
import numpy as np
import base64
from AnalyzeOnRoadBase import AnalyzeOnRoadBase

# Đặt như này để tránh trường hợp lỗi do dùng chung thư viện AI 
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

class AnalyzeOnRoad(AnalyzeOnRoadBase):
    """Class này kế thừa từ class Base (xử lý tuần tự). Class con này chưa phải là code để multiprocessing\
    mà chỉ là một chút cải tiến từ code base (class Base) để có thể vừa xử lý video đầu vào ở một process\
    khác vừa có thể truy xuất thông tin về kết quả mà không bị hiện tượng tranh chấp dữ liệu
    
    """    
    def __init__(self, path_video, meter_per_pixel, info_dict, frame_dict, 
                 lock_info, lock_frame, model_path="best.pt", time_step=30,
                 is_draw=True, device='cpu', iou=0.3, conf=0.2, show=True):
        """Class này kế thừa từ class Base (xử lý tuần tự). Class con này chưa phải là code để multiprocessing\
        mà chỉ là một chút cải tiến từ code base (class Base) để có thể vừa xử lý video đầu vào ở một process\
        khác vừa có thể truy xuất thông tin về kết quả mà không bị hiện tượng tranh chấp dữ liệu

        Args:
            path_video (str): Đường dẫn đến video
            meter_per_pixel (float): Tỉ lệ 1 mét ngoài đời với 1 pixel
            lock_info (Manager().Lock()): Khoá để lấy và cập nhật dữ liệu thông tin các phương tiện hiện tại.
            lock_frame (Manager().Lock()): Khoá lấy để và cập nhật dữ liệu frame hiện tại.
            info_dict (Manager().dict()): Một dict dùng để chia sẽ giữ liệu trung gian giữa các process với nhau,\
            mặc định là sẽ được truyền tham chiếu và nó sẽ được thay đỏi nếu các process con thay đổi nó cho nên\
            ta có thể truy cập dữ liệu kết quả xử lý ở bên ngoài dễ dàng nhưng phải đảm bảo truy cập an toàn
            frame_dict (Manager().dict()): Tương tự info_dict nhưng dùng để chứa thông tin mã hoá base64 của ảnh.\
            Lý do tại sao dùng dict mà không dùng Manager().Value(str, "") là do tính bất biến của str dễ bị lỗi.\
            Dùng dict thay thế thì cấu trúc nó sẽ như sau {"frame": <base64 string>}
            model_path (str): Đường dẫn đến model. Defaults to "best.pt".
            time_step (int): Khoảng thời gian giữa 2 lần cập nhật thông tin các phương tiện. Defaults to 30.
            is_draw (bool): Biến chỉ định có vẽ các thông tin xử lý được lên frame hay không. Defaults to True.
            device (str): Dùng GPU hoặc CPU. Defaults to 'cpu'.
            iou (float): Ngưỡng tin cậy về bounding box . Defaults to 0.3.
            conf (float): Ngưỡng tin cậy về nhãn được dự đoán. Defaults to 0.2.
            show (bool): Hiển thị video xử lý qua opencv, đặt là False khi tích làm server tránh lãng phí tài nguyên.\
            Defaults to True.
            
        Examples:
        Hướng dẫn chạy xử lý 1 video đơn
        >>> analyzer = AnalyzeOnRoad(
        >>>     path_video=path_video,
        >>>     meter_per_pixel=meter_per_pixel,
        >>>     info_dict=info_dict,
        >>>     frame_dict=frame_dict,
        >>>     lock_info=lock_info,
        >>>     lock_frame=lock_frame,
        >>>     **kwargs
        >>> )
        >>> analyzer.process_on_single_video()
        """
        super().__init__(path_video, meter_per_pixel, model_path, time_step,
                 is_draw, device, iou, conf, show)
        self.lock_info = lock_info
        self.lock_frame = lock_frame
        self.info_dict = info_dict
        self.frame_dict = frame_dict
        
    def convert_frame_to_base64(self, img: np.array) -> str:
        """ Hàm chuyển đổi ảnh dạng numpy sang base64

        Args:
            img (np.array): dũ liệu ảnh được đọc bởi cv2

        Returns:
            str: mã base64
        """
        if img is not None:
            try:
                _, jpeg = cv2.imencode('.jpg', img)
                return base64.b64encode(jpeg.tobytes()).decode('utf-8')
            except Exception as e:
                print(f"Lỗi chuyển đổi sang base64 của {self.name}: {e}")
                return None
        return None

    def update_for_frame(self):
        """Hàm ghi đè hàm ở class cha cập nhật frame đang xử lý hiện tại, chuyển qua base64 và gán vào Manage.dict()\
        để chia sẽ dữ liệu các process với nhau dễ dàng. 
        
        Thực hiện việc lấy khoá Manager().Lock() rồi mới cập nhật để tránh data hazard
        >>> with self.lock_frame:
        >>>     self.frame_dict["frame"] = self.convert_frame_to_base64(self.frame_output)
        
        """
        try: 
            with self.lock_frame:
                self.frame_dict["frame"] = self.convert_frame_to_base64(self.frame_output)
        except Exception as e:
            print(f"Lỗi khi chuyển đổi frame sang base64 hoặc lỗi khoá lock của process của {self.name}: {e}")

    def update_for_vehicle(self):
        """Hàm ghi đè hàm ở class cha cập nhật thông tin về processing đang xử lý hiện tại và gán vào Manage.dict()\ 
        để chia sẽ với nhau. Thực hiện việc lấy khoá Manager().Lock() rồi mới cập nhật để tránh data hazard"""
        try:
            with self.lock_info:
                self.info_dict["count_car"] = self.count_car_display
                self.info_dict["count_motor"] = self.count_motor_display
                self.info_dict["speed_car"] = self.speed_car_display
                self.info_dict["speed_motor"] = self.speed_motor_display
        except Exception as e:
            print(f"Lỗi khi update thông tin phương tiện của {self.name}: {e}")

#************************************************************************ Script for testing *******************************************************
if __name__ == "__main__":
    from multiprocessing import Manager
    manager = Manager()
    lock_info = manager.Lock()
    lock_frame = manager.Lock()
    
    # Example usage
    path_video = "./video_test/Đường Láng.mp4"
    meter_per_pixel = 0.04
    info_dict = manager.dict({"count_car": 0,
                             "count_motor": 0,
                             "speed_car": 0,
                             "speed_motor": 0})
    frame_dict = manager.dict({"frame": None})
    
    analyzer = AnalyzeOnRoad(
        path_video=path_video,
        meter_per_pixel=meter_per_pixel,
        info_dict=info_dict,
        frame_dict=frame_dict,
        lock_info=lock_info,
        lock_frame=lock_frame,
        show=True
    )
    
    analyzer.process_on_single_video()