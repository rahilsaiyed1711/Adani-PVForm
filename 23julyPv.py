function loadData(block) {
    fetch(`/load_data?plant=${currentPlant}&block=${block}`)
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                document.getElementById('data').innerHTML = '<p>No data available</p>';
                return;
            }

            // Use the keys from the first row to define headers
            const headers = Object.keys(data[0]);

            let table = '<table><tr>';
            headers.forEach(header => {
                table += `<th>${header}</th>`;
            });
            table += '</tr>';

            // Populate rows with data
            data.forEach(row => {
                table += '<tr>';
                headers.forEach(header => {
                    table += `<td contenteditable="true">${row[header] || ''}</td>`;
                });
                table += '<td><button class="delete-button" onclick="deleteRow(this)">Delete</button></td>';
                table += '</tr>';
            });

            table += '</table>';
            document.getElementById('data').innerHTML = table;
        });
}
