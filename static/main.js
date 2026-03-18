function filterTable(){

let t=
document.getElementById("search")
.value.toLowerCase()

let rows=
document.querySelectorAll("#table tbody tr")

rows.forEach(r=>{

if(r.innerText.toLowerCase().includes(t))
r.style.display=""

else
r.style.display="none"

})

}

function saveData(){

let rows=
document.querySelectorAll("#table tbody tr")

let data=[]

rows.forEach(r=>{

let c=r.querySelectorAll("td")

data.push({

tz:c[0].innerText,
name:c[1].innerText

})

})

fetch("/save",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify(data)

})

alert("נשמר")

}
