import pydirectinput, time, sys, random, colorama, mss, cv2
import numpy as np
from colorama import Fore, Style, just_fix_windows_console
just_fix_windows_console()

# ============== 配置区 ==============

# 是否启用调试模式 (True/False)
debug = True

# 钓鱼区域坐标 (Top, Left, Width, Height)
REEL_REGION = {"top": 1755, "left": 1145, "width": 1547, "height": 81}

# 鱼漂颜色范围 (Lower, Upper)
# 【一般来讲无需调整，如遇到无法识别鱼漂或白条再进行调整，下同】
lower_blue = np.array([100, 27, 51])
upper_blue = np.array([120, 255, 255])

# 白条颜色范围 (Lower, Upper)
lower_white = np.array([0, 0, 200])
upper_white = np.array([180, 50, 255])

# ====================================

def log_message(type, message):
    time=time.strftime("%H:%M:%S", time.localtime())
    if type == "INFO":
        print(f"{Fore.LIGHTGREEN_EX}[{type}]{Style.RESET_ALL} {message}")
    if type == "WARNING":
        print(f"{Fore.LIGHTYELLOW_EX}[{type}]{Style.RESET_ALL} {message}")
    if type == "ERROR":
        print(f"{Fore.RED}[{type}]{Style.RESET_ALL} {message}")
    if type == "DEBUG":
        print(f"{Fore.CYAN}[{type} {Style.RESET_ALL}{time}{Fore.CYAN}]{Style.RESET_ALL} {message}") # 当log类型为DEBUG时，打印时间

def cast_rod(): # 甩杆
    pydirectinput.mouseDown()
    time.sleep(random.uniform(0.35, 1.40))
    pydirectinput.mouseUp()

def do_shake(): # 摇晃
    pydirectinput.press('enter')

def get_center_x(mask): # 获取掩模中最大轮廓的中心X坐标
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) < 20: # 面积太小可能是噪点，忽略
            return None
        x, y, w, h = cv2.boundingRect(largest_contour)
        return x + w // 2
    return None

log_message("INFO", "AutoFisching v1.0")
log_message("INFO", "Made by XxdMkbMark")
log_message("WARNING", "免责声明: 使用本脚本\033[1m可能\033[0m违反Roblox的使用条款及服务协议, 对于使用本脚本所可能导致和造成的任何后果及伤害, 本人\033[1m概不负责\033[0m\n")
time.sleep(0.3)
log_message("WARNING", "准备事项:")
log_message("WARNING", "1.请确保UI导航模式开启并已将选择框选择至SHAKE按钮")
log_message("WARNING", "2.请确保已在Roblox设置中将图形画质调至最低")
log_message("WARNING", "3.请确保在Fisch的Menu中开启了Preformance Mode选项并关闭了Higher Brightness和Higher Saturarion选项 (重要! 不按照说明操作可能导致图像识别不准确进而导致脱钩!)")
log_message("WARNING", "完成所有准备工作后按下Enter继续")
input()  # 等待用户按下 Enter 键继续
log_message("INFO", "脚本将在 5 秒后启动, 请切换至Roblox窗口\n")
time.sleep(5) # 等待 5 秒钟
log_message("INFO", "脚本已启动, 在终端按Ctrl+C可停止脚本")

cast_rod()
time.sleep(0.4)
try:
    while True:
        # 截图&转换
        img = np.array(sct.grab(REEL_REGION))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        hsv = cv2.cvtColor(hsv, cv2.COLOR_BGR2HSV)

        # 创建掩模
        mask_fish = cv2.inRange(hsv, lower_blue, upper_blue)
        mask_bar = cv2.inRange(hsv, lower_white, upper_white)

        # =========================
        # 调试，只有在debug为true时才显示窗口（ToDo）
        #cv2.imshow("Debug: Fish Mask", mask_fish)
        #cv2.imshow("Debug: Bar Mask", mask_bar)
        #cv2.imshow("Vision", mask_fish + mask_bar)
        #cv2.imshow("Debug: Source", img)     # 显示原图以方便对比
        # =========================

        # 寻找坐标与控制
        # get_center_x
        fish_x = get_center_x(mask_fish)
        bar_x = get_center_x(mask_bar)
        # 控制部分
        if fish_x is not None and bar_x is not None:
            diff = fish_x - bar_x
            threshold = 15 # 死区范围 【应根据鱼竿控制力进行调整(后期移动至配置区: todo)】
                
                # --- 核心逻辑 ---
            if diff > threshold: 
                    # 鱼在右边，且超过了死区，则向右追
                if not mouse_is_down:
                    pydirectinput.mouseDown()
                    mouse_is_down = True
                    # print("按下 ->") # 调试
                        
            elif diff < -threshold:
                    # 鱼在左边，且超过了死区，则向左退
                if mouse_is_down:
                    pydirectinput.mouseUp()
                    mouse_is_down = False
                    # print("<- 松开") # 同上
                
            else:
                # 鱼在死区间，则稳住白条
                pass
                    
        else: # 待优化！！！！！！！！！
            # 视觉丢失 (可能小游戏还没开始，或者结束了)
            # 安全措施：松开鼠标，防止跑路
            if mouse_is_down:
                pydirectinput.mouseUp()
                mouse_is_down = False
except KeyboardInterrupt:
    if debug:
        log_message("INFO", "脚本已停止")
        log_message("DEBUG", "Script exited with status code 0 (KeyboardInterrupt)")
    else:
        log_message("INFO", "脚本已停止")
    sys.exit(0)
except Exception as e:
    if debug:
        log_message("DEBUG", f"\n {e}")
    else:
        log_message("ERROR", "发生未知错误, 请在调试模式下运行以获取更多信息")
finally:
    cv2.destroyAllWindows()
    pydirectinput.mouseUp() # 确保程序结束时鼠标已松开