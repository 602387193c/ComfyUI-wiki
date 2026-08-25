#!/usr/bin/env python3
"""Build a generic 768p H3 Ref2VA prompt and inject it into an API workflow."""
import argparse
import json
import re
import shutil
from pathlib import Path

SHOT_RE = re.compile(r'\[Shot\s+(\d+)\]', re.I)
TIME_RE = re.compile(r'At\s+(\d{2}):(\d{2}\.\d{3})', re.I)


def hms(seconds):
    milliseconds = int(round(seconds * 1000))
    return f'{milliseconds // 60000:02d}:{(milliseconds % 60000) / 1000:06.3f}'


def probe(path):
    import subprocess
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-of', 'json', str(path)], check=True, capture_output=True, text=True, encoding='utf-8')
    return json.loads(result.stdout)


def starts_for(text, duration):
    marks = list(SHOT_RE.finditer(text))
    starts = []
    for index, mark in enumerate(marks):
        segment = text[mark.start():marks[index + 1].start() if index + 1 < len(marks) else len(text)]
        hits = TIME_RE.findall(segment)
        starts.append(0.0 if index == 0 else (int(hits[0][0]) * 60 + float(hits[0][1]) if hits else duration * index / max(1, len(marks))))
    return starts


def clean_segment(segment):
    segment = re.sub(r'3D CG animated,?\s*|cinematic,?\s*|Chinese xianxia fantasy style,?\s*', '', segment, flags=re.I)
    segment = re.sub(r'\bthe on-screen text\b[^.;]*[.;]?', 'an empty lower field with no writing. ', segment, flags=re.I)
    segment = re.sub(r'\b(?:a\s+)?(?:tall\s+vertical\s+)?(?:banner|calligraphy banner)[^.;]*[.;]?', 'a plain graphic shape with no writing. ', segment, flags=re.I)
    def dialogue(match):
        content = match.group(1).strip()
        return f'<d>spoken dialogue timing only; never render text; original dialogue: {content}</d>'
    segment = re.sub(r'<d>(.*?)</d>', dialogue, segment, flags=re.I | re.S)
    return segment.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', required=True, type=Path)
    parser.add_argument('--segment', required=True)
    parser.add_argument('--source-video', required=True, type=Path)
    parser.add_argument('--description', type=Path)
    parser.add_argument('--storyboard', required=True, type=Path)
    parser.add_argument('--base-workflow', required=True, type=Path)
    parser.add_argument('--comfy-input', required=True, type=Path)
    parser.add_argument('--output-workflow', type=Path)
    parser.add_argument('--output-prompt', type=Path)
    parser.add_argument('--style-lock', type=Path)
    parser.add_argument('--style-tag', default='style_2d')
    parser.add_argument('--width', type=int, default=1376)
    parser.add_argument('--height', type=int, default=768)
    parser.add_argument('--fps', type=int, default=24)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--image-node', default='101')
    parser.add_argument('--prompt-node', default='110')
    parser.add_argument('--seed-node', default='120')
    parser.add_argument('--output-node', default='133')
    args = parser.parse_args()
    desc_path = args.description or args.project_root / args.segment / f'{args.segment}.txt'
    folder = args.project_root / args.segment
    style_lock_path = args.style_lock or args.project_root / 'style_lock.md'
    style_lock = style_lock_path.read_text(encoding='utf-8-sig') if style_lock_path.exists() else 'Apply the user-approved style specification for this project. Do not invent a replacement style.'
    duration = float(probe(args.source_video)['format']['duration'])
    text = desc_path.read_text(encoding='utf-8-sig')
    marks = list(SHOT_RE.finditer(text))
    starts = starts_for(text, duration)
    shots = []
    for index, mark in enumerate(marks):
        end = marks[index + 1].start() if index + 1 < len(marks) else text.find('\n\noverall_soundscape:')
        end = len(text) if end < 0 else end
        start = starts[index] if index < len(starts) else duration * index / max(1, len(marks))
        finish = starts[index + 1] if index + 1 < len(starts) else duration
        shots.append(f'[Shot {index + 1}] From {hms(start)} to {hms(finish)}, {clean_segment(text[mark.end():end])}')
    sound = text.split('\n\noverall_soundscape:', 1)[1].split('\n\nnon_diegetic_music:', 1)[0].strip() if '\n\noverall_soundscape:' in text else 'Use the source audio only as timing guidance.'
    music = text.split('\n\nnon_diegetic_music:', 1)[1].strip() if '\n\nnon_diegetic_music:' in text else 'Use the source audio only as timing guidance.'
    prompt = '\n'.join([
        'subject_definitions:',
        f'<Picture 1> is the single user-approved style-locked storyboard reference for {args.segment}. It defines the exact shot order, camera scales, character placement, gestures, props, and visual language.',
        f'<Subject 1> is the original adult cast, costumes, props, environments, and whole-video 2D language shown in <Picture 1>; preserve identity, silhouette, gaze and spatial relationships. The locked style specification is:\n{style_lock}',
        '', 'summary:',
        f'[reference generation] Generate one continuous original sequence for {args.segment}, matching the complete source duration of {duration:.3f} seconds. Preserve all {len(shots)} shots, their order, timing, actions and major subjects. Animate continuously, not as a slideshow.',
        '', 'retention_analysis:',
        '<Picture 1> (shot order, composition, character placement, gestures, props, and locked visual rhythm): fully_preserved.',
        '<Subject 1> (original characters and hand-drawn theatrical 2D language): fully_preserved.',
        'Storyboard borders, panel numbers, labels and layout: removed from the final video.',
        '', 'detailed_description:',
        f'ABSOLUTE VISUAL RULE: render zero written characters of any kind. Dialogue is audio timing guidance only; never draw subtitles, captions, Chinese characters, speech bubbles, labels, watermark, logo or UI text. Apply the locked style specification exactly:\n{style_lock}\nKeep every frame readable without accidental clipping or muddy exposure. No unintended dense detail, glossy CGI, photorealism, or accidental fade to black.',
        *shots, '', 'overall_soundscape:',
        f'Use only as timing guidance; discard all H3-generated sound and replace it with the original source audio. {sound}',
        '', 'non_diegetic_music:',
        f'Use only as timing guidance; discard all H3-generated sound and replace it with the original source audio. {music}',
    ])
    prompt_path = args.output_prompt or folder / f'{args.segment}_H3_Ref2VA_prompt_768p_v1.txt'
    workflow_path = args.output_workflow or folder / 'storyboard_process' / '05_workflow' / f'{args.segment}_H3_Ref2VA_768p_api.json'
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding='utf-8')
    comfy_rel = Path('fanren_2d_768p') / args.segment / 'storyboard.png'
    comfy_target = args.comfy_input / comfy_rel
    comfy_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.storyboard, comfy_target)
    workflow = json.loads(args.base_workflow.read_text(encoding='utf-8-sig'))
    for node in (args.image_node, args.prompt_node, args.seed_node, args.output_node):
        if node not in workflow:
            raise KeyError(f'workflow node not found: {node}')
    workflow[args.image_node]['inputs']['image'] = str(comfy_rel).replace('\\', '/')
    workflow[args.prompt_node]['inputs']['prompt'] = prompt
    workflow[args.prompt_node]['inputs']['width'] = args.width
    workflow[args.prompt_node]['inputs']['height'] = args.height
    workflow[args.prompt_node]['inputs']['length'] = round(duration * args.fps) + 2
    workflow[args.seed_node]['inputs']['noise_seed'] = args.seed
    workflow[args.output_node]['inputs']['filename_prefix'] = f'video/{args.style_tag}_{args.width}x{args.height}/{args.segment}/{args.segment}_H3'
    workflow_path.write_text(json.dumps(workflow, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'segment': args.segment, 'duration': duration, 'shots': len(shots), 'length': round(duration * args.fps) + 2, 'prompt': str(prompt_path), 'workflow': str(workflow_path), 'reference_in_comfy_input': str(comfy_target)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
