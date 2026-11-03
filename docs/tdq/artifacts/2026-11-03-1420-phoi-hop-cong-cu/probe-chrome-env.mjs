import { ChromeVisualBrowser } from 'file:///C:/Users/admin/Documents/archify/archify/bin/visual-check.mjs';
const browser = new ChromeVisualBrowser('C:/Program Files/Google/Chrome/Application/chrome.exe', {startupTimeoutMs:5000});
try { await browser.sessionPromise; console.log(JSON.stringify({ready:true})); }
catch(error) { console.log(JSON.stringify({ready:false,error:String(error)})); process.exitCode=1; }
finally { await browser.close(); }
