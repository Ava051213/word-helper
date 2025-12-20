#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词典API模块
通过Free Dictionary API获取单词的释义、例句等信息，并提供中文翻译功能
"""

import requests
import json
import logging
from typing import Dict, Optional, List

# 导入翻译API
try:
    from translation_api import TranslationAPI
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
        try:
            # 记录请求开始
            logger.info(f"正在查询单词: {word}")
            
            # 发送API请求
            url = f"{self.base_url}/{word.lower()}"
            response = requests.get(url, timeout=10)
            
            # 检查响应状态
            if response.status_code == 200:
                data = response.json()
                result = self._parse_response(data[0])  # API返回的是列表，取第一个结果
                logger.info(f"成功获取单词 '{word}' 的信息")
                return result
            elif response.status_code == 404:
                logger.warning(f"未找到单词 '{word}' 的定义")
                return None
            else:
                logger.error(f"API请求失败，状态码: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"网络请求超时: {word}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"网络连接错误: 无法连接到词典服务器")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求错误: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {e}")
            return None
        except Exception as e:
            logger.error(f"获取单词信息时发生错误: {e}")
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
    
    def get_random_words_info(self, count: int = 10) -> List[Dict]:
        """
        获取随机单词的信息列表
        
        Args:
            count: 要获取的随机单词数量
            
        Returns:
            包含单词信息的字典列表
        """
        import random
        
        # 常用英语单词列表作为种子
        common_words = [
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "I",
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
            "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
            "or", "an", "will", "my", "one", "all", "would", "there", "their",
            "what", "so", "up", "out", "if", "about", "who", "get", "which", "go",
            "me", "when", "make", "can", "like", "time", "no", "just", "him", "know",
            "take", "people", "into", "year", "your", "good", "some", "could", "them",
            "see", "other", "than", "then", "now", "look", "only", "come", "its",
            "over", "think", "also", "back", "after", "use", "two", "how", "our",
            "work", "first", "well", "way", "even", "new", "want", "because", "any",
            "these", "give", "day", "most", "us", "is", "was", "are", "has", "had",
            "been", "were", "said", "each", "which", "their", "time", "will", "about",
            "many", "then", "them", "write", "would", "like", "so", "these", "her",
            "long", "make", "thing", "see", "him", "two", "has", "look", "more",
            "day", "could", "go", "come", "did", "number", "sound", "no", "most",
            "people", "my", "over", "know", "water", "than", "call", "first", "who",
            "may", "down", "side", "been", "now", "find", "any", "new", "work",
            "part", "take", "get", "place", "made", "live", "where", "after", "back",
            "little", "only", "round", "man", "year", "came", "show", "every",
            "good", "me", "give", "our", "under", "name", "very", "through", "just",
            "form", "sentence", "great", "think", "say", "help", "low", "line",
            "differ", "turn", "cause", "much", "mean", "before", "move", "right",
            "boy", "old", "too", "same", "tell", "does", "set", "three", "want",
            "air", "well", "also", "play", "small", "end", "put", "home", "read",
            "hand", "port", "large", "spell", "add", "even", "land", "here", "must",
            "big", "high", "such", "follow", "act", "why", "ask", "men", "change",
            "went", "light", "kind", "off", "need", "house", "picture", "try",
            "again", "animal", "point", "mother", "world", "near", "build", "self",
            "earth", "father", "head", "stand", "own", "page", "should", "country",
            "found", "answer", "school", "grow", "study", "still", "learn", "plant",
            "cover", "food", "sun", "four", "between", "state", "keep", "eye",
            "never", "last", "let", "thought", "city", "tree", "cross", "farm",
            "hard", "start", "might", "story", "saw", "far", "sea", "draw", "left",
            "late", "run", "don't", "while", "press", "close", "night", "real",
            "life", "few", "north", "open", "seem", "together", "next", "white",
            "children", "begin", "got", "walk", "example", "ease", "paper", "group",
            "always", "music", "those", "both", "mark", "often", "letter", "until",
            "mile", "river", "car", "feet", "care", "second", "book", "carry",
            "took", "science", "eat", "room", "friend", "began", "idea", "fish",
            "mountain", "stop", "once", "base", "hear", "horse", "cut", "sure",
            "watch", "color", "face", "wood", "main", "enough", "plain", "girl",
            "usual", "young", "ready", "above", "ever", "red", "list", "though",
            "feel", "talk", "bird", "soon", "body", "dog", "family", "direct",
            "pose", "leave", "song", "measure", "door", "product", "black", "short",
            "numeral", "class", "wind", "question", "happen", "complete", "ship",
            "area", "half", "rock", "order", "fire", "south", "problem", "piece",
            "told", "knew", "pass", "since", "top", "whole", "king", "space",
            "heard", "best", "hour", "better", "during", "hundred", "five", "remember",
            "step", "early", "hold", "west", "ground", "interest", "reach", "fast",
            "verb", "sing", "listen", "six", "table", "travel", "less", "morning",
            "ten", "simple", "several", "vowel", "toward", "war", "lay", "against",
            "pattern", "slow", "center", "love", "person", "money", "serve", "appear",
            "road", "map", "rain", "rule", "govern", "pull", "cold", "notice",
            "voice", "unit", "power", "town", "fine", "certain", "fly", "fall",
            "lead", "cry", "dark", "machine", "note", "wait", "plan", "figure",
            "star", "box", "noun", "field", "rest", "correct", "able", "pound",
            "done", "beauty", "drive", "stood", "contain", "front", "teach", "week",
            "final", "gave", "green", "oh", "quick", "develop", "ocean", "warm",
            "free", "minute", "strong", "special", "mind", "behind", "clear", "tail",
            "produce", "fact", "street", "inch", "multiply", "nothing", "course",
            "stay", "wheel", "full", "force", "blue", "object", "decide", "surface",
            "deep", "moon", "island", "foot", "system", "busy", "test", "record",
            "boat", "common", "gold", "possible", "plane", "stead", "dry", "wonder",
            "laugh", "thousands", "ago", "ran", "check", "game", "shape", "equate",
            "hot", "miss", "brought", "heat", "snow", "tire", "bring", "yes",
            "distant", "fill", "east", "paint", "language", "among"
        ]
        
        # 随机选择指定数量的单词
        selected_words = random.sample(common_words, min(count, len(common_words)))
        
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