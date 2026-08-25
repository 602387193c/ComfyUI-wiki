#!/usr/bin/env python3
"""Replace H3 audio with source audio, align duration, and create a QC grid."""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


def run(command, capture=False):
    return subprocess.run(command, check=True, text=True, capture_output=capture, encoding='utf-8')


def probe(path):
    result = run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)], True)
    return json.loads(result.stdout)


def stream(info, kind):
    return next(item for item in info['streams'] if item.get('codec_type') == kind)


def pcm_sha256(path):
    result = subprocess.run(
        ['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0', '-f', 's16le', '-acodec', 'pcm_s16le', '-ac', '2', '-ar', '48000', 'pipe:1'],
        check=True, stdout=subprocess.PIPE,
    )
    return hashlib.sha256(result.stdout).hexdigest().upper()


def make_grid(video, output, width=1600, height=1200):
    info = probe(video)
    video_stream = stream(info, 'video')
    total = int(video_stream.get('nb_frames') or round(float(info['format']['duration']) * 24))
    total = max(12, total)
    indices = [round(i * (total - 1) / 11) for i in range(12)]
    select = '+'.join(f'eq(n,{index})' for index in indices)
    cell_w, cell_h = width // 4, height // 3
    vf = f"select='{select}',scale={cell_w}:{cell_h}:force_original_aspect_ratio=increase,crop={cell_w}:{cell_h},tile=4x3"
    run(['ffmpeg', '-y', '-v', 'error', '-i', str(video), '-vf', vf, '-frames:v', '1', str(output)])
    return indices


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--segment', required=True)
    parser.add_argument('--ai-video', required=True, type=Path)
    parser.add_argument('--source-video', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--qc-grid', type=Path)
    parser.add_argument('--technical-log', type=Path)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()

    if args.output.exists() and not args.overwrite:
        raise SystemExit(f'output exists; pass --overwrite to replace: {args.output}')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    source_info = probe(args.source_video)
    ai_info = probe(args.ai_video)
    source_duration = float(source_info['format']['duration'])
    ai_duration = float(ai_info['format']['duration'])
    ratio = source_duration / ai_duration
    run([
        'ffmpeg', '-y', '-v', 'error', '-i', str(args.ai_video), '-i', str(args.source_video),
        '-filter_complex', f'[0:v]setpts={ratio:.12f}*PTS[v]',
        '-map', '[v]', '-map', '1:a:0', '-map_metadata', '-1', '-map_chapters', '-1',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-c:a', 'copy', '-movflags', '+faststart', str(args.output),
    ])

    final_info = probe(args.output)
    final_video = stream(final_info, 'video')
    final_audio = stream(final_info, 'audio')
    source_hash = pcm_sha256(args.source_video)
    final_hash = pcm_sha256(args.output)
    qc_grid = args.qc_grid or args.output.with_name(args.output.stem.replace('_原声音轨', '') + '_QC_12f.jpg')
    indices = make_grid(args.output, qc_grid)
    payload = {
        'segment': args.segment,
        'source_video': str(args.source_video),
        'ai_video': str(args.ai_video),
        'final_video': str(args.output),
        'source_duration': source_duration,
        'ai_duration': ai_duration,
        'final_duration': float(final_info['format']['duration']),
        'video_ratio': ratio,
        'width': final_video.get('width'),
        'height': final_video.get('height'),
        'fps': final_video.get('r_frame_rate'),
        'audio_codec': final_audio.get('codec_name'),
        'audio_sample_rate': final_audio.get('sample_rate'),
        'audio_channels': final_audio.get('channels'),
        'source_pcm_sha256': source_hash,
        'final_pcm_sha256': final_hash,
        'audio_match': source_hash == final_hash,
        'decode_pass': True,
        'qc_grid': str(qc_grid),
        'qc_indices': indices,
    }
    log = args.technical_log or args.output.with_name('technical_qc_768p.json')
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == '__main__':
    main()
