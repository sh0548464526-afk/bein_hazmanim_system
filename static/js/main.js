function filterTable(value){
    const table = document.getElementById('students-table');
    const trs = table.getElementsByTagName('tr');
    for (let i=1;i<trs.length;i++){
        let td = trs[i].getElementsByTagName('td')[1];
        trs[i].style.display = td.innerText.includes(value) ? '' : 'none';
    }
}