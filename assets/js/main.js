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
    document.querySelectorAll("[data-theme-choice]").forEach(function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.themeChoice === theme));
    });
    syncGiscus();
  }

  document.querySelectorAll("[data-theme-choice]").forEach(function (button) {
    button.addEventListener("click", function () {
      applyTheme(button.dataset.themeChoice);
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
