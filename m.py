import json
import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage
import pygame
import time

def parse_message(data_str):
    """反序列化消息数据"""
    data = json.loads(data_str)
    
    # 恢复二进制数据
    if 'data' in data and isinstance(data['data'], list):
        data['data'] = bytes(data['data'])
    
    # 恢复文本编码
    if 'text' in data:
        data['text'] = bytes(data['text'], 'utf-8').decode('unicode_escape')
    
    return data

def import_midi(input_path, output_path):
    mid = MidiFile()
    current_track = None
    last_time = 0
    
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # 处理文件头
            if line.startswith("[MIDI HEADER]"):
                mid.type = int(next(f).split("=")[1])
                mid.ticks_per_beat = int(next(f).split("=")[1])
                next(f)  # 跳过track_count
                continue
            
            # 新建音轨
            if line.startswith("[TRACK"):
                current_track = MidiTrack()
                mid.tracks.append(current_track)
                last_time = 0
                continue
            
            # 解析消息行
            if '|' in line:
                parts = line.split('|', 3)
                prefix, abs_time, msg_type, msg_data = parts
                abs_time = int(abs_time)
                
                # 计算相对时间
                delta_time = abs_time - last_time
                last_time = abs_time
                
                # 反序列化数据
                data = parse_message(msg_data)
                
                # 创建消息对象
                try:
                    if prefix == "META":
                        msg = MetaMessage(type=msg_type, time=delta_time, **data)
                    else:
                        # 强制转换数值类型
                        int_fields = ['channel', 'note', 'velocity', 'control', 
                                    'value', 'program', 'pitch']
                        for field in int_fields:
                            if field in data:
                                data[field] = int(data[field])
                        msg = Message(type=msg_type, time=delta_time, **data)
                    
                    current_track.append(msg)
                except Exception as e:
                    print(f"消息解析失败: {line}")
                    print(f"错误详情: {str(e)}")
    
    mid.save(output_path)
    return mid

def play_midi(midi_path):
    pygame.mixer.init()
    pygame.mixer.music.load(midi_path)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    print("播放完成")

if __name__ == "__main__":
    rebuilt = import_midi('midi_content.txt', 'rebuilt.mid')
    play_midi('rebuilt.mid')