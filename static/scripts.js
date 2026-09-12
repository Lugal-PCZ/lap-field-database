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

function resetForm() {
  document.getElementById("details").reset();
  location.reload()
}

function saveResultsList(ids_list) {
  localStorage.setItem('listview', window.location.href);
  localStorage.setItem('ids_list', ids_list);
}

function returnToListView() {
  window.open(localStorage.getItem('listview'), '_self');
}

function makePrevAndNextRecordLinks() {
  if (document.querySelector("#details")) {
    const ids_list = localStorage.getItem("ids_list").split(",")
    const current_id = window.location.pathname.split('/').filter(entry => entry !== '').pop();
    const currentIdIndex = ids_list.indexOf(current_id);
    const prevId = ids_list[currentIdIndex - 1];
    const nextId = ids_list[currentIdIndex + 1];
    const prevUrl = window.location.pathname.replace(`/${current_id}/`, `/${prevId}/`);
    const nextUrl = window.location.pathname.replace(`/${current_id}/`, `/${nextId}/`);
    if (prevId) {
      document.getElementById("prev_record").setAttribute("href", prevUrl);
      document.getElementById("prev_record").style["visibility"] = "visible"
    };
    if (nextId) {
      document.getElementById("next_record").setAttribute("href", nextUrl);
      document.getElementById("next_record").style["visibility"] = "visible"
    };
  };
}

function handleDependentFields() {
  if (document.querySelector("#details")) {
    switch (document.getElementById("details").name) {
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
        // nolot is checked, so hide lot
        if (document.getElementById("id_nolot").checked) {
          document.getElementById("id_lot").closest("div.form-group").hidden = true;
          document.getElementById("id_lot").required = false;
          document.getElementById("id_lot").innerHTML = '';
          document.getElementById("select2-id_lot-container").removeAttribute("title");
          document.getElementById("id_su").required = true;
          document.getElementById("id_su").nextSibling.style.width = document.getElementById("id_lot").nextSibling.style.width;
          document.getElementById("id_su").closest("div.form-group").hidden = false;
          document.getElementById("id_su_display").closest("div.form-group").hidden = true;
        } else {
          document.getElementById("id_lot").closest("div.form-group").hidden = false;
          document.getElementById("id_lot").required = true;
          document.getElementById("id_su").required = false;
          document.getElementById("id_su").closest("div.form-group").hidden = true;
          document.getElementById("id_su_display").closest("div.form-group").hidden = false;
        };
        // lot is entered, so populate SU field
        if (document.getElementById("id_lot").value) {
          loadSU('object');
        };
        // SU is entered, so populate area and locale fields
        if (document.getElementById("id_su").value) {
          loadLocale('object');
        };
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
              document.getElementById(`id_${material}subtype`).value = '';
            });
        };
        // subtype is Clay Slab or Sealing, so show clayslaborsealingmarking
        let currentsubtype = ""
        if (document.getElementById("id_objectsubtype").selectedIndex > -1) {
          currentsubtype = document.getElementById("id_objectsubtype").selectedOptions[0].text;
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
              document.getElementById("id_clayslaborsealingmarking").value = '';
          };
          // subtype is Sealing, so show sealingfunction
          if (currentsubtype === "Sealing") {
            document.getElementById("id_sealingfunction").closest("div.form-group").hidden = false;
            document.getElementById("id_sealingfunction").required = true;
          } else {
            document.getElementById("id_sealingfunction").closest("div.form-group").hidden = true;
            document.getElementById("id_sealingfunction").required = false;
            document.getElementById("id_sealingfunction").value = '';
          };
        };
        // subtype is Blade, so show bladeserration
        if (document.getElementById("id_objecttype").selectedOptions[0].text === "Lithic" && document.getElementById("id_objectsubtype").selectedOptions[0].text === "Blade"){
          document.getElementById("id_bladeserration").closest("div.form-group").hidden = false;
          document.getElementById("id_bladeserration").required = true;
        } else {
          document.getElementById("id_bladeserration").closest("div.form-group").hidden = true;
          document.getElementById("id_bladeserration").required = false;
          document.getElementById("id_bladeserration").value = '';
        };
        // senttobaghdad is checked, so show baghdadnumber
        if (document.getElementById("id_senttobaghdad").checked) {
          document.getElementById("id_baghdadnumber").closest("div.form-group").hidden = false;
          document.getElementById("id_baghdadnumber").required = true;
        } else {
          document.getElementById("id_baghdadnumber").closest("div.form-group").hidden = true;
          document.getElementById("id_baghdadnumber").required = false;
        };
        // published is checked, so show publicationcitations
        if (document.getElementById("id_published").checked) {
          document.getElementById("id_publicationcitations").closest("div.form-group").hidden = false;
          document.getElementById("id_publicationcitations").required = true;
        } else {
          document.getElementById("id_publicationcitations").closest("div.form-group").hidden = true;
          document.getElementById("id_publicationcitations").required = false;
        };
        break;
      case "SampleForm":
        // lot is entered, so populate SU, Area, and Locale fields
        if (document.getElementById("id_lot").value) {
          loadSU('sample');
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
    } else {
      labels.forEach(label => {
        label.classList.remove('voided');
      });
    };
  };
}

