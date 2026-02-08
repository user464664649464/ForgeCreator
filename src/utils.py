#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
包含通用的辅助功能，如权限管理、路径处理等
"""

import sys
import os
import subprocess
import ctypes
import re


def is_admin() -> bool:
    """
    检查当前程序是否以管理员/root权限运行
    
    :return: bool - 如果是管理员/root权限则返回True，否则返回False
    """
    try:
        if sys.platform == 'win32':
            # Windows系统：使用ctypes检查是否为管理员
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            # Unix/Linux系统：检查euid是否为0（root用户）
            return os.geteuid() == 0
    except Exception:
        return False


def run_as_admin() -> bool:
    """
    尝试以管理员权限重新启动程序
    
    :return: bool - 如果提权请求成功发送则返回True，否则返回False
    """
    try:
        if sys.platform == 'win32':
            # Windows系统：使用ctypes重新启动程序并请求管理员权限
            script_path = os.path.abspath(sys.argv[0])
            params = f'"{script_path}"' + ' ' + ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
            
            # 使用ShellExecuteW以管理员权限运行
            result = ctypes.windll.shell32.ShellExecuteW(
                None,        # hwnd
                "runas",     # lpOperation
                sys.executable,  # lpFile (Python解释器)
                params,      # lpParameters (脚本路径和参数)
                None,        # lpDirectory
                1            # nShowCmd (SW_SHOWNORMAL)
            )
            
            if result <= 32:
                return False
            else:
                return True
        else:
            # Unix/Linux系统：使用sudo重新启动程序
            subprocess.call(['sudo', sys.executable] + sys.argv)
            return True
    except Exception:
        return False


def ensure_admin_privileges() -> bool:
    """
    确保程序以管理员权限运行
    如果不是管理员权限，尝试提权并重新启动程序
    
    :return: bool - 如果当前已有管理员权限则返回True，否则提权后返回True（如果提权成功）或False（如果提权失败）
    """
    if not is_admin():
        # 尝试以管理员权限重新启动程序
        if run_as_admin():
            sys.exit(0)
        else:
            return False
    else:
        return True


def safe_path_join(*paths) -> str:
    """
    安全地连接路径，避免路径遍历攻击
    
    :param paths: 路径片段列表
    :return: 连接后的绝对路径
    """
    # 获取第一个绝对路径
    abs_path = os.path.abspath(paths[0])
    
    # 依次连接剩余路径
    for path in paths[1:]:
        # 确保路径不包含路径遍历字符
        safe_path = path.replace('..', '').replace('/', '').replace('\\', '')
        abs_path = os.path.join(abs_path, safe_path)
    
    return abs_path


def validate_modid(modid: str) -> str:
    """
    验证并格式化模组ID
    
    :param modid: 原始模组ID
    :return: 格式化后的模组ID
    :raises ValueError: 如果模组ID无效
    """
    # 验证modid只包含小写字母、数字和下划线
    if not re.match(r'^[a-z0-9_]+$', modid):
        raise ValueError("模组ID只能包含小写字母、数字和下划线")
    
    return modid.lower().replace(" ", "_").replace("-", "_")


def create_main_class_name(modid: str) -> str:
    """
    根据模组ID创建主类名
    
    :param modid: 模组ID
    :return: 主类名
    """
    return modid.capitalize() + "Mod"


def create_package_name(base_package: str, modid: str) -> str:
    """
    创建完整的包名
    
    :param base_package: 基础包名
    :param modid: 模组ID
    :return: 完整的包名
    """
    return f"com.{base_package}.{modid}mod"