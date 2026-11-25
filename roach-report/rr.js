
(function(){
var WU=[],CLN=[],shownR='all',shownC='all',kind='both',page=0,PER=30;
var bs=document.querySelectorAll('.rr-chip'),ks=document.querySelectorAll('.rr-kind'),sel=document.getElementById('rr-county'),
cs=document.querySelectorAll('.rr-card'),out=document.getElementById('rr-showing'),wl=document.getElementById('wu-list'),
more=document.getElementById('wu-more'),secC=document.getElementById('sec-closed'),secW=document.getElementById('sec-written'),
emC=document.getElementById('empty-closed'),emW=document.getElementById('empty-written');
function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function match(county,region){return (shownC!=='all')?county===shownC:(shownR==='all'||region===shownR);}
function fmt(d){var x=new Date(d+'T12:00:00');return x.toLocaleDateString('en-US',{weekday:'short',month:'short',day:'numeric'});}
function cls(r){return r.indexOf('Admin')>=0?'rr-bad':(r.indexOf('Warning')>=0?'rr-warn':(r.indexOf('Fixed')>=0?'rr-ok':'rr-pending'));}
function wcard(w){var q=encodeURIComponent(w.name+' '+w.address+' '+w.city+' FL');
return '<article class="rr-card wu"><div class="rr-emoji" aria-hidden="true">⚠️</div><div class="rr-body"><h3>'+esc(w.name)+'</h3>'+
'<p class="meta"><a href="https://www.google.com/maps/search/?api=1&query='+q+'" rel="noopener" target="_blank">'+esc(w.address)+', '+esc(w.city)+'</a> · '+esc(w.county)+' County</p>'+
'<p class="rr-why"><strong>'+w.hp+' high-priority violation'+(w.hp===1?'':'s')+'</strong> ('+w.total+' total) · Inspected '+fmt(w.date)+'</p>'+
'<span class="'+cls(w.result)+'">'+esc(w.result)+'</span></div></article>';}
function render(push){
 var nc=0;cs.forEach(function(x){var s=match(x.dataset.county,x.dataset.region);x.style.display=s?'':'none';if(s)nc++;});
 var f=WU.filter(function(w){return match(w.county,w.region);});
 wl.innerHTML=f.slice(0,(page+1)*PER).map(wcard).join('');
 more.hidden=f.length<=(page+1)*PER; more.textContent='Show more ('+(f.length-(page+1)*PER)+' left)';
 secC.hidden=kind==='written'; secW.hidden=kind==='closed';
 emC.hidden=nc>0; emW.hidden=f.length>0;
 var where=shownC!=='all'?shownC+' County':(shownR==='all'?'Florida':shownR);
 out.textContent=where+': '+nc+' shut down · '+f.length+' written up';
 bs.forEach(function(b){b.classList.toggle('on',shownC==='all'&&b.dataset.r===shownR);});
 ks.forEach(function(b){b.classList.toggle('on',b.dataset.k===kind);});
 var el=document.getElementById('ei-list'),et=document.getElementById('ei-title');
 if(el){var cf=CLN.filter(function(c){return match(c.county,c.region);}),hh2=shownC!=='all'?shownC+' County':(shownR!=='all'?shownR:'Florida');
  et.textContent='✨ Where to eat instead in '+hh2;
  el.innerHTML=cf.slice(0,8).map(function(c){var q=encodeURIComponent(c.name+' '+c.address+' '+c.city+' FL');
   return '<article class="cp-card"><span class="cp-badge" aria-hidden="true">✨</span><div><h3>'+esc(c.name)+'</h3><p class="meta"><a href="https://www.google.com/maps/search/?api=1&query='+q+'" rel="noopener" target="_blank">'+esc(c.address)+', '+esc(c.city)+'</a> · Perfect inspection</p></div></article>';}).join('')+
   (cf.length>8?'<a class="cp-countylink" style="display:block;margin-top:8px;font-weight:800;color:var(--accent-ink)" href="/clean-plate-club/'+(shownC!=='all'?'#'+encodeURIComponent(shownC):(shownR!=='all'?'#'+encodeURIComponent(shownR):''))+'">See all '+cf.length+' →</a>':'');}
 var cl=document.getElementById('rr-countylink'),cx=document.getElementById('rr-cleanlink');
 if(cl)cl.innerHTML=shownC!=='all'?'<a href="/restaurant-inspections/'+shownC.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')+'-county/">Open the full '+esc(shownC)+' County page →</a>':'';
 if(cx){var hh=shownC!=='all'?shownC:(shownR!=='all'?shownR:'');cx.href='/clean-plate-club/'+(hh?'#'+encodeURIComponent(hh):'');cx.textContent='✨ Want somewhere clean instead? See the cleanest restaurants in '+(hh?(shownC!=='all'?hh+' County':hh):'Florida')+' →';}
 if(push){var h=shownC!=='all'?shownC:(shownR!=='all'?shownR:'');history.replaceState(null,'',h?'#'+encodeURIComponent(h):location.pathname);}
}
bs.forEach(function(b){b.addEventListener('click',function(){shownR=b.dataset.r;shownC='all';sel.value='all';page=0;render(true);});});
sel.addEventListener('change',function(){shownC=sel.value;shownR='all';page=0;render(true);});
ks.forEach(function(b){b.addEventListener('click',function(){kind=b.dataset.k;render(false);});});
more.addEventListener('click',function(){page++;render(false);});
var h=decodeURIComponent(location.hash.slice(1));
if(h){if([].some.call(bs,function(b){return b.dataset.r===h;}))shownR=h;else if([].some.call(sel.options,function(o){return o.value===h;})){shownC=h;sel.value=h;}}
render(false);
fetch('/roach-report/clean.json?v='+(window.RR_V||'')).then(function(r){return r.json();}).then(function(d){
 CLN=(d.items||[]).map(function(w){w.region=(window.RR_REGION||{})[w.county]||'North Florida & Panhandle';return w;});render(false);});
fetch('/roach-report/writeups.json?v='+(window.RR_V||'')).then(function(r){return r.json();}).then(function(d){
 WU=(d.items||[]).map(function(w){w.region=(window.RR_REGION||{})[w.county]||'North Florida & Panhandle';return w;});render(false);});
})();