function voidedAlert() {
  if (document.getElementById("id_voided").checked) {
    alert("Be sure to write in the notes why this record is being voided.");
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
    if (selectfield.required && (!selectfield.options || !optionselected)) {
      field.style.borderColor = "red";
      field.style.borderWidth = "2px";
    } else {
      field.style.borderColor = null;
      field.style.borderWidth = null;
    };
  });
}

function showImage(thewidget, original) {
  const image = thewidget;
  new Viewer(image, {url(image) {return original}, title: false, navbar: false, toolbar: false,});
}

async function loadSU(recordtype) {
  const lot_id = document.getElementById("id_lot").value;
  await fetch(`/${recordtype}/ajax/load_su/?lot_id=${lot_id}`)
    .then(response => response.json())
    .then(data => {
      switch  (recordtype) {
        case "object":
          document.getElementById("id_su").length = 0;
          document.getElementById("id_su").value = data.su.id;
          var newOption = document.createElement("option");
          newOption.value = data.su.id;
          newOption.text = data.su.name;
          document.getElementById("id_su").add(newOption);
          document.getElementById("select2-id_su-container").setAttribute("title", data.su.name);
          document.getElementById("select2-id_su-container").innerHTML = data.su.name;
          document.getElementById("id_su").value = data.su.id;
          document.getElementById("id_su_display").value = data.su.name;
          document.getElementById("id_area").value = data.area;
          document.getElementById("id_locale").value = data.locale;
          break;
        case "sample":
          document.getElementById("id_su").value = data.su.name;
          document.getElementById("id_area").value = data.area;
          document.getElementById("id_locale").value = data.locale;
          break;
      };
      // also load the exavationdate with the date that the lot was assigned
      if (!document.getElementById("id_excavationdate").value) {
        document.getElementById("id_excavationdate").value = data.lot_dateassigned;
      };
    });
}

async function loadLocale(recordtype) {
  const su_id = document.getElementById("id_su").value;
  await fetch(`/${recordtype}/ajax/load_locale/?su_id=${su_id}`)
    .then(response => response.json())
    .then(data => {
      document.getElementById("id_locale").value = data.locale;
      if (document.querySelector("#id_area")) {
        document.getElementById("id_area").value = data.area;
      };
    });
}

async function loadNextRecordNumberForSeason(recordtype) {
  const season = document.getElementById("id_season").selectedOptions[0].innerText;
  await fetch(`/${recordtype}/ajax/load_nextnumber/?season=${season}`)
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

async function loadObjectSubtypes() {
  const subtypemenu = document.getElementById("id_objectsubtype");
  subtypemenu.options.length = 0;
  subtypemenu.add(document.createElement('option'));  // add a blank dummy option
  const objecttype_id = document.getElementById("id_objecttype").value;
  if (objecttype_id){
    await fetch(`/object/ajax/load_objectsubtypes/?objecttype_id=${objecttype_id}`)
      .then(response => response.json())
      .then(data => {
        data.forEach(subtype => {
          var newOption = document.createElement("option");
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
