"""Round 10: SkillSelect 3.0.0, the short command and categorize, in the round-6 test folder."""
import json, os, subprocess, sys, time
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(H)); import lab
SB = '/tmp/skillselect-round6'  # the round-6 test folder; PLUG = os.path.expanduser('~/skillselect')
ASKS = dict(Bb='/skillselect build a landing page for my product', Bc='/skillselect build a landing page for my product', B='/skillselect build a landing page for my product', B2='/skillselect:skillselect build a landing page for my product', K='/skillselect categorize')
START = float(open(H + '/start.txt').read()) if os.path.exists(H + '/start.txt') else lab.spent(); open(H + '/start.txt', 'w').write(str(START))
def run(key):
    out = f'{H}/raw/{key}.jsonl'
    lab.guard()
    if lab.spent() - START > 2: lab.stop('round-10 cap reached')
    cmd = [lab.CL, '-p', ASKS[key], '--plugin-dir', PLUG, '--model', 'opus', '--setting-sources', 'project', '--max-turns', '20', '--no-session-persistence', '--strict-mcp-config', '--mcp-config', lab.L + '/nomcp.json',
           '--output-format', 'stream-json', '--verbose', '--disallowedTools', 'Write', 'Edit', 'NotebookEdit', 'Agent', 'Task', 'Artifact', '--allowedTools', 'Skill', 'Bash(python3:*)', 'Read']
    env = dict(os.environ, SKILL_FINDER_ONLY=SB + '/proj/.claude/skills', SKILL_FINDER_CACHE=f'{H}/cache-{key}')
    t0 = time.time(); p = subprocess.Popen(cmd, cwd=SB + '/proj', stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, text=True, env=env); res = None
    with open(out, 'w') as f:
        for line in p.stdout:
            line = line.strip()
            if not line: continue
            try: d = json.loads(line)
            except ValueError: continue
            f.write(json.dumps({'t': round(time.time() - t0, 2), 'e': d}, ensure_ascii=False) + '\n')
            if d.get('type') == 'result': res = d
    p.wait()
    if not res: lab.stop(f'r10 {key}: no result')
    models = list((res.get('modelUsage') or {}).keys())
    if not any('opus' in m for m in models): 
        print(key, 'no Opus in', models, '|', (res.get('result') or '')[:200]); return res
    u = res.get('usage') or {}
    lab.log(dict(kind='v10_run', meta={'run': key}, models=models, cost=res.get('total_cost_usd', 0), sec=round(time.time() - t0, 1), tok_in=u.get('input_tokens', 0) + u.get('cache_creation_input_tokens', 0) + u.get('cache_read_input_tokens', 0), tok_out=u.get('output_tokens', 0)))
    print(key, 'done', round(time.time() - t0), 's $%.2f' % res.get('total_cost_usd', 0), 'turns', res.get('num_turns'), models, flush=True)
    return res
try:
    for k in sys.argv[1:]:
        r = run(k); print((r.get('result') or '')[:1800]); print('-----')
except lab.Stop as e: print('STOPPED:', e)
print('round-10 spend $%.2f' % (lab.spent() - START), 'STOP' if lab.stopped() else 'no STOP')
