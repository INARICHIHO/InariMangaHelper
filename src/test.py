from core import run_rename, run_psd_export
import os

# 1. 这里的路径请务必确保是在资源管理器地址栏复制出来的
# 2. 如果路径末尾有反斜杠，删掉它或者确保它在引号内
path = r"D:\1File\InariMangaHelper\test_images"

# 增加一个保险：先检查路径是否存在，不存在就报错提醒
if not os.path.exists(path):
    print(f"❌ 路径错误：找不到文件夹 '{path}'")
    print("请确认文件夹名字是否正确，或者路径里是否有不该有的空格。")
else:
    print(f"✅ 找到路径：{path}，准备开始...")
    # 运行一键执行
    run_rename(path)
    run_psd_export(path, 40)