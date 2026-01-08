# Written by Gemini, do not create issues about this script
import cv2
import numpy as np
import mss

# === 这里填入你之前测量好的区域 (必须和主脚本一致) ===
REEL_REGION = {"top": 1755, "left": 1145, "width": 1547, "height": 81}

sct = mss.mss()

# 鼠标回调函数
def pick_color(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # 获取被点击点的 HSV 值
        pixel = hsv_img[y, x]
        h_val = pixel[0]
        s_val = pixel[1]
        v_val = pixel[2]
        
        print(f"\n[取色结果] 坐标({x},{y}) -> HSV: [{h_val}, {s_val}, {v_val}]")
        print("-" * 30)
        print(f"建议 Lower: np.array([{max(0, h_val-10)}, {max(0, s_val-40)}, {max(0, v_val-40)}])")
        print(f"建议 Upper: np.array([{min(180, h_val+10)}, 255, 255])")
        print("-" * 30)

cv2.namedWindow("Color Probe")
cv2.setMouseCallback("Color Probe", pick_color)

print("=== 色彩探针已启动 ===")
print("1. 切换到游戏，触发钓鱼小游戏。")
print("2. 当看到蓝鱼出现时，迅速按键盘上的 's' 键冻结画面。")
print("3. 在冻结的图片上，用鼠标点击那条'蓝鱼'的中心。")
print("4. 看终端输出的 HSV 数值。")
print("5. 按 'q' 退出。")

while True:
    img = np.array(sct.grab(REEL_REGION))
    
    # 实时转换 HSV
    hsv_source = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    hsv_img = cv2.cvtColor(hsv_source, cv2.COLOR_BGR2HSV)
    
    cv2.imshow("Color Probe", img)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        print("\n>>> 画面已冻结！请点击图片里的鱼...")
        while True:
            # 冻结状态，等待点击
            cv2.imshow("Color Probe", img) # 保持显示这一帧
            if cv2.waitKey(1) & 0xFF == ord('q'):
                exit() # 直接完全退出
            # 按 r 恢复运行
            if cv2.waitKey(1) & 0xFF == ord('r'):
                print(">>> 恢复实时监测")
                break
    elif key == ord('q'):
        break

cv2.destroyAllWindows()