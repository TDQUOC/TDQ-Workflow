"""Actual Chrome direct-CDP capture in a disposable browser context."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import time
from urllib.request import urlopen

import websocket

ROOT = Path(__file__).resolve().parents[5]
EVIDENCE = Path(__file__).resolve().parents[1]
FOLDER = Path(__file__).resolve().parent


def binding(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class CDP:
    def __init__(self):
        version = json.loads(urlopen("http://127.0.0.1:9222/json/version", timeout=5).read())
        self.socket = websocket.create_connection(version["webSocketDebuggerUrl"], timeout=10, suppress_origin=True)
        self.serial = 0
        self.events = []

    def call(self, method, params=None, session=None):
        self.serial += 1
        message = {"id": self.serial, "method": method, "params": params or {}}
        if session:
            message["sessionId"] = session
        self.socket.send(json.dumps(message))
        while True:
            reply = json.loads(self.socket.recv())
            if reply.get("id") == self.serial:
                if "error" in reply:
                    raise RuntimeError(reply["error"])
                return reply.get("result", {})
            self.events.append(reply)

    def evaluate(self, expression, session):
        result = self.call("Runtime.evaluate", {"expression": expression, "returnByValue": True,
                                               "awaitPromise": True}, session)
        if "exceptionDetails" in result:
            raise RuntimeError(result["exceptionDetails"])
        return result["result"].get("value")


DOM = r'''(() => {
const box=e=>{const r=e.getBoundingClientRect();return {width:r.width,height:r.height}};
return {url:location.href,title:document.title,lang:document.documentElement.lang,
 viewport:{width:innerWidth,height:innerHeight},scroll_width:document.documentElement.scrollWidth,
 client_width:document.documentElement.clientWidth,
 regions:[...document.querySelectorAll('main,header,nav,section')].map(e=>({tag:e.tagName,id:e.id,...box(e)})),
 headings:[...document.querySelectorAll('h1,h2,h3')].map(e=>({level:e.tagName,text:e.textContent})),
 links:[...document.querySelectorAll('a')].map(e=>({text:e.textContent,href:e.getAttribute('href'),...box(e)})),
 tables:[...document.querySelectorAll('table')].map(e=>({rows:e.tBodies[0]?.rows.length||0,headers:[...e.querySelectorAll('th')].map(t=>({text:t.textContent,scope:t.scope})),...box(e),parent_width:e.parentElement.clientWidth,parent_scroll_width:e.parentElement.scrollWidth,overflow:getComputedStyle(e.parentElement).overflowX})),
 assets:[...document.querySelectorAll('script[src],link[href],img[src]')].map(e=>e.src||e.href),
 forms:document.forms.length,body_font:getComputedStyle(document.body).fontSize,
 body_color:getComputedStyle(document.body).color,body_background:getComputedStyle(document.body).backgroundColor,
 text_length:document.body.innerText.length};})()'''


def capture(role, html):
    cdp = CDP()
    context = cdp.call("Target.createBrowserContext", {"disposeOnDetach": False})["browserContextId"]
    html_sha = binding(html)["sha256"]
    browser = {"html_sha256": html_sha, "tool": "Python websocket-client direct CDP 9222 (MCP transport closed)",
               "session_id": context, "views": []}
    try:
        for name, width, height in (("desktop", 1440, 900), ("mobile", 375, 812)):
            target = cdp.call("Target.createTarget", {"url": "about:blank", "browserContextId": context})["targetId"]
            session = cdp.call("Target.attachToTarget", {"targetId": target, "flatten": True})["sessionId"]
            for domain in ("Page", "Runtime", "Network", "Log", "Accessibility"):
                cdp.call(domain + ".enable", session=session)
            cdp.call("Emulation.setDeviceMetricsOverride", {"width": width, "height": height,
                     "deviceScaleFactor": 1, "mobile": name == "mobile"}, session)
            start = len(cdp.events)
            cdp.call("Page.navigate", {"url": html.as_uri()}, session)
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if cdp.evaluate("document.readyState", session) == "complete":
                    break
                time.sleep(.05)
            cdp.evaluate("document.fonts.ready.then(()=>true)", session)
            observation = cdp.evaluate(DOM, session)
            observation["html_sha256"] = html_sha
            ax = cdp.call("Accessibility.getFullAXTree", session=session)
            write(FOLDER / f"{role}-{name}-accessibility.json", ax)
            interactions = cdp.evaluate('''(() => {
const result={anchors:[],table_scroll:[]};
for(const a of document.querySelectorAll('nav a[href^="#"]')){
 a.focus();const s=getComputedStyle(a);const focused=document.activeElement===a;
 a.click();const id=decodeURIComponent(a.hash.slice(1));
 result.anchors.push({href:a.getAttribute('href'),focused,outline:s.outline,target_exists:!!document.getElementById(id),hash:location.hash});}
for(const e of document.querySelectorAll('div')){
 const s=getComputedStyle(e);if(['auto','scroll'].includes(s.overflowX)&&e.scrollWidth>e.clientWidth){
  e.scrollLeft=0;const before=e.scrollLeft;e.scrollLeft=e.scrollWidth;
  result.table_scroll.push({before,after:e.scrollLeft,client_width:e.clientWidth,scroll_width:e.scrollWidth});e.scrollLeft=0;}}
history.replaceState(null,'',location.pathname);document.activeElement?.blur();scrollTo(0,0);return result;})()''', session)
            observation["interactions"] = interactions
            cdp.evaluate("document.querySelector('nav a')?.focus()", session)
            cdp.call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Tab", "code": "Tab", "windowsVirtualKeyCode": 9}, session)
            cdp.call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Tab", "code": "Tab", "windowsVirtualKeyCode": 9}, session)
            observation["keyboard_focus"] = cdp.evaluate("({tag:document.activeElement.tagName,text:document.activeElement.textContent,outline:getComputedStyle(document.activeElement).outline})", session)
            first = cdp.evaluate("(() => {const a=document.querySelector('nav a');if(!a)return null;const r=a.getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2}})()", session)
            if first:
                cdp.call("Input.dispatchMouseEvent", {"type": "mouseMoved", **first}, session)
                observation["hover"] = cdp.evaluate("({text:document.querySelector('nav a').textContent,color:getComputedStyle(document.querySelector('nav a')).color})", session)
            cdp.evaluate("document.activeElement?.blur();scrollTo(0,0)", session)
            shot = FOLDER / f"{role}-{name}.png"
            image = cdp.call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False}, session)
            shot.write_bytes(base64.b64decode(image["data"]))
            layout = cdp.call("Page.getLayoutMetrics", session=session)["cssContentSize"]
            full = cdp.call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True,
                "clip": {"x": 0, "y": 0, "width": width, "height": layout["height"], "scale": 1}}, session)
            (FOLDER / f"{role}-{name}-full.png").write_bytes(base64.b64decode(full["data"]))
            events = [event for event in cdp.events[start:] if event.get("sessionId") == session]
            errors = [event for event in events if event.get("method") == "Runtime.exceptionThrown" or
                      (event.get("method") == "Runtime.consoleAPICalled" and event.get("params", {}).get("type") == "error") or
                      (event.get("method") == "Log.entryAdded" and event.get("params", {}).get("entry", {}).get("level") == "error")]
            observation["console_errors"] = errors
            observation["network_failures"] = [event for event in events if event.get("method") == "Network.loadingFailed" or
                      (event.get("method") == "Network.responseReceived" and event["params"]["response"].get("status", 0) >= 400)]
            observation["network_responses"] = [{"url": event["params"]["response"]["url"], "status": event["params"]["response"]["status"]}
                      for event in events if event.get("method") == "Network.responseReceived"]
            observed = FOLDER / f"{role}-{name}.json"
            write(observed, observation)
            write(FOLDER / f"{role}-{name}-events.json", events)
            browser["views"].append({"name": name, "viewport": {"width": width, "height": height},
                                     "screenshot": binding(shot), "observation": binding(observed)})
            cdp.call("Target.closeTarget", {"targetId": target})
        output = EVIDENCE / ("slow-tests-browser.json" if role == "slow-tests" else "request-browser.json")
        write(output, browser)
        print(json.dumps(binding(output)))
    finally:
        cdp.call("Target.disposeBrowserContext", {"browserContextId": context})
        cdp.socket.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("role", choices=("slow-tests", "request"))
    args = parser.parse_args()
    capture(args.role, EVIDENCE / ("slow-tests.html" if args.role == "slow-tests" else "request-report.html"))
