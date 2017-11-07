function getQueryVariable(variable) {
  var query = window.location.search.substring(1);
  var vars = query.split('&');
  for (var i = 0; i < vars.length; i++) {
      var pair = vars[i].split('=');
      if (decodeURIComponent(pair[0]) == variable) {
          return decodeURIComponent(pair[1]);
      }
  }
  return 0;
}

var selectNode = document.getElementById('limit_select');
selectNode.onchange = function() {
  offset = getQueryVariable('offset');
  window.location.search = '?limit=' + selectNode.value + '&offset=' + offset;
};