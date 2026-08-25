#!/usr/bin/env python3
"""Submit one ComfyUI API workflow and wait for completion."""
import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request_json(url, method='GET', payload=None):
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode('utf-8')
    request = Request(url, data=body, method=method, headers={'Content-Type': 'application/json'} if body else {})
    with urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode('utf-8'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workflow', required=True, type=Path)
    parser.add_argument('--segment', required=True)
    parser.add_argument('--log', required=True, type=Path)
    parser.add_argument('--host', default=os.environ.get('COMFY_HOST', 'http://127.0.0.1:8188'))
    parser.add_argument('--poll-seconds', type=float, default=5)
    parser.add_argument('--timeout-seconds', type=float, default=1800)
    args = parser.parse_args()

    workflow = json.loads(args.workflow.read_text(encoding='utf-8-sig'))
    client_id = f'fanren-2d-{args.segment}'
    try:
        result = request_json(args.host.rstrip('/') + '/prompt', 'POST', {'prompt': workflow, 'client_id': client_id})
    except (HTTPError, URLError) as exc:
        raise SystemExit(f'ComfyUI submission failed: {exc}')
    if result.get('node_errors'):
        raise SystemExit(json.dumps({'segment': args.segment, 'node_errors': result['node_errors']}, ensure_ascii=False))

    prompt_id = result.get('prompt_id')
    if not prompt_id:
        raise SystemExit(f'No prompt_id returned: {result}')
    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.log.write_text(prompt_id + '\n', encoding='utf-8')
    print(json.dumps({'submitted': True, 'segment': args.segment, 'prompt_id': prompt_id}, ensure_ascii=False), flush=True)

    started = time.time()
    while True:
        if time.time() - started > args.timeout_seconds:
            raise SystemExit(f'timeout waiting for {prompt_id}')
        try:
            history = request_json(args.host.rstrip('/') + '/history/' + prompt_id)
        except (HTTPError, URLError) as exc:
            print(json.dumps({'warning': str(exc)}, ensure_ascii=False), flush=True)
            time.sleep(args.poll_seconds)
            continue
        entry = history.get(prompt_id)
        if entry:
            status = entry.get('status', {})
            status_str = status.get('status_str')
            if status.get('completed') or status_str in ('success', 'error'):
                outputs = []
                for node_id, node_output in entry.get('outputs', {}).items():
                    for kind, values in node_output.items():
                        if isinstance(values, list):
                            for value in values:
                                if isinstance(value, dict) and ('filename' in value or 'subfolder' in value):
                                    outputs.append({'node': node_id, 'kind': kind, **value})
                payload = {
                    'completed': bool(status.get('completed')),
                    'status': status_str,
                    'outputs': outputs,
                    'elapsed_seconds': round(time.time() - started, 1),
                }
                print(json.dumps(payload, ensure_ascii=False), flush=True)
                if status_str == 'error' or not status.get('completed'):
                    print(json.dumps({'messages': status.get('messages', [])}, ensure_ascii=False), flush=True)
                    return 2
                return 0
        elapsed = int(time.time() - started)
        if elapsed % 30 < int(args.poll_seconds):
            print(json.dumps({'waiting_seconds': elapsed, 'segment': args.segment}, ensure_ascii=False), flush=True)
        time.sleep(args.poll_seconds)


if __name__ == '__main__':
    sys.exit(main())
