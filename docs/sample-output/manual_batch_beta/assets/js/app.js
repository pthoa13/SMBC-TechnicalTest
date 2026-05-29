document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-language]");
  if (!button) {
    return;
  }

  const switcher = button.closest(".book-page")?.querySelector("[data-summary-switcher]");
  const output = switcher?.querySelector("[data-summary-output]");
  const language = button.dataset.language;
  const summary = switcher?.dataset[`summary${language[0].toUpperCase()}${language.slice(1)}`];

  if (!switcher || !output || !summary) {
    return;
  }

  output.textContent = summary;
  button.parentElement
    ?.querySelectorAll("[data-language]")
    .forEach((item) => item.setAttribute("aria-pressed", "false"));
  button.setAttribute("aria-pressed", "true");
});
