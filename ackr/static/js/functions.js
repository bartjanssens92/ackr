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

  getobjects();

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
  getobjects();
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
    backend_div.innerHTML = 'Loading services...';
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

async function getobjects() {

  //const msg = document.createElement('p');
  //msg.id = 'display_message';
  const msg = document.getElementById('table_messages');
  msg.innerHTML = "Loading services...";
  //document.body.appendChild(msg);

  //Only render the complete table for the visable backend
  backend_div_id = get_visable_backend();
  const table_location = document.getElementById(backend_div_id);
  
  let backend_id = backend_div_id.replace('backend_table_', '');

  //Generate the div to hold the renered tables
  const results_div = document.createElement('div');
  results_div.id = 'results_' + backend_id;

  //Get the hosts for the visable backend if the type is icinga2
  const backends = await doGet('/backends'); 
  for (let i = 0; i < backends.length; ++i) {
    if (backends[i]['id'] === backend_id) {
      if (backends[i]['type'] === 'icinga2') {

        //Get the services of the visable backend
        msg.innerHTML = "Loading hosts...";
        const hosts = await doGet('/hosts?backend_id=' + backend_id); 

        msg.innerHTML = "Rendering hosts table...";
        hosts_table = await generateTable(backend_id, hosts);

        results_div.appendChild(hosts_table);
      }
    }
  }

  msg.innerHTML = "Loading services...";
  //Get the services of the visable backend
  const services = await doGet('/services?backend_id=' + backend_id); 

  //Filter out the services with notifications if toggled in the ui
  let filtered_services = {};
  for (var severity in services) {
  
    let filtered_services_array = [];
    for (let i = 0; i < services[severity].length; ++i) {
      if (user_notification(services[severity][i])) {
        filtered_services_array.push(services[severity][i]);
      }
    }
    filtered_services[severity] = filtered_services_array;
  }

  msg.innerHTML = "Rendering services table...";

  services_table = await generateTable(backend_id, filtered_services);
  results_div.appendChild(services_table);

  table_location.replaceChild(results_div, table_location.childNodes[0]);
  const t = new Date();
  msg.innerHTML = "Table last updated at: " + t.getHours() + ':' + t.getMinutes() + ':' + t.getSeconds();
}

async function generateTable(backend_id, objects) {

  //Create the div element containing the table
  let table_div = document.createElement('div');
  table_div.classList.add('table-responsive');

  //Add the services to the table
  for (var severity in objects) {

    //Create the table elements
    let table = document.createElement('table');
    table.classList.add('table');
    table.classList.add('table-striped');
    let table_head = document.createElement('thead');
    let table_body = document.createElement('tbody');

    //Don't bother with empty severities
    if ( objects[severity].length > 0) {
      var table_severity = document.createElement('div');
      table_severity.id = severity;
      var table_title = document.createElement('h4');
      table_title.innerHTML = objects[severity].length + ' | ' + severity[0].toUpperCase() + severity.slice(1);
      table_title.style.marginLeft = "10px";
      table_severity.appendChild(table_title);

      switch (severity) {
        case 'critical':
          table_severity.classList.add('bg-danger');
          break;
        case 'down':
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

      for (let i = 0; i < objects[severity].length; ++i) {
        //If the user selected to only show services they get notifications for
        //then the service should be checked first
        var tr_service = document.createElement('tr');
        var service_name = objects[severity][i]['name'];
        var service_host_name = objects[severity][i]['host_name'];
        //Ugly part to get the button in there
        let service = '';
        service += '<td><button type="button" id="' + 
          objects[severity][i]['host_name'] + '_' + 
          objects[severity][i]['name'] + 
          '" class="btn btn-block" onclick="ack_service(\'' + 
          backend_id + '\',\'' + 
          objects[severity][i]['host_name'] + '\',\'' + 
          objects[severity][i]['name'] + '\')">' + 
          objects[severity][i]['host_name'] + '</button></td>';

        service += '<td><div id="service">' + objects[severity][i]['display_name'] + '</div></td>';
        service += '<td><div id="service">' + objects[severity][i]['output'] + '</div></td>';
        tr_service.innerHTML = service;
        table_body.appendChild(tr_service);
      }
      table.appendChild(table_head);
      table.appendChild(table_body);
      table_div.appendChild(table);
    }
  }

  return table_div;
}

async function doGet(endpoint) {
  try {
    const base_url = window.location.origin;
    const request = new Request(base_url + endpoint, {
      method: 'GET',
    });

    const response = await fetch(request);
    if (! await response.status === 200) {
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
