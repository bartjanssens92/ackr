async function ack_service(backend_id, host_name, service) {
  const button = document.getElementById(host_name + '_' + service);
  button.setAttribute('disabled', true); 

  let message_id = host_name + '_' + service;
  add_message('Acknowledging: ' + service + ' on ' + host_name, message_id);

  await doPost('/ack', '{"backend_id": "' + backend_id + '", "service_name": "' + service + '", "host_name": "' + host_name + '"}');

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

function user_notification(service) {
  // check if "show all notifications" is toggled
  const checkbox = document.getElementById('show_all');
  if (checkbox.checked) {
    return true
  }

  // check if the notification is enabled
  if (service['notification']['enable'] == false) {
    return false
  }
  
  return true
}

function show_backend(backend_id) {

  const backend_divs = document.getElementsByClassName("backend_table");

  for (let i = 0; i < backend_divs.length; i++) {
    if (backend_divs[i].id === 'backend_table_' + backend_id) {
      backend_divs[i].style.setProperty('display', 'inline');
    } else {
      backend_divs[i].style.setProperty('display', 'none');
    }
  }

  generateTable();

}

function get_visable_backend() {

  const backend_divs = document.getElementsByClassName("backend_table");

  for (let i = 0; i < backend_divs.length; i++) {
    if (backend_divs[i].style.display === 'inline') {
      return backend_divs[i].id;
    }
  }

}

async function build_layout() {
  await generateBackends();
  generateTable();
}

async function generateBackends() {

  const table_location = document.getElementById('table_location');

  let backend_table= document.createElement('table');
  backend_table.classList.add('table');
  let backend_table_head = document.createElement('tr');
  let backend_divs = document.createElement('div');

  const backends = await doGet('/backends'); 
  for (var backend in backends) {
    var backend_header = document.createElement('td');
    var sane_backend_name = backends[backend]['id'];
    var backend_display_name = backends[backend]['display_name'];

    backend_header.innerHTML = '<button type="button" id="' + sane_backend_name + '" class="btn btn-block" onclick="show_backend(\'' + sane_backend_name + '\'' + ')"> ' + backend_display_name + '</button></td>';
    //backend_header.innerHTML = backends[backend]['name'];
    backend_header.id = sane_backend_name;
    backend_table_head.appendChild(backend_header);

    var backend_div = document.createElement('div');
    backend_div.id = 'backend_table_' + sane_backend_name;
    backend_div.classList.add('backend_table');
    backend_div.innerHTML = 'services go here ' + sane_backend_name;
    if (backend > 0) {
      backend_div.style.setProperty('display', 'none');
    } else {
      backend_div.style.setProperty('display', 'inline');
    }

    backend_divs.appendChild(backend_div);
  }    

  backend_table.appendChild(backend_table_head);
  table_location.appendChild(backend_table);
  table_location.appendChild(backend_divs);
}

async function generateTable() {

  //const msg = document.createElement('p');
  //msg.id = 'display_message';
  const msg = document.getElementById('table_messages');
  msg.innerHTML = "Loading services...";
  //document.body.appendChild(msg);

  //Only render the complete table for the visable backend
  backend_div_id = get_visable_backend();
  const table_location = document.getElementById(backend_div_id);
  
  let backend_id = backend_div_id.replace('backend_table_', '');
  const services = await doGet('/services?backend_id=' + backend_id); 
  msg.innerHTML = "Rendering table...";

  let table_div = document.createElement('div');
  table_div.classList.add('table-responsive');

  for (var severity in services) {
    let table = document.createElement('table');
    table.classList.add('table');
    table.classList.add('table-striped');

    let table_head = document.createElement('thead');
    let table_body = document.createElement('tbody');
    let filtered_services = [];

    for (let i = 0; i < services[severity].length; ++i) {
      if (user_notification(services[severity][i])) {
        filtered_services.push(services[severity][i]);
      }
    }

    //element.innerHTML = severity;
    if ( filtered_services.length > 0) {
      var table_severity = document.createElement('div');
      table_severity.id = severity;
      var table_title = document.createElement('h4');
      table_title.innerHTML = filtered_services.length + ' | ' + severity[0].toUpperCase() + severity.slice(1);
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
        case 'info':
          table_severity.classList.add('bg-info');
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

      for (let i = 0; i < filtered_services.length; ++i) {
        //console.log(filtered_services[i]['display_name']);
        //service += '<td><div id="service"><button type="button" class="btn btn-block">' + filtered_services[i]['host_name'] + '</button></div></td>';

        // if the user selected to only show services they get notifications for
        // then the service should be checked first
        var tr_service = document.createElement('tr');
        var service_name = filtered_services[i]['name'];
        var service_host_name = filtered_services[i]['host_name'];
        let service = '';
        service += '<td><button type="button" id="' + service_host_name + '_' + service_name +'" class="btn btn-block" onclick="ack_service(\'' + backend_id + '\',\'' + service_host_name + '\',\'' + service_name + '\')">' + filtered_services[i]['host_name'] + '</button></td>';
        service += '<td><div id="service">' + filtered_services[i]['display_name'] + '</div></td>';
        service += '<td><div id="service">' + filtered_services[i]['output'] + '</div></td>';
        tr_service.innerHTML = service;
        table_body.appendChild(tr_service);
      }
      table.appendChild(table_head);
      table.appendChild(table_body);
      table_div.appendChild(table)
      //table_div.appendChild(document.createElement('br'));
      //document.body.appendChild(table_div);
      //document.body.appendChild(document.createElement('br'));
    }
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
