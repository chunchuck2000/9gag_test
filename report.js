
// reads csv using d3.js
function init(csv_filename, callback){
  d3.csv(csv_filename, function(data){
    callback(data);
  });
}

// draws html table
// from: http://bl.ocks.org/jfreels/6734025
function draw_table(field, condition, data, columns, args){

    data = data.filter(function(r){
        return r[field] == condition;
    });
    
    if(args.hasOwnProperty("n")){
      data = data.slice(0,args.n);
    }

    var table = d3.select("#main").append("table"),
        thead = table.append("thead"),
        tbody = table.append("tbody");

    thead.append("tr")
      .selectAll("th")
      .data(columns)
      .enter()
      .append("th")
      .text(function(column) { return column; });

    var rows = tbody.selectAll("tr")
      .data(data)
      .enter()
      .append("tr");

    var cells = rows.selectAll("td")
      .data(function(row) {
          return columns.map(function(column) {
            if(column == 'daily_rank'){
                return {column: column, value: row[column] + ' / ' + row['daily_total_rank']};
            } else {
                return {column: column, value: row[column]};
            }
          });
      })
    .enter()
    .append("td")
    .text(function(d) { return d.value; });

}

function update_title(title){
  document.getElementById('title').innerHTML = title;
}