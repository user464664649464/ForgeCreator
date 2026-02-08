#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Forge模组构建器主程序
应用程序入口点，负责整合所有组件并处理用户交互
"""

# 标准库导入
import sys
import os
import json
import shutil
import re
import subprocess
import tempfile

# PyQt5导入
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox,
    QAction, QMenu, QDialog, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QHBoxLayout, QListWidget, QListWidgetItem,
    QLineEdit, QGridLayout, QGroupBox, QCheckBox, QSpinBox,
    QDoubleSpinBox, QInputDialog
)

# 本地模块导入
from Ui_main import Ui_MainWindow  # 导入Qt Designer生成的UI类
from editor import Editor  # 导入JSON编辑器
from wizard import ForgeModCreator  # 导入模组创建向导
from utils import ensure_admin_privileges  # 导入管理员权限工具


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    主窗口类，继承自QMainWindow和Ui_MainWindow
    负责处理所有用户交互和业务逻辑
    """
    
    def __init__(self):
        """
        初始化主窗口
        """
        super().__init__()
        
        # 加载语言文件
        self.load_language('zh_CN')
        
        # 在初始化UI之前获取管理员权限
        ensure_admin_privileges()
        
        # 设置UI界面
        self.setupUi(self)
        
        # 更新菜单项文本为中文
        self.update_menu_texts()
        
        # 添加Open菜单项
        self.add_open_menu()
        
        # 修改Block菜单项，添加子菜单
        self.modify_block_menu()
        
        # 添加Run菜单
        self.add_run_menu()
        
        # 创建JSON编辑器
        self.editor = Editor()
        
        # 将编辑器设置为中央部件
        self.setCentralWidget(self.editor)
        
        # 加载默认的mod.json文件
        self.load_default_mod_json()
    
    def load_language(self, lang_code):
        """
        加载指定语言的语言文件
        
        :param lang_code: 语言代码，如'zh_CN'
        """
        # 如果语言已经加载，直接返回
        if hasattr(self, 'lang') and self.lang is not None:
            return
            
        try:
            # 构建语言文件路径
            lang_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lang', f'{lang_code}.language')
            
            # 加载语言文件
            with open(lang_file_path, 'r', encoding='utf-8') as f:
                self.lang = json.load(f)
            
            self.log_message(f"已加载语言文件: {lang_file_path}")
        except Exception as e:
            # 如果加载失败，使用默认语言
            self.lang = {
                'app_title': 'Forge模组构建器',
                'open_action': 'Open',
                'block_menu': 'Block',
                'block_inherit': '继承自...',
                'block_custom': '自定义...',
                'run_menu': 'Run...',
                'run_client': 'Run Client',
                'new_project_success': '成功',
                'new_project_success_message': '方块创建成功！',
                'error_title': '错误',
                'warning_title': '警告',
                'information_title': '提示',
                'block_type_warning': '请选择一个实际的方块类型，而不是分类标题',
                'block_name_required': '请输入方块名称',
                'display_name_required': '请输入显示名称',
                'block_name_format_error': '方块名称只能包含小写字母、数字和下划线',
                'help_title': '帮助',
                'help_content': 'Forge模组构建器帮助信息\n\n版本: 1.0.0\n功能: 创建Minecraft Forge 1.16.5模组\n作者: 华为',
                'about_title': '关于',
                'about_content': 'Forge模组构建器\n\n版本: 1.0.0\n基于Minecraft Forge 1.16.5\n(c) Copyright by 华为',
                'open_file_title': '打开模组JSON文件',
                'file_read_warning': '无法读取选择的文件',
                'file_opened_message': '已打开文件: {file_path}',
                'no_file_error': '请先打开/创建文件',
                'forge_dir_not_found': 'Forge目录不存在: {forge_dir}',
                'gradle_script_not_found': 'Gradle脚本不存在: {gradle_script}',
                'client_running_message': '已启动客户端运行任务',
                'client_error_message': '运行客户端时出错: {e}',
                'dialog_title_create_block': '继承自现有方块',
                'group_box_basic_info': '方块基本信息',
                'label_block_name': '方块名称 (英文小写，无空格):',
                'placeholder_block_name': '例如: example_block',
                'label_display_name': '显示名称 (中文):',
                'placeholder_display_name': '例如: 示例方块',
                'label_block_type': '选择方块类型:',
                'label_material_type': '方块材质类型:',
                'group_box_properties': '方块属性设置',
                'label_hardness': '硬度:',
                'label_resistance': '爆炸抗性:',
                'label_harvest_level': '挖掘等级:',
                'label_tool_type': '挖掘工具:',
                'label_light_level': '发光等级 (0-15):',
                'label_sound_type': '音效类型:',
                'label_special_properties': '特殊属性:',
                'check_not_solid': '非固体 (notSolid)',
                'check_no_collision': '无碰撞 (noCollision)',
                'check_requires_tool': '需要工具挖掘 (requiresTool)',
                'check_no_drops': '无掉落 (noDrops)',
                'check_ticks_randomly': '随机更新 (ticksRandomly)',
                'check_waterlogged': '可被水淹没 (waterlogged)',
                'button_create_block': '创建方块',
                'button_cancel': '取消',
                'select_itemgroup_title': '选择ItemGroup',
                'select_itemgroup_label': '请选择一个ItemGroup:',
                'create_itemgroup_title': '创建ItemGroup',
                'label_itemgroup_classname': 'ItemGroup类名:',
                'no_itemgroup_message': '没有检测到ItemGroup，需要先创建一个ItemGroup。是否现在创建？',
                'button_new': '新建...',
                'button_confirm': '确定',
                'button_create': '创建',
                'classname_required': '请输入类名',
                'label_itemgroup': '物品分组 (ItemGroup):',
                'texture_select_title': '选择贴图',
                'texture_select_message': '是否要为方块选择贴图文件？\n提示：请尽量选择1:1比例的PNG格式图片',
                'texture_select_dialog': '选择贴图文件'
            }
            self.log_message(f"加载语言文件失败，使用默认语言: {e}")
    
    def log_message(self, message):
        """
        记录日志信息
        
        :param message: 日志信息
        """
        print(message)
    
    def add_open_menu(self):
        """
        在File菜单下添加Open选项
        """
        
        # 创建Open动作
        self.Open = QAction(self.lang.get('open_action', 'Open'), self)
        self.Open.setObjectName("Open")
        self.Open.setText(self.lang.get('open_action', 'Open'))
        
        # 将Open动作添加到File菜单
        self.File.addAction(self.Open)
    
    def modify_block_menu(self):
        """
        修改Block菜单项，添加子菜单
        """
        
        # 从Create菜单中移除原有的Block动作
        self.Create.removeAction(self.Block)
        
        # 创建Block子菜单
        self.BlockMenu = QMenu(self.lang.get('block_menu', 'Block'), self)
        self.BlockMenu.setObjectName("BlockMenu")
        
        # 创建"继承自..."动作
        self.BlockInherit = QAction(self.lang.get('block_inherit', '继承自...'), self)
        self.BlockInherit.setObjectName("BlockInherit")
        self.BlockInherit.setText(self.lang.get('block_inherit', '继承自...'))
        
        # 创建"自定义..."动作
        self.BlockCustom = QAction(self.lang.get('block_custom', '自定义...'), self)
        self.BlockCustom.setObjectName("BlockCustom")
        self.BlockCustom.setText(self.lang.get('block_custom', '自定义...'))
        
        # 将子动作添加到Block子菜单
        self.BlockMenu.addAction(self.BlockInherit)
        self.BlockMenu.addAction(self.BlockCustom)
        
        # 将Block子菜单添加到Create菜单
        self.Create.addAction(self.BlockMenu.menuAction())
    
    def add_run_menu(self):
        """
        添加Run菜单，包含编译选项
        根据readme.md要求：运行菜单应有"编译..."选项
        """
        
        # 创建Run菜单
        self.Run = QMenu(self.lang.get('run_menu', '运行'), self)
        self.Run.setObjectName("Run")
        
        # 创建编译动作（对应"运行客户端"）
        self.Compile = QAction(self.lang.get('compile_action', '编译...'), self)
        self.Compile.setObjectName("Compile")
        
        # 将编译动作添加到Run菜单
        self.Run.addAction(self.Compile)
        
        # 将Run菜单添加到菜单栏
        self.menubar.addAction(self.Run.menuAction())
    
    def update_menu_texts(self):
        """
        更新所有菜单项的文本为中文翻译
        """
        # 更新文件菜单
        self.File.setTitle(self.lang.get('menu_file', '文件'))
        self.New.setText(self.lang.get('menu_new', '新建'))
        
        # 更新编辑菜单
        self.Edit.setTitle(self.lang.get('menu_edit', '编辑'))
        
        # 更新创建子菜单
        self.Create.setTitle(self.lang.get('menu_create', '创建...'))
        self.Block.setText(self.lang.get('menu_block', '方块'))
        
        # 更新Block子菜单文本
        if hasattr(self, 'BlockMenu'):
            self.BlockMenu.setTitle(self.lang.get('block_menu', '方块'))
            
        self.Item.setText(self.lang.get('menu_item', '物品'))
        self.Tag.setText(self.lang.get('menu_tag', '标签'))
        self.Sound.setText(self.lang.get('menu_sound', '音效'))
        self.Command.setText(self.lang.get('menu_command', '命令'))
        self.Recipe.setText(self.lang.get('menu_recipe', '配方'))
        
        # 更新帮助菜单
        self.Help.setTitle(self.lang.get('menu_help', '帮助'))
        self.aHelp.setText(self.lang.get('menu_help_item', '帮助...'))
        self.About.setText(self.lang.get('menu_about_item', '关于...'))
    
    def load_default_mod_json(self):
        """
        加载默认的mod.json文件
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_mod_json_path = os.path.join(
            current_dir, "..", "res", "nullpack", "mod.json"
        )
        default_mod_json_path = os.path.abspath(default_mod_json_path)
        
        if os.path.exists(default_mod_json_path):
            self.editor.read(default_mod_json_path)
    
    def createNew(self, action):
        """
        处理菜单栏动作触发事件
        
        :param action: 被触发的QAction对象
        """
        action_name = action.objectName()
        action_text = action.text()
        
        # 根据不同的动作执行不同的操作
        if action_name == "New":
            self.handle_new_project()
        elif action_name == "BlockInherit":
            self.handle_block_inherit()
        elif action_name == "BlockCustom":
            self.handle_block_custom()
        elif action_name == "Item":
            self.handle_create_item()
        elif action_name == "Tag":
            self.handle_create_tag()
        elif action_name == "Sound":
            self.handle_create_sound()
        elif action_name == "Command":
            self.handle_create_command()
        elif action_name == "Recipe":
            self.handle_create_recipe()
        elif action_name == "aHelp":
            self.handle_help()
        elif action_name == "About":
            self.handle_about()
        elif action_name == "Open":
            self.handle_open()
        elif action_name == "Compile":
            self.handle_run_client()
        elif action_name == "RunClient":
            self.handle_run_client()
        else:
            QMessageBox.information(self, self.lang.get('information_title', '提示'), f"未实现的功能: {action_text}")
    
    def handle_new_project(self):
        """
        处理新建项目动作
        根据CreateModExample.md的要求：当用户创建完成后，应当自动打开模组
        """
        try:
            # 打开模组创建向导窗口
            self.forge_wizard = ForgeModCreator()
            # 连接模组创建完成信号，自动打开mod.json
            self.forge_wizard.mod_created.connect(self.on_mod_created)
            self.forge_wizard.show()
        except Exception as e:
            QMessageBox.critical(self, self.lang.get('error_title', '错误'), f"打开模组创建向导失败: {e}")
    
    def on_mod_created(self, mod_json_path):
        """
        处理模组创建完成事件
        自动打开创建的mod.json文件
        
        :param mod_json_path: mod.json文件路径
        """
        try:
            # 打开并显示mod.json文件
            if self.editor.read(mod_json_path):
                # 保存当前打开的文件路径
                self.current_mod_json_path = mod_json_path
                self.log_message(f"已自动打开创建的模组: {mod_json_path}")
                QMessageBox.information(self, self.lang.get('information_title', '提示'), 
                                       f"模组已创建并自动打开！")
            else:
                QMessageBox.warning(self, self.lang.get('warning_title', '警告'), 
                                   f"无法读取模组文件: {mod_json_path}")
        except Exception as e:
            QMessageBox.critical(self, self.lang.get('error_title', '错误'), 
                               f"自动打开模组失败: {e}")
    
    def check_and_select_item_group(self, mod_json_path):
        """
        检查并选择ItemGroup
        根据BlockExample.md的要求：
        - 检查是否有ItemGroup，如果没有则弹出新建ItemGroup的向导
        - 如果有：在当前窗口列出所有已有的ItemGroup，用户可以选择其中一个
        
        :param mod_json_path: mod.json文件路径
        :return: 选择的ItemGroup类名，如果取消则返回None
        """
        
        try:
            # 读取mod.json获取已有的itemGroups
            with open(mod_json_path, 'r', encoding='utf-8') as f:
                mod_data = json.load(f)
            
            item_groups = mod_data.get("itemGroups", [])
            
            # 如果没有ItemGroup，弹出新建向导
            if not item_groups:
                reply = QMessageBox.question(
                    self,
                    self.lang.get('information_title', '提示'),
                    self.lang.get('no_itemgroup_message', '没有检测到ItemGroup，需要先创建一个ItemGroup。是否现在创建？'),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    # 打开ItemGroup创建向导
                    return self.create_item_group_wizard(mod_json_path)
                else:
                    return None
            
            # 如果有ItemGroup，显示选择对话框
            dialog = QDialog(self)
            dialog.setWindowTitle(self.lang.get('select_itemgroup_title', '选择ItemGroup'))
            dialog.resize(400, 300)
            
            layout = QVBoxLayout(dialog)
            
            # 提示标签
            layout.addWidget(QLabel(self.lang.get('select_itemgroup_label', '请选择一个ItemGroup:')))
            
            # ItemGroup列表
            list_widget = QListWidget()
            for item_group in item_groups:
                name = item_group.get("name", "Unknown")
                item = QListWidgetItem(name)
                list_widget.addItem(item)
            
            # 默认选择第一个
            if list_widget.count() > 0:
                list_widget.setCurrentRow(0)
            
            layout.addWidget(list_widget)
            
            # 按钮布局
            button_layout = QHBoxLayout()
            
            # 新建按钮
            new_button = QPushButton(self.lang.get('button_new', '新建...'))
            new_button.clicked.connect(lambda: self.create_item_group_wizard(mod_json_path))
            button_layout.addWidget(new_button)
            
            button_layout.addStretch()
            
            # 确认按钮
            ok_button = QPushButton(self.lang.get('button_confirm', '确定'))
            ok_button.clicked.connect(dialog.accept)
            button_layout.addWidget(ok_button)
            
            # 取消按钮
            cancel_button = QPushButton(self.lang.get('button_cancel', '取消'))
            cancel_button.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_button)
            
            layout.addLayout(button_layout)
            
            if dialog.exec_() == QDialog.Accepted:
                current_item = list_widget.currentItem()
                if current_item:
                    return current_item.text()
            
            return None
            
        except Exception as e:
            QMessageBox.critical(self, self.lang.get('error_title', '错误'), f"检查ItemGroup失败: {e}")
            return None
    
    def create_item_group_wizard(self, mod_json_path):
        """
        创建ItemGroup向导
        根据ItemGroupExample.md的要求创建ItemGroup
        
        :param mod_json_path: mod.json文件路径
        :return: 创建的ItemGroup类名，如果取消则返回None
        """
        
        try:
            # 根据readme.md第6行：从mods.toml读取模组信息
            mod_id = self.get_modid_from_mods_toml(mod_json_path)
            if not mod_id:
                # 如果读取失败，尝试从mod.json读取作为备选
                with open(mod_json_path, 'r', encoding='utf-8') as f:
                    mod_data = json.load(f)
                mod_id = mod_data.get("modInfo", {}).get("modid", "unknown")
            
            base_package = self.get_base_package_from_mod_json(mod_json_path, mod_id)
            main_class_name = mod_id.replace('_', '').title() + "Mod"
            
            # 创建对话框
            dialog = QDialog(self)
            dialog.setWindowTitle(self.lang.get('create_itemgroup_title', '创建ItemGroup'))
            dialog.resize(400, 200)
            
            layout = QVBoxLayout(dialog)
            
            # ItemGroup类名输入
            layout.addWidget(QLabel(self.lang.get('label_itemgroup_classname', 'ItemGroup类名:')))
            class_name_edit = QLineEdit()
            class_name_edit.setPlaceholderText("例如: ExampleItemGroup")
            layout.addWidget(class_name_edit)
            
            # 按钮布局
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            # 确认按钮
            ok_button = QPushButton(self.lang.get('button_create', '创建'))
            ok_button.clicked.connect(dialog.accept)
            button_layout.addWidget(ok_button)
            
            # 取消按钮
            cancel_button = QPushButton(self.lang.get('button_cancel', '取消'))
            cancel_button.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_button)
            
            layout.addLayout(button_layout)
            
            if dialog.exec_() == QDialog.Accepted:
                class_name = class_name_edit.text().strip()
                if not class_name:
                    QMessageBox.warning(self, self.lang.get('warning_title', '警告'), 
                                       self.lang.get('classname_required', '请输入类名'))
                    return None
                
                # 创建ItemGroup文件
                item_group_class_name = self.create_item_group_file(
                    mod_json_path, base_package, mod_id, main_class_name, class_name
                )
                
                # 更新mod.json
                self.add_item_group_to_mod_json(mod_json_path, item_group_class_name)
                
                return item_group_class_name
            
            return None
            
        except Exception as e:
            QMessageBox.critical(self, self.lang.get('error_title', '错误'), f"创建ItemGroup失败: {e}")
            return None
    
    def create_item_group_file(self, mod_json_path, base_package, mod_id, main_class_name, item_group_class_name="ExampleItemGroup"):
        """
        创建ItemGroup Java文件
        根据BlockExample.md第59行，使用{item_group_class_name}.java
        
        :param mod_json_path: mod.json文件路径
        :param base_package: 基础包名
        :param mod_id: 模组ID
        :param main_class_name: 主类名
        :param item_group_class_name: ItemGroup类名（默认为ExampleItemGroup）
        :return: ItemGroup类名
        """
        try:
            # 计算路径
            mod_json_dir = os.path.dirname(mod_json_path)
            mdk_path = os.path.join(mod_json_dir, "forge-1.16.5-36.2.34-mdk")
            java_src_path = os.path.join(mdk_path, "src", "main", "java")
            package_dir = os.path.join(java_src_path, *base_package.split("."), "group")
            
            # 创建group文件夹
            os.makedirs(package_dir, exist_ok=True)
            
            # 创建ItemGroup文件 - 使用传入的item_group_class_name
            file_path = os.path.join(package_dir, f"{item_group_class_name}.java")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"package {base_package}.group;\n\n")
                f.write(f"import {base_package}.{main_class_name};\n")
                f.write(f"import {base_package}.item.ModItems;\n")
                f.write("import net.minecraft.item.ItemGroup;\n")
                f.write("import net.minecraft.item.ItemStack;\n\n")
                f.write(f"public class {item_group_class_name} {{\n")
                f.write(f'    public static final ItemGroup TAB = new ItemGroup("{mod_id}_tab") {{\n')
                f.write("        @Override\n")
                f.write("        public ItemStack createIcon() {\n")
                f.write("            return new ItemStack(ModItems.EXAMPLE.get());\n")
                f.write("        }\n")
                f.write("    };\n")
                f.write("}\n")
            
            return item_group_class_name
            
        except Exception as e:
            raise Exception(f"创建ItemGroup文件失败: {e}")
    
    def add_item_group_to_mod_json(self, mod_json_path, item_group_class_name):
        """
        向mod.json添加ItemGroup信息
        
        :param mod_json_path: mod.json文件路径
        :param item_group_class_name: ItemGroup类名
        """
        try:
            with open(mod_json_path, 'r', encoding='utf-8') as f:
                mod_data = json.load(f)
            
            if "itemGroups" not in mod_data:
                mod_data["itemGroups"] = []
            
            # 检查是否已存在
            exists = False
            for ig in mod_data["itemGroups"]:
                if ig.get("name") == item_group_class_name:
                    exists = True
                    break
            
            if not exists:
                mod_data["itemGroups"].append({
                    "name": item_group_class_name
                })
                
                with open(mod_json_path, 'w', encoding='utf-8') as f:
                    json.dump(mod_data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            raise Exception(f"更新mod.json失败: {e}")
    
    def get_modid_from_mods_toml(self, mod_json_path):
        """
        从mods.toml读取modId
        根据readme.md第6行要求：模组信息的获取请直接读取mods.toml
        
        :param mod_json_path: mod.json文件路径
        :return: modId字符串
        """
        try:
            # 从mod.json路径推导mods.toml路径
            mod_json_dir = os.path.dirname(mod_json_path)
            mods_toml_path = os.path.join(
                mod_json_dir, 
                "forge-1.16.5-36.2.34-mdk",
                "src", "main", "resources", "META-INF", 
                "mods.toml"
            )
            
            if not os.path.exists(mods_toml_path):
                self.log_message(f"警告: mods.toml不存在: {mods_toml_path}")
                return None
            
            # 读取并解析mods.toml
            with open(mods_toml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用正则表达式提取modId
            import re
            match = re.search(r'modId\s*=\s*"([^"]+)"', content)
            if match:
                mod_id = match.group(1)
                self.log_message(f"从mods.toml读取modId: {mod_id}")
                return mod_id
            else:
                self.log_message("警告: 无法在mods.toml中找到modId")
                return None
                
        except Exception as e:
            self.log_message(f"读取mods.toml失败: {e}")
            return None
    
    def get_base_package_from_mod_json(self, mod_json_path, mod_id):
        """
        从mod.json路径推导基础包名
        """
        mod_json_dir = os.path.dirname(mod_json_path)
        mdk_path = os.path.join(mod_json_dir, "forge-1.16.5-36.2.34-mdk")
        java_src_path = os.path.join(mdk_path, "src", "main", "java")
        com_dir = os.path.join(java_src_path, "com")
        
        if os.path.exists(com_dir):
            com_subdirs = [d for d in os.listdir(com_dir) if os.path.isdir(os.path.join(com_dir, d))]
            if com_subdirs:
                base_package_name = com_subdirs[0]
                com_base_dir = os.path.join(com_dir, base_package_name)
                
                if os.path.exists(com_base_dir):
                    modid_subdirs = [d for d in os.listdir(com_base_dir) if os.path.isdir(os.path.join(com_base_dir, d))]
                    if modid_subdirs:
                        return f"com.{base_package_name}.{modid_subdirs[0]}"
                    else:
                        return f"com.{base_package_name}.{mod_id}mod"
                else:
                    return f"com.{base_package_name}.{mod_id}mod"
            else:
                return f"com.example.{mod_id}mod"
        else:
            return f"com.example.{mod_id}mod"

    def handle_block_inherit(self):
        """
        处理从现有方块继承创建新方块的动作
        根据BlockExample.md的要求，需要先检查ItemGroup
        """
        try:
            # 获取当前编辑器中打开的mod.json路径
            if hasattr(self.editor, 'file_path') and self.editor.file_path:
                mod_json_path = self.editor.file_path
            else:
                QMessageBox.warning(self, self.lang.get('warning_title', '警告'), "没有打开的mod.json文件")
                return
            
            # 检查并选择ItemGroup
            item_group_class_name = self.check_and_select_item_group(mod_json_path)
            if not item_group_class_name:
                return  # 用户取消或未创建ItemGroup
            
            # 保存选择的ItemGroup类名供后续使用
            self.current_item_group_class_name = item_group_class_name
            
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QLineEdit, QGridLayout, QGroupBox, QCheckBox, QSpinBox, QDoubleSpinBox
            
            # 创建对话框
            dialog = QDialog(self)
            dialog.setWindowTitle(self.lang.get('dialog_title_create_block', '继承自现有方块'))
            dialog.resize(600, 550)  # 增加高度以容纳ItemGroup选择
            
            # 获取所有可用的ItemGroups用于下拉框
            available_item_groups = []
            try:
                with open(mod_json_path, 'r', encoding='utf-8') as f:
                    mod_data = json.load(f)
                available_item_groups = [ig.get("name", "Unknown") for ig in mod_data.get("itemGroups", [])]
            except:
                available_item_groups = [item_group_class_name]
            
            # 创建主布局
            main_layout = QVBoxLayout(dialog)
            
            # 创建表单布局
            form_layout = QGridLayout()
            
            # 1. 方块基本信息
            basic_group = QGroupBox(self.lang.get('group_box_basic_info', '方块基本信息'))
            basic_layout = QGridLayout(basic_group)
            
            # 方块名称
            basic_layout.addWidget(QLabel(self.lang.get('label_block_name', '方块名称 (英文小写，无空格):')), 0, 0)
            self.block_name_edit = QLineEdit()
            self.block_name_edit.setPlaceholderText(self.lang.get('placeholder_block_name', '例如: example_block'))
            basic_layout.addWidget(self.block_name_edit, 0, 1)
            
            # 显示名称
            basic_layout.addWidget(QLabel(self.lang.get('label_display_name', '显示名称 (中文):')), 1, 0)
            self.display_name_edit = QLineEdit()
            self.display_name_edit.setPlaceholderText(self.lang.get('placeholder_display_name', '例如: 示例方块'))
            basic_layout.addWidget(self.display_name_edit, 1, 1)
            
            # 选择方块类型
            basic_layout.addWidget(QLabel(self.lang.get('label_block_type', '选择方块类型:')), 2, 0)
            self.block_type_combo = QComboBox()
            
            # 按分类添加Forge方块模板
            # 0. 最基础方块类
            self.block_type_combo.addItem("-- 0. 最基础方块类 --")
            self.block_type_combo.addItem("Block - 最基础的方块类 (new Block(properties))")
            
            # 1. 基础形状方块模板
            self.block_type_combo.addItem("-- 1. 基础形状方块模板 --")
            self.block_type_combo.addItem("StairsBlock - 楼梯方块 (new StairsBlock(() -> baseBlock.getDefaultState(), properties))")
            self.block_type_combo.addItem("SlabBlock - 半砖/台阶方块 (new SlabBlock(properties))")
            self.block_type_combo.addItem("WallBlock - 墙方块 (new WallBlock(properties))")
            self.block_type_combo.addItem("FenceBlock - 栅栏方块 (new FenceBlock(properties))")
            self.block_type_combo.addItem("FenceGateBlock - 栅栏门方块 (new FenceGateBlock(properties))")
            
            # 2. 交互类方块模板
            self.block_type_combo.addItem("-- 2. 交互类方块模板 --")
            self.block_type_combo.addItem("DoorBlock - 门方块（上下两部分） (new DoorBlock(properties.notSolid()))")
            self.block_type_combo.addItem("TrapDoorBlock - 活板门方块 (new TrapDoorBlock(properties.notSolid()))")
            self.block_type_combo.addItem("PressurePlateBlock - 压力板（可检测实体/物品） (new PressurePlateBlock(Sensitivity.MOBS, properties))")
            self.block_type_combo.addItem("ButtonBlock - 按钮方块 (new ButtonBlock(Mode.PUSH_BUTTON, properties))")
            self.block_type_combo.addItem("LeverBlock - 拉杆方块 (new LeverBlock(properties))")
            
            # 3. 功能性方块模板
            self.block_type_combo.addItem("-- 3. 功能性方块模板 --")
            self.block_type_combo.addItem("TorchBlock - 火把方块（发光） (new TorchBlock(properties.lightValue(14)))")
            self.block_type_combo.addItem("LanternBlock - 灯笼方块 (new LanternBlock(properties.lightValue(15)))")
            self.block_type_combo.addItem("ChestBlock - 箱子方块 (new ChestBlock(properties))")
            self.block_type_combo.addItem("FurnaceBlock - 熔炉方块 (new FurnaceBlock(properties))")
            self.block_type_combo.addItem("CraftingTableBlock - 工作台方块 (new CraftingTableBlock(properties))")
            
            # 4. 特殊方块模板
            self.block_type_combo.addItem("-- 4. 特殊方块模板 --")
            self.block_type_combo.addItem("BedBlock - 床方块 (new BedBlock(BlockColors.COLOR_RED, properties))")
            self.block_type_combo.addItem("CakeBlock - 蛋糕方块 (new CakeBlock(properties))")
            self.block_type_combo.addItem("PistonBlock - 活塞方块 (new PistonBlock(false, properties))")
            self.block_type_combo.addItem("StickyPistonBlock - 粘性活塞方块 (new StickyPistonBlock(properties))")
            self.block_type_combo.addItem("RedstoneLampBlock - 红石灯方块 (new RedstoneLampBlock(properties))")
            
            # 设置默认选择为Block类
            self.block_type_combo.setCurrentIndex(2)
            basic_layout.addWidget(self.block_type_combo, 2, 1)
            
            # 根据BlockExample.md第65行要求：添加ItemGroup选择项
            basic_layout.addWidget(QLabel(self.lang.get('label_itemgroup', '物品分组 (ItemGroup):')), 3, 0)
            self.itemgroup_combo = QComboBox()
            for ig_name in available_item_groups:
                self.itemgroup_combo.addItem(ig_name)
            # 设置默认选中之前选择的ItemGroup
            default_index = self.itemgroup_combo.findText(item_group_class_name)
            if default_index >= 0:
                self.itemgroup_combo.setCurrentIndex(default_index)
            basic_layout.addWidget(self.itemgroup_combo, 3, 1)
            
            # 方块材质类型
            basic_layout.addWidget(QLabel(self.lang.get('label_material_type', '方块材质类型:')), 4, 0)
            self.material_combo = QComboBox()
            
            # 添加所有材质选项
            materials = [
                "AIR - 空气", "STRUCTURE_VOID - 结构虚空", "PORTAL - 传送门", "CARPET - 地毯", 
                "PLANTS - 植物", "OCEAN_PLANT - 海洋植物", "TALL_PLANTS - 高大植物", "NETHER_PLANTS - 下界植物",
                "SEA_GRASS - 海草", "WATER - 水", "BUBBLE_COLUMN - 气泡柱", "LAVA - 岩浆", "SNOW - 雪",
                "FIRE - 火", "MISCELLANEOUS - 杂项", "WEB - 蜘蛛网", "REDSTONE_LIGHT - 红石灯",
                "CLAY - 黏土", "EARTH - 泥土", "ORGANIC - 有机物", "PACKED_ICE - 打包冰", "SAND - 沙子",
                "SPONGE - 海绵", "SHULKER - 潜影贝", "WOOD - 木材", "NETHER_WOOD - 下界木材",
                "BAMBOO_SAPLING - 竹子树苗", "BAMBOO - 竹子", "WOOL - 羊毛", "TNT - TNT", "LEAVES - 树叶",
                "GLASS - 玻璃", "ICE - 冰", "CACTUS - 仙人掌", "ROCK - 岩石", "IRON - 铁",
                "SNOW_BLOCK - 雪块", "ANVIL - 铁砧", "BARRIER - 屏障", "PISTON - 活塞", "CORAL - 珊瑚",
                "GOURD - 葫芦", "DRAGON_EGG - 龙蛋", "CAKE - 蛋糕"
            ]
            
            for material in materials:
                self.material_combo.addItem(material)
            
            # 默认选择岩石材质
            self.material_combo.setCurrentText("ROCK - 岩石")
            basic_layout.addWidget(self.material_combo, 4, 1)
            
            main_layout.addWidget(basic_group)
            
            # 2. 方块属性设置
            properties_group = QGroupBox(self.lang.get('group_box_properties', '方块属性设置'))
            properties_layout = QGridLayout(properties_group)
            
            # 硬度和爆炸抗性
            properties_layout.addWidget(QLabel(self.lang.get('label_hardness', '硬度:')), 0, 0)
            self.hardness_spin = QDoubleSpinBox()
            self.hardness_spin.setRange(0, 100)
            self.hardness_spin.setValue(1.0)
            properties_layout.addWidget(self.hardness_spin, 0, 1)
            
            properties_layout.addWidget(QLabel(self.lang.get('label_resistance', '爆炸抗性:')), 0, 2)
            self.resistance_spin = QDoubleSpinBox()
            self.resistance_spin.setRange(0, 1000)
            self.resistance_spin.setValue(1.0)
            properties_layout.addWidget(self.resistance_spin, 0, 3)
            
            # 挖掘属性
            properties_layout.addWidget(QLabel(self.lang.get('label_harvest_level', '挖掘等级:')), 1, 0)
            self.harvest_level_spin = QSpinBox()
            self.harvest_level_spin.setRange(0, 4)
            self.harvest_level_spin.setValue(0)
            properties_layout.addWidget(self.harvest_level_spin, 1, 1)
            
            properties_layout.addWidget(QLabel(self.lang.get('label_tool_type', '挖掘工具:')), 1, 2)
            self.tool_type_combo = QComboBox()
            self.tool_type_combo.addItems(["无", "PICKAXE - 镐", "AXE - 斧", "SHOVEL - 铲", "HOE - 锄"])
            properties_layout.addWidget(self.tool_type_combo, 1, 3)
            
            # 发光等级
            properties_layout.addWidget(QLabel(self.lang.get('label_light_level', '发光等级 (0-15):')), 2, 0)
            self.light_level_spin = QSpinBox()
            self.light_level_spin.setRange(0, 15)
            self.light_level_spin.setValue(0)
            properties_layout.addWidget(self.light_level_spin, 2, 1)
            
            # 音效类型
            properties_layout.addWidget(QLabel(self.lang.get('label_sound_type', '音效类型:')), 2, 2)
            self.sound_type_combo = QComboBox()
            self.sound_type_combo.addItems(["STONE - 石头", "WOOD - 木头", "METAL - 金属", "GLASS - 玻璃", "GRAVEL - 沙砾", "GRASS - 草", "SNOW - 雪"])
            properties_layout.addWidget(self.sound_type_combo, 2, 3)
            
            # 特殊属性
            properties_layout.addWidget(QLabel(self.lang.get('label_special_properties', '特殊属性:')), 3, 0)
            
            # 非固体
            self.not_solid_check = QCheckBox(self.lang.get('check_not_solid', '非固体 (notSolid)'))
            properties_layout.addWidget(self.not_solid_check, 3, 1)
            
            # 无碰撞
            self.no_collision_check = QCheckBox(self.lang.get('check_no_collision', '无碰撞 (noCollision)'))
            properties_layout.addWidget(self.no_collision_check, 3, 2)
            
            # 需要工具挖掘
            self.requires_tool_check = QCheckBox(self.lang.get('check_requires_tool', '需要工具挖掘 (requiresTool)'))
            properties_layout.addWidget(self.requires_tool_check, 3, 3)
            
            # 无掉落
            self.no_drops_check = QCheckBox(self.lang.get('check_no_drops', '无掉落 (noDrops)'))
            properties_layout.addWidget(self.no_drops_check, 4, 1)
            
            # 随机更新
            self.ticks_randomly_check = QCheckBox(self.lang.get('check_ticks_randomly', '随机更新 (ticksRandomly)'))
            properties_layout.addWidget(self.ticks_randomly_check, 4, 2)
            
            # 可被水淹没
            self.waterlogged_check = QCheckBox(self.lang.get('check_waterlogged', '可被水淹没 (waterlogged)'))
            properties_layout.addWidget(self.waterlogged_check, 4, 3)
            
            main_layout.addWidget(properties_group)
            
            # 创建按钮布局
            button_layout = QHBoxLayout()
            
            # 添加确认按钮
            ok_button = QPushButton(self.lang.get('button_create_block', '创建方块'))
            ok_button.clicked.connect(self.handle_block_inherit_confirm)
            ok_button.clicked.connect(dialog.accept)
            button_layout.addWidget(ok_button)
            
            # 添加取消按钮
            cancel_button = QPushButton(self.lang.get('button_cancel', '取消'))
            cancel_button.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_button)
            
            main_layout.addLayout(button_layout)
            
            # 显示对话框
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, self.lang.get('error_title', '错误'), f"打开方块创建对话框失败: {e}")
    
    def handle_block_inherit_confirm(self):
        """
        处理从现有方块继承创建新方块的确认操作
        """
        try:
            # 获取选择的方块类型文本
            selected_text = self.block_type_combo.currentText()
            
            # 检查是否是分类标题
            if selected_text.startswith("--"):
                QMessageBox.warning(self, self.lang.get('warning_title', '警告'), 
                                   self.lang.get('block_type_warning', '请选择一个实际的方块类型，而不是分类标题'))
                return
            
            # 从选择的文本中提取类名
            selected_block = selected_text.split()[0]
            
            # 获取用户输入的方块名称和显示名称
            block_name = self.block_name_edit.text().strip()
            display_name = self.display_name_edit.text().strip()
            
            # 验证输入
            if not block_name:
                QMessageBox.warning(self, self.lang.get('warning_title', '警告'), 
                                   self.lang.get('block_name_required', '请输入方块名称'))
                return
            
            if not display_name:
                QMessageBox.warning(self, self.lang.get('warning_title', '警告'), 
                                   self.lang.get('display_name_required', '请输入显示名称'))
                return
            
            # 检查方块名称格式
            import re
            if not re.match(r'^[a-z0-9_]+$', block_name):
                QMessageBox.warning(self, self.lang.get('warning_title', '警告'), 
                                   self.lang.get('block_name_format_error', '方块名称只能包含小写字母、数字和下划线'))
                return
            
            # 获取材质类型
            material = self.material_combo.currentText().split()[0]
            
            # 获取属性设置
            hardness = self.hardness_spin.value()
            resistance = self.resistance_spin.value()
            harvest_level = self.harvest_level_spin.value()
            tool_type = self.tool_type_combo.currentText().split()[0] if self.tool_type_combo.currentIndex() > 0 else ""
            light_level = self.light_level_spin.value()
            sound_type = self.sound_type_combo.currentText().split()[0]
            
            # 获取特殊属性
            not_solid = self.not_solid_check.isChecked()
            no_collision = self.no_collision_check.isChecked()
            requires_tool = self.requires_tool_check.isChecked()
            no_drops = self.no_drops_check.isChecked()
            ticks_randomly = self.ticks_randomly_check.isChecked()
            waterlogged = self.waterlogged_check.isChecked()
            
            # 根据BlockExample.md第65行要求：获取对话框中选择的ItemGroup
            selected_item_group = self.itemgroup_combo.currentText()
            self.current_item_group_class_name = selected_item_group
            
            # 生成方块代码
            self.generate_block_code(selected_block, block_name, display_name, material, 
                                   hardness, resistance, harvest_level, tool_type, 
                                   light_level, sound_type, not_solid, no_collision, 
                                   requires_tool, no_drops, ticks_randomly, waterlogged)
            
            QMessageBox.information(self, self.lang.get('new_project_success', '成功'), 
                                   self.lang.get('new_project_success_message', '方块创建成功！'))
            
        except Exception as e:
            QMessageBox.critical(self, self.lang.get('error_title', '错误'), f"创建方块失败: {e}")
    
    def generate_block_code(self, base_block_class, block_name, display_name, material, 
                          hardness, resistance, harvest_level, tool_type, 
                          light_level, sound_type, not_solid, no_collision, 
                          requires_tool, no_drops, ticks_randomly, waterlogged):
        """
        生成方块的Java代码
        根据BlockExample.md的要求，使用选择的ItemGroup
        
        :param base_block_class: 基础方块类名
        :param block_name: 方块名称
        :param display_name: 方块显示名称
        :param material: 方块材质
        :param hardness: 方块硬度
        :param resistance: 方块爆炸抗性
        :param harvest_level: 挖掘等级
        :param tool_type: 挖掘工具类型
        :param light_level: 发光等级
        :param sound_type: 音效类型
        :param not_solid: 是否为非固体
        :param no_collision: 是否无碰撞
        :param requires_tool: 是否需要工具挖掘
        :param no_drops: 是否无掉落
        :param ticks_randomly: 是否随机更新
        :param waterlogged: 是否可被水淹没
        """
        
        # 获取当前编辑器中打开的mod.json路径
        if hasattr(self.editor, 'file_path') and self.editor.file_path:
            mod_json_path = self.editor.file_path
        else:
            QMessageBox.warning(self, self.lang.get('warning_title', '警告'), "没有打开的mod.json文件，无法生成方块代码")
            return
        
        try:
            # 根据readme.md第6行：从mods.toml读取模组信息
            mod_id = self.get_modid_from_mods_toml(mod_json_path)
            if not mod_id:
                # 如果读取失败，尝试从mod.json读取作为备选
                with open(mod_json_path, 'r', encoding='utf-8') as f:
                    mod_data = json.load(f)
                mod_id = mod_data.get("modInfo", {}).get("modid", "unknown")
            
            # 获取选择的ItemGroup类名
            item_group_class_name = getattr(self, 'current_item_group_class_name', None)
            if not item_group_class_name:
                # 尝试从mod.json读取
                with open(mod_json_path, 'r', encoding='utf-8') as f:
                    mod_data = json.load(f)
                item_groups = mod_data.get("itemGroups", [])
                if item_groups:
                    item_group_class_name = item_groups[0].get("name", "ExampleItemGroup")
                else:
                    item_group_class_name = "ExampleItemGroup"
            
            # 根据BlockExample.md的要求：当没有block文件夹时，创建一个新的block文件夹
            
            # 计算mod.json所在目录
            mod_json_dir = os.path.dirname(mod_json_path)
            
            # 查找mdk路径
            mdk_path = os.path.join(mod_json_dir, "forge-1.16.5-36.2.34-mdk")
            
            # 确定Java源文件路径
            java_src_path = os.path.join(mdk_path, "src", "main", "java")
            
            # 从现有的文件夹结构中提取包名信息
            com_dir = os.path.join(java_src_path, "com")
            
            # 检查com目录是否存在
            if os.path.exists(com_dir):
                # 列出com目录下的所有文件夹
                com_subdirs = [d for d in os.listdir(com_dir) if os.path.isdir(os.path.join(com_dir, d))]
                
                if com_subdirs:
                    # 假设com目录下的第一个文件夹就是basePackageName
                    base_package_name = com_subdirs[0]
                    com_base_dir = os.path.join(com_dir, base_package_name)
                    
                    # 列出com.basePackageName目录下的所有文件夹
                    if os.path.exists(com_base_dir):
                        modid_subdirs = [d for d in os.listdir(com_base_dir) if os.path.isdir(os.path.join(com_base_dir, d))]
                        
                        if modid_subdirs:
                            base_package = f"com.{base_package_name}.{modid_subdirs[0]}"
                        else:
                            base_package = f"com.{base_package_name}.{mod_id}mod"
                    else:
                        base_package = f"com.{base_package_name}.{mod_id}mod"
                else:
                    base_package = f"com.example.{mod_id}mod"
            else:
                base_package = f"com.example.{mod_id}mod"
            
            # 创建完整的包路径
            package_dir = os.path.join(java_src_path, *base_package.split("."))
            
            # 根据BlockExample.md的要求，创建block文件夹
            block_dir = os.path.join(package_dir, "block")
            os.makedirs(block_dir, exist_ok=True)
            
            # 创建ModBlocks.java文件
            mod_blocks_path = os.path.join(block_dir, "ModBlocks.java")
            
            # 设置正确的包名
            package_path = f"{base_package}.block"
            
            # 如果文件不存在，创建新文件
            if not os.path.exists(mod_blocks_path):
                self.create_mod_blocks_file(mod_blocks_path, package_path, mod_id, item_group_class_name)
            
            # 添加新方块到ModBlocks.java
            self.add_block_to_mod_blocks(mod_blocks_path, base_block_class, block_name, display_name, 
                                       material, hardness, resistance, harvest_level, tool_type, 
                                       light_level, sound_type, not_solid, no_collision, 
                                       requires_tool, no_drops, ticks_randomly, waterlogged,
                                       item_group_class_name)
            
            # 更新mod.json文件，添加方块信息
            self.update_mod_json(mod_json_path, block_name, mod_id, material, hardness, resistance, 
                               harvest_level, tool_type, light_level)
            
            # 重新加载mod.json文件以显示更新
            self.editor.read(mod_json_path)
            
        except Exception as e:
            QMessageBox.critical(self, self.lang.get('error_title', '错误'), f"生成方块代码失败: {e}")
        
        # 获取当前编辑器中打开的mod.json路径
        if hasattr(self.editor, 'file_path') and self.editor.file_path:
            mod_json_path = self.editor.file_path
        else:
            QMessageBox.warning(self, self.lang.get('warning_title', '警告'), "没有打开的mod.json文件，无法生成方块代码")
            return
        
        try:
            # 根据readme.md第6行：从mods.toml读取模组信息
            mod_id = self.get_modid_from_mods_toml(mod_json_path)
            if not mod_id:
                # 如果读取失败，尝试从mod.json读取作为备选
                with open(mod_json_path, 'r', encoding='utf-8') as f:
                    mod_data = json.load(f)
                mod_id = mod_data.get("modInfo", {}).get("modid", "unknown")
            
            # 根据BlockExample.md的要求：当没有block文件夹时，创建一个新的block文件夹
            
            # 计算mod.json所在目录
            mod_json_dir = os.path.dirname(mod_json_path)
            
            # 查找mdk路径
            mdk_path = os.path.join(mod_json_dir, "forge-1.16.5-36.2.34-mdk")
            
            # 确定Java源文件路径
            java_src_path = os.path.join(mdk_path, "src", "main", "java")
            
            # 从现有的文件夹结构中提取包名信息
            com_dir = os.path.join(java_src_path, "com")
            
            # 检查com目录是否存在
            if os.path.exists(com_dir):
                # 列出com目录下的所有文件夹
                com_subdirs = [d for d in os.listdir(com_dir) if os.path.isdir(os.path.join(com_dir, d))]
                
                if com_subdirs:
                    # 假设com目录下的第一个文件夹就是basePackageName
                    base_package_name = com_subdirs[0]
                    com_base_dir = os.path.join(com_dir, base_package_name)
                    
                    # 列出com.basePackageName目录下的所有文件夹
                    if os.path.exists(com_base_dir):
                        modid_subdirs = [d for d in os.listdir(com_base_dir) if os.path.isdir(os.path.join(com_base_dir, d))]
                        
                        if modid_subdirs:
                            base_package = f"com.{base_package_name}.{modid_subdirs[0]}"
                        else:
                            base_package = f"com.{base_package_name}.{mod_id}mod"
                    else:
                        base_package = f"com.{base_package_name}.{mod_id}mod"
                else:
                    base_package = f"com.example.{mod_id}mod"
            else:
                base_package = f"com.example.{mod_id}mod"
            
            # 创建完整的包路径
            package_dir = os.path.join(java_src_path, *base_package.split("."))
            
            # 根据BlockExample.md的要求，创建block文件夹
            block_dir = os.path.join(package_dir, "block")
            os.makedirs(block_dir, exist_ok=True)
            
            # 创建ModBlocks.java文件
            mod_blocks_path = os.path.join(block_dir, "ModBlocks.java")
            
            # 设置正确的包名
            package_path = f"{base_package}.block"
            
            # 如果文件不存在，创建新文件
            if not os.path.exists(mod_blocks_path):
                self.create_mod_blocks_file(mod_blocks_path, package_path, mod_id)
            
            # 添加新方块到ModBlocks.java
            self.add_block_to_mod_blocks(mod_blocks_path, base_block_class, block_name, display_name, 
                                       material, hardness, resistance, harvest_level, tool_type, 
                                       light_level, sound_type, not_solid, no_collision, 
                                       requires_tool, no_drops, ticks_randomly, waterlogged)
            
            # 更新mod.json文件，添加方块信息
            self.update_mod_json(mod_json_path, block_name, mod_id, material, hardness, resistance, 
                               harvest_level, tool_type, light_level)
            
            # 根据BlockExample.md要求：生成blockState文件
            self.create_blockstate_file(mdk_path, mod_id, block_name)
            
            # 根据BlockExample.md要求：生成模型文件
            self.create_block_model_file(mdk_path, mod_id, block_name)
            self.create_item_model_file(mdk_path, mod_id, block_name)
            
            # 根据BlockExample.md要求：生成战利品表文件
            self.create_loot_table_file(mdk_path, mod_id, block_name)
            
            # 根据BlockExample.md要求：提示用户选择贴图文件
            self.select_and_copy_texture(mdk_path, mod_id, block_name)
            
            # 重新加载mod.json文件以显示更新
            self.editor.read(mod_json_path)
            
        except Exception as e:
            QMessageBox.critical(self, self.lang.get('error_title', '错误'), f"生成方块代码失败: {e}")
    
    def update_mod_json(self, mod_json_path, block_name, mod_id, material, hardness, resistance, 
                       harvest_level, tool_type, light_level):
        """
        更新mod.json文件，添加方块信息
        
        :param mod_json_path: mod.json文件路径
        :param block_name: 方块名称
        :param mod_id: 模组ID
        :param material: 方块材质
        :param hardness: 方块硬度
        :param resistance: 方块爆炸抗性
        :param harvest_level: 挖掘等级
        :param tool_type: 挖掘工具类型
        :param light_level: 发光等级
        """
        
        try:
            # 读取mod.json文件
            with open(mod_json_path, 'r', encoding='utf-8') as f:
                mod_data = json.load(f)
            
            # 确保blocks数组存在
            if "blocks" not in mod_data:
                mod_data["blocks"] = []
            
            # 检查方块是否已存在
            block_exists = False
            for block in mod_data["blocks"]:
                if block["name"] == block_name:
                    block_exists = True
                    break
            
            if not block_exists:
                # 创建新的方块信息
                new_block = {
                    "name": block_name,
                    "registryName": f"{mod_id}:{block_name}",
                    "unlocalizedName": f"tile.{mod_id}.{block_name}",
                    "material": material,
                    "hardness": float(hardness),  # 确保是浮点数
                    "resistance": float(resistance),  # 确保是浮点数
                    "harvestLevel": int(harvest_level),
                    "harvestTool": tool_type.lower() if tool_type else "",
                    "lightValue": int(light_level),
                    "lightOpacity": 255,  # 默认不透明
                    "creativeTab": mod_id,
                    "textureName": f"{mod_id}:blocks/{block_name}",
                    "model": f"{mod_id}:block/{block_name}",
                    "defaultState": {},
                    "variants": []
                }
                
                # 添加方块到blocks数组
                mod_data["blocks"].append(new_block)
                
                # 写入更新后的mod.json文件
                with open(mod_json_path, 'w', encoding='utf-8') as f:
                    json.dump(mod_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            raise Exception(f"更新mod.json失败: {e}")
    
    def create_mod_blocks_file(self, file_path, package_path, mod_id, item_group_class_name="ExampleItemGroup"):
        """
        创建ModBlocks.java文件
        根据BlockExample.md的要求，使用指定的ItemGroup
        
        :param file_path: 文件路径
        :param package_path: 包名
        :param mod_id: 模组ID
        :param item_group_class_name: ItemGroup类名
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # 使用正确的字符串拼接方法
                mod_class_name = mod_id.replace('_', '').title() + "Mod"
                
                # 写入package声明
                f.write(f"package {package_path};\n\n")
                
                # 写入import声明
                f.write(f"import {package_path.replace('.block', '')}.{mod_class_name};\n")
                f.write(f"import {package_path.replace('.block', '')}.item.ModItems;\n")
                f.write(f"import {package_path.replace('.block', '')}.group.{item_group_class_name};\n\n")
                f.write("import net.minecraft.block.AbstractBlock;\n")
                f.write("import net.minecraft.block.Block;\n")
                f.write("import net.minecraft.block.material.Material;\n")
                f.write("import net.minecraft.item.BlockItem;\n")
                f.write("import net.minecraft.item.Item;\n")
                f.write("import net.minecraftforge.common.ToolType;\n")
                f.write("import net.minecraftforge.eventbus.api.IEventBus;\n")
                f.write("import net.minecraftforge.fml.RegistryObject;\n")
                f.write("import net.minecraftforge.registries.DeferredRegister;\n")
                f.write("import net.minecraftforge.registries.ForgeRegistries;\n\n")
                f.write("import java.util.Arrays;\n")
                f.write("import java.util.function.Supplier;\n\n")
                
                # 写入类声明
                f.write("public class ModBlocks {\n")
                
                # 写入BLOCKS注册器
                f.write(f"    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, {mod_class_name}.MOD_ID);\n\n")
                
                # 写入registerBlock方法
                f.write("    private static <T extends Block> RegistryObject<T> registerBlock(String name, Supplier<T> block) {\n")
                f.write("        RegistryObject<T> tro = BLOCKS.register(name, block);\n")
                f.write("        registerBlockItem(name, tro);\n")
                f.write("        return tro;\n")
                f.write("    }\n\n")
                
                # 写入registerBlockItem方法 - 根据BlockExample.md第52行使用{ItemGroupClassName}.TAB
                f.write("    private static <T extends Block> void registerBlockItem(String name, RegistryObject<T> block) {\n")
                f.write(f"        ModItems.ITEMS.register(\n")
                f.write(f"            name, () -> new BlockItem(\n")
                f.write(f"                block.get(),\n")
                f.write(f"                new Item.Properties().group({item_group_class_name}.TAB)\n")
                f.write(f"            )\n")
                f.write(f"        );\n")
                f.write("    }\n\n")
                
                # 写入register方法
                f.write("    public static void register(IEventBus eventBus) {\n")
                f.write("        BLOCKS.register(eventBus);\n")
                f.write("    }\n")
                
                # 写入类结束
                f.write("}\n")
                
        except Exception as e:
            raise Exception(f"创建ModBlocks.java文件失败: {e}")
    
    def add_block_to_mod_blocks(self, file_path, base_block_class, block_name, display_name, material, 
                               hardness, resistance, harvest_level, tool_type, 
                               light_level, sound_type, not_solid, no_collision, 
                               requires_tool, no_drops, ticks_randomly, waterlogged,
                               item_group_class_name="ExampleItemGroup"):
        """
        向ModBlocks.java文件添加新方块
        
        :param file_path: ModBlocks.java文件路径
        :param base_block_class: 基础方块类名
        :param block_name: 方块名称
        :param display_name: 方块显示名称
        :param material: 方块材质
        :param hardness: 方块硬度
        :param resistance: 方块爆炸抗性
        :param harvest_level: 挖掘等级
        :param tool_type: 挖掘工具类型
        :param light_level: 发光等级
        :param sound_type: 音效类型
        :param not_solid: 是否为非固体
        :param no_collision: 是否无碰撞
        :param requires_tool: 是否需要工具挖掘
        :param no_drops: 是否无掉落
        :param ticks_randomly: 是否随机更新
        :param waterlogged: 是否可被水淹没
        :param item_group_class_name: ItemGroup类名
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 生成方块注册代码
            block_registry = []
            block_registry.append(f"    public static final RegistryObject<{base_block_class}> {block_name.upper()} = registerBlock(")
            block_registry.append(f"        \"{block_name}\",")
            block_registry.append(f"        () -> new {base_block_class}(")
            block_registry.append(f"            AbstractBlock.Properties.create(Material.{material})")
            
            # 添加属性设置
            if hardness > 0 or resistance > 0:
                block_registry.append(f"                .hardnessAndResistance({hardness}f, {resistance}f)")
            elif hardness > 0:
                block_registry.append(f"                .hardnessAndResistance({hardness}f)")
            
            if harvest_level > 0:
                block_registry.append(f"                .harvestLevel({harvest_level})")
            
            if tool_type:
                block_registry.append(f"                .harvestTool(ToolType.{tool_type})")
            
            if light_level > 0:
                block_registry.append(f"                .setLightLevel(state -> {light_level})")
            
            if sound_type:
                block_registry.append(f"                .sound(SoundType.{sound_type})")
            
            if not_solid:
                block_registry.append(f"                .notSolid()")
            
            if no_collision:
                block_registry.append(f"                .noCollision()")
            
            if requires_tool:
                block_registry.append(f"                .setRequiresTool()")
            
            if no_drops:
                block_registry.append(f"                .noDrops()")
            
            if ticks_randomly:
                block_registry.append(f"                .ticksRandomly()")
            
            if waterlogged:
                block_registry.append(f"                .waterlogged()")
            
            block_registry.append(f"            )")
            block_registry.append(f"    );")
            
            # 将列表转换为字符串
            block_registry_str = "\n".join(block_registry) + "\n"
            
            # 在register方法之前插入新方块
            register_method_index = content.find("    public static void register(IEventBus eventBus) {")
            if register_method_index != -1:
                new_content = content[:register_method_index] + block_registry_str + "\n" + content[register_method_index:]
            else:
                # 如果没找到register方法，在类末尾插入
                class_end_index = content.rfind("}")
                new_content = content[:class_end_index] + "\n" + block_registry_str + "\n" + content[class_end_index:]
            
            # 添加必要的导入
            if base_block_class not in ["Block"]:
                new_content = new_content.replace("import net.minecraft.block.Block;", 
                                                f"import net.minecraft.block.Block;\nimport net.minecraft.block.{base_block_class};")
            
            if not new_content.__contains__("import net.minecraft.block.SoundType;"):
                new_content = new_content.replace("import net.minecraft.block.AbstractBlock;", 
                                                f"import net.minecraft.block.AbstractBlock;\nimport net.minecraft.block.SoundType;")
            
            # 写入更新后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
        except Exception as e:
            raise Exception(f"向ModBlocks.java添加方块失败: {e}")
    
    def handle_create_block_custom(self):
        """
        处理自定义创建新方块的动作
        """
        QMessageBox.information(self, self.lang.get('information_title', '提示'), "自定义方块创建功能尚未实现")
    
    def handle_create_item(self):
        """
        处理创建物品动作
        """
        QMessageBox.information(self, self.lang.get('information_title', '提示'), "物品创建功能尚未实现")
    
    def handle_create_tag(self):
        """
        处理创建标签动作
        """
        QMessageBox.information(self, self.lang.get('information_title', '提示'), "标签创建功能尚未实现")
    
    def handle_create_sound(self):
        """
        处理创建声音动作
        """
        QMessageBox.information(self, self.lang.get('information_title', '提示'), "声音创建功能尚未实现")
    
    def handle_create_command(self):
        """
        处理创建命令动作
        """
        QMessageBox.information(self, self.lang.get('information_title', '提示'), "命令创建功能尚未实现")
    
    def handle_create_recipe(self):
        """
        处理创建配方动作
        """
        QMessageBox.information(self, self.lang.get('information_title', '提示'), "配方创建功能尚未实现")
    
    def handle_help(self):
        """
        处理帮助动作
        """
        QMessageBox.information(self, self.lang.get('help_title', '帮助'), self.lang.get('help_content', 'Forge模组构建器帮助信息\n\n版本: 1.0.0\n功能: 创建Minecraft Forge 1.16.5模组\n作者: 华为'))
    
    def handle_about(self):
        """
        处理关于动作
        """
        QMessageBox.information(self, self.lang.get('about_title', '关于'), self.lang.get('about_content', 'Forge模组构建器\n\n版本: 1.0.0\n基于Minecraft Forge 1.16.5\n(c) Copyright by 华为'))
    
    def handle_open(self):
        """
        处理打开模组JSON文件动作
        """
        try:
            # 弹出文件对话框，让用户选择mod.json文件
            file_path, _ = QFileDialog.getOpenFileName(
                self, self.lang.get('open_file_title', '打开模组JSON文件'), ".", "JSON文件 (*.json);;所有文件 (*.*)"
            )
            
            if file_path:
                # 读取并显示JSON文件
                if self.editor.read(file_path):
                    # 保存当前打开的文件路径
                    self.current_mod_json_path = file_path
                    self.log_message(self.lang.get('file_opened_message', '已打开文件: {file_path}').format(file_path=file_path))
                else:
                    QMessageBox.warning(self, self.lang.get('warning_title', '警告'), self.lang.get('file_read_warning', '无法读取选择的文件'))
                    
        except Exception as e:
            QMessageBox.critical(self, self.lang.get('error_title', '错误'), f"打开文件失败: {e}")
    
    def handle_run_client(self):
        """
        执行gradle runClient任务
        """
        
        # 检查用户是否打开或创建了文件
        if not hasattr(self, 'current_mod_json_path') or not self.current_mod_json_path:
            QMessageBox.critical(self, self.lang.get('error_title', '错误'), self.lang.get('no_file_error', '请先打开/创建文件'))
            return
        
        # 确定项目的forge目录路径
        try:
            mod_json_dir = os.path.dirname(self.current_mod_json_path)
            forge_dir = os.path.join(mod_json_dir, 'forge-1.16.5-36.2.34-mdk')
            
            # 验证forge目录存在
            if not os.path.exists(forge_dir):
                QMessageBox.critical(self, self.lang.get('error_title', '错误'), self.lang.get('forge_dir_not_found', 'Forge目录不存在: {forge_dir}').format(forge_dir=forge_dir))
                return
            
            # 确定Gradle脚本的路径
            if os.name == 'nt':  # Windows
                gradle_script = os.path.join(forge_dir, 'gradlew.bat')
            else:  # Unix/Linux/macOS
                gradle_script = os.path.join(forge_dir, 'gradlew')
            
            # 验证Gradle脚本存在
            if not os.path.exists(gradle_script):
                QMessageBox.critical(self, self.lang.get('error_title', '错误'), self.lang.get('gradle_script_not_found', 'Gradle脚本不存在: {gradle_script}').format(gradle_script=gradle_script))
                return
            
            # 构建runClient命令
            build_command = [gradle_script, 'runClient', '--no-daemon']
            
            # 执行命令
            self.log_message("开始运行Minecraft客户端...")
            self.log_message(f"执行命令: {' '.join(build_command)}")
            
            # 标准化路径，确保使用正确的路径分隔符
            forge_dir = os.path.normpath(forge_dir)
            gradle_script = os.path.normpath(gradle_script)
            
            # 启动一个新的终端窗口执行命令（这样用户可以看到运行过程和输出）
            if os.name == 'nt':  # Windows
                # 创建一个批处理文件来执行命令，这样更可靠
                import tempfile
                batch_content = f"""@echo off
