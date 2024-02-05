async function ack_service(host_name, service) {
  const button = document.getElementById(host_name + '_' + service);
  button.setAttribute('disabled', true); 

  let message_id = host_name + '_' + service;
  add_message('Acknowledging: ' + service + ' on ' + host_name, message_id);

  await doPost('/ack', '{"service_name": "' + service + '", "host_name": "' + host_name + '"}');

  remove_message(message_id);
}

function add_message(message, message_id) {
  const messages_div = document.getElementById('messages');
  messages_div.style.setProperty('visibility', 'visible'); 
 
  let p = document.createElement('h5');
  p.id = message_id;
  p.innerHTML = message;
  messages_div.appendChild(p);
}

function remove_message(message_id) {
  const message = document.getElementById(message_id);
  message.remove();
}

async function generateTable() {

  //const msg = document.createElement('p');
  //msg.id = 'display_message';
  const msg = document.getElementById('table_messages');
  msg.innerHTML = "Loading services...";
  //document.body.appendChild(msg);

  const table_location = document.getElementById('table_location');

  const services = await doGet('/services'); 
  msg.innerHTML = "Rendering table...";

  let table_div = document.createElement('div');
  table_div.classList.add('table-responsive');

  for (var severity in services) {
    let table = document.createElement('table');
    table.classList.add('table');
    table.classList.add('table-striped');

    let table_body = document.createElement('tbody');
    let table_head = document.createElement('thead');

    //element.innerHTML = severity;
    if ( services[severity].length > 0) {
      //console.log(severity);
      var table_severity = document.createElement('div');
      table_severity.id = severity;
      var table_title = document.createElement('h4');
      table_title.innerHTML = services[severity].length + ' | ' + severity[0].toUpperCase() + severity.slice(1);
      table_title.style.marginLeft = "10px";
      table_severity.appendChild(table_title);

      switch (severity) {
        case 'critical':
          table_severity.classList.add('bg-danger');
          break;
        case 'unknown':
          table_severity.classList.add('bg-info');
          break;
        case 'warning':
          table_severity.classList.add('bg-warning');
          break;
        default:
          table_severity.classList.add('bg-dark');
      }
      table_severity.classList.add('text-white');
      table_div.appendChild(table_severity);

      let header = '';
      header += '<td><div id="header">Host name</div></td>';
      header += '<td><div id="header">Service name</div></td>';
      header += '<td><div id="header">Output</div></td>';
      var tr_header = document.createElement('tr');
      tr_header.innerHTML = header;
      table_head.appendChild(tr_header);

      for (let i = 0; i < services[severity].length; ++i) {
        //console.log(services[severity][i]['display_name']);
        //service += '<td><div id="service"><button type="button" class="btn btn-block">' + services[severity][i]['host_name'] + '</button></div></td>';
        var tr_service = document.createElement('tr');
        var service_name = services[severity][i]['name'];
        var service_host_name = services[severity][i]['host_name'];
        let service = '';
        service += '<td><button type="button" id="' + service_host_name + '_' + service_name +'" class="btn btn-block" onclick="ack_service(\'' + service_host_name + '\',\'' + service_name + '\')">' + services[severity][i]['host_name'] + '</button></td>';
        service += '<td><div id="service">' + services[severity][i]['display_name'] + '</div></td>';
        service += '<td><div id="service">' + services[severity][i]['output'] + '</div></td>';
        tr_service.innerHTML = service;
        table_body.appendChild(tr_service);
      }
    }
    table.appendChild(table_head);
    table.appendChild(table_body);
    table_div.appendChild(table)
    //table_div.appendChild(document.createElement('br'));
    //document.body.appendChild(table_div);
    //document.body.appendChild(document.createElement('br'));
  }

  table_location.replaceChild(table_div, table_location.childNodes[0]);
  const t = new Date();
  msg.innerHTML = "Table last updated at: " + t.getHours() + ':' + t.getMinutes() + ':' + t.getSeconds();

  //msg.style.setProperty('visibility', 'hidden'); 
}

async function doGet(endpoint) {
  try {
    const base_url = window.location.origin;
    const request = new Request(base_url + endpoint, {
      method: 'GET',
    });

    const response = await fetch(request);
    if (! response.status === 200) {
      throw new Error('Backend did not return 200')
    }

    const data = await response.json();
    return data;
  }
  catch (error) {
    console.log("Expected 200 but got this: " + error);
  }
}

async function doPost(endpoint, data='{}') {
  try {
    const base_url = window.location.origin;
    const response = await fetch(base_url + endpoint, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: data,
    });

    return response.json();
  }
  catch (error) {
    console.log("Expected 200 but got this: " + error);
  }

}
