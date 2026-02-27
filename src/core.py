import os
import cv2
import numpy as np
import pytoshop
from pytoshop import layers
from pytoshop.enums import ColorMode

def to_psd_channels(img_rgb):
    h, w = img_rgb.shape[:2]
    return {
        0: layers.ChannelImageData(image=img_rgb[:, :, 0]),
        1: layers.ChannelImageData(image=img_rgb[:, :, 1]),
        2: layers.ChannelImageData(image=img_rgb[:, :, 2]),
        -1: layers.ChannelImageData(image=np.ones((h, w), dtype=np.uint8) * 255)
    }

import os

def run_rename(folder_path):
    # 1. 获取所有支持的图片文件
    extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(extensions)]
    
    # 2. 排序，确保按当前顺序进行重编号
    files.sort()
    
    total_files = len(files)
    if total_files == 0:
        return

    # 3. 计算位宽：10张以内是1位(1), 100张以内是2位(01), 1000张以内是3位(000)
    # 使用 len(str(total_files)) 自动获取总数的位数
    width = len(str(total_files))

    for i, filename in enumerate(files, start=1):
        old_path = os.path.join(folder_path, filename)
        ext = os.path.splitext(filename)[1]
        
        # 4. 关键：使用 zfill(width) 进行动态补零
        new_name = f"{str(i).zfill(width)}{ext}"
        new_path = os.path.join(folder_path, new_name)
        
        # 防止原地重命名冲突（虽然通常不会，但建议加上检查）
        if old_path != new_path:
            os.rename(old_path, new_path)

def run_psd_export(folder_path, opacity_val, progress_callback=None):
    """
    增加了进度回调函数 progress_callback
    """
    # 1. 自动创建子文件夹
    output_dir = os.path.join(folder_path, "PSD")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    exts = ('.jpg', '.png', '.jpeg', '.webp')
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(exts)]
    
    total = len(files)
    for i, file_name in enumerate(files):
        img_path = os.path.join(folder_path, file_name)
        # 兼容中文路径的读取方式
        img_bgr = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img_bgr is None: continue
        
        h, w = img_bgr.shape[:2]
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        psd = pytoshop.core.PsdFile(num_channels=4, height=h, width=w, color_mode=ColorMode.rgb)
        l1 = layers.LayerRecord(name='Reference', channels=to_psd_channels(img_rgb), 
                                top=0, left=0, bottom=h, right=w)
        l2 = layers.LayerRecord(name='Edit_Layer', opacity=opacity_val, 
                                channels=to_psd_channels(img_rgb),
                                top=0, left=0, bottom=h, right=w)
        psd.layer_and_mask_info.layer_info.layer_records.extend([l1, l2])

        out_path = os.path.join(output_dir, os.path.splitext(file_name)[0] + ".psd")
        with open(out_path, 'wb') as f:
            psd.write(f)
        
        # 2. 触发进度更新
        if progress_callback:
            progress_callback(int((i + 1) / total * 100))