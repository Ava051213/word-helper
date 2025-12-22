#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常处理模块
定义统一的异常类
"""


class WordHelperException(Exception):
    """基础异常类"""
    pass


class DatabaseError(WordHelperException):
    """数据库操作错误"""
    pass


class APIError(WordHelperException):
    """API请求错误"""
    pass


class ValidationError(WordHelperException):
    """数据验证错误"""
    pass


class NotFoundError(WordHelperException):
    """资源未找到错误"""
    pass

