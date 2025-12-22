#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译API模块
通过Deep Translator实现英文到中文的翻译
"""

import logging
from typing import Optional
from deep_translator import GoogleTranslator

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranslationAPI:
    """翻译API客户端"""
    
    def __init__(self):
        """初始化翻译API客户端"""
        try:
            # 使用Deep Translator的GoogleTranslator
            self.translator = GoogleTranslator(source='en', target='zh-CN')
            logger.info("翻译API客户端初始化成功")
        except Exception as e:
            logger.error(f"翻译API客户端初始化失败: {e}")
            self.translator = None
    
    def translate_to_chinese(self, text: str) -> Optional[str]:
        """将英文翻译为中文
        
        Args:
            text: 要翻译的英文文本
            
        Returns:
            翻译后的中文文本，如果翻译失败则返回None
        """
        if not self.translator:
            logger.error("翻译API客户端未初始化")
            return None
            
        if not text:
            return None
            
        try:
            # 记录翻译请求
            logger.info(f"正在翻译文本: {text[:50]}...")
            
            # 执行翻译
            result = self.translator.translate(text)
            
            if result:
                logger.info("翻译成功")
                return result
            else:
                logger.warning("翻译结果为空")
                return None
                
        except Exception as e:
            logger.error(f"翻译过程中发生错误: {e}")
            return None


def demo():
    """演示函数"""
    api = TranslationAPI()
    
    # 测试翻译
    texts = [
        "Hello, how are you?",
        "The quick brown fox jumps over the lazy dog.",
        "Artificial Intelligence is transforming the world."
    ]
    
    for text in texts:
        print(f"原文: {text}")
        translated = api.translate_to_chinese(text)
        if translated:
            print(f"译文: {translated}")
        else:
            print("翻译失败")
        print("-" * 50)


if __name__ == "__main__":
    demo()