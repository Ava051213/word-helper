#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立测试搜索历史清空功能
"""

import os
import json

def test_clear_search_history():
    """测试清空搜索历史功能"""
    print("=== 开始独立测试清空搜索历史 ===")
    
    # 使用绝对路径确保正确
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = current_dir  # 当前目录就是项目根目录
    history_file = os.path.join(project_dir, "data", "search_history.json")
    
    print(f"项目目录: {project_dir}")
    print(f"目标文件路径: {history_file}")
    print(f"文件存在: {os.path.exists(history_file)}")
    
    if os.path.exists(history_file):
        # 读取当前内容
        with open(history_file, 'r', encoding='utf-8') as f:
            current_content = json.load(f)
            print(f"当前文件内容: {current_content}")
        
        # 方法1: 使用json.dump清空文件
        print("\n方法1: 使用json.dump清空文件")
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
                f.flush()
                print("方法1写入完成")
            
            # 验证方法1
            with open(history_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
                print(f"方法1后文件内容: {content}")
                
            if content == []:
                print("✓ 方法1成功")
            else:
                print("✗ 方法1失败")
                
        except Exception as e:
            print(f"方法1错误: {e}")
        
        # 方法2: 直接写入空数组
        print("\n方法2: 直接写入空数组")
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                f.write('[]')
                f.flush()
                print("方法2写入完成")
            
            # 验证方法2
            with open(history_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
                print(f"方法2后文件内容: {content}")
                
            if content == []:
                print("✓ 方法2成功")
            else:
                print("✗ 方法2失败")
                
        except Exception as e:
            print(f"方法2错误: {e}")
        
        # 最终验证
        print("\n最终验证:")
        with open(history_file, 'r', encoding='utf-8') as f:
            final_content = json.load(f)
            print(f"最终文件内容: {final_content}")
            
        if final_content == []:
            print("=== 测试成功: 搜索历史已清空 ===")
        else:
            print("=== 测试失败: 文件内容未被清空 ===")
            
    else:
        print("=== 测试失败: 文件不存在 ===")

if __name__ == "__main__":
    test_clear_search_history()