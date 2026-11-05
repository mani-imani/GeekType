/* GeekType page: theme switch (System / Light / Dark) and copy buttons.
   Everything works without it; the page just follows the system theme. */
(function () {
  var root = document.documentElement;
  var KEY = "geekmani-theme";

  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function save(value) {
    try {
      if (value) { localStorage.setItem(KEY, value); } else { localStorage.removeItem(KEY); }
    } catch (e) { /* private mode: the choice just lasts for this visit */ }
  }
  function apply(value) {
    if (value === "light" || value === "dark") { root.setAttribute("data-theme", value); }
    else { root.removeAttribute("data-theme"); }
  }

  var seg = document.querySelector(".gm-seg");
  if (seg) {
    var buttons = seg.querySelectorAll("button");
    var mark = function (value) {
      for (var i = 0; i < buttons.length; i++) {
        buttons[i].setAttribute("aria-pressed", String((buttons[i].getAttribute("data-theme") || "system") === (value || "system")));
      }
    };
    var current = stored();
    apply(current);
    mark(current);
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].addEventListener("click", function () {
        var value = this.getAttribute("data-theme");
        value = value === "system" ? null : value;
        save(value); apply(value); mark(value);
      });
    }
  }

  var copyButtons = document.querySelectorAll(".copy");
  for (var j = 0; j < copyButtons.length; j++) {
    copyButtons[j].addEventListener("click", function () {
      var button = this;
      var text = button.parentNode.querySelector("pre").innerText.replace(/\n$/, "");
      var done = function () {
        button.setAttribute("data-done", "true");
        setTimeout(function () { button.removeAttribute("data-done"); }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () {});
      }
    });
  }
})();
