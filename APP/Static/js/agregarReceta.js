const inputNombre = document.getElementById("inputNombreRecetaAdd");
const inputImagen = document.getElementById("inputImagenRecetaAdd");
const inputIngredientes = document.getElementById("inputIngredientesRecetaAdd");
const inputInstrucciones = document.getElementById("inputInstruccionesRecetaAdd");
const inputAlcohol = document.getElementById("inputAlcoholRecetaAdd");

const agregarReceta = async (evt) => {
    evt.preventDefault();
    console.log("Formulario enviado");
    try {
        const formData = new FormData();
        formData.append("imagen", inputImagen.files[0]);
        formData.append("nombre", inputNombre.value);
        formData.append("ingredientes", inputIngredientes.value);
        formData.append("instrucciones", inputInstrucciones.value);
        formData.append("alcohol", inputAlcohol.value);
        const opcionesFetch = {
            method: 'POST',
            body: formData
        }
        const resp = await fetch(`${URL}/recetas`, opcionesFetch);

        const contentType = resp.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            // La respuesta es en formato JSON
            const jsonResponse = await resp.json();
            console.log("Respuesta del servidor (JSON):", jsonResponse);

            if (resp.ok) {
                alert("Receta agregada exitosamente");
                inputImagen.value = "";
                inputNombre.value = "";
                inputIngredientes.value = "";
                inputInstrucciones.value = "";
                inputAlcohol.value = "";
                ocultarModal('addRecetaModal');
                obtenerTodasLasRecetas();
            }
            else {
                throw new Error('Error al agregar la receta. Respuesta del servidor: ${JSON.stringify(jsonResponse)}');
            }
        } else {
            // La respuesta no es en formato JSON
            throw new Error(`Error al agregar la receta. Respuesta del servidor: ${JSON.stringify(jsonResponse)}`);

        }
    } catch (err) {
        console.error(err);
    }
}

