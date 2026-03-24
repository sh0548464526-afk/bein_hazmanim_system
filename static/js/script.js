document.getElementById("search").addEventListener("input", function() {
  var filter = this.value.toLowerCase();
  var rows = document.querySelectorAll("#main-table tr");
  rows.forEach(function(row, i) {
    if(i === 0) return;
    row.style.display = row.cells[1].innerText.toLowerCase().includes(filter) ? "" : "none";
  });
});
