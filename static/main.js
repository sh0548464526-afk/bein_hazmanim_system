function enableEdit(){
document.querySelectorAll("#table td").forEach(td=>{
td.contentEditable="true"
})
}

function saveData(){

let rows=document.querySelectorAll("#table tbody tr")
let headers=document.querySelectorAll("#table thead th")

let days=[]
for(let i=2;i<headers.length;i+=3){
days.push(headers[i].innerText.split(" ")[1])
}

let data=[]

rows.forEach(r=>{

let c=r.querySelectorAll("td")

let tz=c[0].innerText.trim()
let name=c[1].innerText.trim()

if(!tz) return

let obj={
tz:tz,
name:name,
days:[]
}

let idx=2

days.forEach(d=>{

obj.days.push({
day:d,
before:c[idx].innerText,
prayer:c[idx+1].innerText,
seder:c[idx+2].innerText
})

idx+=3
})

data.push(obj)

})

fetch("/save",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify(data)
})

alert("נשמר")
}

function filterAll(){

let text=document.getElementById("search").value.toLowerCase()
let day=document.getElementById("dayFilter").value

let rows=document.querySelectorAll("#table tbody tr")

rows.forEach(r=>{

let show=true

if(text && !r.innerText.toLowerCase().includes(text))
show=false

if(day){
let headers=document.querySelectorAll("#table thead th")
let idx=-1

headers.forEach((h,i)=>{
if(h.innerText.includes(day)) idx=i
})

if(idx!=-1){
let val=r.children[idx].innerText
if(!val) show=false
}
}

r.style.display=show?"":"none"

})

}

function togglePassword(){
let b=document.getElementById("passBox")
b.style.display=(b.style.display=="none")?"block":"none"
}