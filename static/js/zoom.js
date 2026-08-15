document.addEventListener("click", function (event) {
  const img = event.target.closest(".zoomable");
  if (!img) return;

  const zoomedContainer = document.createElement("div");
  zoomedContainer.classList.add("zoomed-image-container");

  const zoomedImage = document.createElement("img");
  zoomedImage.classList.add("zoomed-image");
  zoomedImage.src = img.src;
  zoomedImage.alt = img.alt;

  zoomedContainer.appendChild(zoomedImage);
  document.body.appendChild(zoomedContainer);

  function cerrar() {
    zoomedContainer.remove();
    document.removeEventListener("keydown", onKeydown);
  }

  function onKeydown(e) {
    if (e.key === "Escape") cerrar();
  }

  zoomedContainer.addEventListener("click", cerrar);
  document.addEventListener("keydown", onKeydown);
});
