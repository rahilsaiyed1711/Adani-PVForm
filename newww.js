function loadData(block) {
    fetch(`/load_data?plant=${currentPlant}&block=${block}`)
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                document.getElementById('data').innerHTML = '<p>No data available</p>';
                return;
            }

            // Create table with only the "Actions" column at the end
            let table = '<table><tr>';
            for (let key in data[0]) {
                if (key !== 'Actions') {
                    table += `<th>${key}</th>`;
                }
            }
            table += `<th>Actions</th></tr>`;
            
            data.forEach(row => {
                table += '<tr>';
                for (let key in row) {
                    if (key !== 'Actions') {
                        table += `<td contenteditable="true">${row[key]}</td>`;
                    }
                }
                table += '<td><button class="delete-button" onclick="deleteRow(this)">Delete</button></td></tr>';
            });
            table += '</table>';
            document.getElementById('data').innerHTML = table;
        });
}
