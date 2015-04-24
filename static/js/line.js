var res;
	$.getJSON('/_get_time_stats', function(data) {
       var res = data;
	    doStuff(res);
	
      });
function doStuff(result) {
var chart = c3.generate({
    bindto: '#chart2',
	size: {
        height: 240,
    },
    data: {
        x: 'x',
        columns: [
			result[0],
			result[1]
            //['x', '2010-01-01', '2011-01-01', '2012-01-01', '2013-01-01', '2014-01-01', '2015-01-01'],
            //['sample', 30, 200, 100, 400, 150, 250]
        ]
    },
    axis : {
        x : {
            type : 'timeseries',
            tick: {
                format: '%d %H'
              //format: '%Y' // format string is also available for timeseries data
            }
        }
    }
});
};
