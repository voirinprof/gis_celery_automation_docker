var map = L.map('map').setView([48.8566, 2.3522], 13); // Centré sur Paris
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);

var markers = [];
var bufferLayer = null;

map.on('click', function(e) {
    var radius = parseInt(document.getElementById('radius').value);
    fetch('/add_point', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lat: e.latlng.lat, lon: e.latlng.lng, radius: radius })
    }).then(response => response.json()).then(data => {
        updatePoints();
    });
});

function updatePoints() {
    fetch('/get_points')
        .then(response => response.json())
        .then(points => {
            markers.forEach(marker => map.removeLayer(marker));
            markers = [];
            points.forEach(pt => {
                var marker = L.marker([pt.lat, pt.lon])
                    .bindPopup(`Rayon: ${pt.radius} m`)
                    .addTo(map);
                markers.push(marker);
            });
        });
}

function computeBuffers() {
    document.getElementById('status').innerText = 'Calcul en cours...';
    fetch('/compute_buffers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
    })
        .then(response => response.json())
        .then(data => {
            pollTaskStatus(data.task_id);
        });
}

function pollTaskStatus(task_id) {
    fetch(`/task_status/${task_id}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('status').innerText = `État: ${data.state}`;
            if (data.state === 'SUCCESS') {
                if (bufferLayer) map.removeLayer(bufferLayer);
                bufferLayer = L.geoJSON(data.buffers, {
                    style: { color: 'blue', fillOpacity: 0.3 }
                }).addTo(map);
                map.fitBounds(bufferLayer.getBounds());
                document.getElementById('status').innerText = 'Calcul terminé!';
            } else if (data.state === 'FAILURE') {
                document.getElementById('status').innerText = `Erreur: ${data.status}`;
            } else {
                setTimeout(() => pollTaskStatus(task_id), 1000);
            }
        });
}

updatePoints();