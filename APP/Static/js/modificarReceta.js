const inputNombre = document.getElementById("inputNombreRecetaPut");
const inputImagen = document.getElementById("inputImagenRecetaPut");
const inputIngredientes = document.getElementById("inputIngredientesRecetaPut");
const inputInstrucciones = document.getElementById("inputInstruccionesRecetaPut");
const inputAlcohol = document.getElementById("inputAlcoholRecetaPut");
const inputIDReceta = document.getElementById("inputIDRecetaAEditar");

document.getElementById("putRecetaModal").addEventListener('show.bs.modal', evt => {
    const recetaId = evt.relatedTarget.getAttribute('data-bs-receta-id');
    inputIDReceta.value = recetaId;
});

const modificarReceta = async (evt) => {
    evt.preventDefault();
    try {
        const formData = new FormData();
        const id = inputIDReceta.value;
        // formData.append("id", inputIDReceta.value);
        formData.append("imagen", inputImagen.files[0]);
        formData.append("nombre", inputNombre.value);
        formData.append("ingredientes", inputIngredientes.value);
        formData.append("instrucciones", inputInstrucciones.value);
        formData.append("alcohol", inputAlcohol.value);
        const opcionesFetch = {
            method: 'PUT',
            body: formData
        }
        const resp = await fetch(`${URL}/recetas/${id}`, opcionesFetch);
        if (resp.ok) {
            alert("Receta modificada exitosamente");
            inputImagen.value = "";
            inputNombre.value = "";
            inputIngredientes.value = "";
            inputInstrucciones.value = "";
            inputAlcohol.value = "";
            ocultarModal('putRecetaModal');
            obtenerTodasLasRecetas();
        }
        else {
            throw new Error('Error al editar la receta.');
        }
    } catch(err) {
        console.error(err);
    }
}

const recetaNombre = recetaData => {
    return `<input type="text" class="input" name="nombre" id="inputNombreRecetaPut" required placeholder=">${recetaData.nombre}" />`
}

const recetaIngredientes = recetaData => {
    return `${recetaData.ingredientes}`
}

const recetaInstrucciones = recetaData => {
    return `${recetaData.instrucciones}`
}