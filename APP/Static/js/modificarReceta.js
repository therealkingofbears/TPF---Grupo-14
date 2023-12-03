const inputNombre = document.getElementById("inputNombreRecetaPut");
const inputImagen = document.getElementById("inputImagenRecetaPut");
const inputIngredientes = document.getElementById("inputIngredientesRecetaPut");
const inputInstrucciones = document.getElementById("inputInstruccionesRecetaPut");
const inputAlcohol = document.getElementById("inputAlcoholRecetaPut");

const modificarReceta = async (evt) => {
    evt.preventDefault();
    try {
        const formData = new FormData();
        formData.append("imagen", inputImagen.files[0]);
        formData.append("nombre", inputNombre.value);
        formData.append("ingredientes", inputIngredientes.value);
        formData.append("instrucciones", inputInstrucciones.value);
        formData.append("alcohol", inputAlcohol.value);
        const opcionesFetch = {
            method: 'PUT',
            body: formData
        }
        const resp = await fetch(`${URL}/recetas`, opcionesFetch);
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

