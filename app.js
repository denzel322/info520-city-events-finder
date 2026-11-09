const form=document.querySelector('#search'),status=document.querySelector('#status'),results=document.querySelector('#results');
function node(tag,text){const el=document.createElement(tag);el.textContent=text;return el;}
form.addEventListener('submit',async e=>{e.preventDefault(); const button=form.querySelector('button');button.disabled=true;results.replaceChildren();document.querySelector('#providers').textContent='';status.textContent='Finding upcoming events…';
try{const response=await fetch('/api/events?city='+encodeURIComponent(form.city.value.trim()));const data=await response.json();if(!response.ok)throw Error(data.error||'Search failed.');
status.textContent=`${data.location} · ${data.start} to ${data.end} · ${data.events.length} events${data.complete?'':' · Partial results'}`;
document.querySelector('#providers').textContent=Object.entries(data.providers).map(([name,s])=>`${name}: ${s.ok?'connected':s.message}`).join(' | ');
results.append(node('p',data.coverage_note));if(!data.events.length)results.append(node('p',data.complete?'No events found for this location and date range.':'No events returned. One or more sources are unavailable; this does not mean there are no events.'));
for(const item of data.events){const card=node('article','');card.append(node('p',item.date+(item.time?' · '+item.time.slice(0,5):'')),node('h2',item.title),node('p',item.venue||'Venue details unavailable'),node('p','Sources: '+item.sources.join(', ')));
if(item.weather){const w=item.weather;card.append(node('p',`Weather: ${w.low_f}–${w.high_f} °F · Rain chance ${w.rain_percent??'unavailable'}%`));}
for(const [source,url] of Object.entries(item.links)){try{const parsed=new URL(url);if(parsed.protocol!=='https:')continue;const link=node('a',`View on ${source}`);link.href=parsed.href;link.target='_blank';link.rel='noopener noreferrer';card.append(link);}catch{}}
results.append(card);}}
catch(err){status.textContent=err.message;}finally{button.disabled=false;}});
