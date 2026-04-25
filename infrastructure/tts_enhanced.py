#!/usr/bin/env python3
"""TTS 增强模块 V1.0.0

让语音更自然、更有真人感
"""

import json
from pathlib import Path
from typing import Optional, Dict

class EnhancedTTS:
    """增强 TTS"""
    
    # 高质量中文声音
    VOICES = {
        'zh_female_joyful': {
            'voice_id': 'b4775100',
            'name': '悦悦',
            'style': '社交分享',
            'emotion': 'Joyful'
        },
        'zh_female_calm': {
            'voice_id': '77e15f2c',
            'name': '婉青',
            'style': '情绪抚慰',
            'emotion': 'Calm'
        },
        'zh_male_calm': {
            'voice_id': 'ac09aeb4',
            'name': '阿豪',
            'style': '磁性主持',
            'emotion': 'Calm'
        },
        'zh_male_knowledge': {
            'voice_id': '87cb2405',
            'name': '建国',
            'style': '知识科普',
            'emotion': 'Calm'
        },
        'zh_male_tech': {
            'voice_id': '3b9f1e27',
            'name': '小明',
            'style': '科技达人',
            'emotion': 'Joyful'
        }
    }
    
    # 情感参数
    EMOTIONS = {
        'happy': {'Joy': 0.8, 'Surprise': 0.2},
        'sad': {'Sadness': 0.7, 'Fear': 0.1},
        'angry': {'Anger': 0.8, 'Disgust': 0.1},
        'calm': {'Calm': 0.9},
        'excited': {'Joy': 0.6, 'Surprise': 0.4},
        'neutral': {}
    }
    
    # 语速预设
    SPEEDS = {
        'very_slow': 0.7,
        'slow': 0.85,
        'normal': 1.0,
        'fast': 1.15,
        'very_fast': 1.3
    }
    
    def __init__(self):
        self.config_file = Path('infrastructure/tts_config.json')
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'default_voice': 'zh_female_calm',
            'default_speed': 'normal',
            'default_emotion': 'neutral',
            'auto_punctuation_pause': True,
            'auto_emotion': True
        }
    
    def _save_config(self):
        """保存配置"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def enhance_text(self, text: str) -> str:
        """增强文本（添加自然停顿）"""
        if not self.config.get('auto_punctuation_pause', True):
            return text
        
        # 在标点后添加适当停顿
        enhanced = text
        enhanced = enhanced.replace('。', '... ')
        enhanced = enhanced.replace('！', '... ')
        enhanced = enhanced.replace('？', '... ')
        enhanced = enhanced.replace('，', '.. ')
        enhanced = enhanced.replace('、', '. ')
        
        return enhanced
    
    def get_voice_params(self, voice_type: str = None, 
                         emotion: str = None,
                         speed: str = None) -> dict:
        """获取语音参数"""
        voice_type = voice_type or self.config.get('default_voice', 'zh_female_calm')
        emotion = emotion or self.config.get('default_emotion', 'neutral')
        speed = speed or self.config.get('default_speed', 'normal')
        
        voice = self.VOICES.get(voice_type, self.VOICES['zh_female_calm'])
        emo_params = self.EMOTIONS.get(emotion, {})
        speed_val = self.SPEEDS.get(speed, 1.0)
        
        return {
            'voice_id': voice['voice_id'],
            'voice_name': voice['name'],
            'speed': speed_val,
            'emotion': emo_params
        }
    
    def build_command(self, text: str, 
                      voice_type: str = None,
                      emotion: str = None,
                      speed: str = None,
                      output: str = None) -> str:
        """构建 TTS 命令"""
        params = self.get_voice_params(voice_type, emotion, speed)
        enhanced_text = self.enhance_text(text)
        
        cmd = f'python3 skills/tts/scripts/tts.py -t "{enhanced_text}"'
        cmd += f' --voice-id {params["voice_id"]}'
        
        if params['speed'] != 1.0:
            cmd += f' --speed {params["speed"]}'
        
        if output:
            cmd += f' -o {output}'
        
        return cmd
    
    def list_voices(self):
        """列出可用声音"""
        print("可用的高质量中文声音：")
        print("-" * 40)
        for key, voice in self.VOICES.items():
            print(f"  {voice['name']} ({voice['style']}) - {voice['emotion']}")
    
    def list_emotions(self):
        """列出可用情感"""
        print("可用的情感模式：")
        print("-" * 40)
        for key in self.EMOTIONS.keys():
            print(f"  {key}")

if __name__ == '__main__':
    tts = EnhancedTTS()
    
    print("=" * 50)
    print("TTS 增强模块")
    print("=" * 50)
    
    tts.list_voices()
    print()
    tts.list_emotions()
    
    print("\n示例命令：")
    cmd = tts.build_command(
        "你好，我是小艺Claw！",
        voice_type='zh_female_joyful',
        emotion='happy',
        speed='normal',
        output='/tmp/hello.wav'
    )
    print(f"  {cmd}")
