#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft Forge 1.16.5 模组创建向导
用于快速创建基于Forge的Minecraft模组项目
"""

import sys
import os
import re
import tempfile
import shutil
import platform
import urllib.request
import urllib.error
import subprocess
import ctypes
import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, 
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, 
    QComboBox, QTextEdit, QGroupBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# 导入工具函数
from utils import is_admin, run_as_admin, ensure_admin_privileges, validate_modid, create_main_class_name, create_package_name


# 构建线程类
class BuildThread(QThread):
    """
    用于在后台执行模组构建过程的线程类
    """
    # 信号定义
    log_signal = pyqtSignal(str)  # 日志信号
    build_finished = pyqtSignal(bool)  # 构建完成信号
    
    def __init__(self, mod_creator, directory, modid, basename, main_class):
        """
        初始化构建线程
        
        :param mod_creator: ForgeModCreator实例
        :param directory: 模组保存目录
        :param modid: 模组ID
        :param basename: 基础包名
        :param main_class: 主类名
        """
        super().__init__()
        self.mod_creator = mod_creator
        self.directory = directory
        self.modid = modid
        self.basename = basename
        self.main_class = main_class
    
    def run(self):
        """线程执行的构建过程"""
        try:
            # 执行配置和构建
            self.mod_creator.config_mod_async(self.directory, self.modid, self.basename, self.main_class)
            self.build_finished.emit(True)
        except Exception as e:
            self.log_signal.emit(f"构建过程中发生异常: {e}")
            import traceback
            for line in traceback.format_exc().split('\n'):
                if line:
                    self.log_signal.emit(line)
            self.build_finished.emit(False)


class ForgeModCreator(QMainWindow):
    """
    Minecraft Forge 1.16.5 模组创建向导主窗口
    """
    # 信号定义
    log_signal = pyqtSignal(str)  # 用于子线程向主线程发送日志信息
    mod_created = pyqtSignal(str)  # 模组创建完成信号，传递mod.json文件路径
    
    def __init__(self):
        """
        初始化模组创建向导
        """
        super().__init__()
        # 加载语言文件
        self.load_language('zh_CN')
        # 连接信号
        self.log_signal.connect(self.log_message)
        self.init_ui()
        
        # 检查是否有Java 8
        java_path = self.has_java8()
        if not java_path:
            QMessageBox.critical(self, self.lang.get('java_error_title', '错误'), self.lang.get('java_error_message', '未找到Java 8！Minecraft Forge 1.16.5需要Java 8才能正常工作。'))
            sys.exit(0)
        else:
            self.log_message(self.lang.get('java_found_message', 'Java 8 已安装：{java_path}').format(java_path=java_path))
            self.java_path = java_path
    
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
                'window_title': 'Minecraft Forge 1.16.5 模组快速创建器',
                'mod_info_group': '模组基本信息',
                'mod_name_label': '模组名称:',
                'mod_version_label': '模组版本:',
                'mc_version_label': 'Minecraft版本:',
                'forge_version_label': 'Forge版本:',
                'mod_author_label': '模组作者:',
                'mod_description_label': '模组描述:',
                'save_path_label': '保存位置:',
                'browse_button': '浏览...',
                'package_group': '包结构设置',
                'base_package_label': '基础包名:',
                'modid_label': '模组ID:',
                'dependencies_group': '依赖管理',
                'dep_jei': 'Just Enough Items (JEI)',
                'dep_cc': 'Curios API',
                'dep_tconstruct': "Tinkers' Construct",
                'dep_custom': '自定义依赖 (格式: modid:version)',
                'resources_group': '资源文件选项',
                'resources_models': '模型文件（必选）',
                'resources_textures': '纹理文件（必选）',
                'resources_lang': '语言文件（必选）',
                'resources_recipes': '配方文件',
                'resources_loot_tables': '战利品表',
                'resources_tags_mod': '模组标签表',
                'resources_tags_common': '公共标签表',
                'log_group': '构建日志',
                'create_button': '创建模组项目',
                'create_mod_message': '创建模组...'
            }
            self.log_message(f"加载语言文件失败，使用默认语言: {e}")
    
    def init_ui(self):
        """
        初始化用户界面
        """
        self.setWindowTitle(self.lang.get('window_title', 'Minecraft Forge 1.16.5 模组快速创建器'))
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # 模组基本信息
        mod_info_group = QGroupBox(self.lang.get('mod_info_group', '模组基本信息'))
        mod_info_layout = QGridLayout()
        
        mod_info_layout.addWidget(QLabel(self.lang.get('mod_name_label', '模组名称:')), 0, 0)
        self.mod_name = QLineEdit()
        mod_info_layout.addWidget(self.mod_name, 0, 1)
        
        mod_info_layout.addWidget(QLabel(self.lang.get('mod_version_label', '模组版本:')), 0, 2)
        self.mod_version = QLineEdit('1.0.0')
        mod_info_layout.addWidget(self.mod_version, 0, 3)
        
        mod_info_layout.addWidget(QLabel(self.lang.get('mc_version_label', 'Minecraft版本:')), 1, 0)
        self.mc_version = QComboBox()
        self.mc_version.addItem('1.16.5')
        mod_info_layout.addWidget(self.mc_version, 1, 1)
        
        mod_info_layout.addWidget(QLabel(self.lang.get('forge_version_label', 'Forge版本:')), 1, 2)
        self.forge_version = QLineEdit('36.2.34')
        mod_info_layout.addWidget(self.forge_version, 1, 3)
        
        mod_info_layout.addWidget(QLabel(self.lang.get('mod_author_label', '模组作者:')), 2, 0)
        self.mod_author = QLineEdit()
        mod_info_layout.addWidget(self.mod_author, 2, 1)
        
        mod_info_layout.addWidget(QLabel(self.lang.get('mod_description_label', '模组描述:')), 3, 0)
        self.mod_description = QTextEdit()
        mod_info_layout.addWidget(self.mod_description, 3, 1, 1, 3)
        
        # 保存位置
        mod_info_layout.addWidget(QLabel(self.lang.get('save_path_label', '保存位置:')), 4, 0)
        self.save_path = QLineEdit(os.path.join(os.path.expanduser("~"), "Desktop"))
        mod_info_layout.addWidget(self.save_path, 4, 1, 1, 2)
        
        self.browse_button = QPushButton(self.lang.get('browse_button', '浏览...'))
        self.browse_button.clicked.connect(self.browse_save_path)
        mod_info_layout.addWidget(self.browse_button, 4, 3)
        
        mod_info_group.setLayout(mod_info_layout)
        main_layout.addWidget(mod_info_group)
        
        # 包结构设置

        package_group = QGroupBox(self.lang.get('package_group', '包结构设置'))
        package_layout = QGridLayout()
        
        package_layout.addWidget(QLabel(self.lang.get('base_package_label', '基础包名:')), 0, 0)
        self.base_package = QLineEdit('example')
        package_layout.addWidget(self.base_package, 0, 1)
        
        package_layout.addWidget(QLabel(self.lang.get('modid_label', '模组ID:')), 0, 2)
        self.modid_input = QLineEdit('mymod')
        package_layout.addWidget(self.modid_input, 0, 3)
        
        package_group.setLayout(package_layout)
        main_layout.addWidget(package_group)
        
        # 依赖管理
        dependencies_group = QGroupBox(self.lang.get('dependencies_group', '依赖管理'))
        dependencies_layout = QVBoxLayout()
        
        self.dep_jei = QCheckBox(self.lang.get('dep_jei', 'Just Enough Items (JEI)'))
        dependencies_layout.addWidget(self.dep_jei)
        
        self.dep_cc = QCheckBox(self.lang.get('dep_cc', 'Curios API'))
        dependencies_layout.addWidget(self.dep_cc)
        
        self.dep_tconstruct = QCheckBox(self.lang.get('dep_tconstruct', "Tinkers' Construct"))
        dependencies_layout.addWidget(self.dep_tconstruct)
        
        self.dep_custom = QLineEdit(self.lang.get('dep_custom', '自定义依赖 (格式: modid:version)'))
        dependencies_layout.addWidget(self.dep_custom)
        
        dependencies_group.setLayout(dependencies_layout)
        main_layout.addWidget(dependencies_group)
        
        # 资源文件选项
        resources_group = QGroupBox(self.lang.get('resources_group', '资源文件选项'))
        resources_layout = QVBoxLayout()
        
        # 必选项（无法取消）
        self.resources_models = QCheckBox(self.lang.get('resources_models', '模型文件（必选）'))
        self.resources_models.setChecked(True)
        self.resources_models.setEnabled(False)
        resources_layout.addWidget(self.resources_models)
        
        self.resources_textures = QCheckBox(self.lang.get('resources_textures', '纹理文件（必选）'))
        self.resources_textures.setChecked(True)
        self.resources_textures.setEnabled(False)
        resources_layout.addWidget(self.resources_textures)
        
        self.resources_lang = QCheckBox(self.lang.get('resources_lang', '语言文件（必选）'))
        self.resources_lang.setChecked(True)
        self.resources_lang.setEnabled(False)
        resources_layout.addWidget(self.resources_lang)
        
        # 可选项
        self.resources_recipes = QCheckBox(self.lang.get('resources_recipes', '配方文件'))
        resources_layout.addWidget(self.resources_recipes)
        
        self.resources_loot_tables = QCheckBox(self.lang.get('resources_loot_tables', '战利品表'))
        resources_layout.addWidget(self.resources_loot_tables)
        
        self.resources_tags_mod = QCheckBox(self.lang.get('resources_tags_mod', '模组标签表'))
        resources_layout.addWidget(self.resources_tags_mod)
        
        self.resources_tags_common = QCheckBox(self.lang.get('resources_tags_common', '公共标签表'))
        resources_layout.addWidget(self.resources_tags_common)
        
        resources_group.setLayout(resources_layout)
        main_layout.addWidget(resources_group)
        
        # 构建日志显示区域
        log_group = QGroupBox(self.lang.get('log_group', '构建日志'))
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # 创建按钮
        create_layout = QHBoxLayout()
        create_layout.addStretch()
        
        self.create_button = QPushButton(self.lang.get('create_button', '创建模组项目'))
        self.create_button.setStyleSheet('background-color: #4CAF50; color: white; font-weight: bold;')
        self.create_button.clicked.connect(self.create_mod)
        create_layout.addWidget(self.create_button)
        
        main_layout.addLayout(create_layout)
    
    def log_message(self, message):
        """
        将日志信息同时输出到控制台和GUI日志区域
        
        :param message: 日志信息
        """
        print(message)
        
        # 检查log_text属性是否已创建
        if hasattr(self, 'log_text') and self.log_text is not None:
            self.log_text.append(message)
            # 确保日志区域始终显示最新内容
            self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    def browse_save_path(self):
        """
        打开文件夹选择对话框，让用户选择模组保存位置
        """
        directory = QFileDialog.getExistingDirectory(
            self, 
            self.lang.get('select_save_location', '选择模组保存位置'), 
            self.save_path.text(),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if directory:
            self.save_path.setText(directory)
    
    def create_mod(self):
        """
        开始创建模组项目
        """
        try:
            # 获取并验证modid
            modid_input = self.modid_input.text()
            modid = validate_modid(modid_input)
            
            # 自动创建主类名
            main_class = create_main_class_name(modid)
            
            # 构建完整包名
            full_package = create_package_name(self.base_package.text(), modid)
            
            # 这里将实现创建模组的逻辑
            self.log_message(self.lang.get('create_mod_message', '创建模组...'))
            self.log_message(self.lang.get('mod_name_log', '模组名称: {name}').format(name=self.mod_name.text()))
            self.log_message(self.lang.get('mod_version_log', '模组版本: {version}').format(version=self.mod_version.text()))
            self.log_message(self.lang.get('mc_version_log', 'Minecraft版本: {version}').format(version=self.mc_version.currentText()))
            self.log_message(self.lang.get('forge_version_log', 'Forge版本: {version}').format(version=self.forge_version.text()))
            self.log_message(self.lang.get('mod_author_log', '模组作者: {author}').format(author=self.mod_author.text()))
            self.log_message(self.lang.get('mod_description_log', '模组描述: {description}').format(description=self.mod_description.toPlainText()))
            self.log_message(self.lang.get('save_path_log', '保存位置: {path}').format(path=self.save_path.text()))
            self.log_message(self.lang.get('full_package_log', '完整包名: {package}').format(package=full_package))
            self.log_message(self.lang.get('main_class_log', '主类名: {main_class}').format(main_class=main_class))

            # 依赖信息
            dependencies = []
            if self.dep_jei.isChecked():
                dependencies.append(self.lang.get('dep_jei_short', 'JEI'))
            if self.dep_cc.isChecked():
                dependencies.append(self.lang.get('dep_cc_short', 'Curios API'))
            if self.dep_tconstruct.isChecked():
                dependencies.append(self.lang.get('dep_tconstruct_short', 'Tinkers\' Construct'))
            
            # 检查自定义依赖
            custom_dep = self.dep_custom.text()
            default_dep_text = self.lang.get('dep_custom', '自定义依赖 (格式: modid:version)')
            if custom_dep and custom_dep != default_dep_text:
                dependencies.append(f'{self.lang.get("custom_dep_prefix", "自定义")}: {custom_dep}')
            self.log_message(self.lang.get('dependencies_log', '依赖: {deps}').format(deps=", ".join(dependencies) if dependencies else self.lang.get("none", "无")))

            # 资源文件信息 - 定义将要被移除的文件夹路径
            all_possible_paths = [
                f'forge-1.16.5-36.2.34-mdk/src/main/resources/assets/{modid}/lang',
                f'forge-1.16.5-36.2.34-mdk/src/main/resources/data/{modid}/advancements',
                f'forge-1.16.5-36.2.34-mdk/src/main/resources/data/{modid}/loot_tables',
                f'forge-1.16.5-36.2.34-mdk/src/main/resources/data/{modid}/recipes',
                f'forge-1.16.5-36.2.34-mdk/src/main/resources/data/{modid}/structures',
                f'forge-1.16.5-36.2.34-mdk/src/main/resources/data/{modid}/tags/blocks',
                f'forge-1.16.5-36.2.34-mdk/src/main/resources/data/{modid}/tags/entity_types',
                f'forge-1.16.5-36.2.34-mdk/src/main/resources/data/{modid}/tags/fluids',
                f'forge-1.16.5-36.2.34-mdk/src/main/resources/data/{modid}/tags/items',
                'forge-1.16.5-36.2.34-mdk/src/main/resources/data/minecraft/tags/blocks',
                'forge-1.16.5-36.2.34-mdk/src/main/resources/data/minecraft/tags/entity_types',
                'forge-1.16.5-36.2.34-mdk/src/main/resources/data/minecraft/tags/fluids',
                'forge-1.16.5-36.2.34-mdk/src/main/resources/data/minecraft/tags/functions',
                'forge-1.16.5-36.2.34-mdk/src/main/resources/data/minecraft/tags/items',
                'forge-1.16.5-36.2.34-mdk/src/main/resources/data/forge/tags/blocks',
                'forge-1.16.5-36.2.34-mdk/src/main/resources/data/forge/tags/entity_types',
                'forge-1.16.5-36.2.34-mdk/src/main/resources/data/forge/tags/fluids',
                'forge-1.16.5-36.2.34-mdk/src/main/resources/data/forge/tags/functions',
                'forge-1.16.5-36.2.34-mdk/src/main/resources/data/forge/tags/items'
            ]
            
            # 初始化将要被移除的路径列表
            willremoved = all_possible_paths[:]
            
            # 根据用户的选择决定哪些文件夹要被保留
            if self.resources_lang.isChecked():
                willremoved = [path for path in willremoved if not path.endswith('/lang')]
            
            if self.resources_recipes.isChecked():
                willremoved = [path for path in willremoved if not path.endswith('/recipes')]
            
            if self.resources_loot_tables.isChecked():
                willremoved = [path for path in willremoved if '/loot_tables' not in path and '/advancements' not in path]
            
            if self.resources_tags_mod.isChecked():
                willremoved = [path for path in willremoved if not ('/tags/' in path and 'minecraft' not in path and 'forge' not in path)]
            
            if self.resources_tags_common.isChecked():
                willremoved = [path for path in willremoved if not ('minecraft/tags/' in path)]
                
            # 去重
            willremoved = list(set(willremoved))
            
            self.log_message(f'要删除的资源文件夹: {", ".join(willremoved) if willremoved else "无"}')

            # 复制nullpack到目标目录并重命名为{modid}pack
            # 使用当前文件的绝对路径来确定res目录位置，更可靠
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            source_dir = os.path.join(os.path.dirname(current_file_dir), "res", 'nullpack')
            target_dir = os.path.join(self.save_path.text(), f'{modid}pack')
            
            # 检查源目录是否存在
            if not os.path.exists(source_dir):
                error_msg = f"源目录不存在: {source_dir}\n请确保res/nullpack目录存在。"
                self.log_message(error_msg)
                QMessageBox.critical(self, self.lang.get('error_title', '错误'), error_msg)
                return

            # 检查目标目录是否存在
            if os.path.exists(target_dir):
                reply = QMessageBox.question(self, self.lang.get('overwrite_warning_title', '警告'), 
                                            self.lang.get('overwrite_warning_message', '{modid}mod 已存在。你要覆盖它吗？').format(modid=modid),
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                
                if reply == QMessageBox.No:
                    self.log_message(self.lang.get('overwrite_cancel_message', '用户取消覆盖现有模组: {target_dir}').format(target_dir=target_dir))
                    QMessageBox.information(self, self.lang.get('information_title', '提示'), 
                                           self.lang.get('information_message', '构建已取消'))
                    return
                else:
                    self.log_message(self.lang.get('overwrite_confirm_message', '删除现有模组目录: {target_dir}').format(target_dir=target_dir))
                    try:
                        shutil.rmtree(target_dir)
                        # 确保目录被完全删除
                        import time
                        max_wait = 5
                        waited = 0
                        while os.path.exists(target_dir) and waited < max_wait:
                            time.sleep(0.5)
                            waited += 0.5
                        if os.path.exists(target_dir):
                            raise Exception(f"无法删除目录: {target_dir}")
                    except Exception as e:
                        error_msg = f"删除现有目录失败: {target_dir}\n错误: {str(e)}"
                        self.log_message(error_msg)
                        QMessageBox.critical(self, self.lang.get('error_title', '错误'), error_msg)
                        return
                    
            # 创建目标目录
            try:
                os.makedirs(target_dir, exist_ok=True)
            except Exception as e:
                error_msg = f"创建目标目录失败: {target_dir}\n错误: {str(e)}"
                self.log_message(error_msg)
                QMessageBox.critical(self, self.lang.get('error_title', '错误'), error_msg)
                return
            self.log_message(self.lang.get('target_dir_created_message', '已创建目标目录: {target_dir}').format(target_dir=target_dir))
            
            # 然后复制nullpack的内容到目标目录
            try:
                for item in os.listdir(source_dir):
                    source_item = os.path.join(source_dir, item)
                    target_item = os.path.join(target_dir, item)

                    if os.path.isdir(source_item):
                        shutil.copytree(source_item, target_item)
                    else:
                        shutil.copy2(source_item, target_item)
            except Exception as e:
                error_msg = f"复制模板文件失败\n源: {source_dir}\n目标: {target_dir}\n错误: {str(e)}"
                self.log_message(error_msg)
                QMessageBox.critical(self, self.lang.get('error_title', '错误'), error_msg)
                return

            self.log_message(self.lang.get('template_copied_message', '已复制模板内容到: {target_dir}').format(target_dir=target_dir))
            
            # 删除示例文件
            example_files = [
                os.path.join(target_dir, "example_commands.json"),
                os.path.join(target_dir, "(example).json")
            ]
            
            for file_path in example_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self.log_message(self.lang.get('example_file_deleted_message', '已删除示例文件: {file_path}').format(file_path=file_path))

            # 搭建开发环境，传递模组名称、作者和描述以修改mods.toml
            mod_name = self.mod_name.text()
            mod_author = self.mod_author.text()
            mod_description = self.mod_description.toPlainText()
            self.config_mod(target_dir, modid, self.base_package.text(), main_class, mod_name, mod_author, mod_description)

            # 删除不需要的路径
            for path_to_remove in willremoved:
                abs_path = os.path.join(target_dir, path_to_remove)
                if os.path.exists(abs_path):
                    if os.path.isfile(abs_path):
                        os.remove(abs_path)
                        self.log_message(f'已删除文件: {abs_path}')
                    elif os.path.isdir(abs_path):
                        shutil.rmtree(abs_path)
                        self.log_message(f'已删除目录: {abs_path}')

            self.log_message(self.lang.get('create_mod_success', '模组项目创建完成!'))
            QMessageBox.information(self, self.lang.get('create_mod_success_box', '成功'), 
                                   self.lang.get('create_mod_success_message', '模组项目已成功创建！'))
            
            # 根据CreateModExample.md的要求：当用户创建完成后，应当自动打开模组
            # 发出信号通知主窗口打开mod.json
            mod_json_path = os.path.join(target_dir, "mod.json")
            if os.path.exists(mod_json_path):
                self.mod_created.emit(mod_json_path)
                self.log_message(f"已发送模组创建完成信号，mod.json路径: {mod_json_path}")

        except ValueError as e:
            QMessageBox.critical(self, self.lang.get('error_title', '错误'), str(e))
        except Exception as e:
            self.log_message(self.lang.get('create_mod_error_message', '创建模组时发生错误: {e}').format(e=e))
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, self.lang.get('error_title', '错误'), 
                                self.lang.get('create_mod_error_message', '创建模组时发生错误: {e}').format(e=e))

    def download_java8(self):
        """
        从Oracle下载并安装Java 8
        注意：此功能可能因Oracle下载链接变化而失效
        """
        try:
            # 检测操作系统和架构
            system = sys.platform
            arch = platform.architecture()[0]
            
            # 根据操作系统和架构选择合适地下载链接
            if system == 'win32':
                if arch == '64bit':
                    download_url = 'https://javadl.oracle.com/webapps/download/AutoDL?BundleId=247340_4d5417147a92418ea8b615e228bb6935'
                    filename = 'jre-8u361-windows-x64.exe'
                else:
                    download_url = 'https://javadl.oracle.com/webapps/download/AutoDL?BundleId=247338_4d5417147a92418ea8b615e228bb6935'
                    filename = 'jre-8u361-windows-i586.exe'
            elif system == 'darwin':
                download_url = 'https://javadl.oracle.com/webapps/download/AutoDL?BundleId=247342_4d5417147a92418ea8b615e228bb6935'
                filename = 'jre-8u361-macosx-x64.dmg'
            elif system == 'linux':
                if arch == '64bit':
                    download_url = 'https://javadl.oracle.com/webapps/download/AutoDL?BundleId=247344_4d5417147a92418ea8b615e228bb6935'
                    filename = 'jre-8u361-linux-x64.tar.gz'
                else:
                    download_url = 'https://javadl.oracle.com/webapps/download/AutoDL?BundleId=247343_4d5417147a92418ea8b615e228bb6935'
                    filename = 'jre-8u361-linux-i586.tar.gz'
            else:
                return False
            
            # 创建临时目录保存下载的文件
            temp_dir = tempfile.mkdtemp()
            download_path = os.path.join(temp_dir, filename)
            
            # 设置请求头，模拟浏览器访问并接受许可协议
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Cookie': 'oraclelicense=accept-securebackup-cookie'
            }
            
            # 创建请求对象
            req = urllib.request.Request(download_url, headers=headers)
            
            # 下载Java 8安装包
            with urllib.request.urlopen(req) as response:
                with open(download_path, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
            
            # 安装Java 8
            if system == 'win32':
                subprocess.run([download_path, '/s'], check=True)
            elif system == 'darwin':
                mount_point = os.path.join(temp_dir, 'java_mount')
                os.makedirs(mount_point, exist_ok=True)
                subprocess.run(['hdiutil', 'attach', download_path, '-mountpoint', mount_point], check=True)
                
                for root, dirs, files in os.walk(mount_point):
                    for file in files:
                        if file.endswith('.pkg'):
                            pkg_path = os.path.join(root, file)
                            subprocess.run(['sudo', 'installer', '-pkg', pkg_path, '-target', '/'], check=True)
                            break
                
                subprocess.run(['hdiutil', 'detach', mount_point], check=True)
            elif system == 'linux':
                install_dir = '/usr/lib/jvm'
                os.makedirs(install_dir, exist_ok=True)
                subprocess.run(['tar', '-xzf', download_path, '-C', install_dir], check=True)
                
                java_home = os.path.join(install_dir, 'jre1.8.0_361')
                with open('/etc/profile.d/java.sh', 'w') as f:
                    f.write(f'export JAVA_HOME={java_home}\n')
                    f.write(f'export PATH=$PATH:$JAVA_HOME/bin\n')
                subprocess.run(['chmod', '+x', '/etc/profile.d/java.sh'], check=True)
            
            # 清理临时文件
            shutil.rmtree(temp_dir)
            
            return True
            
        except Exception as e:
            self.log_message(f"下载或安装Java 8时出错: {e}")
            return False
    
    def has_java8(self):
        """
        检查用户电脑上是否有Java 8，不存在返回None，否则返回Java 8的bin目录路径
        """
        # 检查是否有管理员权限
        if not ensure_admin_privileges():
            return None
        
        # 首先检查当前JAVA_HOME环境变量是否有效
        if 'JAVA_HOME' in os.environ:
            java_home = os.environ['JAVA_HOME']
            java_bin = os.path.join(java_home, 'bin')
            java_exe = os.path.join(java_bin, 'java.exe' if sys.platform == 'win32' else 'java')
            
            if os.path.exists(java_exe):
                try:
                    # 检查Java版本
                    result = subprocess.run([java_exe, '-version'], capture_output=True, text=True)
                    if '1.8' in result.stderr or '8' in result.stderr:
                        self.log_message(f"使用环境变量中的Java 8: {java_exe}")
                        return java_bin
                except Exception:
                    pass
            else:
                self.log_message(f"环境变量JAVA_HOME指向的路径不存在: {java_home}")
        
        # 如果环境变量中的Java无效，搜索系统中的Java
        try:
            # 获取path环境变量（系统环境变量+用户环境变量）
            path_env = os.environ['PATH'].split(os.pathsep)
            
            # 过滤path_env，保留包含bin目录且有java可执行文件的路径
            filtered_paths = []
            for path in path_env:
                if not path or not os.path.isdir(path):
                    continue
                    
                has_executable = False
                has_java_executable = False
                
                try:
                    for file in os.listdir(path):
                        file_path = os.path.join(path, file)
                        if os.path.isfile(file_path):
                            if sys.platform == 'win32':
                                if file.lower().endswith('.exe'):
                                    has_executable = True
                                    if file.lower() == 'java.exe':
                                        has_java_executable = True
                            else:
                                if os.access(file_path, os.X_OK):
                                    has_executable = True
                                    if file.lower() == 'java':
                                        has_java_executable = True
                except PermissionError:
                    continue
                
                if has_executable and has_java_executable:
                    filtered_paths.append(path)
                    
            # 现在检查Java版本
            for java_path in filtered_paths:
                try:
                    # 构建java可执行文件的完整路径
                    java_exe = os.path.join(java_path, 'java.exe' if sys.platform == 'win32' else 'java')
                    
                    # 执行java -version命令
                    result = subprocess.run([java_exe, '-version'], capture_output=True, text=True)
                    
                    # 检查输出中是否包含Java 8的信息
                    if '1.8' in result.stderr or '8' in result.stderr:
                        # 验证Java主目录存在
                        java_home = os.path.dirname(java_path)
                        if os.path.exists(java_home):
                            self.log_message(f"找到Java 8: {java_exe}")
                            return java_path
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            self.log_message(f"查找Java 8时出错: {e}")
            return None

    def set_environment_variables(self):
        """
        设置或修改JAVA_HOME环境变量，并更新PATH环境变量
        """
        try:
            # 验证self.java_path是否存在
            if not os.path.exists(self.java_path):
                self.log_message(f"Java路径不存在: {self.java_path}")
                
                # 尝试重新检测Java 8
                new_java_path = self.has_java8()
                if new_java_path:
                    self.java_path = new_java_path
                    self.log_message(f"已更新Java路径: {self.java_path}")
                else:
                    self.log_message("无法找到有效的Java 8路径")
                    return False
            
            # 计算JAVA_HOME路径（bin目录的父目录）
            if self.java_path.endswith('\\bin') or self.java_path.endswith('/bin'):
                java_home = os.path.dirname(self.java_path)
            else:
                java_home = self.java_path
            
            # 验证JAVA_HOME目录存在
            if not os.path.exists(java_home):
                self.log_message(f"JAVA_HOME目录不存在: {java_home}")
                return False
            
            # 验证java.exe/java可执行文件存在
            java_exe_name = 'java.exe' if sys.platform == 'win32' else 'java'
            java_exe_path = os.path.join(self.java_path, java_exe_name)
            if not os.path.exists(java_exe_path):
                self.log_message(f"Java可执行文件不存在: {java_exe_path}")
                return False

            self.log_message(f"使用Java 8路径: {java_exe_path}")
            self.log_message(f"设置JAVA_HOME: {java_home}")

            if sys.platform == 'win32':
                import winreg
                
                try:
                    # 尝试设置系统环境变量
                    reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                           r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
                                           0, winreg.KEY_SET_VALUE)

                    winreg.SetValueEx(reg_key, 'JAVA_HOME', 0, winreg.REG_SZ, java_home)
                    winreg.CloseKey(reg_key)
                    self.log_message(f"已设置系统环境变量JAVA_HOME: {java_home}")

                except PermissionError:
                    self.log_message("警告: 没有权限设置系统环境变量")
                    
                    # 尝试设置用户环境变量
                    try:
                        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                               r'Environment',
                                               0, winreg.KEY_SET_VALUE)

                        winreg.SetValueEx(reg_key, 'JAVA_HOME', 0, winreg.REG_SZ, java_home)
                        winreg.CloseKey(reg_key)
                        self.log_message(f"已设置用户环境变量JAVA_HOME: {java_home}")
                    except Exception as e:
                        self.log_message(f"设置用户环境变量失败: {e}")

                # 通知系统环境变量已更新
                try:
                    ctypes.windll.user32.SendMessageW(0xFFFF, 0x001A, 0, 'Environment')
                except Exception:
                    pass

            else:
                try:
                    # Unix/Linux/macOS系统：修改/etc/profile.d/java.sh文件
                    with open('/etc/profile.d/java.sh', 'w') as f:
                        f.write(f'export JAVA_HOME={java_home}\n')
                        f.write(f'export PATH=$PATH:$JAVA_HOME/bin\n')

                    subprocess.run(['chmod', '+x', '/etc/profile.d/java.sh'], check=True)
                    self.log_message(f"已设置系统环境变量JAVA_HOME: {java_home}")

                except PermissionError:
                    # 如果没有权限，设置当前用户的环境变量
                    user_profile = os.path.expanduser('~/.bashrc')
                    with open(user_profile, 'a') as f:
                        f.write(f'\nexport JAVA_HOME={java_home}\n')
                        f.write(f'export PATH=$PATH:$JAVA_HOME/bin\n')

                    self.log_message(f"已在用户配置文件中设置JAVA_HOME: {java_home}")

            # 立即应用环境变量到当前进程
            os.environ['JAVA_HOME'] = java_home
            if sys.platform == 'win32':
                os.environ['PATH'] = f"{os.environ['PATH']};{self.java_path}"
            else:
                os.environ['PATH'] = f"{os.environ['PATH']}:{self.java_path}"
            
            self.log_message(f"已在当前进程中设置JAVA_HOME: {java_home}")
            self.log_message(f"已在当前进程中更新PATH: {os.environ['PATH']}")

            return True

        except Exception as e:
            self.log_message(f"设置环境变量时出错: {e}")
            import traceback
            traceback.print_exc()
            
            # 即使出错，也要尝试确保当前进程可以使用Java
            try:
                # 重新检测Java路径
                new_java_path = self.has_java8()
                if new_java_path:
                    java_home = os.path.dirname(new_java_path) if (new_java_path.endswith('\\bin') or new_java_path.endswith('/bin')) else new_java_path
                    os.environ['JAVA_HOME'] = java_home
                    if sys.platform == 'win32':
                        os.environ['PATH'] = f"{os.environ['PATH']};{new_java_path}"
                    else:
                        os.environ['PATH'] = f"{os.environ['PATH']}:{new_java_path}"
                    self.log_message(f"已在当前进程中设置临时JAVA_HOME: {java_home}")
                    return True
            except Exception as temp_e:
                self.log_message(f"设置临时环境变量时出错: {temp_e}")
                
            return False

    def fix_build_pack(self, directory):
        """
        修复nullpack，使其使用JAVA_HOME中的JDK而不是自动下载
        """
        try:
            # 修改gradle.properties文件，添加org.gradle.java.home属性指向JAVA_HOME
            gradle_properties_path = os.path.join(directory, 'forge-1.16.5-36.2.34-mdk', 'gradle.properties')

            if os.path.exists(gradle_properties_path):
                with open(gradle_properties_path, 'r') as f:
                    content = f.read()

                # 添加或修改org.gradle.java.home属性
                java_home = os.path.dirname(self.java_path) if (self.java_path.endswith('\\bin') or self.java_path.endswith('/bin')) else self.java_path

                if 'org.gradle.java.home' in content:
                    content = re.sub(r'org\\.gradle\\.java\\.home=.*', f'org.gradle.java.home={java_home.replace("\\", "/")}', content)
                else:
                    content += f'\norg.gradle.java.home={java_home.replace("\\", "/")}\n'

                with open(gradle_properties_path, 'w') as f:
                    f.write(content)

                self.log_message(self.lang.get('fixing_build_pack_message', '已修改gradle.properties文件，使用JAVA_HOME: {java_home}').format(java_home=java_home))

            # 修改gradle-wrapper.properties文件
            gradle_wrapper_path = os.path.join(directory, 'forge-1.16.5-36.2.34-mdk', 'gradle', 'wrapper', 'gradle-wrapper.properties')

            if os.path.exists(gradle_wrapper_path):
                with open(gradle_wrapper_path, 'r') as f:
                    content = f.read()

                # 确保使用腾讯云镜像源
                if 'https://services.gradle.org/distributions/' in content:
                    content = content.replace('https://services.gradle.org/distributions/', 'https://mirrors.cloud.tencent.com/gradle/')
                    with open(gradle_wrapper_path, 'w') as f:
                        f.write(content)
                    self.log_message(self.lang.get('gradle_wrapper_updated_message', '已修改gradle-wrapper.properties文件，使用腾讯云镜像源'))

            return True

        except Exception as e:
            self.log_message(self.lang.get('fix_build_pack_error_message', '修复nullpack时出错: {e}').format(e=e))
            return False
    
    def execute_build(self, directory):
        """
        执行Forge模组项目的构建命令
        """
        try:
            # 进入forge目录
            forge_dir = os.path.join(directory, 'forge-1.16.5-36.2.34-mdk')
            
            # 验证forge目录存在
            if not os.path.exists(forge_dir):
                self.log_message(f"Forge目录不存在: {forge_dir}")
                return False
            
            self.log_message(f"进入目录: {forge_dir}")
            
            # 执行构建命令
            if sys.platform == 'win32':
                gradle_script_name = 'gradlew.bat'
            else:
                gradle_script_name = 'gradlew'
            
            # 构建Gradle脚本的绝对路径
            gradle_script_path = os.path.abspath(os.path.join(forge_dir, gradle_script_name))
            
            # 验证Gradle脚本存在
            if not os.path.exists(gradle_script_path):
                self.log_message(f"Gradle脚本不存在: {gradle_script_path}")
                
                # 列出forge目录中的所有文件，帮助调试
                self.log_message(f"Forge目录中的文件: {os.listdir(forge_dir)}")
                return False
            
            self.log_message(f"找到Gradle脚本: {gradle_script_path}")
            
            # 为非Windows系统确保脚本可执行
            if sys.platform != 'win32':
                subprocess.run(['chmod', '+x', gradle_script_path], check=True)
                self.log_message(f"已设置脚本可执行权限: {gradle_script_path}")
            
            # 构建命令
            # 根据CreateModExample.md第101行：应执行genIntellijRuns而非build
            build_command = [gradle_script_path, 'genIntellijRuns', '--no-daemon']
            self.log_message(f"执行构建命令: {' '.join(build_command)}")
            
            # 执行构建并捕获输出，确保在Forge目录中执行
            process = subprocess.Popen(
                build_command, 
                cwd=forge_dir,  # 确保在正确的目录中执行
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True
            )
            
            # 实时输出构建日志
            for line in process.stdout:
                if line.strip():
                    self.log_message(line.strip())
            
            # 等待构建完成
            process.wait()
            
            if process.returncode == 0:
                self.log_message("构建成功完成！")
                
                # 显示构建产物位置
                build_output_dir = os.path.join(forge_dir, 'build', 'libs')
                if os.path.exists(build_output_dir):
                    self.log_message(f"构建产物位于: {build_output_dir}")
                    
                    # 列出构建产物
                    for root, dirs, files in os.walk(build_output_dir):
                        for file in files:
                            if file.endswith('.jar'):
                                self.log_message(f"构建产物: {os.path.join(root, file)}")
                return True
            else:
                self.log_message(f"构建失败，退出码: {process.returncode}")
                return False
                
        except subprocess.CalledProcessError as e:
            self.log_message(f"执行构建命令时出错: {e}")
            return False
        except Exception as e:
            self.log_message(f"构建过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False

    def config_mod(self, directory, modid, basename, main_class, mod_name="", mod_author="", mod_description=""):
        """
        配置模组项目并执行构建
        根据CreateModExample.md的要求实现
        """
        try:
            # 设置环境变量
            self.set_environment_variables()
            
            # 修复nullpack
            self.fix_build_pack(directory)
            
            # 替换文件和目录名，修改文件内容（包括mods.toml和Java文件）
            self.replace_file_dir_name(directory, modid, basename, main_class, mod_name, mod_author, mod_description)
            
            # 执行构建命令
            self.execute_build(directory)
            
            return True
        except Exception as e:
            self.log_message(f"配置模组时出错: {e}")
            return False
    
    def config_mod_async(self, directory, modid, basename, main_class):
        """
        异步配置模组项目（用于线程中调用）
        """
        self.config_mod(directory, modid, basename, main_class)
    
    def replace_file_dir_name(self, directory, modid, basename, main_class, mod_name="", mod_author="", mod_description=""):
        """
        替换文件和目录名，修改mods.toml和Java文件内容
        根据CreateModExample.md的要求实现
        :param directory: 项目根目录（{modid}pack）
        :param modid: 模组ID
        :param basename: 基础包名
        :param main_class: 主类名
        :param mod_name: 模组显示名称
        :param mod_author: 模组作者
        :param mod_description: 模组描述
        """
        try:
            forge_dir = os.path.join(directory, "forge-1.16.5-36.2.34-mdk")

            # ========== 1. rename操作 ==========
            # 1.1 重命名resources/assets/yangmod为resources/assets/{modid}mod
            assets_old = os.path.join(forge_dir, "src", "main", "resources", "assets", "yangmod")
            assets_new = os.path.join(forge_dir, "src", "main", "resources", "assets", f"{modid}mod")
            if os.path.exists(assets_old):
                os.rename(assets_old, assets_new)
                self.log_message(f"已重命名资源目录: {assets_old} -> {assets_new}")

            # 1.2 重命名resources/data/yangmod为resources/data/{modid}mod
            data_old = os.path.join(forge_dir, "src", "main", "resources", "data", "yangmod")
            data_new = os.path.join(forge_dir, "src", "main", "resources", "data", f"{modid}mod")
            if os.path.exists(data_old):
                os.rename(data_old, data_new)
                self.log_message(f"已重命名数据目录: {data_old} -> {data_new}")

            # 1.3 检查并删除可能存在的com/yangmod目录
            yangmod_dir = os.path.join(forge_dir, "src", "main", "java", "com", "yangmod")
            if os.path.exists(yangmod_dir):
                shutil.rmtree(yangmod_dir)
                self.log_message(f"已删除遗留目录: {yangmod_dir}")

            # 1.4 重命名java/com/yang/mod为java/com/{basename}/{modid}mod
            java_old = os.path.join(forge_dir, "src", "main", "java", "com", "yang", "mod")
            java_new = os.path.join(forge_dir, "src", "main", "java", "com", basename, f"{modid}mod")

            # 创建新的父目录
            java_new_parent = os.path.join(forge_dir, "src", "main", "java", "com", basename)
            os.makedirs(java_new_parent, exist_ok=True)

            if os.path.exists(java_old):
                shutil.move(java_old, java_new)
                self.log_message(f"已重命名Java目录: {java_old} -> {java_new}")

            # 1.5 重命名YangMod.java为{MainClassName}.java
            old_java_file = os.path.join(java_new, "YangMod.java")
            new_java_file = os.path.join(java_new, f"{main_class}.java")
            if os.path.exists(old_java_file):
                os.rename(old_java_file, new_java_file)
                self.log_message(f"已重命名主类文件: {old_java_file} -> {new_java_file}")

            # ========== 2. replace操作 ==========
            # 2.1 修改mods.toml文件
            mods_toml_path = os.path.join(forge_dir, "src", "main", "resources", "META-INF", "mods.toml")
            if os.path.exists(mods_toml_path):
                with open(mods_toml_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 替换modId: modId="yangmod" -> modId="{modid}mod"
                # 注意：根据CreateModExample.md，应该是{modid}mod，不是{modid}
                modid_replacement = f"{modid}mod"
                content = content.replace('modId="yangmod"', f'modId="{modid_replacement}"')
                content = content.replace("modId='yangmod'", f'modId="{modid_replacement}"')
                
                # 替换displayName: displayName="朝阳Mod" -> displayName="{modName}"
                if mod_name:
                    content = content.replace('displayName="朝阳Mod"', f'displayName="{mod_name}"')
                    content = content.replace("displayName='朝阳Mod'", f'displayName="{mod_name}"')
                
                # 替换authors: authors="朝阳" -> authors="{modAuthor}"
                if mod_author:
                    content = content.replace('authors="朝阳"', f'authors="{mod_author}"')
                    content = content.replace("authors='朝阳'", f'authors="{mod_author}"')
                
                # 替换description
                if mod_description:
                    # 查找并替换description字段
                    # TOML格式要求字符串必须用引号包裹
                    import re
                    
                    # 处理用户输入：转义双引号，处理换行符
                    escaped_description = mod_description.replace('"', '\\"').replace('\n', '\\n')
                    
                    # 替换三引号包裹的description（支持多行）
                    # 使用三引号可以包含换行和特殊字符
                    description_pattern = r'description\s*=\s*"""[\s\S]*?"""'
                    if re.search(description_pattern, content):
                        # 如果原文件使用三引号，继续使用三引号
                        content = re.sub(
                            description_pattern,
                            f'description="""\n{mod_description}\n"""',
                            content
                        )
                    else:
                        # 替换单引号或双引号包裹的description
                        # 使用转义后的字符串
                        content = re.sub(
                            r'description\s*=\s*["\'][^"\']*["\']',
                            f'description="{escaped_description}"',
                            content
                        )
                
                # 替换所有examplemod -> {modid}mod
                content = content.replace("examplemod", modid_replacement)
                content = content.replace("exampleMod", modid_replacement)
                content = content.replace("ExampleMod", modid_replacement)

                # 写入修改后的内容
                with open(mods_toml_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                self.log_message(f"已修改mods.toml文件: {mods_toml_path}")

            # 2.2 修改主类Java文件内容
            if os.path.exists(new_java_file):
                with open(new_java_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 替换包名
                old_package = "com.yang.mod"
                new_package = f"com.{basename}.{modid}mod"
                content = content.replace(old_package, new_package)

                # 替换@Mod注解: @Mod("yangmod") -> @Mod("{modid}mod")
                modid_replacement = f"{modid}mod"
                content = content.replace('@Mod("yangmod")', f'@Mod("{modid_replacement}")')
                content = content.replace("@Mod('yangmod')", f'@Mod("{modid_replacement}")')

                # 替换MOD_ID常量
                old_mod_id = 'public static final String MOD_ID = "yangmod"'
                new_mod_id = f'public static final String MOD_ID = "{modid_replacement}"'
                content = content.replace(old_mod_id, new_mod_id)

                # 替换所有YangMod -> {MainClassName}
                content = content.replace("YangMod", main_class)

                # 写入修改后的内容
                with open(new_java_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                self.log_message(f"已修改主类文件内容: {new_java_file}")

            # 2.3 修改build.gradle文件
            build_gradle_path = os.path.join(forge_dir, "build.gradle")
            if os.path.exists(build_gradle_path):
                with open(build_gradle_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 根据CreateModExample.md第71-77行要求进行替换
                # 注意：替换顺序很重要，先替换较长的字符串
                
                # 替换 examplemod -> {modid}mod
                modid_replacement = f"{modid}mod"
                content = content.replace("examplemod", modid_replacement)
                content = content.replace("exampleMod", modid_replacement)
                content = content.replace("ExampleMod", modid_replacement)
                
                # 替换 modid -> {modid}mod （注意：不是{modid}，而是{modid}mod）
                content = content.replace("modid", modid_replacement)
                
                # 替换 yourname -> {basePackageName}
                content = content.replace("yourname", basename)

                # 写入修改后的内容
                with open(build_gradle_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                self.log_message(f"已修改build.gradle文件: {build_gradle_path}")

            return True
        except Exception as e:
            self.log_message(f"替换文件和目录名时出错: {e}")
            import traceback
            traceback.print_exc()
            return False