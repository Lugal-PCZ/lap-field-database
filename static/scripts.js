document.addEventListener(
  'click',
  function closePanels(event) {
    if (event.target.parentElement.id !== "popupmenus") {
      var thepanel = document.getElementById("loginpanel");
      if (!thepanel.hidden && !thepanel.contains(event.target)) {
        thepanel.hidden = true;
      };
      if (document.querySelector("#downloadpanel")) {
        var thepanel = document.getElementById("downloadpanel");
        if (!thepanel.hidden && !thepanel.contains(event.target)) {
          thepanel.hidden = true;
        };
      };
    }
  },
);

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
  if (document.querySelector("#details")) {
    const initialState = FormSerializer.serialize(document.getElementById("details"));
    localStorage.setItem("initialState", JSON.stringify(initialState));
    const selectfields = document.querySelectorAll("select");
    selectfields.forEach(field => {
      if (field.selectedIndex === -1) {
        localStorage.setItem(field.id, "")
      } else {
        localStorage.setItem(field.id, field.options[field.selectedIndex].innerHTML)
      }
    });
    const filefields = document.querySelectorAll('input[type="file"]');
    filefields.forEach(field => {
      localStorage.setItem(field.id, field.value);
    });
    if (window.location.href.includes("/new/")) {
      localStorage.setItem("okToChangeLapIdentifier", "true")
    } else {
      localStorage.setItem("okToChangeLapIdentifier", "false")
    };
  };
}

function resetForm() {
  if (document.querySelector("#details")) {
    document.getElementById("details").reset();
    const autocompletefields = document.querySelectorAll(".select2-selection__rendered");
    autocompletefields.forEach(field => {
      const target_field = `id_${field.id.split("_")[1].split("-")[0]}`
      field.removeAttribute("title");
      field.innerHTML = localStorage.getItem(target_field);
    });
    document.getElementById('savebutton').disabled=true;
    document.getElementById('discardchangesbutton').disabled=true;
    document.getElementById('newbutton').disabled=false;
    if (document.querySelector("#id_voided")) {
      toggleVoided();
    };
    if (document.querySelector("#details").name === "SUForm" && !document.querySelector("#onscreen")) {
      document.getElementById("id_worldfile").parentElement.hidden = true;
    };
  };
}

function checkForm() {
  if (document.querySelector("#details")) {
    const savedState = JSON.parse(localStorage.getItem("initialState"))
    const currentState = FormSerializer.serialize(document.getElementById("details"));
    var changedFileFields = false;
    const filefields = document.querySelectorAll('input[type="file"]');
    filefields.forEach(field => {
      if (localStorage.getItem(field.id) !== field.value) {
        changedFileFields = true;
      };
    });
    if (JSON.stringify(currentState) !== localStorage.getItem("initialState") || changedFileFields) {
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
      document.getElementById('discardchangesbutton').disabled=false;
      document.getElementById('newbutton').disabled=true;
    } else {
      document.getElementById('savebutton').disabled=true;
      document.getElementById('discardchangesbutton').disabled=true;
      document.getElementById('newbutton').disabled=false;
    };
    if (document.querySelector("#id_voided")) {
      toggleVoided();
    };
    if (document.querySelector("#details").name === "SUForm") {
      if (document.getElementById("id_tracing").value || document.querySelector("#onscreen")) {
        document.getElementById("id_worldfile").parentElement.hidden = false;
        document.getElementById("id_worldfile").required = true;
      };
      if (document.querySelector("#tracing-clear_id") && document.getElementById("tracing-clear_id").checked) {
        document.getElementById("id_worldfile").required = false;
      };
    };
  };
}

function hideFields() {
  if (document.querySelector("#details")) {
    const form_name = document.querySelector("#details").name;
    switch (form_name) {
      case "SUForm":
        if (!document.querySelector("#onscreen")) {
          document.getElementById("id_worldfile").parentElement.hidden = true;
        }
        break;
    };
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

function showImage(thewidget, original) {
  const image = thewidget;
  new Viewer(image, {url(image) {return original}, title: false, navbar: false, toolbar: false,});
}