chcp 65001 >nul
cd /d "{forge_dir}"
echo 正在执行Gradle runClient任务...
echo ----------------------------------
"{gradle_script}" runClient --no-daemon
echo.
echo 任务执行完成。按任意键继续...
pause"""
                
                # 创建临时批处理文件
                with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='utf-8') as temp_batch:
                    temp_batch.write(batch_content)
                    temp_batch_path = temp_batch.name
                
                # 使用cmd.exe打开批处理文件
                subprocess.Popen(['cmd.exe', '/k', temp_batch_path], shell=False)
            elif os.name == 'posix':  # Unix/Linux/macOS
                # 使用xterm -hold参数，即使命令失败，终端窗口也会保持打开
                subprocess.Popen(['xterm', '-hold', '-e', f'cd "{forge_dir}" && echo 正在执行Gradle runClient任务...; echo ----------------------------------; "{gradle_script}" runClient --no-daemon; echo; echo 任务执行完成。按任意键继续...; read -n 1 -s'])
            
            self.log_message(self.lang.get('client_running_message', '已启动客户端运行任务'))
            
        except Exception as e:
            self.log_message(self.lang.get('client_error_message', '运行客户端时出错: {e}').format(e=e))
            QMessageBox.critical(self, self.lang.get('error_title', '错误'), self.lang.get('client_error_message', '运行客户端时出错: {e}').format(e=e))
    
    def create_blockstate_file(self, mdk_path, mod_id, block_name):
        """
        创建blockState文件
        根据BlockExample.md第206-216行
        
        :param mdk_path: MDK路径
        :param mod_id: 模组ID
        :param block_name: 方块名称
        """
        try:
            blockstates_dir = os.path.join(mdk_path, "src", "main", "resources", "assets", mod_id, "blockstates")
            os.makedirs(blockstates_dir, exist_ok=True)
            
            blockstate_file = os.path.join(blockstates_dir, f"{block_name}.json")
            
            blockstate_content = f'''{{
    "variants": {{
        "": {{
            "model": "{mod_id}:block/{block_name}"
        }}
    }}
}}'''
            
            with open(blockstate_file, 'w', encoding='utf-8') as f:
                f.write(blockstate_content)
            
            self.log_message(f"已创建blockState文件: {blockstate_file}")
            
        except Exception as e:
            self.log_message(f"创建blockState文件失败: {e}")
    
    def create_block_model_file(self, mdk_path, mod_id, block_name):
        """
        创建方块模型文件
        根据BlockExample.md第218-227行
        
        :param mdk_path: MDK路径
        :param mod_id: 模组ID
        :param block_name: 方块名称
        """
        try:
            models_block_dir = os.path.join(mdk_path, "src", "main", "resources", "assets", mod_id, "models", "block")
            os.makedirs(models_block_dir, exist_ok=True)
            
            model_file = os.path.join(models_block_dir, f"{block_name}.json")
            
            model_content = f'''{{
    "parent": "block/cube_all",
    "textures": {{
        "all": "{mod_id}:textures/block/{block_name}"
    }}
}}'''
            
            with open(model_file, 'w', encoding='utf-8') as f:
                f.write(model_content)
            
            self.log_message(f"已创建方块模型文件: {model_file}")
            
        except Exception as e:
            self.log_message(f"创建方块模型文件失败: {e}")
    
    def create_item_model_file(self, mdk_path, mod_id, block_name):
        """
        创建物品模型文件（掉落物模型）
        根据BlockExample.md第229-235行
        
        :param mdk_path: MDK路径
        :param mod_id: 模组ID
        :param block_name: 方块名称
        """
        try:
            models_item_dir = os.path.join(mdk_path, "src", "main", "resources", "assets", mod_id, "models", "item")
            os.makedirs(models_item_dir, exist_ok=True)
            
            item_model_file = os.path.join(models_item_dir, f"{block_name}.json")
            
            item_model_content = f'''{{
    "parent": "{mod_id}:block/{block_name}"
}}'''
            
            with open(item_model_file, 'w', encoding='utf-8') as f:
                f.write(item_model_content)
            
            self.log_message(f"已创建物品模型文件: {item_model_file}")
            
        except Exception as e:
            self.log_message(f"创建物品模型文件失败: {e}")
    
    def create_loot_table_file(self, mdk_path, mod_id, block_name):
        """
        创建战利品表文件
        根据BlockExample.md第237-254行
        
        :param mdk_path: MDK路径
        :param mod_id: 模组ID
        :param block_name: 方块名称
        """
        try:
            loot_tables_dir = os.path.join(mdk_path, "src", "main", "resources", "data", mod_id, "loot_tables", "blocks")
            os.makedirs(loot_tables_dir, exist_ok=True)
            
            loot_table_file = os.path.join(loot_tables_dir, f"{block_name}.json")
            
            loot_table_content = f'''{{
    "type": "minecraft:block",
    "pools": [
        {{
            "rolls": 1,
            "entries": [
                {{
                    "type": "minecraft:item",
                    "name": "{mod_id}:{block_name}"
                }}
            ]
        }}
    ]
}}'''
            
            with open(loot_table_file, 'w', encoding='utf-8') as f:
                f.write(loot_table_content)
            
            self.log_message(f"已创建战利品表文件: {loot_table_file}")
            
        except Exception as e:
            self.log_message(f"创建战利品表文件失败: {e}")
    
    def select_and_copy_texture(self, mdk_path, mod_id, block_name):
        """
        提示用户选择贴图文件并复制到指定位置
        根据BlockExample.md第300-301行
        
        :param mdk_path: MDK路径
        :param mod_id: 模组ID
        :param block_name: 方块名称
        """
        
        try:
            # 提示用户选择贴图文件
            reply = QMessageBox.question(
                self,
                self.lang.get('texture_select_title', '选择贴图'),
                self.lang.get('texture_select_message', '是否要为方块选择贴图文件？\n提示：请尽量选择1:1比例的PNG格式图片'),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # 打开文件选择对话框
                texture_file, _ = QFileDialog.getOpenFileName(
                    self,
                    self.lang.get('texture_select_dialog', '选择贴图文件'),
                    "",
                    "PNG Images (*.png)"
                )
                
                if texture_file:
                    # 目标路径
                    textures_dir = os.path.join(mdk_path, "src", "main", "resources", "assets", mod_id, "textures", "block")
                    os.makedirs(textures_dir, exist_ok=True)
                    
                    target_file = os.path.join(textures_dir, f"{block_name}.png")
                    
                    # 复制文件
                    shutil.copy2(texture_file, target_file)
                    self.log_message(f"已复制贴图文件: {texture_file} -> {target_file}")
                else:
                    self.log_message("用户取消了贴图选择")
            else:
                self.log_message("用户选择不添加贴图")
                
        except Exception as e:
            self.log_message(f"处理贴图文件失败: {e}")


if __name__ == "__main__":
    """
    应用程序入口点
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())