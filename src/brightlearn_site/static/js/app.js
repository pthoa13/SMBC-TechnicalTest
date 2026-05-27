document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-language]");
  if (!button) {
    return;
  }

  document.dispatchEvent(
    new CustomEvent("brightlearn:language-selected", {
      detail: { language: button.dataset.language },
    }),
  );
});
