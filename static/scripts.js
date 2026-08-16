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
      if (!localStorage.getItem(target_field)) {
        document.getElementById(target_field).innerHTML = '';
      }
    });
    document.getElementById('savebutton').disabled=true;
    document.getElementById('discardchangesbutton').disabled=true;
    document.getElementById('newbutton').disabled=false;
    if (document.querySelector("#id_voided")) {
      toggleVoided();
    };
    if (document.querySelector("#id_objectsubtype")) {
      loadObjectSubtypes();
      document.getElementById("id_objectsubtype").innerHTML = localStorage.getItem("id_objectsubtype");
    };
    handleDependentFields();
    highlightRequiredSelect2Fields();
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
    handleDependentFields();
    highlightRequiredSelect2Fields();
  };
}

function handleDependentFields() {
  if (document.querySelector("#details")) {
    switch(document.getElementById("details").name) {
      case "SUForm":
        // there is a tracing displayed, so display worldfile
        if (document.querySelector("#onscreen")) {
          document.getElementById("id_worldfile").closest("div.form-group").hidden = false;
        };
        // a tracing is selected, but not yet saved, so show worldfile widget and make it required
        if (document.querySelector("#id_tracing") && document.getElementById("id_tracing").value) {
          document.getElementById("id_worldfile").closest("div.form-group").hidden = false;
          document.getElementById("id_worldfile").required = true;
        };
        break;
      case "ObjectForm":
        // material is Stone, Metal, or Shell, so show the appropriate material subtype widget
        switch (document.getElementById("id_material").value) {
          case "Stone":
            document.getElementById("id_stonesubtype").closest("div.form-group").hidden = false;
            document.getElementById("id_stonesubtype").required = true;
            document.getElementById("id_metalsubtype").closest("div.form-group").hidden = true;
            document.getElementById("id_metalsubtype").required = false;
            document.getElementById("id_shellsubtype").closest("div.form-group").hidden = true;
            document.getElementById("id_shellsubtype").required = false;
            break;
          case "Metal":
            document.getElementById("id_stonesubtype").closest("div.form-group").hidden = true;
            document.getElementById("id_stonesubtype").required = false;
            document.getElementById("id_metalsubtype").closest("div.form-group").hidden = false;
            document.getElementById("id_metalsubtype").required = true;
            document.getElementById("id_shellsubtype").closest("div.form-group").hidden = true;
            document.getElementById("id_shellsubtype").required = false;
            break;
          case "Shell":
            document.getElementById("id_stonesubtype").closest("div.form-group").hidden = true;
            document.getElementById("id_stonesubtype").required = false;
            document.getElementById("id_metalsubtype").closest("div.form-group").hidden = true;
            document.getElementById("id_metalsubtype").required = false;
            document.getElementById("id_shellsubtype").closest("div.form-group").hidden = false;
            document.getElementById("id_shellsubtype").required = true;
            break;
          default:
            ["stone", "metal", "shell"].forEach(material => {
              document.getElementById(`id_${material}subtype`).closest("div.form-group").hidden = true;
              document.getElementById(`id_${material}subtype`).required = false;
            });
        };
        // subtype is Clay Slab or Sealing, so show clayslaborsealingmarking
        let currentsubtype = ""
        if (document.getElementById("id_objecttype").selectedIndex > -1) {
          currentsubtype = document.getElementById("id_objecttype").selectedOptions[0].text;
        };
        if (document.getElementById("id_objecttype").selectedOptions[0].text === "Administrative") {
          switch (currentsubtype) {
            case "Clay Slab":
            case "Sealing":
              document.getElementById("id_clayslaborsealingmarking").closest("div.form-group").hidden = false;
              document.getElementById("id_clayslaborsealingmarking").required = true;
              break;
            default:
              document.getElementById("id_clayslaborsealingmarking").closest("div.form-group").hidden = true;
              document.getElementById("id_clayslaborsealingmarking").required = false;
          };
          // subtype is Sealing, so show sealingfunction
          if (currentsubtype === "Sealing") {
            document.getElementById("id_sealingfunction").closest("div.form-group").hidden = false;
            document.getElementById("id_sealingfunction").required = true;
          } else {
            document.getElementById("id_sealingfunction").closest("div.form-group").hidden = true;
            document.getElementById("id_sealingfunction").required = false;
          };
        };
        // subtype is Blade, so show bladeserration
        if (document.getElementById("id_objecttype").selectedOptions[0].text === "Lithic" && document.getElementById("id_objectsubtype").selectedOptions[0].text === "Blade"){
          document.getElementById("id_bladeserration").closest("div.form-group").hidden = false;
          document.getElementById("id_bladeserration").required = true;
        } else {
          document.getElementById("id_bladeserration").closest("div.form-group").hidden = true;
          document.getElementById("id_bladeserration").required = false;
        };
        // senttobaghdad is checked, so show baghdadnumber
        if (document.getElementById("id_senttobaghdad").checked) {
          document.getElementById("id_baghdadnumber").closest("div.form-group").hidden = false;
          document.getElementById("id_baghdadnumber").required = true;
        } else {
          document.getElementById("id_baghdadnumber").closest("div.form-group").hidden = true;
          document.getElementById("id_baghdadnumber").required = false;
        };
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
      alert("Be sure to write in the notes why this record is being voided.");
    } else {
      labels.forEach(label => {
        label.classList.remove('voided');
      });
    };
  };
}

