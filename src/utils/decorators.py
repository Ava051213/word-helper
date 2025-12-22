#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
装饰器模块
提供通用的装饰器函数
"""

import logging
from functools import wraps
from tkinter import messagebox

from ..core.exceptions import DatabaseError, APIError, ValidationError

logger = logging.getLogger(__name__)


def handle_exceptions(func):
    """统一异常处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DatabaseError as e:
            logger.error(f"数据库错误: {e}")
            if hasattr(args[0], 'root') or (args and hasattr(args[0], 'parent_gui')):
                # GUI环境，显示错误对话框
                try:
                    root = args[0].root if hasattr(args[0], 'root') else args[0].parent_gui.root
                    root.after(0, lambda: messagebox.showerror("数据库错误", str(e)))
                except:
                    pass
            return None
        except APIError as e:
            logger.error(f"API错误: {e}")
            if hasattr(args[0], 'root') or (args and hasattr(args[0], 'parent_gui')):
                try:
                    root = args[0].root if hasattr(args[0], 'root') else args[0].parent_gui.root
                    root.after(0, lambda: messagebox.showwarning("网络错误", "无法连接到词典服务"))
                except:
                    pass
            return None
        except ValidationError as e:
            logger.warning(f"验证错误: {e}")
            if hasattr(args[0], 'root') or (args and hasattr(args[0], 'parent_gui')):
                try:
                    root = args[0].root if hasattr(args[0], 'root') else args[0].parent_gui.root
                    root.after(0, lambda: messagebox.showwarning("输入错误", str(e)))
                except:
                    pass
            return None
        except Exception as e:
            logger.exception(f"未预期的错误: {e}")
            if hasattr(args[0], 'root') or (args and hasattr(args[0], 'parent_gui')):
                try:
                    root = args[0].root if hasattr(args[0], 'root') else args[0].parent_gui.root
                    root.after(0, lambda: messagebox.showerror("错误", f"发生未知错误: {e}"))
                except:
                    pass
            return None
    return wrapper

