// Initialize the Ace editor
const editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode("ace/mode/json");
editor.setValue(JSON.stringify({
    data: [{
        type: "scatter",
        x: [1, 2, 3, 4],
        y: [10, 15, 13, 17],
        mode: "lines+markers"
    }],
    layout: {
        title: "Sample Plot",
        xaxis: { title: "X Axis" },
        yaxis: { title: "Y Axis" }
    }
}, null, 2));

// Keep track of current configuration
let currentConfigName = "";

// Initialize the visualization
function updatePreview() {
    try {
        const config = JSON.parse(editor.getValue());
        Plotly.react("preview", config.data, config.layout);
    } catch (error) {
        console.error("Error updating preview:", error);
        alert("Error in plot configuration. Please check the JSON syntax.");
    }
}

// Save the current configuration
async function saveConfig() {
    try {
        const name = document.getElementById("configName").value.trim();
        if (!name) {
            alert("Please enter a configuration name");
            return;
        }

        const config = JSON.parse(editor.getValue());
        const response = await fetch(`/api/configs/${name}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(config)
        });

        const result = await response.json();
        if (result.status === "success") {
            alert("Configuration saved successfully");
            currentConfigName = name;
            loadConfigs();
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        console.error("Error saving configuration:", error);
        alert("Error saving configuration: " + error.message);
    }
}

// Load a specific configuration
async function loadConfig(name) {
    try {
        const response = await fetch(`/api/configs/${name}`);
        const result = await response.json();
        
        if (result.status === "success") {
            editor.setValue(JSON.stringify(result.config, null, 2));
            editor.clearSelection();
            document.getElementById("configName").value = name;
            currentConfigName = name;
            updatePreview();
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        console.error("Error loading configuration:", error);
        alert("Error loading configuration: " + error.message);
    }
}

// Delete a configuration
async function deleteConfig(name, event) {
    event.stopPropagation();
    if (!confirm(`Are you sure you want to delete "${name}"?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/configs/${name}`, {
            method: "DELETE"
        });
        const result = await response.json();
        
        if (result.status === "success") {
            alert("Configuration deleted successfully");
            if (name === currentConfigName) {
                editor.setValue(JSON.stringify({
                    data: [{
                        type: "scatter",
                        x: [1, 2, 3, 4],
                        y: [10, 15, 13, 17],
                        mode: "lines+markers"
                    }],
                    layout: {
                        title: "Sample Plot",
                        xaxis: { title: "X Axis" },
                        yaxis: { title: "Y Axis" }
                    }
                }, null, 2));
                document.getElementById("configName").value = "";
                currentConfigName = "";
                updatePreview();
            }
            loadConfigs();
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        console.error("Error deleting configuration:", error);
        alert("Error deleting configuration: " + error.message);
    }
}

// Update the configuration list
function updateConfigList(configs) {
    const configList = document.getElementById("configList");
    configList.innerHTML = "";
    
    configs.forEach(config => {
        const configItem = document.createElement("div");
        configItem.className = "config-item";
        
        const details = document.createElement("div");
        details.innerHTML = `
            <strong>${config.name}</strong><br>
            <small>Type: ${config.type}<br>
            Modified: ${new Date(config.last_modified).toLocaleString()}</small>
        `;
        
        const deleteBtn = document.createElement("button");
        deleteBtn.className = "delete-btn";
        deleteBtn.textContent = "Delete";
        deleteBtn.onclick = (e) => deleteConfig(config.name, e);
        
        configItem.appendChild(details);
        configItem.appendChild(deleteBtn);
        configItem.onclick = () => loadConfig(config.name);
        
        configList.appendChild(configItem);
    });
}

// Load all configurations
async function loadConfigs() {
    try {
        const response = await fetch("/api/configs");
        const result = await response.json();
        
        if (result.status === "success") {
            updateConfigList(result.configs);
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        console.error("Error loading configurations:", error);
        alert("Error loading configurations: " + error.message);
    }
}

// Search configurations
let searchTimeout;
document.getElementById("searchInput").addEventListener("input", (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
        try {
            const query = e.target.value.trim();
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const result = await response.json();
            
            if (result.status === "success") {
                updateConfigList(result.configs);
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error("Error searching configurations:", error);
            alert("Error searching configurations: " + error.message);
        }
    }, 300);
});

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
    loadConfigs();
    updatePreview();
});
