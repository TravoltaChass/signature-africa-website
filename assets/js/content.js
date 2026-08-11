// Hydrates the page with the latest content.json — fetched straight from
// GitHub — so edits made in the /admin editor appear on the live site
// within moments, with no rebuild or redeploy needed.
(function () {
  var RAW_BASE = "https://raw.githubusercontent.com/Travoltachass/signature-africa-website/main/";

  function resolveUrl(value) {
    if (/^https?:\/\//i.test(value)) return value;
    return RAW_BASE + value.replace(/^\/+/, "");
  }

  function applyValue(el, value) {
    if (value == null) return;
    if (el.hasAttribute("data-img-key")) {
      var url = resolveUrl(value);
      if (el.tagName === "IMG") {
        el.setAttribute("src", url);
      } else {
        el.style.backgroundImage = "url('" + url + "')";
      }
      return;
    }
    var paras = String(value).split(/\n\s*\n/);
    el.innerHTML = paras.map(function (p) {
      return p.split("\n").join("<br>");
    }).join("</p><p>");
  }

  function hydrate(data) {
    document.querySelectorAll("[data-key]").forEach(function (el) {
      var path = el.getAttribute("data-key").split(".");
      var v = data;
      for (var i = 0; i < path.length; i++) {
        if (v == null) break;
        v = v[path[i]];
      }
      if (v != null) applyValue(el, v);
    });
    document.querySelectorAll("[data-img-key]").forEach(function (el) {
      var path = el.getAttribute("data-img-key").split(".");
      var v = data;
      for (var i = 0; i < path.length; i++) {
        if (v == null) break;
        v = v[path[i]];
      }
      if (v != null) applyValue(el, v);
    });
  }

  fetch(RAW_BASE + "content.json?_=" + Date.now(), { cache: "no-store" })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (data) { if (data) hydrate(data); })
    .catch(function () { /* fall back to the content baked into the HTML */ });
})();
