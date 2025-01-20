document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll(".btn");
  buttons.forEach(btn => {
      btn.addEventListener("mouseenter", () => btn.classList.add("btn-outline-light"));
      btn.addEventListener("mouseleave", () => btn.classList.remove("btn-outline-light"));
  });
});
