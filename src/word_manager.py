#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单词管理模块
负责单词的增删改查等基本操作
"""

import json
import os
import datetime
from typing import Dict, List, Optional

# 导入词典API模块
try:
    from dictionary_api import DictionaryAPI
    DICTIONARY_API_AVAILABLE = True
except ImportError:
    DICTIONARY_API_AVAILABLE = False
    print("警告: 无法导入词典API模块，自动获取单词信息功能将不可用")


class WordManager:
    """单词管理器"""
    
    def __init__(self, data_file: str = "../data/words.json"):
        """初始化单词管理器"""
        self.data_file = data_file
        self.words = self.load_words()
        
        # 初始化词典API
        if DICTIONARY_API_AVAILABLE:
            self.dictionary_api = DictionaryAPI()
        else:
            self.dictionary_api = None
    
    def load_words(self) -> Dict:
        """从文件加载单词数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def save_words(self) -> None:
        """保存单词数据到文件"""
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.words, f, ensure_ascii=False, indent=2)
    
    def add_word(self) -> None:
        """添加新单词（交互式）"""
        print("\n--- 添加单词 ---")
        word = input("请输入单词: ").strip().lower()
        if not word:
            print("单词不能为空！")
            return
        
        if word in self.words:
            print(f"单词 '{word}' 已存在！")
            return
        
        # 尝试从词典API获取单词信息
        meaning = ""
        example = ""
        if self.dictionary_api:
            print("正在从词典获取单词信息...")
            word_info = self.dictionary_api.get_word_info(word)
            if word_info:
                # 显示获取到的信息供用户确认
                print(f"\n找到单词信息:")
                print(f"单词: {word_info['word']}")
                if word_info['phonetic']:
                    print(f"音标: {word_info['phonetic']}")
                if word_info['meanings']:
                    print("释义:")
                    for i, meaning_info in enumerate(word_info['meanings'][:3]):  # 只显示前3个释义
                        print(f"  {i+1}. {meaning_info['part_of_speech']}: {meaning_info['definition']}")
                    # 使用第一个释义作为默认释义
                    meaning = word_info['meanings'][0]['definition']
                if word_info['examples']:
                    print("例句:")
                    for i, ex in enumerate(word_info['examples'][:2]):  # 只显示前2个例句
                        print(f"  {i+1}. {ex}")
                    # 使用第一个例句作为默认例句
                    example = word_info['examples'][0]
        
        # 如果没有自动获取到释义，让用户手动输入
        if not meaning:
            meaning = input("请输入释义: ").strip()
        else:
            confirm = input(f"是否使用获取到的释义 '{meaning}'? (Y/n): ").strip().lower()
            if confirm == 'n':
                meaning = input("请输入释义: ").strip()
        
        # 如果没有自动获取到例句，让用户手动输入
        if not example:
            example = input("请输入例句 (可选): ").strip()
        else:
            confirm = input(f"是否使用获取到的例句 '{example}'? (Y/n): ").strip().lower()
            if confirm == 'n':
                example = input("请输入例句 (可选): ").strip()
        
        category = input("请输入分类 (可选): ").strip()
        
        # 初始化单词信息
        self.words[word] = {
            "meaning": meaning,
            "example": example,
            "category": category,
            "add_date": datetime.datetime.now().isoformat(),
            "last_reviewed": None,
            "next_review": None,
            "review_count": 0,
            "interval": 1,  # 初始间隔为1天
            "difficulty": "normal"
        }
        
        self.save_words()
        print(f"单词 '{word}' 添加成功！")
    
    def add_word_direct(self, word: str, meaning: str, example: str = "", category: str = "") -> bool:
        """直接添加新单词（编程接口）
        
        Args:
            word: 单词
            meaning: 释义
            example: 例句
            category: 分类
            
        Returns:
            bool: 添加成功返回True，否则返回False
        """
        if not word or not meaning:
            return False
        
        word = word.strip().lower()
        
        if word in self.words:
            return False
        
        # 初始化单词信息
        self.words[word] = {
            "meaning": meaning,
            "example": example,
            "category": category,
            "add_date": datetime.datetime.now().isoformat(),
            "last_reviewed": None,
            "next_review": None,
            "review_count": 0,
            "interval": 1,  # 初始间隔为1天
            "difficulty": "normal"
        }
        
        self.save_words()
        return True
    
    def delete_word(self) -> None:
        """删除单词"""
        print("\n--- 删除单词 ---")
        word = input("请输入要删除的单词: ").strip().lower()
        if not word:
            print("单词不能为空！")
            return
        
        if word in self.words:
            confirm = input(f"确定要删除单词 '{word}' 吗? (y/N): ").strip().lower()
            if confirm == 'y':
                del self.words[word]
                self.save_words()
                print(f"单词 '{word}' 删除成功！")
            else:
                print("取消删除操作。")
        else:
            print(f"单词 '{word}' 不存在！")
    
    def view_words(self) -> None:
        """查看所有单词"""
        print("\n--- 单词列表 ---")
        if not self.words:
            print("暂无单词数据。")
            return
        
        print(f"{'单词':<15} {'释义':<20} {'分类':<10} {'添加日期':<20}")
        print("-" * 70)
        for word, info in self.words.items():
            add_date = info.get('add_date', '')[:10] if info.get('add_date') else ''
            print(f"{word:<15} {info['meaning']:<20} {info['category']:<10} {add_date:<20}")
    
    def search_word(self) -> None:
        """搜索单词"""
        print("\n--- 搜索单词 ---")
        keyword = input("请输入搜索关键词: ").strip().lower()
        if not keyword:
            print("关键词不能为空！")
            return
        
        found_words = []
        for word, info in self.words.items():
            if (keyword in word or 
                keyword in info['meaning'] or 
                keyword in info.get('example', '') or
                keyword in info.get('category', '')):
                found_words.append((word, info))
        
        if found_words:
            print(f"\n找到 {len(found_words)} 个相关单词:")
            print(f"{'单词':<15} {'释义':<20} {'分类':<10}")
            print("-" * 50)
            for word, info in found_words:
                print(f"{word:<15} {info['meaning']:<20} {info['category']:<10}")
        else:
            print("未找到相关单词。")
    
    def get_word(self, word: str) -> Optional[Dict]:
        """获取单词信息"""
        return self.words.get(word)
    
    def update_word(self, word: str, info: Dict) -> None:
        """更新单词信息"""
        self.words[word] = info
        self.save_words()
    
    def get_words_for_review(self) -> List[str]:
        """获取需要复习的单词列表"""
        now = datetime.datetime.now()
        review_words = []
        
        for word, info in self.words.items():
            next_review = info.get('next_review')
            if next_review:
                next_review_time = datetime.datetime.fromisoformat(next_review)
                if now >= next_review_time:
                    review_words.append(word)
            # 如果没有设置下次复习时间，则认为需要复习
            elif info['review_count'] > 0:
                review_words.append(word)
        
        return review_words
    
    def show_statistics(self) -> None:
        """显示学习统计"""
        print("\n--- 学习统计 ---")
        total_words = len(self.words)
        reviewed_words = sum(1 for info in self.words.values() if info['review_count'] > 0)
        
        print(f"总单词数: {total_words}")
        print(f"已复习单词数: {reviewed_words}")
        print(f"未复习单词数: {total_words - reviewed_words}")
        
        if total_words > 0:
            review_rate = (reviewed_words / total_words) * 100
            print(f"复习率: {review_rate:.1f}%")
    
    def generate_random_words(self, count: int = 10) -> List[str]:
        """
        生成随机英语单词列表
        
        Args:
            count (int): 要生成的单词数量，默认为10个
            
        Returns:
            List[str]: 随机单词列表
        """
        # 常用英语单词列表
        common_words = [
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
            "edge", "education", "effect", "effort", "eight", "either", "election", "else", "employee", "end",
            "energy", "enjoy", "enough", "enter", "entire", "environment", "environmental", "especially", "establish", "even",
            "evening", "event", "ever", "every", "everybody", "everyone", "everything", "evidence", "exactly", "example",
            "executive", "exist", "expect", "experience", "expert", "explain", "eye", "face", "fact", "factor",
            "fail", "fall", "family", "far", "fast", "father", "fear", "federal", "feel", "feeling",
            "few", "field", "fight", "figure", "fill", "film", "final", "finally", "financial", "find",
            "fine", "finger", "finish", "fire", "firm", "first", "fish", "five", "floor", "fly",
            "focus", "follow", "food", "foot", "for", "force", "foreign", "forget", "form", "former",
            "forward", "four", "free", "friend", "from", "front", "full", "fund", "future", "game",
            "garden", "gas", "general", "generation", "get", "girl", "give", "glass", "go", "goal",
            "good", "government", "great", "green", "ground", "group", "grow", "growth", "guess", "gun",
            "guy", "hair", "half", "hand", "hang", "happen", "happy", "hard", "have", "he",
            "head", "health", "hear", "heart", "heat", "heavy", "help", "her", "here", "herself",
            "high", "him", "himself", "his", "history", "hit", "hold", "home", "hope", "hospital",
            "hot", "hotel", "hour", "house", "how", "however", "huge", "human", "hundred", "husband",
            "I", "idea", "identify", "if", "image", "imagine", "impact", "important", "improve", "in",
            "include", "including", "increase", "indeed", "indicate", "individual", "industry", "information", "inside", "instead",
            "institution", "interest", "interesting", "international", "interview", "into", "investment", "involve", "issue", "it",
            "item", "its", "itself", "job", "join", "just", "keep", "key", "kid", "kill",
            "kind", "kitchen", "know", "knowledge", "land", "language", "large", "last", "late", "later",
            "laugh", "law", "lawyer", "lay", "lead", "leader", "learn", "least", "leave", "left",
            "leg", "legal", "less", "let", "letter", "level", "lie", "life", "light", "like",
            "likely", "line", "list", "listen", "little", "live", "local", "long", "look", "lose",
            "loss", "lot", "love", "low", "machine", "magazine", "main", "maintain", "major", "majority",
            "make", "man", "manage", "management", "manager", "many", "market", "marriage", "material", "matter",
            "may", "maybe", "me", "mean", "measure", "media", "medical", "meet", "meeting", "member",
            "memory", "mention", "message", "method", "middle", "might", "military", "million", "mind", "minute",
            "miss", "mission", "model", "modern", "moment", "money", "month", "more", "morning", "most",
            "mother", "mouth", "move", "movement", "movie", "Mr", "Mrs", "much", "music", "must",
            "my", "myself", "name", "nation", "national", "natural", "nature", "near", "nearly", "necessary",
            "need", "network", "never", "new", "news", "newspaper", "next", "nice", "night", "no",
            "none", "nor", "north", "not", "note", "nothing", "notice", "now", "n't", "number",
            "occur", "of", "off", "offer", "office", "officer", "official", "often", "oh", "oil",
            "ok", "old", "on", "once", "one", "only", "onto", "open", "operation", "opportunity",
            "option", "or", "order", "organization", "other", "others", "our", "out", "outside", "over",
            "own", "owner", "page", "pain", "painting", "paper", "parent", "part", "participant", "particular",
            "particularly", "partner", "party", "pass", "past", "patient", "pattern", "pay", "peace", "people",
            "per", "perform", "performance", "perhaps", "period", "person", "personal", "phone", "physical", "pick",
            "picture", "piece", "place", "plan", "plant", "play", "player", "PM", "point", "police",
            "policy", "political", "politics", "poor", "popular", "population", "position", "positive", "possible", "power",
            "practice", "prepare", "present", "president", "pressure", "pretty", "prevent", "price", "private", "probably",
            "problem", "process", "produce", "product", "production", "professional", "professor", "program", "project", "property",
            "protect", "prove", "provide", "public", "pull", "purpose", "push", "put", "quality", "question",
            "quickly", "quite", "race", "radio", "raise", "range", "rate", "rather", "reach", "read",
            "ready", "real", "reality", "realize", "really", "reason", "receive", "recent", "recently", "recognize",
            "record", "red", "reduce", "reflect", "region", "relate", "relationship", "religious", "remain", "remember",
            "remove", "report", "represent", "Republican", "require", "research", "resource", "respond", "response", "responsibility",
            "rest", "result", "return", "reveal", "rich", "right", "rise", "risk", "road", "rock",
            "role", "room", "rule", "run", "safe", "same", "save", "say", "scene", "school",
            "science", "scientist", "score", "sea", "season", "seat", "second", "section", "security", "see",
            "seek", "seem", "sell", "send", "senior", "sense", "series", "serious", "serve", "service",
            "set", "seven", "several", "sex", "sexual", "shake", "share", "she", "shoot", "short",
            "shot", "should", "shoulder", "show", "side", "sign", "significant", "similar", "simple", "simply",
            "since", "sing", "single", "sister", "sit", "site", "situation", "six", "size", "skill",
            "skin", "small", "smile", "so", "social", "society", "soldier", "some", "somebody", "someone",
            "something", "sometimes", "son", "song", "soon", "sort", "sound", "source", "south", "southern",
            "space", "speak", "special", "specific", "speech", "spend", "sport", "spring", "staff", "stage",
            "stand", "standard", "star", "start", "state", "statement", "station", "stay", "step", "still",
            "stock", "stop", "store", "story", "strategy", "street", "strong", "structure", "student", "study",
            "stuff", "style", "subject", "success", "successful", "such", "suddenly", "suffer", "suggest", "summer",
            "support", "sure", "surface", "system", "table", "take", "talk", "task", "tax", "teach",
            "teacher", "team", "technology", "television", "tell", "ten", "tend", "term", "test", "than",
            "thank", "that", "the", "their", "them", "themselves", "then", "theory", "there", "these",
            "they", "thing", "think", "third", "this", "those", "though", "thought", "thousand", "threat",
            "three", "through", "throughout", "throw", "thus", "time", "to", "today", "together", "tonight",
            "too", "top", "total", "tough", "toward", "town", "trade", "traditional", "training", "travel",
            "treat", "treatment", "tree", "trial", "trip", "trouble", "true", "truth", "try", "turn",
            "TV", "two", "type", "under", "understand", "unit", "until", "up", "upon", "us",
            "use", "usually", "value", "various", "very", "victim", "view", "violence", "visit", "voice",
            "vote", "wait", "walk", "wall", "want", "war", "watch", "water", "way", "we",
            "weapon", "wear", "week", "weight", "well", "west", "western", "what", "whatever", "when",
            "where", "whether", "which", "while", "white", "who", "whole", "whom", "whose", "why",
            "wide", "wife", "will", "win", "wind", "window", "wish", "with", "within", "without",
            "woman", "wonder", "word", "work", "worker", "world", "worry", "would", "write", "writer",
            "wrong", "yard", "yeah", "year", "yes", "yet", "you", "young", "your", "yourself"
        ]
        
        # 如果请求的数量大于单词库大小，则返回整个单词库
        if count >= len(common_words):
            return common_words.copy()
        
        # 随机选择指定数量的单词
        import random
        return random.sample(common_words, count)