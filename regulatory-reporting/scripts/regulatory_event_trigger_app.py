#!/usr/bin/env python3
import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
import requests

HTML = """<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Regulatory Reporting Tracker</title>
<style>body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:2rem;}
.card{max-width:720px;padding:1.25rem 1.5rem;border:1px solid #e5e7eb;border-radius:14px;box-shadow:0 1px 2px rgba(0,0,0,.03);}
.row{display:flex;gap:1rem;flex-wrap:wrap;}label{display:block;font-weight:600;margin-bottom:.25rem;}
input,select{width:100%;padding:.6rem .8rem;border:1px solid #d1d5db;border-radius:10px;}
button{padding:.7rem 1.1rem;border-radius:10px;border:0;background:#111827;color:white;font-weight:600;cursor:pointer;}
button:disabled{opacity:.55;cursor:not-allowed;}
.muted{color:#6b7280;font-size:.9rem;}.success{background:#ecfdf5;color:#065f46;padding:.6rem .8rem;border-radius:10px;}
.error{background:#fef2f2;color:#991b1b;padding:.6rem .8rem;border-radius:10px;}
.kv{display:grid;grid-template-columns:200px 1fr;gap:.5rem 1rem;margin-top:1rem;}.kv div{padding:.25rem 0;}
</style></head><body>
<div class='card'><h2>📤 Regulatory Reporting – Event Trigger</h2>
<p class='muted'>Order the Control-M workflow on demand (e.g., ad-hoc regulator requests). Ensure your environment variables are set (below).</p>
<form id='form'><div class='row'><div style='flex:1 1 240px'>
<label for='regulator'>Regulator</label><input id='regulator' name='regulator' placeholder='GENERIC / SEC / EBA'/></div>
<div style='flex:1 1 160px'><label for='region'>Region</label><input id='region' name='region' placeholder='NA / EU / APAC'/></div></div>
<div class='row' style='margin-top:1rem'><button type='submit'>Order Workflow</button></div></form>
<div id='msg' style='margin-top:1rem'></div><h3 style='margin-top:2rem'>Environment</h3>
<div class='kv muted'><div>CTM_AAPI_ENDPOINT</div><div>{{endpoint}}</div>
<div>CTM_AUTH_TOKEN</div><div>{{token_masked}}</div>
<div>CTM_SERVER</div><div>{{server}}</div>
<div>CTM_FOLDER</div><div>{{folder}}</div></div></div>
<script>
const form=document.getElementById('form');
form.addEventListener('submit',async(e)=>{e.preventDefault();
const regulator=document.getElementById('regulator').value||'GENERIC';
const region=document.getElementById('region').value||'NA';
const res=await fetch('/order',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({regulator,region})});
const data=await res.json();const msg=document.getElementById('msg');
if(res.ok){msg.innerHTML=`<div class='success'>Ordered ✔️<br><div class='muted'>Run Info:</div><pre>${JSON.stringify(data,null,2)}</pre></div>`;}
else{msg.innerHTML=`<div class='error'>Failed ❌<br><div class='muted'>${data.error||'Unknown error'}</div></div>`;}});
</script></body></html>"""

def mask_token(tok: str, visible: int = 6) -> str:
    if not tok:
        return "(unset)"
    if len(tok) <= visible:
        return "*" * len(tok)
    return tok[:visible] + "…" + "*" * (len(tok) - visible)

def make_app():
    app = Flask(__name__)
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    @app.get('/')
    def index():
        endpoint = os.getenv('CTM_AAPI_ENDPOINT', '')
        token = os.getenv('CTM_AUTH_TOKEN', '')
        server = os.getenv('CTM_SERVER', 'IN01')
        folder = os.getenv('CTM_FOLDER', 'Regulatory_Reporting_Workflow')
        return render_template_string(HTML,
                                     endpoint=endpoint or '(unset)',
                                     token_masked=mask_token(token),
                                     server=server,
                                     folder=folder)

    @app.post('/order')
    def order():
        endpoint = os.getenv('CTM_AAPI_ENDPOINT')
        token = os.getenv('CTM_AUTH_TOKEN')
        server = os.getenv('CTM_SERVER', 'IN01')
        folder = os.getenv('CTM_FOLDER', 'Regulatory_Reporting_Workflow')
        if not endpoint or not token:
            return jsonify({'error': 'CTM_AAPI_ENDPOINT and CTM_AUTH_TOKEN must be set'}), 400
        payload = {'folders': [{'folder': folder, 'variables': {
            'regulator': (request.json or {}).get('regulator', 'GENERIC'),
            'region': (request.json or {}).get('region', 'NA')}}]}
        url = f"{endpoint.rstrip('/')}/run/order"
        headers = {'Content-Type': 'application/json', 'x-api-key': token}
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            ok = resp.status_code in (200,201,202)
            try: data = resp.json()
            except Exception: data = {'text': resp.text}
            if not ok:
                return jsonify({'error':'Order failed','status':resp.status_code,'response':data}), 502
            return jsonify({'ordered_at':'now','server':server,'folder':folder,'payload':payload,'api_response':data}), 200
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Request to AAPI failed: {e}'}), 502

    return app

if __name__ == '__main__':
    port = int(os.getenv('PORT','8080'))
    app = make_app()
    app.run(host='0.0.0.0', port=port, debug=False)
