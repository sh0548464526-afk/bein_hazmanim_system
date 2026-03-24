document.getElementById("search").addEventListener("keyup",function(){

let value=this.value.toLowerCase()

document.querySelectorAll("#table tr").forEach(row=>{

if(row.innerText.toLowerCase().includes(value))
row.style.display=""
else
row.style.display="none"

})

})