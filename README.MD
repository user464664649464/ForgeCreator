# 避雷说明：本程序完全使用Ai进行编写，所以会有大量的提示词相关文件。这不仅是给AI看的，在座的各位也能加入这个项目，依照提示词帮我检查一下AI有啥不对的地方吗

# ForgeCreator(Demo)
## 一个旨在让用户0模组开发基础就能轻松上手的可视化快速模组创建器

![图片](pic/img.png)

## 未来将要实现的特点
- 0模组开发基础就能轻松上手
- 自动创建、构建模组
- 可视化操作，90%以上的操作都可以通过可视化界面完成

![图片](pic/img.png)

## 使用方法
### Python版本要求：>=3.8
```shell
python src/main.py
```

## 项目结构
```
ForgeCreator/
├── lang/                 # 语言文件目录
├── old_master/           # 旧版本代码（备份）
├── pic/                  # 图片资源
├── res/                  # 模板资源
│   └── nullpack/         # Forge模组模板
├── src/                  # 主源码目录
│   ├── Ui_main.py        # UI界面文件
│   ├── editor.py         # JSON编辑器
│   ├── main.py           # 主程序入口
│   ├── utils.py          # 工具函数
│   └── wizard.py         # 模组创建向导
└── README.md             # 项目说明文档```
```

## 贡献指南

1. Fork本项目
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送到分支：`git push origin feature/new-feature`
5. 提交Pull Request

## 许可证

- 本项目采用Apache2.0许可证，详情请查看LICENSE文件。
- 本项目基于Mojang/Microsoft 的Forge MDK 36.2.34 版本开发，使用本项目创建的任何程序需要用户自行承担风险。
- 本项目的代码和资源仅供学习和研究使用，禁止将其应用于任何非法商业用途、禁止上架任何软件园如华▮▮▮▮

## 联系方式

- 作者：粉丝不破千不改名@bilibili.com
- 问题反馈：请在GitHub Issues中提交

