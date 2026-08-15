document.addEventListener("DOMContentLoaded", function () {
  const buscador = document.getElementById("buscador");
  const galeria = document.getElementById("galeria");
  if (!buscador || !galeria) return;

  const tarjetas = Array.from(galeria.querySelectorAll(".dino-card"));
  const vacio = document.getElementById("galeriaVacio");

  buscador.addEventListener("input", function () {
    const termino = buscador.value.trim().toLowerCase();
    let visibles = 0;

    tarjetas.forEach(function (tarjeta) {
      const nombre = (tarjeta.dataset.nombre || "").toLowerCase();
      const coincide = nombre.includes(termino);
      tarjeta.classList.toggle("galeria-oculto", !coincide);
      if (coincide) visibles++;
    });

    if (vacio) {
      vacio.classList.toggle("galeria-oculto", visibles !== 0);
    }
  });
});
