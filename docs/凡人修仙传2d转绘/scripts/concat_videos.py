#!/usr/bin/env python3
"""Concatenate already-QC-passed segment videos in numeric order."""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path


def probe(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)], check=True, capture_output=True, text=True, encoding='utf-8')
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-root', required=True, type=Path)
    parser.add_argument('--pattern', default='{name}/{name}_style_2d_H3_768p_原声音轨_v1.mp4')
    parser.add_argument('--start', type=int, default=1)
    parser.add_argument('--end', type=int, required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    files = []
    for index in range(args.start, args.end + 1):
        name = f'Merge-{index:03d}'
        path = args.input_root / args.pattern.format(index=index, name=name)
        if not path.exists():
            raise FileNotFoundError(path)
        files.append(path)
    first = probe(files[0])
    first_v = next(s for s in first['streams'] if s['codec_type'] == 'video')
    first_a = next(s for s in first['streams'] if s['codec_type'] == 'audio')
    total = 0.0
    for path in files:
        info = probe(path)
        video = next(s for s in info['streams'] if s['codec_type'] == 'video')
        audio = next(s for s in info['streams'] if s['codec_type'] == 'audio')
        if (video.get('codec_name'), video.get('width'), video.get('height'), video.get('r_frame_rate'), audio.get('codec_name'), audio.get('sample_rate'), audio.get('channels')) != (first_v.get('codec_name'), first_v.get('width'), first_v.get('height'), first_v.get('r_frame_rate'), first_a.get('codec_name'), first_a.get('sample_rate'), first_a.get('channels')):
            raise RuntimeError(f'inconsistent streams: {path}')
        total += float(info['format']['duration'])
    if args.output.exists() and not args.overwrite:
        raise SystemExit(f'output exists; pass --overwrite: {args.output}')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.ffconcat', delete=False) as f:
        list_path = Path(f.name)
        for path in files:
            f.write("file '" + str(path).replace("'", "'\\''") + "'\n")
    try:
        subprocess.run(['ffmpeg', '-hide_banner', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(list_path), '-map', '0:v:0', '-map', '0:a:0', '-c', 'copy', '-movflags', '+faststart', str(args.output)], check=True)
    finally:
        list_path.unlink(missing_ok=True)
    final = probe(args.output)
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(args.output), '-f', 'null', '-'], check=True)
    print(json.dumps({'segments': len(files), 'output': str(args.output), 'expected_duration_seconds': round(total, 3), 'final_duration_seconds': round(float(final['format']['duration']), 3), 'video': {'width': first_v.get('width'), 'height': first_v.get('height'), 'fps': first_v.get('r_frame_rate')}, 'audio': {'codec': first_a.get('codec_name'), 'sample_rate': first_a.get('sample_rate'), 'channels': first_a.get('channels')}}, ensure_ascii=False))


if __name__ == '__main__':
    main()
