function toggleLogin() {
  if (document.querySelector("#downloadpanel")) {
    document.getElementById("downloadpanel").hidden = true;
  };
  document.getElementById("loginpanel").toggleAttribute("hidden");
  if (document.querySelector("#username")) {
    document.getElementById("username").focus();
  };
}

function toggleDownloadPanel() {
  if (document.querySelector("#downloadpanel")) {
    document.getElementById("loginpanel").hidden = true;
    document.getElementById("downloadpanel").toggleAttribute("hidden");
  };
}

function submitCleanURL(form) {
  const controls = form.elements;
  for (var i=0, num=controls.length; i<num; i++) {
    controls[i].disabled = controls[i].value == '';
  };
  form.submit();
}

function cacheForm() {
  if (document.querySelector("#detail")) {
    const initialState = FormSerializer.serialize(document.getElementById('detail'));
    localStorage.setItem("initialState", JSON.stringify(initialState));
    if (window.location.href.includes("/new/")) {
      localStorage.setItem("okToChangeLapIdentifier", "true")
    } else {
      localStorage.setItem("okToChangeLapIdentifier", "false")
    };
  };
}

function checkForm() {
  if (document.querySelector("#detail")) {
    const currentState = FormSerializer.serialize(document.getElementById('detail'));
    const savedState = JSON.parse(localStorage.getItem("initialState"))
    if (JSON.stringify(currentState) !== localStorage.getItem("initialState")) {
      if (currentState.name != savedState.name && localStorage.getItem("okToChangeLapIdentifier") === "false") {
        if (confirm("Are you sure that you want to change this record’s name?")) {
          localStorage.setItem("okToChangeLapIdentifier", "true");
        } else {
          document.getElementById("id_name").value = savedState.name;
        };
      };
      if (currentState.number != savedState.number && localStorage.getItem("okToChangeLapIdentifier") === "false") {
        if (confirm("Are you sure that you want to change this record’s number?")) {
          localStorage.setItem("okToChangeLapIdentifier", "true");
        } else {
          document.getElementById("id_number").value = savedState.number;
        };
      };
      document.getElementById('savebutton').disabled=false;
      document.getElementById('newbutton').disabled=true;
    } else {
      document.getElementById('savebutton').disabled=true;
      document.getElementById('newbutton').disabled=false;
    };
    if (document.querySelector("#id_voided")) {
      toggleVoided();
    }
  };
}

function toggleVoided() {
  if (document.querySelector("#id_voided")) {
    const labels = document.querySelectorAll('label');
    if (document.getElementById("id_voided").checked) {
      labels.forEach(label => {
        label.classList.add('voided');
      });
    } else {
      labels.forEach(label => {
        label.classList.remove('voided');
      });
    };
  };
}

function loadLocale() {
  const su_id = document.getElementById("id_su").value;
  fetch(`/ajax/load_locale/?su_id=${su_id}`)
    .then(response => response.json())
    .then(data => {
      document.getElementById("id_locale").value = data[0].name;
    });
}
