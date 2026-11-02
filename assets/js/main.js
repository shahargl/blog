(function () {
  var root = document.documentElement;
  var darkQuery = window.matchMedia("(prefers-color-scheme: dark)");

  function storedTheme() {
    var theme = localStorage.getItem("theme");
    return theme === "light" || theme === "dark" ? theme : "auto";
  }

  function effectiveTheme() {
    var theme = storedTheme();
    if (theme !== "auto") return theme;
    return darkQuery.matches ? "dark" : "light";
  }

  function giscusTheme() {
    return effectiveTheme() === "dark" ? "transparent_dark" : "light";
  }

  function syncGiscus() {
    var frame = document.querySelector("iframe.giscus-frame");
    if (!frame) return;
    frame.contentWindow.postMessage(
      { giscus: { setConfig: { theme: giscusTheme() } } },
      "https://giscus.app"
    );
  }

  function applyTheme(theme) {
    if (theme === "auto") {
      localStorage.removeItem("theme");
      delete root.dataset.theme;
    } else {
      localStorage.setItem("theme", theme);
      root.dataset.theme = theme;
    }
    document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
      var label = "Color scheme: " + theme;
      button.dataset.mode = theme;
      button.setAttribute("aria-label", label);
      button.title = label;
    });
    syncGiscus();
  }

  var themeCycle = { auto: "light", light: "dark", dark: "auto" };
  document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
    button.addEventListener("click", function () {
      applyTheme(themeCycle[storedTheme()]);
    });
  });
  darkQuery.addEventListener("change", syncGiscus);
  applyTheme(storedTheme());

  document.querySelectorAll("[data-copy-markdown]").forEach(function (button) {
    var label = button.textContent;
    button.addEventListener("click", function () {
      fetch(button.dataset.copyMarkdown)
        .then(function (response) {
          if (!response.ok) throw new Error(response.statusText);
          return response.text();
        })
        .then(function (text) {
          return navigator.clipboard.writeText(text);
        })
        .then(
          function () { button.textContent = "copied"; },
          function () { button.textContent = "copy failed"; }
        )
        .finally(function () {
          setTimeout(function () { button.textContent = label; }, 1500);
        });
    });
  });

  document.querySelectorAll(".heatmap-scroll").forEach(function (element) {
    element.scrollLeft = element.scrollWidth;
  });

  var heatmaps = document.querySelectorAll(".heatmap-scroll svg");
  if (heatmaps.length) {
    var tip = document.createElement("div");
    tip.className = "heatmap-tip";
    tip.hidden = true;
    document.body.appendChild(tip);

    var showTip = function (cell) {
      tip.replaceChildren();
      cell.dataset.tip.split("\n").forEach(function (line, index) {
        var row = document.createElement("div");
        if (index === 0) row.className = "heatmap-tip-title";
        row.textContent = line;
        tip.appendChild(row);
      });
      tip.hidden = false;
      var box = cell.getBoundingClientRect();
      var left = box.left + box.width / 2 - tip.offsetWidth / 2;
      var top = box.top - tip.offsetHeight - 8;
      if (top < 8) top = box.bottom + 8;
      tip.style.left = Math.max(8, Math.min(left, window.innerWidth - tip.offsetWidth - 8)) + "px";
      tip.style.top = top + "px";
    };
    var hideTip = function () { tip.hidden = true; };

    heatmaps.forEach(function (svg) {
      var onCell = function (event) {
        if (event.target.dataset && event.target.dataset.tip) showTip(event.target);
      };
      svg.addEventListener("mouseover", onCell);
      svg.addEventListener("click", onCell);
      svg.addEventListener("mouseleave", hideTip);
    });
    window.addEventListener("scroll", hideTip, { passive: true });
    document.querySelectorAll(".heatmap-scroll").forEach(function (element) {
      element.addEventListener("scroll", hideTip, { passive: true });
    });
  }

  var comments = document.getElementById("comments");
  if (comments) {
    var script = document.createElement("script");
    script.src = "https://giscus.app/client.js";
    script.async = true;
    script.crossOrigin = "anonymous";
    Object.keys(comments.dataset).forEach(function (key) {
      script.dataset[key] = comments.dataset[key];
    });
    script.dataset.theme = giscusTheme();
    comments.appendChild(script);
  }
})();
