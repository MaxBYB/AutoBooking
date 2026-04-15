import ddddocr
import cv2
import numpy as np
from PIL import Image
import io

# def preprocess_captcha(image_bytes):
#     # 转换为OpenCV格式
#     nparr = np.frombuffer(image_bytes, np.uint8)
#     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
#     # 灰度化
#     # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
#     # 二值化
#     _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
#     # 去除小噪点
#     kernel = np.ones((2, 2), np.uint8)
#     opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
#     # 转回字节流
#     is_success, buffer = cv2.imencode(".jpg", opening)
#     processed_bytes = io.BytesIO(buffer).getvalue()
    
#     return processed_bytes

# 初始化两个模型：一个用于检测框，一个用于文字识别
det = ddddocr.DdddOcr(det=True)
ocr = ddddocr.DdddOcr(ocr=True)

# 读取图片
with open(r"C:\Users\18810\Desktop\test.png", 'rb') as f:
    image = f.read()
# 预处理图片
np_image = np.frombuffer(image, np.uint8)
np_image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
# 检测目标
bboxes = det.detection(image)
print(bboxes)  # 输出格式：[[x1, y1, x2, y2], ...]
# 裁剪检测到的文字
cropped_images = []
for bbox in bboxes:
    x1, y1, x2, y2 = bbox
    cropped = np_image[y1:y2, x1:x2]
    cropped_images.append(cropped)
# # 保存裁剪的图片
# for i, cropped in enumerate(cropped_images):
#     cv2.imwrite(f"C:\\Users\\18810\\Desktop\\cropped_{i}.jpg", cropped)

# 识别汉字
# processed_image = preprocess_captcha(image)
for cropped in cropped_images:
    res = ocr.classification(cropped)
    print(res)  # 输出格式：识别结果字符串
# 设定识别范围为汉字
# ocr.set_ranges(6)
# print(res)  # 输出格式：识别结果字符串

# # 可视化检测结果
# im = cv2.imread(r"C:\Users\18810\Desktop\test.png")
# for bbox in bboxes:
#     x1, y1, x2, y2 = bbox
#     im = cv2.rectangle(im, (x1, y1), (x2, y2), color=(0, 0, 255), thickness=2)
# # 弹窗显示结果
# # cv2.imshow("Detection Result", im)
# cv2.imwrite(r"C:\Users\18810\Desktop\result.jpg", im)


# if __name__ == '__main__':
#     # 检查ddddocr是否安装成功
#     print
#     print("正在检查环境...")