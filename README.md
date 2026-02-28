⛩ Inari Manga Helper (稻荷漫画助手)
这是一个为了提高个人汉化效率而开发的轻量级辅助工具。它主要解决汉化过程中最枯燥的两个环节：文件排序和基础 PSD 模板搭建。

This is a lightweight toolkit developed to improve the efficiency of solo manga scanlation. It focuses on automating file sorting and basic PSD template setup.

🛠️ 核心功能 | Core Features
🔢 智能序号重命名:

根据文件夹内图片总数自动计算位数（如 50 张图自动补零为 01-50，500 张图补为 001-500）。

解决 Windows 系统下 1, 10, 2 排序混乱的问题，确保后期修图顺序严谨。

🖼️ 自动化 PSD 遮罩生成:

批量将图片封装进 PSD 格式。

自动创建一个半透明图层作为辅助参考，方便修图师快速定位需要清理（Clean）的区域，无需在 PS 中反复手动建层。

🚀 使用说明 | How to Use
选择路径: 拖入或选择包含漫画原图的文件夹。

设定参数: 调节滑块或输入数字，设置辅助层的透明度（默认 50%）。

一键执行:

点击“重命名”：执行图片序号对齐。

点击“导出 PSD”：为每张图生成带辅助层的 PSD。

点击“执行全部”：一次性完成上述所有工序。

📂 项目结构 | Project Structure
```text
InariMangaHelper/
├── assets/          # 存放程序图标 (inari.ico)
├── locales/         # 语言包 (zh/en/jp)
│   ├── __init__.py
│   ├── zh.py
│   ├── en.py
│   └── jp.py
├── src/
│   ├── main.py      # GUI 界面逻辑
│   └── core.py      # 重命名与 PSD 处理逻辑
```

📄 许可说明 | License
代码: 本项目采用 MIT License，欢迎学习交流。

图标: 图标素材来源于网络，仅供个人学习与交流使用，请勿用于商业用途。

💡 开发初衷
写这个脚本是因为受够了手动改几十页文件名和在 PS 里重复新建图层。如果你也有同样的烦恼，希望这个小工具能帮你省下一点时间。

⚖️ 碎碎念
这是一个初学者的练手习作，代码逻辑很简单，纯粹是为了自己方便。如果你发现写得太烂或者有 Bug，欢迎吐槽或随手帮忙改改。
