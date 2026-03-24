
document.getElementById("search").addEventListener("keyup",function(){

let v=this.value.toLowerCase()

document.querySelectorAll("#table tr").forEach(r=>{

if(r.innerText.toLowerCase().includes(v))
 r.style.display=""
else
 r.style.display="none"

})

})
