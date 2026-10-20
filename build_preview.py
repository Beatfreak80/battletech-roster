# Build design-preview.html: the built app plus preview/skins.css, an in-memory storage stand-in and preview/demo.js.
# Run build.py first. The preview never reads or writes the real saved game.
t=open('battletech-roster.html',encoding='utf-8').read()
skins=open('preview/skins.css',encoding='utf-8').read()
demo=open('preview/demo.js',encoding='utf-8').read()
shim="""<script>
// in-memory localStorage for the preview, so the demo data never touches the real saved game
(function(){const m=new Map(),s={getItem:k=>m.has(k)?m.get(k):null,setItem:(k,v)=>{m.set(k,String(v))},removeItem:k=>{m.delete(k)},clear:()=>m.clear(),key:i=>[...m.keys()][i]??null,get length(){return m.size}};
  try{Object.defineProperty(window,'localStorage',{value:s,configurable:true});if(window.localStorage===s)window.__demoStore=s}catch(e){}})();
</script>
"""
assert t.count('<script>')==1, 'expected one app script'
t=t.replace('</style>','</style>\n<style id="skins">\n'+skins+'</style>',1)
t=t.replace('</script>','</script>\n<script>\n'+demo+'</script>',1)   # after the app script
t=t.replace('<script>',shim+'<script>',1)                              # before it
open('design-preview.html','w',encoding='utf-8',newline='\n').write(t)
print('built design-preview.html')
