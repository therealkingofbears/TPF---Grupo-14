const obtenerTodasLasRecetas = async (evt) => {
    try {
        const resp = await fetch(`${URL}/recetas`);
        if (resp.ok) {
            const data = await resp.json();
            console.log(data)
            const cuerpoDeTabla = document.querySelector("#tablaDeRecetas>tbody");
            cuerpoDeTabla.innerHTML = "";
            data.forEach(ing => {
                const fila = document.createElement('tr');
                fila.innerHTML = nuevaFila(ing);
                cuerpoDeTabla.appendChild(fila);
            })
        }
        else {
            throw new Error('Error al obtener las recetas.');
        }
    } catch(err) {
        console.log("algo malio sal");
    }
}

const nuevaFila = recetaData => {
    return `
    <td><img src="/app/Static/img/${recetaData.imagen}" alt="Imagen de ${recetaData.nombre}" height="100vw" width="auto"></td>
    <td>${recetaData.nombre}</td>
    <td>${recetaData.ingredientes}</td>
    <td>${recetaData.instrucciones}</td>
    <td>${recetaData.tiene_alcohol}</td>
    <td>
        <a href="#editRecetaModal" class="edit" data-bs-toggle="modal" data-bs-receta-id=${recetaData.id}><i class="material-icons" data-bs-toggle="tooltip" title="Edit">&#xE254;</i></a>
        <a href="#deleteRecetaModal" class="delete" data-bs-toggle="modal" data-bs-receta-id=${recetaData.id}><i class="material-icons" data-bs-toggle="tooltip" title="Delete">&#xE872;</i></a>
    </td>
    `
}