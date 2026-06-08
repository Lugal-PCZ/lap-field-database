function toggleLogin() {
  document.getElementById("login").toggleAttribute("hidden");
  if (document.querySelector("#username")) {
    document.getElementById("username").focus();
  };
}

function submitCleanURL(form) {
  const controls = form.elements;
  for (var i=0, num=controls.length; i<num; i++) {
    controls[i].disabled = controls[i].value == '';
  };
  form.submit();
}

function saveForm() {
  if (document.querySelector("#detail")) {
    const initialState = FormSerializer.serialize(document.getElementById('detail'));
    localStorage.setItem("initialState", JSON.stringify(initialState));
  };
}

function checkForm() {
  if (document.querySelector("#detail")) {
    const currentState = FormSerializer.serialize(document.getElementById('detail'));
    if (JSON.stringify(currentState) !== localStorage.getItem("initialState")) {
      document.getElementById('savebutton').disabled=false;
    } else {
      document.getElementById('savebutton').disabled=true;
    };
    if (document.querySelector("#id_voided")) {
      toggleVoided();
    }
  };
}

function toggleVoided() {
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
}
