import pandas as pd
from flask import Flask, request, jsonify, render_template, render_template_string, session, redirect, url_for
import socket
import webbrowser
from threading import Timer
from google.cloud import bigquery
from google.oauth2 import service_account

client = bigquery.Client(credentials=credentials, project=project_id)
Tablename = "Static_plants"
selectQuery = "SELECT * FROM agel-svc-winddata-dmz-prod.winddata." + Tablename

df = client.query(selectQuery).to_dataframe()
plants = df.Plantname.unique()

def listToString(s):
    return "".join(s)

def remove(string):
    return string.replace(" ", "")

app = Flask(__name__)
app.secret_key = 'your_secret_key'      # Change this to a random secret key for session management

USERNAME = 'admin'
PASSWORD = 'password123'

@app.route('/load_data')
def load_data():
    plant = request.args.get('plant')
    block = request.args.get('block')
    filter_plant = df[df['Plantname'] == plant]
    mytable = filter_plant.Tablename.unique()
    mytable = listToString(mytable)
    mytable = remove(mytable)
    selectQuery = "SELECT * FROM agel-svc-winddata-dmz-prod.winddata." + mytable + " WHERE Plant = '" + plant + "'"
    df1 = client.query(selectQuery).to_dataframe()
    df2 = df1[df1['Plant'] == plant]
    host = socket.gethostname()
    if block:
        block_data = df2[df2['Block'] == block]
        return jsonify(block_data.to_dict(orient='records'))
    blocks = df2.Block.unique()
    # Calculate summary statistics
    rt = df2.astype(str)
    rt['DCCapacityKWp'] = pd.to_numeric(rt['DCCapacityKWp'], errors='coerce')
    totalblocks = len(rt.Block.unique())
    rt1 = rt[rt.DCCapacityKWp.notnull()]
    totaldcMWp = round(sum(rt1['DCCapacityKWp']) / 1000, 2)
    invMake = rt.INVMake.unique()
    invMake = str(invMake)
    invModel = str(rt.INVERTERModel.unique())
    modMake = str(rt.Modulemake.unique())
    ModModel = str(rt.ModuleModel.unique())
    stringcounts = len(rt.STRINGS.notnull())

    summary = {
        'total_blocks': totalblocks,
        'total_dc_mwp': totaldcMWp,
        'strCount': stringcounts,
        'invMake': invMake,
        'total_invModel': invModel,
        'total_modMake': modMake,
        'total_ModModel': ModModel
    }

    return jsonify({
        'blocks': blocks.tolist(),
        'summary': summary
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'})
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f9f9f9;
            margin: 0;
        }
        .login-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 300px;
        }
        .login-container h2 {
            margin-bottom: 20px;
        }
        .login-container input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .login-container button {
            width: 100%;
            padding: 10px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .login-container button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>Login</h2>
        <form method="post">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
    """)

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PV Form</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f9f9f9;
            margin: 0;
            padding: 0;
            background-image: url("https://github.com/Tusharlad123/PVform/blob/main/solar-881.gif?raw=true");
            background-repeat: no-repeat;
            background-size: cover;
        }
        .summary-container {
            padding: 20px;
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-top: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .summary-row {
            display: flex;
            justify-content: space-between;
        }
        .summary-item {
            width: 45%;
        }
        .header {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            background-color: #fff;
            position: relative;
        }
        .underline {
            width: 100%;
            height: 5px;
            background: linear-gradient(90deg, #0a7caa, #5b58a5, #0056b3, #8f298f, #0a7caa);
            background-size: 500% 100%;
            animation: colorChange 3s infinite;
        }
        @keyframes colorChange {
            0% { background-position: 0% 0%; }
            25% { background-position: 25% 0%; }
            50% { background-position: 50% 0%; }
            75% { background-position: 75% 0%; }
            100% { background-position: 100% 0%; }
        }
        .logo {
            width: 150px;
            position: absolute;
            left: 20px;
        }
        .main-content {
            padding: 20px;
        }
        h1 {
            font-size: 5rem;
            text-align: center;
            margin-top: -1rem;
            margin-bottom: 0;
            animation: changeColor infinite 3s;
        }
        @keyframes changeColor {
            0% { color: #0a7caa; }
            25% { color: #5b58a5; }
            50% { color: #0056b3; }
            75% { color: #8f298f; }
            100% { color: #0a7caa; }
        }
        .dropdown-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 10px;
            gap: 20px;
        }
        .dropdown {
            width: 200px;
            padding: 10px;
            background-color: #fff;
            border: 2px solid #007BFF;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        .dropdown:focus {
            border-color: #005bb3;
            box-shadow: 0 0 8px rgba(0, 91, 187, 0.5);
            outline: none;
        }
        .search-bar {
            display: block;
            width: 300px;
            padding: 10px;
            margin: 20px auto;
            background-color: #fff;
            border: 2px solid #007BFF;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        .search-bar:focus {
            border-color: #005bb3;
            box-shadow: 0 0 8px rgba(0, 91, 187, 0.5);
            outline: none;
        }
        .button {
            background-color: #007BFF;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s ease;
        }
        .button:hover {
            background-color: #0056b3;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            border: 1px solid #ddd;
            text-align: left;
        }
        th {
            background-color: #007BFF;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
        .checkbox-cell {
            text-align: center;
        }
        .delete-button {
            background-color: #FF0000;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s ease;
        }
        .delete-button:hover {
            background-color: #cc0000;
        }
    </style>
</head>
<body>
    <header class="header">
        <img src="https://github.com/Tusharlad123/PVform/blob/main/adani-logo.png?raw=true" alt="Logo" class="logo">
        <h1>Adani Green Energy</h1>
    </header>
    <div class="underline"></div>
    <div class="main-content">
        <div class="dropdown-container">
            <select id="plantDropdown" class="dropdown">
                <option value="">Select Plant</option>
                {% for plant in plants %}
                    <option value="{{ plant }}">{{ plant }}</option>
                {% endfor %}
            </select>
            <select id="blockDropdown" class="dropdown">
                <option value="">Select Block</option>
            </select>
        </div>
        <div class="summary-container">
            <div class="summary-row">
                <div class="summary-item">Total Blocks: <span id="totalBlocks"></span></div>
                <div class="summary-item">Total DC MWp: <span id="totalDcMWp"></span></div>
            </div>
            <div class="summary-row">
                <div class="summary-item">Inverter Make: <span id="invMake"></span></div>
                <div class="summary-item">Inverter Model: <span id="total_invModel"></span></div>
            </div>
            <div class="summary-row">
                <div class="summary-item">Module Make: <span id="total_modMake"></span></div>
                <div class="summary-item">Module Model: <span id="total_ModModel"></span></div>
            </div>
            <div class="summary-row">
                <div class="summary-item">String Count: <span id="strCount"></span></div>
            </div>
        </div>
        <input type="text" id="searchInput" class="search-bar" placeholder="Search...">
        <table id="dataTable">
            <thead>
                <tr>
                    {% for column in df1.columns %}
                        <th>{{ column }}</th>
                    {% endfor %}
                    <th class="checkbox-cell"><input type="checkbox" id="selectAll"></th>
                </tr>
            </thead>
            <tbody>
                <!-- Data rows will be added here dynamically -->
            </tbody>
        </table>
        <button class="delete-button" id="deleteSelected">Delete Selected</button>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function () {
            const plantDropdown = document.getElementById('plantDropdown');
            const blockDropdown = document.getElementById('blockDropdown');
            const searchInput = document.getElementById('searchInput');
            const selectAllCheckbox = document.getElementById('selectAll');
            const deleteSelectedButton = document.getElementById('deleteSelected');

            plantDropdown.addEventListener('change', function () {
                const plant = plantDropdown.value;
                if (plant) {
                    fetchBlocksAndSummary(plant);
                } else {
                    blockDropdown.innerHTML = '<option value="">Select Block</option>';
                }
            });

            blockDropdown.addEventListener('change', function () {
                const plant = plantDropdown.value;
                const block = blockDropdown.value;
                if (plant && block) {
                    loadData(plant, block);
                }
            });

            searchInput.addEventListener('input', function () {
                const searchTerm = searchInput.value.toLowerCase();
                filterTable(searchTerm);
            });

            selectAllCheckbox.addEventListener('change', function () {
                const checkboxes = document.querySelectorAll('tbody input[type="checkbox"]');
                checkboxes.forEach(checkbox => {
                    checkbox.checked = selectAllCheckbox.checked;
                });
            });

            deleteSelectedButton.addEventListener('click', function () {
                deleteSelectedRows();
            });

            function fetchBlocksAndSummary(plant) {
                fetch(`/load_data?plant=${plant}`)
                    .then(response => response.json())
                    .then(data => {
                        populateBlockDropdown(data.blocks);
                        updateSummary(data.summary);
                    })
                    .catch(error => console.error('Error fetching blocks:', error));
            }

            function populateBlockDropdown(blocks) {
                blockDropdown.innerHTML = '<option value="">Select Block</option>';
                blocks.forEach(block => {
                    const option = document.createElement('option');
                    option.value = block;
                    option.textContent = block;
                    blockDropdown.appendChild(option);
                });
            }

            function updateSummary(summary) {
                document.getElementById('totalBlocks').textContent = summary.total_blocks;
                document.getElementById('totalDcMWp').textContent = summary.total_dc_mwp;
                document.getElementById('invMake').textContent = summary.invMake;
                document.getElementById('total_invModel').textContent = summary.total_invModel;
                document.getElementById('total_modMake').textContent = summary.total_modMake;
                document.getElementById('total_ModModel').textContent = summary.total_ModModel;
                document.getElementById('strCount').textContent = summary.strCount;
            }

            function loadData(plant, block) {
                fetch(`/load_data?plant=${plant}&block=${block}`)
                    .then(response => response.json())
                    .then(data => {
                        populateTable(data);
                    })
                    .catch(error => console.error('Error loading data:', error));
            }

            function populateTable(data) {
                const tbody = document.querySelector('#dataTable tbody');
                tbody.innerHTML = '';
                data.forEach(row => {
                    const tr = document.createElement('tr');
                    {% for column in df1.columns %}
                        const td{{ column }} = document.createElement('td');
                        td{{ column }}.textContent = row.{{ column }};
                        tr.appendChild(td{{ column }});
                    {% endfor %}
                    const checkboxTd = document.createElement('td');
                    checkboxTd.className = 'checkbox-cell';
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkboxTd.appendChild(checkbox);
                    tr.appendChild(checkboxTd);
                    tbody.appendChild(tr);
                });
            }

            function filterTable(searchTerm) {
                const rows = document.querySelectorAll('#dataTable tbody tr');
                rows.forEach(row => {
                    const cells = Array.from(row.cells).slice(0, -1); // Exclude the last cell (checkbox cell)
                    const rowText = cells.map(cell => cell.textContent.toLowerCase()).join(' ');
                    row.style.display = rowText.includes(searchTerm) ? '' : 'none';
                });
            }

            function deleteSelectedRows() {
                const checkboxes = document.querySelectorAll('tbody input[type="checkbox"]:checked');
                checkboxes.forEach(checkbox => {
                    const row = checkbox.closest('tr');
                    row.remove();
                });
                selectAllCheckbox.checked = false;
            }
        });
    </script>
</body>
</html>
    """, plants=plants)

if __name__ == '__main__':
    port = 5000
    url = f"http://127.0.0.1:{port}"
    Timer(1, lambda: webbrowser.open(url)).start()
    app.run(port=port)
