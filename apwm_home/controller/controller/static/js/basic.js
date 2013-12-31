    function init_controller_view() {
      $.getJSON("get_controller_list/", function(data, textStatus) {
        $("#controller_view").html( "Controller list: <ul></ul><div></div> " );
        data.forEach( function(controller) {
          $("#controller_view ul").append(
            '<li><a href="#controller-tab-' + controller["pk"] + '">' +
            controller["fields"]["description"] + '</a></li>'
            );
          $("#controller_view div").append(
            '<div id="controller-tab-' + controller["pk"] +
            '"><div id="controller-tab-desc-' + controller["pk"] +
            '"></div><div id="controller-tab-view-' + controller["pk"] + '"></div></div>'
            );
          set_controller_description(controller);
          $.getJSON("get_port_list/" + controller["pk"], function(data, textStatus) {
            set_controller_view(controller, data);
          });
        });
        $( "#controller_view" ).tabs();
      });
    }

    function set_controller_description(controller) {
      content = '<div>Controller Info</div><table>' +
        '<tr><th align="right">id</th><td id="controller_id">' + controller["pk"] + '</td></tr>';
      [ 'frequency', 'description', 'i2c_bus', 'i2c_address' ].forEach( function(k){
        content += '<tr><th align="right">' + k + '</th><td>' + controller["fields"][k] + '</td></tr>';
      });
      $("#controller-tab-desc-" + controller["pk"]).html( content + '</table>' );
    }

    function set_controller_view(controller, ports) {
      // Two tables:
      //   layout for configured ports sliders and the graph
      //   the sliders themselves are in a table
      content = '<div style="padding-top: 1em;"></div><div>Configured Ports</div>' +
        '<table style="width:100%"><tr><td>' +
        '<table><tr><th>chan</th><th style="width: 15em;">duty cycle</th></tr>';
      var pk, high, low;
      // create the content
      ports.forEach(function(port){
        pk   = port['pk'];
        high = port['fields']['high'];
        low  = port['fields']['low'];
        if( high - low < 0 ) {
          port['fields']['duty_cycle'] = (4096 + high - low)/4096 * 100;
        } else {
          port['fields']['duty_cycle'] = (high - low)/4096 * 100;
        }
        content+= '<tr>' +
          '<td>' + port["fields"]["port"] + '</td>' +
          '<td><label for="port-' + pk + '-slider" class="ui-hidden-accessible">Duty Cycle for port ' + port['fields']['port'] + '</label>' +
          '<input type="number" data-type="range" name="slider" id="port-' + pk + '-slider" value="' + Math.floor(port['fields']['duty_cycle']) + '" min="0" max="100" data-highlight="true" class="ui-hidden-accessible" /></td>' +
          '</tr>';
      });
      // set the content
      content += '</table><br><br><!-- a href="add_port_dialog" data-rel="dialog">Add Port</a -->' +
        '</td><td>' + // layout table data cells
        '<div id="controller-graph-' + controller["pk"] + '" style="width: 30em;;height:' + ports.length * 1.9 + 'em;"> testing !</div>' +
        '</td></table>';
      $("#controller-tab-view-" + controller["pk"]).html( content );
      // activate the content
      ports.forEach(function(port){
        $('#port-' + port['pk'] + '-slider').slider()
        $('#port-' + port['pk'] + '-slider').bind( 'change', function(event,ui) {
            $.getJSON( "set_port/" + port['pk'] + "/" + Math.floor(event.currentTarget.valueAsNumber * 4096 / 100) + "/0",
                       function(data, textStatus) {
                         for( port_i=0; port_i<ports.length; port_i++) {
                           if( ports[port_i]['pk'] == data[0]['pk'] ) {
                             data[0]['fields']['duty_cycle'] = event.currentTarget.valueAsNumber;
                             ports[port_i] = data[0];
                           }
                         }
                         draw_port_graph( $("#controller-graph-" + controller["pk"]), ports );
                       }
            );
          }
        );
      });
      draw_port_graph( $("#controller-graph-" + controller["pk"]), ports );
    }

    function init_add_port_dialog() {
      $.getJSON("get_controller_list/", function(data, textStatus) {
        $("#add_port").html( "Add port to controller:" );
      });
    }

    // use flot to draw a graph
    function draw_port_graph(port_graph_div, ports) {
      graph_data = []
      height = 1;
      padding = .1;
      base = ports.length * (height + padding);
      base_height = base + height;
      ports.forEach(function(port){
        duty_cycle = port['fields']['duty_cycle'];
        var d = [];
        for (var i = 0; i < 100; i += 1)
            d.push([i, (i>=duty_cycle)?base_height:base]);
        base -= height + padding;
        base_height =  base + height;
        // graph_data.push( { label: port["fields"]["port"], data: d } );
        graph_data.push( { data: d } );
      });

      function blankFormatter(v, axis) { return ""; }

      function percentFormatter(v, axis) {
        return v.toFixed(axis.tickDecimals) + "%";
      }

      // alert(graph_data[0]['data']);

      $.plot(port_graph_div, graph_data,
      {
          series: { lines: {show: true}, points: {show: false} },
          xaxes: [ { tickFormatter: percentFormatter } ],
          yaxes: [ { tickFormatter: blankFormatter } ],
      });
    }

