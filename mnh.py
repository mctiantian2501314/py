import mido
import json

def serialize_message(msg):
    """安全序列化MIDI消息"""
    data = msg.dict()
    
    # 移除冗余字段
    data.pop('type', None)
    data.pop('time', None)
    
    # 处理二进制数据
    if 'data' in data and isinstance(data['data'], bytes):
        data['data'] = list(data['data'])
    
    # 处理文本编码
    if 'text' in data:
        data['text'] = data['text'].encode('unicode_escape').decode('utf-8')
    
    return json.dumps(data, ensure_ascii=False)

def export_midi(input_path, output_path):
    mid = mido.MidiFile(input_path)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # 文件头
        f.write("[MIDI HEADER]\n")
        f.write(f"type={mid.type}\n")
        f.write(f"ticks_per_beat={mid.ticks_per_beat}\n")
        f.write(f"track_count={len(mid.tracks)}\n\n")
        
        # 处理音轨
        for track_idx, track in enumerate(mid.tracks):
            f.write(f"[TRACK {track_idx}]\n")
            abs_time = 0
            
            for msg in track:
                abs_time += msg.time
                prefix = "META" if msg.is_meta else "MSG"
                msg_data = serialize_message(msg)
                
                f.write(f"{prefix}|{abs_time}|{msg.type}|{msg_data}\n")
            
            f.write("\n")

if __name__ == "__main__":
    export_midi('input.mid', 'midi_content.txt')