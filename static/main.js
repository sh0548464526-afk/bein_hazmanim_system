function filterTable() {
    let searchValue = document.getElementById("search").value.toLowerCase();
    let dayFilter = document.getElementById("dayFilter").value;
    let rows = document.querySelectorAll("#table tbody tr");

    rows.forEach(row => {
        let cells = row.querySelectorAll("td");
        let textMatch = cells[0].innerText.toLowerCase().includes(searchValue) ||
                        cells[1].innerText.toLowerCase().includes(searchValue);

        let dayMatch = true;
        if (dayFilter) {
            let dayColsStart = 2; // עמודה ראשונה של היום הראשון
            let dayMap = { "א": 0, "ב": 3, "ג": 6 }; // מיפוי של תחילת עמודות לכל יום
            let idx = dayMap[dayFilter];
            let dayCells = [cells[2+idx].innerText, cells[3+idx].innerText, cells[4+idx].innerText];
            dayMatch = dayCells.some(c => c.trim() !== "");
        }

        row.style.display = (textMatch && dayMatch) ? "" : "none";
    });
}

function saveData() {
    let rows = document.querySelectorAll("#table tbody tr");
    let data = [];

    rows.forEach(row => {
        let c = row.querySelectorAll("td");
        if (!c[0].innerText.trim() && !c[1].innerText.trim()) return; // דילוג על שורות ריקות לחלוטין

        data.push({
            tz: c[0].innerText,
            name: c[1].innerText,
            days: {
                "א": { before: c[2].innerText, prayer: c[3].innerText, seder: c[4].innerText },
                "ב": { before: c[5].innerText, prayer: c[6].innerText, seder: c[7].innerText },
                "ג": { before: c[8].innerText, prayer: c[9].innerText, seder: c[10].innerText }
            }
        });
    });

    fetch("/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(resp => {
        if (resp.ok) alert("נשמר בהצלחה!");
        else alert("שגיאה בשמירה!");
    })
    .catch(err => alert("שגיאה: " + err));
}

// הוספת שורה ריקה אוטומטית בסוף הטבלה
function addEmptyRow() {
    let tbody = document.querySelector("#table tbody");
    let row = document.createElement("tr");
    row.classList.add("empty-row");
    for (let i = 0; i < 11; i++) { // 2 + 3*3 = 11 עמודות
        let td = document.createElement("td");
        td.contentEditable = "true";
        td.innerText = "";
        row.appendChild(td);
    }
    tbody.appendChild(row);
}

// הוספה של שורה ריקה בעת טעינת הדף
window.onload = function() {
    addEmptyRow();
};