function highlightRequiredSelect2Fields() {
  const select2widgets = document.querySelectorAll(".select2-selection");
  select2widgets.forEach(field => {
    const selectfield = field.closest(".form-group").querySelector("select");
    let optionselected = false
    selectfield.querySelectorAll("option").forEach(option => {
      if (option.innerText) {
        optionselected = true;
      };
    });
    if (selectfield.required && (!selectfield.querySelector("option") || !optionselected)) {
      field.setAttribute("style", "border-color: red;");
    } else {
      field.removeAttribute("style");
    };
  });
}

async function loadLocale() {
  const su_id = document.getElementById("id_su").value;
  await fetch(`/ajax/load_locale/?su_id=${su_id}`)
    .then(response => response.json())
    .then(data => {
      document.getElementById("id_locale").value = data[0].name;
    });
}

async function loadObjectSubtypes() {
  const subtypemenu = document.getElementById("id_objectsubtype");
  subtypemenu.options.length = 0;
  subtypemenu.add(document.createElement('option'));  // add a blank dummy option
  const objecttype_id = document.getElementById("id_objecttype").value;
  if (objecttype_id){
    await fetch(`/ajax/load_objectsubtypes/?objecttype_id=${objecttype_id}`)
      .then(response => response.json())
      .then(data => {
        data.forEach(subtype => {
          var newOption = document.createElement('option');
          newOption.value = subtype[0];
          newOption.text = subtype[1];
          subtypemenu.add(newOption);
        });
      });
  }
  if (subtypemenu.options.length > 1) {
    subtypemenu.closest("div.form-group").hidden = false;
    subtypemenu.required = true;
  } else {
    subtypemenu.closest("div.form-group").hidden = true;
    subtypemenu.required = false;
  };
}

async function loadNextObjectNumberForSeason() {
  const season = document.getElementById("id_season").selectedOptions[0].innerText;
  await fetch(`/ajax/load_nextnumber/?season=${season}`)
    .then(response => response.json())
    .then(data => {
      document.getElementById("id_number").value = data;
      document.getElementById("id_excavationnumber").value = season;
    });
  const savedState = JSON.parse(localStorage.getItem("initialState"))
  if (localStorage.getItem("okToChangeLapIdentifier") === "false") {
    if (confirm("Are you sure that you want to change this record’s number?")) {
      localStorage.setItem("okToChangeLapIdentifier", "true");
    } else {
      document.getElementById("id_number").value = savedState.number;
      document.getElementById("id_excavationnumber").value = savedState.excavationnumber;
      document.getElementById("id_season").value = savedState.season;
    };
  } else if (document.getElementById("id_season").value == savedState.season) {
    document.getElementById("id_number").value = savedState.number;
    document.getElementById("id_excavationnumber").value = savedState.excavationnumber;
    checkForm();
  };
}

function showImage(thewidget, original) {
  const image = thewidget;
  new Viewer(image, {url(image) {return original}, title: false, navbar: false, toolbar: false,});
}
