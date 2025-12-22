#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词典API模块
通过Free Dictionary API获取单词的释义、例句等信息，并提供中文翻译功能
"""

import requests
import json
import logging
import time
import os
from typing import Dict, Optional, List

# 导入翻译API
try:
    from .translation_api import TranslationAPI
    TRANSLATION_API_AVAILABLE = True
except ImportError:
    TRANSLATION_API_AVAILABLE = False
    print("警告: 无法导入翻译API模块")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DictionaryAPI:
    """词典API客户端"""
    
    def __init__(self):
        """初始化词典API客户端"""
        self.base_url = "https://api.dictionaryapi.dev/api/v2/entries/en"
        self.max_retries = 3
        self.backoff_factor = 0.5
        
        # 初始化翻译API
        if TRANSLATION_API_AVAILABLE:
            self.translation_api = TranslationAPI()
        else:
            self.translation_api = None
    
    def get_word_info(self, word: str) -> Optional[Dict]:
        """获取单词信息
        
        Args:
            word: 要查询的单词
            
        Returns:
            包含单词信息的字典，如果查询失败则返回None
        """
        url = f"{self.base_url}/{word.lower()}"
        attempt = 0
        last_error = None
        
        while attempt < self.max_retries:
            try:
                logger.info(f"正在查询单词: {word} (尝试 {attempt + 1}/{self.max_retries})")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    result = self._parse_response(data[0])
                    logger.info(f"成功获取单词 '{word}' 的信息")
                    return result
                if response.status_code == 404:
                    logger.warning(f"未找到单词 '{word}' 的定义")
                    return None
                
                last_error = f"状态码 {response.status_code}"
                logger.warning(f"API请求失败: {last_error}")
            except requests.exceptions.Timeout as e:
                last_error = f"超时: {e}"
                logger.warning(f"网络请求超时: {word}")
            except requests.exceptions.ConnectionError as e:
                last_error = f"连接错误: {e}"
                logger.warning("网络连接错误: 无法连接到词典服务器")
            except requests.exceptions.RequestException as e:
                last_error = f"请求错误: {e}"
                logger.warning(f"网络请求错误: {e}")
            except json.JSONDecodeError as e:
                last_error = f"JSON解析错误: {e}"
                logger.warning(f"JSON解析错误: {e}")
            except Exception as e:
                last_error = f"未知错误: {e}"
                logger.warning(f"获取单词信息时发生错误: {e}")
            
            attempt += 1
            if attempt < self.max_retries:
                sleep_seconds = self.backoff_factor * (2 ** (attempt - 1))
                time.sleep(sleep_seconds)
        
        logger.error(f"获取单词 '{word}' 信息失败: {last_error}")
        return None
    
    def _parse_response(self, data: Dict) -> Dict:
        """解析API响应数据
        
        Args:
            data: API返回的原始数据
            
        Returns:
            解析后的单词信息字典
        """
        word_info = {
            "word": data.get("word", ""),
            "phonetic": "",
            "meanings": [],
            "examples": [],
            "chinese_meanings": []  # 添加中文释义字段
        }
        
        # 获取音标
        if "phonetic" in data:
            word_info["phonetic"] = data["phonetic"]
        elif "phonetics" in data and len(data["phonetics"]) > 0:
            # 尝试从phonetics数组中获取音标
            for phonetic in data["phonetics"]:
                if phonetic.get("text"):
                    word_info["phonetic"] = phonetic["text"]
                    break
        
        # 获取释义和例句
        if "meanings" in data:
            for meaning in data["meanings"]:
                part_of_speech = meaning.get("partOfSpeech", "")
                definitions = meaning.get("definitions", [])
                
                for definition in definitions:
                    meaning_text = definition.get("definition", "")
                    example = definition.get("example", "")
                    
                    word_info["meanings"].append({
                        "part_of_speech": part_of_speech,
                        "definition": meaning_text
                    })
                    
                    if example:
                        word_info["examples"].append(example)
        
        # 尝试获取中文释义
        if self.translation_api and word_info["meanings"]:
            try:
                # 翻译前几个释义
                for i, meaning_info in enumerate(word_info["meanings"][:3]):
                    english_definition = meaning_info["definition"]
                    chinese_translation = self.translation_api.translate_to_chinese(english_definition)
                    if chinese_translation:
                        word_info["chinese_meanings"].append({
                            "part_of_speech": meaning_info["part_of_speech"],
                            "definition": chinese_translation
                        })
            except Exception as e:
                logger.error(f"翻译释义时发生错误: {e}")
        
        return word_info
    
    def get_random_words_info(self, count: int = 10, vocabulary_level: str = "cet6") -> List[Dict]:
        """
        获取随机单词的信息列表
        
        Args:
            count: 要获取的随机单词数量
            vocabulary_level: 词汇级别，可选值: "cet4", "cet6", "gre"
            
        Returns:
            包含单词信息的字典列表
        """
        import random
        
        # 根据词汇级别选择对应的词汇文件
        base_dir = os.path.dirname(os.path.dirname(__file__))
        vocabulary_files = {
            "cet4": os.path.join(base_dir, "data", "cet4_words.txt"),
            "cet6": os.path.join(base_dir, "data", "cet6_words.txt"),
            "gre": os.path.join(base_dir, "data", "gre_words.txt")
        }
        
        # 默认词汇级别为cet6
        if vocabulary_level not in vocabulary_files:
            logger.warning(f"未知的词汇级别: {vocabulary_level}，使用默认级别: cet6")
            vocabulary_level = "cet6"
        
        vocabulary_file = vocabulary_files[vocabulary_level]
        
        try:
            # 尝试读取指定级别的词汇文件
            with open(vocabulary_file, 'r', encoding='utf-8') as f:
                vocabulary_words = [line.strip() for line in f.readlines() if line.strip()]
            logger.info(f"成功加载 {vocabulary_level.upper()} 词汇，共 {len(vocabulary_words)} 个单词")
            
        except FileNotFoundError:
            # 如果找不到指定级别的词汇文件，尝试使用其他级别的文件作为备选
            logger.warning(f"未找到 {vocabulary_level.upper()} 词汇文件: {vocabulary_file}")
            
            # 备选方案：按优先级尝试其他词汇文件
            fallback_levels = ["cet6", "cet4", "gre"]
            vocabulary_words = None
            
            for level in fallback_levels:
                if level != vocabulary_level:
                    fallback_file = vocabulary_files[level]
                    try:
                        with open(fallback_file, 'r', encoding='utf-8') as f:
                            vocabulary_words = [line.strip() for line in f.readlines() if line.strip()]
                        logger.info(f"使用备选词汇级别: {level.upper()}，共 {len(vocabulary_words)} 个单词")
                        break
                    except FileNotFoundError:
                        continue
            
            # 如果所有词汇文件都找不到，使用默认词汇列表
            if vocabulary_words is None:
                logger.warning("未找到任何词汇文件，使用默认词汇列表")
                vocabulary_words = [
                    "ability", "able", "about", "above", "accept", "according", "account", "across", "act", "action",
                    "activity", "actually", "add", "address", "administration", "admit", "adult", "affect", "after",
                    "again", "against", "age", "agency", "agent", "ago", "agree", "agreement", "ahead", "air",
                    "all", "allow", "almost", "alone", "along", "already", "also", "although", "always", "American",
                    "among", "amount", "analysis", "and", "animal", "another", "answer", "any", "anyone", "anything",
                    "appear", "apply", "approach", "area", "argue", "arm", "around", "arrive", "art", "article",
                    "artist", "as", "ask", "assume", "at", "attack", "attention", "attorney", "audience", "author",
                    "authority", "available", "avoid", "away", "baby", "back", "bad", "bag", "ball", "bank",
                    "bar", "base", "be", "beat", "beautiful", "because", "become", "bed", "before", "begin",
                    "behavior", "behind", "believe", "benefit", "best", "better", "between", "beyond", "big", "bill",
                    "billion", "bit", "black", "blood", "blue", "board", "body", "book", "born", "both",
                    "box", "boy", "break", "bring", "brother", "budget", "build", "building", "business", "but",
                    "buy", "by", "call", "camera", "campaign", "can", "cancer", "candidate", "capital", "car",
                    "card", "care", "career", "carry", "case", "catch", "cause", "cell", "center", "central",
                    "century", "certain", "certainly", "chair", "challenge", "chance", "change", "character", "charge", "check",
                    "child", "choice", "choose", "church", "citizen", "city", "civil", "claim", "class", "clear",
                    "clearly", "close", "coach", "cold", "collection", "college", "color", "come", "commercial", "common",
                    "community", "company", "compare", "computer", "concern", "condition", "conference", "Congress", "consider", "consumer",
                    "contain", "continue", "control", "cost", "could", "country", "couple", "course", "court", "cover",
                    "create", "crime", "cultural", "culture", "cup", "current", "customer", "cut", "dark", "data",
                    "daughter", "day", "dead", "deal", "death", "debate", "decade", "decide", "decision", "deep",
                    "defense", "degree", "Democrat", "democratic", "describe", "design", "despite", "detail", "determine", "develop",
                    "development", "die", "difference", "different", "difficult", "dinner", "direction", "director", "discover", "discuss",
                    "discussion", "disease", "do", "doctor", "dog", "door", "down", "draw", "dream", "drive",
                    "drop", "drug", "during", "each", "early", "east", "easy", "eat", "economic", "economy",
                    "edge", "education", "effect", "effort", "eight", "either", "election", "else", "employee", "end"
                ]
        
        # 随机选择指定数量的单词
        selected_words = random.sample(vocabulary_words, min(count, len(vocabulary_words)))
        
        # 获取每个单词的详细信息
        word_infos = []
        for word in selected_words:
            word_info = self.get_word_info(word)
            if word_info:
                word_infos.append(word_info)
        
        return word_infos


def demo():
    """演示函数"""
    api = DictionaryAPI()
    
    # 测试查询单词
    word = "hello"
    print(f"查询单词: {word}")
    info = api.get_word_info(word)
    
    if info:
        print(f"单词: {info['word']}")
        print(f"音标: {info['phonetic']}")
        print("英文释义:")
        for meaning in info["meanings"]:
            print(f"  {meaning['part_of_speech']}: {meaning['definition']}")
        
        # 显示中文释义（如果有的话）
        if info["chinese_meanings"]:
            print("中文释义:")
            for meaning in info["chinese_meanings"]:
                print(f"  {meaning['part_of_speech']}: {meaning['definition']}")
        
        print("例句:")
        for example in info["examples"]:
            print(f"  {example}")
    else:
        print("未能获取单词信息")


if __name__ == "__main__":
    demo()
