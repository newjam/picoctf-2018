var alasql= require('alasql');
var fs = require('fs')

var contents = fs.readFileSync("incidents.json");
var json = JSON.parse(contents);
var data = json['tickets']

var result = alasql('SELECT count(*) AS answer FROM ? WHERE src_ip = "9.94.163.45" GROUP BY dest_ip',[data]);
console.log(result[0]['answer']);

var result = alasql('SELECT count(distinct dst_ip) AS answer FROM ? WHERE src_ip = "43.250.172.185"',[data]);
console.log(result[0]['answer']);

var result = alasql('SELECT avg(n) AS answer FROM (SELECT count(distinct dst_ip) as n FROM ? GROUP BY file_hash)',[data]);
console.log(result[0]['answer']);

