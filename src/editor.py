#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON编辑器模块
用于读取和显示mod.json文件的内容，以树形结构展示
"""

import json
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt


class Editor(QWidget):
    """
    JSON编辑器类
    使用QTreeView展示JSON数据的树形结构
    """
    
    def __init__(self, parent=None):
        """
        初始化编辑器
        
        :param parent: 父窗口
        """
        super().__init__(parent)
        self.parent = parent
        self.json_data = None  # 存储加载的JSON数据
        self.model = None       # 树形视图模型
        self.tree_view = None   # 树形视图组件
        self.file_path = None   # 当前加载的文件路径
        
        # 加载语言文件
        self.load_language('zh_CN')
        
        self.init_ui()
    
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
            
            print(f"已加载语言文件: {lang_file_path}")
        except Exception as e:
            # 如果加载失败，使用默认语言
            self.lang = {
                # 基本信息
                "json_key_modInfo": "模组信息",
                "json_key_modid": "模组ID",
                "json_key_name": "名称",
                "json_key_version": "版本",
                "json_key_author": "作者",
                "json_key_description": "描述",
                "json_key_mcversion": "Minecraft版本",
                "json_key_forgeversion": "Forge版本",
                
                # 方块相关
                "json_key_blocks": "方块列表",
                "json_key_material": "材质",
                "json_key_hardness": "硬度",
                "json_key_resistance": "爆炸抗性",
                "json_key_harvestLevel": "挖掘等级",
                "json_key_harvestTool": "挖掘工具",
                "json_key_lightValue": "发光等级",
                "json_key_lightOpacity": "透明度",
                "json_key_creativeTab": "创造模式标签",
                "json_key_textureName": "纹理名称",
                "json_key_model": "模型",
                "json_key_defaultState": "默认状态",
                "json_key_variants": "变体",
                "json_key_tileEntity": "方块实体",
                "json_key_type": "类型",
                "json_key_class": "类",
                
                # 物品组相关
                "json_key_itemGroups": "物品组列表",
                "json_key_ItemGroupID": "物品组ID"
            }
            print(f"加载语言文件失败，使用默认语言: {e}")
    
    def init_ui(self):
        """
        初始化UI组件
        """
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 创建树视图
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(False)
        self.tree_view.setAlternatingRowColors(True)
        
        # 创建模型
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Key', 'Value'])
        self.tree_view.setModel(self.model)
        
        # 添加树视图到布局
        layout.addWidget(self.tree_view)
        
        # 设置布局
        self.setLayout(layout)
    
    def read(self, file_path):
        """
        读取JSON文件并以树状结构显示
        
        :param file_path: JSON文件路径
        :return: 是否读取成功
        """
        try:
            # 存储文件路径
            self.file_path = file_path
            
            # 打开并读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                self.json_data = json.load(f)
            
            # 清空模型
            self.model.clear()
            self.model.setHorizontalHeaderLabels(['Key', 'Value'])
            
            # 构建树状结构
            self._build_tree('', self.json_data, self.model.invisibleRootItem())
            
            # 展开所有节点
            self.tree_view.expandAll()
            
            return True
        except Exception as e:
            print(f"读取JSON文件失败: {e}")
            return False
    
    def _build_tree(self, key, value, parent_item):
        """
        递归构建树状结构
        
        :param key: 当前键名
        :param value: 当前值
        :param parent_item: 父节点
        """
        if isinstance(value, dict):
            # 创建字典节点
            if key:
                dict_item = QStandardItem(self._get_translated_key(key))
                dict_item.setEditable(False)
                parent_item.appendRow([dict_item, QStandardItem("{...}")])
                parent = dict_item
            else:
                parent = parent_item
            
            # 递归处理字典中的每个键值对
            for k, v in value.items():
                self._build_tree(k, v, parent)
        elif isinstance(value, list):
            # 创建列表节点
            if key:
                list_item = QStandardItem(self._get_translated_key(key))
                list_item.setEditable(False)
                parent_item.appendRow([list_item, QStandardItem(f"[{len(value)} items]")])
                parent = list_item
            else:
                parent = parent_item
            
            # 递归处理列表中的每个元素
            for i, item in enumerate(value):
                self._build_tree(f"[{i}]", item, parent)
        else:
            # 创建值节点
            if not key:
                # 处理根节点为非字典/列表的情况
                key_item = QStandardItem("root")
                value_item = QStandardItem(str(value))
            else:
                key_item = QStandardItem(self._get_translated_key(key))
                value_item = QStandardItem(str(value))
            
            key_item.setEditable(False)
            value_item.setEditable(False)
            
            parent_item.appendRow([key_item, value_item])
    
    def _get_translated_key(self, key):
        """
        将JSON键转换为中文显示
        
        :param key: 原始键名
        :return: 翻译后的键名
        """
        # 移除列表索引标记（如 "[0]"）
        if key.startswith("[") and key.endswith("]"):
            return key
            
        # 使用语言系统获取翻译
        lang_key = f"json_key_{key}"
        return self.lang.get(lang_key, key)
    
    def get_json_data(self):
        """
        获取当前加载的JSON数据
        
        :return: JSON数据字典
        """
        return self.json_data
    
    def clear(self):
        """
        清空树状视图
        """
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Key', 'Value'])
        self.json_data = None
        self.file_path = None