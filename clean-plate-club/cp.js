
(function(){
var CL=[],R='all',C='all',page=0,PER=40,bs=document.querySelectorAll('.rr-chip'),sel=document.getElementById('cp-county'),
list=document.getElementById('cp-list'),more=document.getElementById('cp-more'),out=document.getElementById('cp-showing'),cty=document.getElementById('cp-countylink');
function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function slug(c){return c.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')+'-county';}
function card(c){var q=encodeURIComponent(c.name+' '+c.address+' '+c.city+' FL'),d=new Date(c.date+'T12:00:00').toLocaleDateString('en-US',{month:'short',day:'numeric'});
return '<article class="cp-card"><span class="cp-badge" aria-hidden="true">✨</span><div><h3>'+esc(c.name)+'</h3><p class="meta"><a href="https://www.google.com/maps/search/?api=1&query='+q+'" rel="noopener" target="_blank">'+esc(c.address)+', '+esc(c.city)+'</a> · '+esc(c.county)+' County · Perfect inspection '+d+'</p></div></article>';}
function render(push){var f=CL.filter(function(c){return C!=='all'?c.county===C:(R==='all'||c.region===R);});
list.innerHTML=f.slice(0,(page+1)*PER).map(card).join('')||'<p class="rr-empty">No perfect inspections listed here in the last 30 days yet. Check back soon.</p>';
more.hidden=f.length<=(page+1)*PER;more.textContent='Show more ('+(f.length-(page+1)*PER)+' left)';
var where=C!=='all'?C+' County':(R==='all'?'Florida':R);out.textContent=f.length+' restaurants with a perfect inspection in '+where;
cty.innerHTML=C!=='all'?'<a href="/restaurant-inspections/'+slug(C)+'/">See everything for '+esc(C)+' County: closures, write-ups and clean spots →</a>':'';
bs.forEach(function(b){b.classList.toggle('on',C==='all'&&b.dataset.r===R);});
if(push){var h=C!=='all'?C:(R!=='all'?R:'');history.replaceState(null,'',h?'#'+encodeURIComponent(h):location.pathname);}}
bs.forEach(function(b){b.addEventListener('click',function(){R=b.dataset.r;C='all';sel.value='all';page=0;render(true);});});
sel.addEventListener('change',function(){C=sel.value;R='all';page=0;render(true);});
more.addEventListener('click',function(){page++;render(false);});
var h=decodeURIComponent(location.hash.slice(1));
if(h){if([].some.call(bs,function(b){return b.dataset.r===h;}))R=h;else if([].some.call(sel.options,function(o){return o.value===h;})){C=h;sel.value=h;}}
fetch('/roach-report/clean.json?v='+(window.RR_V||'')).then(function(r){return r.json();}).then(function(d){
CL=(d.items||[]).map(function(c){c.region=(window.RR_REGION||{})[c.county]||'North Florida & Panhandle';return c;});render(false);});
})();
