import cv2
import os
import numpy as np
from datetime import datetime
from ultralytics import solutions
import base64
# Set environment variable to avoid KMP duplicate library error
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


class AnalyzeOnRoad:
    def __init__(self, path_video = None, model_path = "best.pt", time_step = 30,
                 is_draw = True, device= 'cpu', iou = 0.3, conf = 0.2, meter_per_pixel = 0.05, show = True):
        self.speed_tool = solutions.SpeedEstimator(
            model = model_path,
            verbose = False,
            show = False,
            device = device,
            iou = iou,
            conf = conf,
            meter_per_pixel = meter_per_pixel,
        )
        # DEBUG: Print available methods of SpeedEstimator
        # print("SpeedEstimator methods:", dir(self.speed_tool))  # <--- Thêm dòng này
        self.show = show
        self.path_video = path_video
        self.count_car_display = 0
        self.list_count_car = []
        self.speed_car_display = 0
        self.list_speed_car = []
        
        self.count_motor_display = 0
        self.list_count_motor = []
        self.speed_motor_display = 0
        self.list_speed_motor = []
    
        self.time_pre = datetime.now()
        self.result = {
            "frame": None,  # Sẽ được cập nhật sau khi xử lý frame
            "count_car": 0,
            "count_motor": 0,
            "speed_car": 0,
            "speed_motor": 0,
        }
        self.frame_output = None
        self.time_step = time_step
        self.frame_predict = None
        self.is_draw = is_draw
        self.delta_time = 0
        
    def update_data_for_vehicle(self):
        self.update_for_frame()
        
        time_now = datetime.now()
        self.delta_time = (time_now - self.time_pre).total_seconds()
        
        if self.delta_time >= self.time_step:
            self.time_pre = time_now
            
            if self.list_count_car:
                self.count_car_display = sum(self.list_count_car) // len(self.list_count_car)
            else:
                self.count_car_display = 0

            if self.list_speed_car:
                self.speed_car_display = sum(self.list_speed_car) // len(self.list_speed_car)
            else:
                self.speed_car_display = 0

            if self.list_count_motor:
                self.count_motor_display = sum(self.list_count_motor) // len(self.list_count_motor)
            else:
                self.count_motor_display = 0

            if self.list_speed_motor:
                self.speed_motor_display = sum(self.list_speed_motor) // len(self.list_speed_motor)
            else:
                self.speed_motor_display = 0
            
            self.update_for_vehicle()
            
            self.list_count_car.clear()
            self.list_count_motor.clear()
            self.list_speed_car.clear()
            self.list_speed_motor.clear()
            
    def update_for_frame(self):
        # Encode frame sang JPEG
        _, jpeg = cv2.imencode('.jpg', self.frame_output)
        # chuyển sang base64
        self.result["frame"] = base64.b64encode(jpeg.tobytes()).decode('utf-8')
    def update_for_vehicle(self):
        self.result["count_car"] = self.count_car_display
        self.result["count_motor"] = self.count_motor_display
        self.result["speed_car"] = self.speed_car_display
        self.result["speed_motor"] = self.speed_motor_display
    def process_single_frame(self, frame_input) -> None:   
        frame_in = cv2.resize(frame_input.copy(), (1600, 1200))
        self.frame_output = frame_in.copy()
        self.frame_predict = np.ascontiguousarray(frame_in[540:, 150:])
        
        frame_predict_cp = self.frame_predict.copy()
        self.speed_tool.process(frame_predict_cp)
        
        self.speeds = self.speed_tool.spd    
        self.ids = self.speed_tool.track_data.id.cpu().numpy().astype('int')
        self.boxes = self.speed_tool.track_data.xyxy.cpu().numpy().astype('int')
        self.classes = self.speed_tool.track_data.cls.cpu().numpy().astype('int')
    
        count_car = np.count_nonzero(self.classes == 0)    
        count_motor = np.count_nonzero(self.classes == 1)
        self.list_count_car.append(count_car)
        self.list_count_motor.append(count_motor)
        
        car_ids = self.ids[self.classes == 0]
        motor_ids = self.ids[self.classes == 1]
        self.list_speed_car.extend([self.speeds[tid] for tid in car_ids if tid in self.speeds])
        self.list_speed_motor.extend([self.speeds[tid] for tid in motor_ids if tid in self.speeds])

        if self.is_draw:
            self.draw_info_to_frame_output()
        
        self.update_data_for_vehicle()
                    
    def draw_info_to_frame_output(self):
        if self.ids is not None:
            for i, box in enumerate(self.boxes):
                track_id = self.ids[i]
                class_id = self.classes[i]
                speed_id = self.speeds.get(track_id, 0)  # 0 là giá trị mặc định nếu không tìm thấy

                x1, y1, x2, y2 = box
                cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
                    
                label = f"{str(speed_id)} km/h" if class_id == 0 else f"{str(speed_id)} km/h"
                color = (0, 0, 255) if class_id == 1 else (255, 0, 0)
                
                # cv2.putText(self.frame_predict, label, (cx - 50, cy - 15),
                            # cv2.FONT_HERSHEY_SIMPLEX, 0.9, (51, 153, 255), 3)
                # cv2.circle(self.frame_predict, (cx, cy), 6, color, -1)

        self.frame_output[540:, 150:] = self.frame_predict
        
        cv2.rectangle(self.frame_output, (150, 540), (1600, 1200), (0, 255, 255), 4)
        cv2.putText(self.frame_output, f"Xe may: {self.count_motor_display} xe, Vtb = {self.speed_motor_display} km/h", (15, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 2.8, (0, 0, 200), 14)
        cv2.putText(self.frame_output, f"O to: {self.count_car_display} xe, Vtb = {self.speed_car_display} km/h", (15, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 2.8, (200, 0, 0), 14)
    
    def process_on_single_video(self):
        cam = cv2.VideoCapture(self.path_video)
            
        while True:
            check, cap = cam.read()
            if not check:
                print('Khong doc duoc video')
            
            self.process_single_frame(cap)

            frame_display = cv2.resize(self.frame_output, (600, 400))
            if(self.show):
                cv2.imshow('out', frame_display)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        if self.show:
            cam.release()
            cv2.destroyAllWindows()
            
            




#***************************************************  Code for testing script  *********************************************************************#

if __name__ == '__main__':
    obj = AnalyzeOnRoad(path_video= './video_test/Ngã Tư Sở.mp4')
    
    obj.process_on_single_video()