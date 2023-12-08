const inputNombreRecetaPut = document.getElementById("inputNombreRecetaPut");
const inputImagenRecetaPut = document.getElementById("inputImagenRecetaPut");
const inputIngredientesRecetaPut = document.getElementById("inputIngredientesRecetaPut");
const inputInstruccionesRecetaPut = document.getElementById("inputInstruccionesRecetaPut");
const inputAlcoholRecetaPut = document.getElementById("inputAlcoholRecetaPut");
const inputIDRecetaAEditar = document.getElementById("inputIDRecetaAEditar");

document.getElementById("editRecetaModal").addEventListener('show.bs.modal', evt => {
    const recetaId = evt.relatedTarget.getAttribute('data-bs-receta-id');
    inputIDRecetaAEditar.value = recetaId;
});

const modificarReceta = async (evt) => {
    evt.preventDefault();
    try {
        const formData = new FormData();
        const id = inputIDRecetaAEditar.value;
        // formData.append("id", inputIDReceta.value);
        formData.append("imagen", inputImagenRecetaPut.files[0]);
        formData.append("nombre", inputNombreRecetaPut.value);
        formData.append("ingredientes", inputIngredientesRecetaPut.value);
        formData.append("instrucciones", inputInstruccionesRecetaPut.value);
        formData.append("alcohol", inputAlcoholRecetaPut.value);
        const opcionesFetch = {
            method: 'PUT',
            body: formData
        }
        console.log("Intentando modificar");
        const resp = await fetch(`${URL}/api/recetas/${id}`, opcionesFetch);
        console.log("Aún intentando modificar");
        if (resp.ok) {
            alert("Receta modificada exitosamente");
            inputIDRecetaAEditar.value = "";
            inputImagenRecetaPut.value = "";
            inputNombreRecetaPut.value = "";
            inputIngredientesRecetaPut.value = "";
            inputInstruccionesRecetaPut.value = "";
            inputAlcoholRecetaPut.value = "";
            ocultarModal('editRecetaModal');
            obtenerTodasLasRecetas();
        }
        else {
            throw new Error('Error al editar la receta.');
        }
    } catch(err) {
        console.error(err);
    }
}