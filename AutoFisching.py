import pydirectinput, time, sys, random, colorama, mss, cv2
import numpy as np
from colorama import Fore, Style, just_fix_windows_console

# ============== 配置区 ==============

# 是否启用调试模式 (True/False)
debug = True

# 钓鱼区域坐标 (Y, X, 长, 宽)
REEL_REGION = {"top": 1755, "left": 1145, "width": 1547, "height": 81}

# 进度条区域坐标 (Y, X, 长, 宽)
PROGRESS_REGION = {"top": 1903, "left": 1502, "width": 835, "height": 17}

# 鱼漂颜色范围 (Lower, Upper)
# 【一般来讲无需调整，如遇到无法识别鱼漂或白条再进行调整，下同】
lower_blue = np.array([100, 27, 51])
upper_blue = np.array([120, 255, 255])

# 白条颜色范围 (Lower, Upper)
lower_white = np.array([0, 0, 200])
upper_white = np.array([180, 50, 255])

# 死区范围 (应根据鱼竿控制力进行调整，增大可提升稳定性但会降低响应速度)
threshold = 280

# 悬浮配置 (模拟轻点达到白条悬浮效果)
# 【除非有特殊要求，否则以下数值保持默认即可】
# 点按持续时间 (秒): 
hover_click_duration = 0.09
# 两次点按之间的冷却时间 (秒): 
hover_interval = 0.08 

# ====================================

just_fix_windows_console()
sct = mss.mss()
pydirectinput.PAUSE = 0 # 取消延迟
mouse_is_down = False # 初始化flag

def log_message(type, message):
    time_str=time.strftime("%H:%M:%S", time.localtime())
    if type == "INFO":
        print(f"{Fore.LIGHTGREEN_EX}[{type}]{Style.RESET_ALL} {message}")
    if type == "WARNING":
        print(f"{Fore.LIGHTYELLOW_EX}[{type}]{Style.RESET_ALL} {message}")
    if type == "ERROR":
        print(f"{Fore.RED}[{type}]{Style.RESET_ALL} {message}")
    if type == "DEBUG":
        print(f"{Fore.CYAN}[{type} {Style.RESET_ALL}{time_str}{Fore.CYAN}]{Style.RESET_ALL} {message}") # 当log类型为DEBUG时，打印时间

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
        if cv2.contourArea(largest_contour) < 20:
            return None
        x, y, w, h = cv2.boundingRect(largest_contour)
        return x + w // 2
    return None

log_message("INFO", "AutoFisching v1.2")
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

try:
    while True:
        # 截图&转换
        img = np.array(sct.grab(REEL_REGION))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        hsv = cv2.cvtColor(hsv, cv2.COLOR_BGR2HSV)

        # 创建掩模
        mask_fish = cv2.inRange(hsv, lower_blue, upper_blue)
        mask_bar = cv2.inRange(hsv, lower_white, upper_white)

        if debug:
            # 将所有图转为3通道
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            mask_fish_bgr = cv2.cvtColor(mask_fish, cv2.COLOR_GRAY2BGR)
            mask_bar_bgr = cv2.cvtColor(mask_bar, cv2.COLOR_GRAY2BGR)
            vision_bgr = cv2.cvtColor(mask_fish + mask_bar, cv2.COLOR_GRAY2BGR)
            
            # 调整大小以便拼接 
            scale = 0.6 # 缩放比例
            h, w = img_bgr.shape[:2]
            new_size = (int(w * scale), int(h * scale))
            
            img_s = cv2.resize(img_bgr, new_size)
            fish_s = cv2.resize(mask_fish_bgr, new_size)
            bar_s = cv2.resize(mask_bar_bgr, new_size)
            vision_s = cv2.resize(vision_bgr, new_size)

            # 拼接图片
            # 原图&视觉
            top_row = cv2.hconcat([img_s, vision_s])
            # 鱼掩膜&白条掩膜
            bottom_row = cv2.hconcat([fish_s, bar_s])
            # 合并
            final_debug = cv2.vconcat([top_row, bottom_row])

            # 显示&置顶
            window_name = "AutoFisch Debug View"
            cv2.imshow(window_name, final_debug)
            cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

            if cv2.waitKey(1) & 0xFF == ord('q'): # 按q退出
                log_message("DEBUG", "Script exited with status code 0 (Requested by user via opencv window)")
                break

        # 寻找坐标与控制
        # get_center_x
        fish_x = get_center_x(mask_fish)
        bar_x = get_center_x(mask_bar)
        # 控制部分
        if fish_x is not None and bar_x is not None:
            diff = fish_x - bar_x

            # 鱼在白条右侧，向右追
            if diff > threshold: 
                if not mouse_is_down:
                    pydirectinput.mouseDown()
                    mouse_is_down = True
                    if debug: log_message("DEBUG", f"向右 -> (Diff: {diff})")
            
            # 鱼在白条左侧，向左退
            elif diff < -threshold:
                if mouse_is_down:
                    pydirectinput.mouseUp()
                    mouse_is_down = False
                    if debug: log_message("DEBUG", f"向左 <- (Diff: {diff})")
            
            # 鱼在死区内，需要白条悬浮
            elif diff >= -threshold and diff <= threshold:
                # 松开鼠标防止冲突
                if mouse_is_down:
                    pydirectinput.mouseUp()
                    mouse_is_down = False

                if debug:
                    log_message("DEBUG", f"悬浮中... Diff: {diff}")
                
                # 执行一次快速点按 (Tap)
                # 这种操作可以让白条获得一点点向上的力，对抗重力，从而实现"悬浮"
                pydirectinput.mouseDown()
                time.sleep(hover_click_duration) # 极短的按压
                pydirectinput.mouseUp()
                
                # 这里的 sleep 很关键，决定了悬浮的力度
                # 如果这个时间太短，白条会慢慢上升；太长，白条会慢慢下降
                time.sleep(hover_interval) 

        else:
            # 视觉丢失保护
            if mouse_is_down:
                pydirectinput.mouseUp()
                mouse_is_down = False

        time.sleep(0.001) # 降低CPU占用率

except KeyboardInterrupt:
    if debug:
        log_message("INFO", "脚本已停止")
        log_message("DEBUG", "Script exited with status code 0 (KeyboardInterrupt)")
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