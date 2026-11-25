"""Round 15: one real session with the merged finder (the one-line list always printed). Same command and request as round 13's run B31. usage: live15.py"""
import json, os, re, shutil, subprocess, sys, time
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(H))
sys.path.insert(0, os.environ.get('SKILLSELECT_LAB') or os.path.join(os.path.dirname(H), 'harness')); import lab
SB = os.environ['SANDBOX50']; ASK = '/skillselect build a landing page for my product'; START = float(open(H + '/start.txt').read())
lab.guard()
if lab.spent() - START > 5.3: lab.stop('round 15 cap')
cmd = [lab.CL, '-p', ASK, '--plugin-dir', ROOT, '--model', 'opus', '--setting-sources', 'project', '--max-turns', '20', '--no-session-persistence', '--strict-mcp-config', '--mcp-config', lab.L + '/nomcp.json',
       '--output-format', 'stream-json', '--verbose', '--disallowedTools', 'Write', 'Edit', 'NotebookEdit', 'Agent', 'Task', 'Artifact', '--allowedTools', 'Skill', 'Bash(python3:*)', 'Read']
env = dict(os.environ, SKILL_FINDER_ONLY=SB, SKILL_FINDER_CACHE=H + '/cache-live', SKILLSELECT_CONFIG=H + '/live-settings.json'); shutil.rmtree(env['SKILL_FINDER_CACHE'], ignore_errors=True)
t0 = time.time(); p = subprocess.Popen(cmd, cwd=os.path.dirname(os.path.dirname(SB)), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, text=True, env=env); res = None; steps = 0; saw_list = False
for line in p.stdout:
    try: d = json.loads(line)
    except ValueError: continue
    if 'EVERY OTHER INSTALLED SKILL' in line: saw_list = True
    if d.get('type') == 'assistant': steps += sum(1 for c in (d.get('message') or {}).get('content') or [] if c.get('type') == 'tool_use')
    if d.get('type') == 'result': res = d
p.wait()
if not res: lab.stop('r15 live: no result')
models = list((res.get('modelUsage') or {}).keys())
if not any('opus' in m for m in models): lab.stop(f'r15 live: no Opus in {models}')
u = res.get('usage') or {}; tok = u.get('input_tokens', 0) + u.get('cache_creation_input_tokens', 0) + u.get('cache_read_input_tokens', 0) + u.get('output_tokens', 0)
lab.log(dict(kind='v15_live', meta={}, models=models, cost=res.get('total_cost_usd', 0), sec=round(time.time() - t0, 1), tok_in=tok - u.get('output_tokens', 0), tok_out=u.get('output_tokens', 0)))
text = re.sub(r'/(?:Users|private|tmp)/\S+', '<path>', res.get('result') or '')
row = dict(sec=round(time.time() - t0, 1), tokens=tok, tool_calls=steps, cost=round(res.get('total_cost_usd', 0), 3), list_reached_the_session=saw_list, found_by_reading=text.count('found by reading'), answer=text)
json.dump(row, open(H + '/live15.json', 'w'), indent=1, ensure_ascii=False); print({k: v for k, v in row.items() if k != 'answer'}); print(text[:1800])
