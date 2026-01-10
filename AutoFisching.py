import pydirectinput, time, sys, random, colorama, mss, cv2
import numpy as np
from colorama import Fore, Style, just_fix_windows_console

# ============== 配置区 ==============

# 调试模式 (True/False)
debug = False

# 钓鱼区域坐标 (Y, X, 长, 宽)
REEL_REGION = {"top": 1755, "left": 1145, "width": 1547, "height": 81}
# 进度条区域坐标 (Y, X, 长, 宽)
PROGRESS_REGION = {"top": 1903, "left": 1502, "width": 835, "height": 17}

# 鱼漂颜色范围 (Lower, Upper)
# 【一般来讲无需调整，如遇到无法识别鱼漂或白条再进行调整，下同】
lower_blue = np.array([110, 67, 91])
upper_blue = np.array([110, 255, 255])
# 白条颜色范围 (Lower, Upper)
lower_white = np.array([0, 0, 200])
upper_white = np.array([180, 50, 255])

# 悬浮配置 (模拟轻点达到白条悬浮效果)
# 【除非有特殊需求，否则以下数值保持默认即可】
# 点按持续时间 (秒): 
hover_click_duration = 0.08
# 两次点按之间的冷却时间 (秒): 
hover_interval = 0.01

# ====================================

def init(): # 此函数在脚本运行期间应只需调用一次
    global sct, mouse_is_down, bar_width_history
    just_fix_windows_console()
    sct = mss.mss()
    pydirectinput.PAUSE = 0 # 取消延迟
    mouse_is_down = False # 初始化flag
    bar_width_history = [] # 用于存储白条宽度的历史记录

def log_message(type, message): # 从旧版本直接copy过来的日志输出函数
    time_str=time.strftime("%H:%M:%S", time.localtime())
    if type == "INFO":
        print(f"{Fore.LIGHTGREEN_EX}[{type}]{Style.RESET_ALL} {message}")
    if type == "WARNING":
        print(f"{Fore.LIGHTYELLOW_EX}[{type}]{Style.RESET_ALL} {message}")
    if type == "ERROR":
        print(f"{Fore.RED}[{type}]{Style.RESET_ALL} {message}")
    if type == "DEBUG":
        print(f"{Fore.CYAN}[{type} {Style.RESET_ALL}{time_str}{Fore.CYAN}]{Style.RESET_ALL} {message}") # 当log类型为DEBUG时，打印时间

def get_contours(mask):
    # 查找白条的轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 200] # 过滤掉面积小于200的轮廓
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)# 获取最大轮廓
        x, y, w, h = cv2.boundingRect(largest_contour)# 获取XY长宽
        bar_width_history.append(w)
        if len(bar_width_history) > 10:
            bar_width_history.pop(0)
        # 获取白条平均宽度
        avg_width = int(sum(bar_width_history) / len(bar_width_history))
        return avg_width, x
    return None, None
    
def get_center_x(mask): # 获取掩模中最大轮廓的中心X坐标
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_fish = max(contours, key=cv2.contourArea)
        fish_x, fish_y, fish_w, fish_h = cv2.boundingRect(largest_fish)
        fish_center_x = fish_x + fish_w // 2
        return fish_center_x, fish_w
    return None, None

def cast_rod(): # 甩杆
    pydirectinput.mouseDown()
    time.sleep(random.uniform(0.35, 1.40))
    pydirectinput.mouseUp()

def do_shake(): # 摇晃 # 暂时没啥用吧，希望不会有人测试这块
    pydirectinput.press('enter')

init() # 初始化
log_message("INFO", "AutoFisching v1.4")
log_message("INFO", "Made by XxdMkbMark")
log_message("WARNING", "免责声明: 使用本脚本\033[1m可能\033[0m违反Roblox的使用条款及服务协议, 对于使用本脚本所可能导致和造成的任何后果及伤害, 本人\033[1m概不负责\033[0m\n")
time.sleep(0.3)
log_message("WARNING", "准备事项:")
log_message("WARNING", "1.请确保UI导航模式开启并已将选择框选择至SHAKE按钮")
log_message("WARNING", "2.请确保已在Fisch Menu中开启了Preformance Mode并关闭了Higher Brightness和Higher Saturarion选项 (重要!)")
log_message("WARNING", "完成所有准备工作后按下Enter继续")
input()  # 等待按下Enter键
log_message("INFO", "脚本将在 5 秒后启动, 请切换至Roblox窗口\n")
time.sleep(5)
log_message("INFO", "脚本已启动, 在终端按Ctrl+C可停止脚本")

