#!/usr/bin/env python3
"""Batch technical QC for final segment videos."""
import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path


def probe(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)], check=True, capture_output=True, text=True, encoding='utf-8')
    return json.loads(result.stdout)


def pcm_sha256(path):
    result = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0', '-f', 's16le', '-acodec', 'pcm_s16le', '-ac', '2', '-ar', '48000', 'pipe:1'], check=True, stdout=subprocess.PIPE)
    return hashlib.sha256(result.stdout).hexdigest().upper()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', required=True, type=Path)
    parser.add_argument('--start', type=int, default=1)
    parser.add_argument('--end', type=int, required=True)
    parser.add_argument('--final-template', default='{name}/{name}_style_2d_H3_768p_原声音轨_v1.mp4')
    parser.add_argument('--source-glob', default='{name}/{name}-*.mp4')
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--decode', action='store_true')
    args = parser.parse_args()
    out_dir = args.output_dir or args.project_root / '_qc_768p'
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for index in range(args.start, args.end + 1):
        name = f'Merge-{index:03d}'
        source_candidates = sorted(args.project_root.joinpath(args.source_glob.format(name=name)).parent.glob(Path(args.source_glob.format(name=name)).name))
        final = args.project_root / args.final_template.format(name=name)
        row = {'segment': name, 'final_video': str(final), 'status': 'qc_pass', 'error': ''}
        try:
            if len(source_candidates) != 1:
                raise RuntimeError(f'expected one source, found {len(source_candidates)}')
            if not final.exists():
                raise FileNotFoundError(final)
            source_info = probe(source_candidates[0])
            final_info = probe(final)
            source_video = next(s for s in source_info['streams'] if s['codec_type'] == 'video')
            final_video = next(s for s in final_info['streams'] if s['codec_type'] == 'video')
            final_audio = next(s for s in final_info['streams'] if s['codec_type'] == 'audio')
            if (final_video.get('width'), final_video.get('height')) != (1376, 768):
                raise RuntimeError('final dimensions are not 1376x768')
            if final_video.get('r_frame_rate') != '24/1':
                raise RuntimeError(f"unexpected fps: {final_video.get('r_frame_rate')}")
            if final_audio.get('sample_rate') != '48000' or final_audio.get('channels') != 2:
                raise RuntimeError('unexpected audio parameters')
            source_hash = pcm_sha256(source_candidates[0])
            final_hash = pcm_sha256(final)
            row.update({'source_duration': float(source_info['format']['duration']), 'final_duration': float(final_info['format']['duration']), 'audio_match': source_hash == final_hash, 'source_pcm_sha256': source_hash, 'final_pcm_sha256': final_hash})
            if source_hash != final_hash:
                raise RuntimeError('source/final PCM SHA256 mismatch')
            if args.decode:
                subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(final), '-f', 'null', '-'], check=True)
        except Exception as exc:
            row['status'] = 'failed'
            row['error'] = str(exc)
        rows.append(row)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_path = out_dir / f'batch_qc_{stamp}.json'
    csv_path = out_dir / f'batch_qc_{stamp}.csv'
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with csv_path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=sorted({key for row in rows for key in row}))
        writer.writeheader()
        writer.writerows(rows)
    passed = sum(row['status'] == 'qc_pass' for row in rows)
    print(json.dumps({'count': len(rows), 'pass_count': passed, 'failed': [row for row in rows if row['status'] != 'qc_pass'], 'json': str(json_path), 'csv': str(csv_path)}, ensure_ascii=False))
    raise SystemExit(0 if passed == len(rows) else 2)


if __name__ == '__main__':
    main()
