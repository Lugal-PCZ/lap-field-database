function submitCleanURL(form) {
  var controls = form.elements;
  for (var i=0, num=controls.length; i<num; i++) {
    controls[i].disabled = controls[i].value == '';
  };
  form.submit();
}

function saveForm() {
  const initialState = FormSerializer.serialize(document.getElementById('detail'));
  localStorage.setItem("initialState", JSON.stringify(initialState));
}

function checkForm() {
  const currentState = FormSerializer.serialize(document.getElementById('detail'));
  if (JSON.stringify(currentState) !== localStorage.getItem("initialState")) {
    document.getElementById('savebutton').disabled=false;
  } else {
    document.getElementById('savebutton').disabled=true;
  };
}