try:
    while True:
        # 截图
        img_reel = np.array(sct.grab(REEL_REGION))
        img_progress = np.array(sct.grab(PROGRESS_REGION))
        # 转换至HSV
        hsv_reel = cv2.cvtColor(img_reel, cv2.COLOR_BGRA2BGR) # 钓鱼条
        hsv_reel = cv2.cvtColor(hsv_reel, cv2.COLOR_BGR2HSV)
        hsv_progress = cv2.cvtColor(img_progress, cv2.COLOR_BGRA2BGR) # 进度条
        hsv_progress = cv2.cvtColor(hsv_progress, cv2.COLOR_BGR2HSV)
        # 生成掩模
        mask_fish = cv2.inRange(hsv_reel, lower_blue, upper_blue) # 蓝鱼
        mask_bar = cv2.inRange(hsv_reel, lower_white, upper_white) # 白条
        mask_prog_white = cv2.inRange(hsv_progress, lower_white, upper_white) # 进度条

        combined_mask = cv2.bitwise_or(mask_bar, mask_fish) # 合并白条和蓝鱼
        # 形态学处理掩模，去除噪点并填补空洞
        kernel = np.ones((3, 3), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        combined_mask = cv2.erode(combined_mask, kernel, iterations=1)

        bar_width, bar_x = get_contours(combined_mask)
        fish_x, fish_w = get_center_x(mask_fish)
        if fish_x != None and bar_width != None and bar_x != None:
            if fish_w < 30: # 鱼宽度过大，说明识别到的不是鱼   
                relative_pos = (fish_x - bar_x) / bar_width
                #log_message("DEBUG", f"鱼X={fish_x}, 白条宽={bar_width}, 相对位置={relative_pos:.2f}")
                if relative_pos <= 0.3: # 鱼在白条左侧，向左移动
                    if mouse_is_down:
                        pydirectinput.mouseUp()
                        mouse_is_down = False
                elif relative_pos >= 0.7: # 鱼在白条右侧，向右移动
                    if not mouse_is_down:
                        pydirectinput.mouseDown()
                        mouse_is_down = True
                elif 0.3 < relative_pos < 0.7: # 鱼在白条中间，悬浮
                    if mouse_is_down:
                        pydirectinput.mouseUp()
                        mouse_is_down = False
                    pydirectinput.mouseDown()
                    time.sleep(hover_click_duration) # 按压
                    pydirectinput.mouseUp()
                    time.sleep(hover_interval) # 等待

        if debug:
            cv2.imshow("mask_combined", combined_mask)
            cv2.imshow("mask_bar", mask_bar)
            cv2.imshow("mask_prog_white", mask_prog_white)
            cv2.setWindowProperty("mask_combined", cv2.WND_PROP_TOPMOST, 1)
            cv2.setWindowProperty("mask_bar", cv2.WND_PROP_TOPMOST, 2)
            cv2.setWindowProperty("mask_prog_white", cv2.WND_PROP_TOPMOST, 3)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    

    time.sleep(0.01) # 降低CPU占用

except KeyboardInterrupt:
    if debug:
        log_message("INFO", "脚本已停止")
        log_message("DEBUG", "Script exited with status code 0")
    else:
        log_message("INFO", "脚本已停止")
    sys.exit(0)
except Exception as e:
    if debug:
        log_message("ERROR", "发生未知错误, 错误信息见下")
        log_message("DEBUG", f"{e}")
        log_message("DEBUG", "Script exited with status code 1")
    else:
        log_message("ERROR", "发生未知错误, 请在调试模式下运行以获取更多信息")
finally:
    cv2.destroyAllWindows()
    pydirectinput.mouseUp() # 确保程序结束时鼠标已松开