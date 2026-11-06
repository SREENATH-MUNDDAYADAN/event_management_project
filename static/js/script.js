document.addEventListener('DOMContentLoaded',()=>{document.querySelectorAll('input[type=date]').forEach(el=>{el.min=new Date().toISOString().slice(0,10)});});
