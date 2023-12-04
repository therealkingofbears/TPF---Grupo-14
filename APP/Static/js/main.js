/*
    Constante global con la URL de la API.
    Cuando la API esté disponible en internet, cambiar su URL.
*/

const URL = "http://127.0.0.1:5000";

document.querySelector("#addRecetaModal form").onsubmit = agregarReceta;
document.querySelector("#deleteRecetaModal form").onsubmit = borrarReceta;
document.querySelector("#editRecetaModal form").onsubmit = modificarReceta;
// document.querySelector("#editRecetaModal form").onsubmit = modificarReceta;


obtenerTodasLasRecetas();