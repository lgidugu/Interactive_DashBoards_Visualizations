/* data route */
var url = "/data";

function buildPlot() {
    Plotly.d3.json(url, function(error, response) {

        console.log(response);
        var trace1 = {
            type: "pie",
            
            name: "BB Sample Values",
            labels: response.map(data => data.otu_ids),
            values: response.map(data => data.sample_values),
            
        };

        var data = [trace1];

        var layout = {
            title: "BB Sample Values",
            values: {
                type: "Sample Values"
            },
            var labels ={
                type:"otu_ids"
            }
        };

        Plotly.newPlot("pie", data, layout);
    });
}

buildPlot();