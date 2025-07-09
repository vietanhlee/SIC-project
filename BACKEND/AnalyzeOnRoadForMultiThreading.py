from multiprocessing import Process, Manager
import time
from multiprocessing import freeze_support
import os
from AnalyzeOnRoad import AnalyzeOnRoad

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

class AnalyzeOnRoadForMultiprocessing():
    """
    Attributes:
        manager (Manager()): Đối tượng để tạo các Lock() và các kiểu dữ liệu chia sẽ chung khác\
            của các process với nhau
        shared_data (Manager().dict()): dict quản lý các Lock và các kiểu dữ liệu chia sẽ chung khác\
            của các process với nhau chặt chẽ hơn
    """
    def __init__(self,path_videos = [
                        "./video_test/Văn Quán.mp4",
                        "./video_test/Văn Phú.mp4",
                        "./video_test/Nguyễn Trãi.mp4",
                        "./video_test/Ngã Tư Sở.mp4",
                        "./video_test/Đường Láng.mp4",
                    ],
        meter_per_pixels = [0.035, 0.08, 0.45, 0.12, 0.06], show_log = False):
        """_summary_

        Args:
            path_videos (list, optional): Đường dẫn các video. \
            Defaults to [ "./video_test/Văn Quán.mp4", "./video_test/Văn Phú.mp4", "./video_test/Nguyễn Trãi.mp4", "./video_test/Ngã Tư Sở.mp4", "./video_test/Đường Láng.mp4", ].
            meter_per_pixels (list, optional): list các tỉ số met/pixel. \
            Defaults to [0.035, 0.08, 0.45, 0.12, 0.06].
            show_log (bool, optional): hiển thị log hoặc không. Defaults to False.
        """
        self.path_videos = path_videos
        self.meter_per_pixels = meter_per_pixels
        
        self.manager = Manager()
        self.shared_data = self.manager.dict()  # Dùng để lưu trữ thông tin chung giữa các process
        self.show_log = show_log
        self.processes = []
        self.names = []
        
    @staticmethod
    def run_analyze_process(path_video, meter_per_pixel, info_dict, frame_dict, 
                        lock_info, lock_frame, **kwargs):
        """Hàm chạy trong process riêng, làm hàm kích hoạt cho Multiprocessing. Đặt hàm này là static method vì\
        để tránh việc sử dụng multiprocessing bị lỗi do nó sẽ picke các biến liên quan đến hàm để chuyển dữ liệu\
        sang process con, đặc biệt là self chứa các tool của YOLO và các biến khác không thể picke được do đó \
        các đối tượng liên quan đến YOLO không picke được ta sẽ đưa nó vào hàm kích hoạt này luôn để khởi tạo\
        và khi gọi kích hoạt nó thì nó sẽ đồng thời được khởi tạo ở process con luôn, đảm bảo tính toàn vẹn dữ liệu
        Tất nhiên sẽ có nhưunxg thuộc tính khác trong self ko picke được nên ta để static cho an toàn dữ liệu
        """
        try:
            analyzer = AnalyzeOnRoad(
                path_video=path_video,
                meter_per_pixel=meter_per_pixel,
                info_dict=info_dict,
                frame_dict=frame_dict,
                lock_info=lock_info,
                lock_frame=lock_frame,
                **kwargs
            )
            analyzer.process_on_single_video()
        except Exception as e:
            print(f"Lỗi khi xử lý {path_video}: {e}")

    @staticmethod
    def log(names, shared_data):
        """Hàm in ra log thông tin các processing
        Hàm này lấy data tổng thể ở share_data (Manager.dict() dùng để giao tiếp các process với nhau)
        Đặt hàm này là static method vì để tránh việc sử dụng multiprocessing bị lỗi do nó sẽ picke các biến\
        liên quan đến hàm để chuyển dữ liệu sang process con, đặc biệt là self chứa các tool của YOLO\
        và các biến khác không thể picke được"""
        
        YELLOW = "\033[93m"
        GREEN = "\033[92m"
        CYAN = "\033[96m"
        RESET = "\033[0m"
        BOLD = "\033[1m"
        
        try:
            while True:
                print(f"{BOLD}{CYAN}--------------------------------------- [Log at {time.strftime('%H:%M:%S')}] --------------------------------------------{RESET}")
                print(f"{BOLD}| {'Tuyến đường':<25} | {'Thông tin':<70} |{RESET}")
                print(f"{'-'*102}")
                
                for name in names:
                    try:
                        if name in shared_data:
                            road_data = shared_data[name]
                            info_dict = road_data['info']
                            
                            # Lấy data với lock
                            with road_data['lock_info']:
                                count_car = info_dict.get('count_car', 0)
                                count_motor = info_dict.get('count_motor', 0)
                                speed_car = info_dict.get('speed_car', 0)
                                speed_motor = info_dict.get('speed_motor', 0)
                            
                            info_str = f"Ô tô: {count_car} xe, Vtb: {speed_car} km/h | Xe máy: {count_motor} xe, Vtb: {speed_motor} km/h"
                            print(f"| {YELLOW}{name:<25}{RESET} | {GREEN}{info_str:<70}{RESET} |")
                        else:
                            print(f"| {YELLOW}{name:<25}{RESET} | {GREEN}{'Đang khởi tạo...':<70}{RESET} |")
                    except Exception as e:
                        print(f"| {YELLOW}{name:<25}{RESET} | {GREEN}{f'Lỗi: {str(e)}':<70}{RESET} |")
                
                print(f"{'-'*102}\n\n")
                time.sleep(5)
        except KeyboardInterrupt:
            print("Kết thúc log.")

    def run_multiprocessing(self):
        """Hàm kích hoạt chạy multi processing"""
        freeze_support()
        # Tạo shared data structures
        for path_video, meter_per_pixel in zip(self.path_videos, self.meter_per_pixels):
            name = path_video.split('/')[-1][:-4]
            self.names.append(name)
            
            # Tạo các manager objects
            info_dict = self.manager.dict({
                "count_car": 0,
                "count_motor": 0,
                "speed_car": 0,
                "speed_motor": 0,
            })
            
            # Do việc chia sẽ các biến kiểu str
            # bị hạn chế trong multi processing nên ta lấy kiểu Manager.dict() chứa data str đó. Ví dụ như: 
            # dict = {'frame': <str base64>} phải cầm được khoá thì mới được lấy dữ liệu
            
            frame_dict = self.manager.dict({"frame": ""})
            
            lock_info = self.manager.Lock()
            lock_frame = self.manager.Lock()

            # Lưu các khoá và các biến quản lý dữ liệu vào dict shared data để dễ quản lý. Việc láy data cũng 
            # đơn giản hơn do các thông tin như khoá và dữ liệu được phân bố vào dict để quản lý giúp chặt chẽ hơn
            self.shared_data[name] = {
                'info': info_dict,
                'frame': frame_dict,
                'lock_info': lock_info,
                'lock_frame': lock_frame
            }
            
            # Tạo process với target là static method
            p = Process(
                target=AnalyzeOnRoadForMultiprocessing.run_analyze_process, 
                args=(
                    path_video, meter_per_pixel, info_dict, frame_dict, 
                    lock_info, lock_frame
                ), 
                kwargs={'show': False}
            )
            self.processes.append(p)
      
        # Start all self.processes
        for p in self.processes:
            p.start()
        
        if self.show_log:
            Process(target= self.log, args=(self.names, self.shared_data)).start()

        
        self.join_process()
    
    def join_process(self):   
        """ Hàm để join các process """ 
        for p in self.processes:
            p.join()
        print("All self.processes stopped.")
    
    def get_veheicles_info(self) -> dict:
        """Hàm để lấy thông tin về các phương tiện qua shared_data là Manager().dict() làm trung gian quản lý\ 
        và phải đặt ở main Process
        >>> with data['lock_info']
        phải cầm được khoá thì mới được lấy dữ liệu

        Returns:
            dict: Thông tin các phương tiện ở mỗi tuyến đường {tuyến đuòng : {thông tin}}
        """
        vehicles_info = {}
        for name, data in self.shared_data.items():
            with data['lock_info']:
                vehicles_info[name] = {
                    "count_car": data['info'].get('count_car', 0),
                    "count_motor": data['info'].get('count_motor', 0),
                    "speed_car": data['info'].get('speed_car', 0),
                    "speed_motor": data['info'].get('speed_motor', 0),
                }
        return vehicles_info
    
    def get_frames(self) -> str:
        """Hàm để lấy frame từ các video qua shared_data là Manager().dict() làm trung gian quản lý\ 
        và phải đặt ở main Process
        >>> with data['lock_frame']
        >>> 'frame': data['frame'].get('frame', "")
        Đoạn này lấy key 'frame' hai lần do bản thân cái data['frame'] là một dict {'frame': ảnh base64} do việc chia sẽ các biến kiểu str
        bị hạn chế trong multi processing nên ta lấy kiểu Manager.dict() chứa data str đó. Ví dụ như: dict = {'frame': <str base64>}
        phải cầm được khoá thì mới được lấy dữ liệu

        Returns:
            str: ảnh được mã hoá base64 
        """
        frames = {}
        for name, data in self.shared_data.items():
            with data['lock_frame']:
                frames[name] = {
                    'frame': data['frame'].get('frame', ""), # Đặt như này cho bên FE gọi, sau này biết FE (call api) sẽ sửa sau
                }
        return frames
    
#********************************************************************Script for testing************************************************************************
if __name__ == '__main__':
    # freeze_support should be called immediately in the main block
    freeze_support()
    analyzer = AnalyzeOnRoadForMultiprocessing(
        show_log= True,
    )
    analyzer.run_multiprocessing()
  
    
  
  

    
    # time.sleep(5)
    # while True:
    #     try:
    #         vehicles_info = analyzer.get_veheicles_info()
    #         frames = analyzer.get_frames()
            
    #         print("\nCurrent Vehicles Info:")
    #         for name, info in vehicles_info.items():
    #             print(f"{name}: {info}")
            
    #         # print("\nCurrent Frames:")
    #         for name, frame in frames.items():
    #             print(f"{name}: {frame['frame'][:10]}...")  # Print first 10 characters of the frame string
            
    #         time.sleep(5)
    #     except KeyboardInterrupt:
    #         print("Exiting...")
    #         break