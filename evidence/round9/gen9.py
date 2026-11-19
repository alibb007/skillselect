"""Round 9, step 1: the 36 requests, the split, and the words Claude would pass to the finder in each arm."""
import json, os, random, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(H), 'harness')); import lab
START = float(open(H + '/start.txt').read()) if os.path.exists(H + '/start.txt') else lab.spent(); open(H + '/start.txt', 'w').write(str(START))
HAS = ["a Word document", "a spreadsheet", "a slide presentation", "a PDF file", "a landing page for a product", "a site's ranking in search engines", "reviewing a code change before it is merged",
       "tracking down a bug", "automated tests for a web app", "putting a website online", "a résumé for one job ad", "invoices and receipts", "notes from recorded meetings", "an announcement to all staff",
       "privacy law for a product with European users", "a company's finances", "an animated GIF for a chat app", "generative art made with code", "making a blurry photo look better", "a name for a new product",
       "a long blog article", "words for an ad", "a connector that lets an AI assistant use a company tool", "a messy downloads folder"]
NOT = ["a mobile app", "a database schema", "a logo", "a podcast episode", "a 3D model for printing", "an email newsletter", "a Kubernetes cluster", "a small browser game", "translating a manual",
       "a travel plan", "a home budget app in Rust", "a wedding speech"]
if not os.path.exists(H + '/jobs.json'):
    fields = HAS + NOT
    t = lab.bare("You write realistic requests that people type to an AI coding assistant. Plain everyday language, like a busy person would type.",
                 "For each field below write one request a person might type: 1 or 2 sentences, in their own words, with one or two concrete details (a product, a number, an audience). "
                 "Do not mention skills, plugins or tools. Vary who is asking. Return only JSON: a list of objects {\"n\": <number>, \"request\": \"...\"}, one per field, same order.\n\n" +
                 "\n".join(f"{i + 1}. {f}" for i, f in enumerate(fields)), 'v9_jobs')
    js = lab.jparse(t); assert js and len(js) == 36, t[:300]
    ids = list(range(36)); random.Random(9).shuffle(ids); tune = set(ids[:12])
    jobs = [dict(id=f"J{i + 1:02d}", field=fields[i], has_skill_field=i < 24, set='tune' if i in tune else 'sealed', request=js[i]['request']) for i in range(36)]
    json.dump(jobs, open(H + '/jobs.json', 'w'), indent=1, ensure_ascii=False)
jobs = json.load(open(H + '/jobs.json'))
STEP_A = ("Put what the user wants into 3 to 5 topic words: the kind of thing they want, another common name for it, and the field or file type it belongs to (for \"turn my quarterly sales numbers into a slide deck\": "
          "`slide deck presentation pptx`; for \"write a blog post about our launch\": `blog post article writing`). Leave out their own details such as dates, amounts and names.")
STEP_B = ("Put what the user wants into 2 to 4 topic words that name the kind of thing or the kind of work they are asking for, in the order people say them, not what their own project is about "
          "(for \"turn my quarterly sales numbers into a slide deck\": `slide deck`; for \"review my pull request that changes our session cache\": `code review`; "
          "for \"connect our assistant to our ticket system\": `mcp server`). Then add up to 6 close words: other common names for that same kind of thing, and the file types or tools it usually means "
          "(`presentation pptx powerpoint slides`; `pull request pr diff`). No words about their particular problem, product or data.")
for arm, step, shape in (('A', STEP_A, '{"id": "J01", "topic": "..."}'), ('B', STEP_B, '{"id": "J01", "topic": "...", "also": "..."}')):
    if os.path.exists(H + f'/words{arm}.json'):
        continue
    t = lab.bare("You are a coding assistant following one step of a skill's instructions. Do exactly that step for each request.",
                 "The step:\n" + step + "\n\nDo it for each request below. Return only JSON: a list of " + shape + ".\n\n" + "\n".join(f"{j['id']}: {j['request']}" for j in jobs), f'v9_words{arm}')
    w = lab.jparse(t); assert w and len(w) == 36, t[:300]
    json.dump({x['id']: x for x in w}, open(H + f'/words{arm}.json', 'w'), indent=1, ensure_ascii=False)
A = json.load(open(H + '/wordsA.json')); B = json.load(open(H + '/wordsB.json'))
for j in jobs[:8]:
    print(j['id'], j['set'], '|', j['request'][:90], '| A:', A[j['id']]['topic'], '| B:', B[j['id']]['topic'], '+', B[j['id']]['also'])
print('tune', [j['id'] for j in jobs if j['set'] == 'tune'], 'spend $%.2f' % (lab.spent() - START))
