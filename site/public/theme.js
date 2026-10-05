// A saved override wins; otherwise initialize from the system preference.
(() => {
  const system = window.matchMedia("(prefers-color-scheme: dark)");
  let storage;
  let overridden = false;
  let mode = system.matches ? "dark" : "light";
  try {
    storage = window.localStorage;
    const saved = storage.getItem("textprov:theme");
    if (saved === "light" || saved === "dark") { mode = saved; overridden = true; }
  } catch { /* The page-local control still works. */ }
  const apply = () => { document.documentElement.dataset.theme = mode; };
  apply();
  document.addEventListener("DOMContentLoaded", () => {
    const button = document.querySelector("[data-theme-toggle]");
    if (!button) return;
    const update = () => {
      const next = mode === "dark" ? "light" : "dark";
      button.textContent = next === "light" ? "☀️" : "🌙";
      button.setAttribute("aria-label", `Switch to ${next} mode`);
      button.title = `Switch to ${next} mode`;
    };
    update();
    button.hidden = false;
    button.addEventListener("click", () => {
      mode = mode === "dark" ? "light" : "dark";
      overridden = true;
      apply();
      update();
      try { storage?.setItem("textprov:theme", mode); } catch { /* Page-local override. */ }
    });
    system.addEventListener("change", () => {
      if (overridden) return;
      mode = system.matches ? "dark" : "light";
      apply();
      update();
    });
  });
})();
