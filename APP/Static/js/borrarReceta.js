const inputIDRecetaABorrar = document.getElementById("inputIDRecetaABorrar")

document.getElementById("deleteRecetaModal").addEventListener('show.bs.modal', evt => {
    const recetaId = evt.relatedTarget.getAttribute('data-bs-receta-id');
    inputIDRFecetaABorrar.value = recetaId;
});

const borrarReceta = async (evt) => {
    evt.preventDefault();
    try {
        const id = inputIDRecetaABorrar.value;
        const opcionesFetch = {
            method: 'DELETE'
        }
        const resp = await fetch(`${URL}/api/recetas/${id}`, opcionesFetch);
        if (resp.ok) {
            alert("Receta borrada exitosamente");
            ocultarModal('deleteRecetaModal');
            await obtenerTodasLasRecetas();
        }
        else {
            throw new Error('Error al borrar la receta.');
        }
    } catch(err) {
        console.error(err);
    }
}