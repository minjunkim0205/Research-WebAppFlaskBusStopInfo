function renderMapMultiple(targetId, stationList) {
    if (!stationList.length) return;

    const map = L.map(targetId);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19
    }).addTo(map);

    const bounds = L.latLngBounds();

    stationList.forEach(station => {
        const lat = parseFloat(station.lat);
        const lng = parseFloat(station.lng);

        if (isNaN(lat) || isNaN(lng)) return;

        const latlng = L.latLng(lat, lng);

        L.marker(latlng)
            .addTo(map)
            .bindPopup(`<strong>${station.name}</strong><br/>ID: ${station.arsId}<br/><a href="/station/${station.arsId}">조회</a>`);

        bounds.extend(latlng);
    });

    if (!bounds.isValid()) {
        console.warn("Invalid bounds: no valid markers to fit");
        return;
    }

    map.fitBounds(bounds);
}

document.addEventListener("DOMContentLoaded", function () {
    if (typeof stationData !== 'undefined') {
        renderMapMultiple("map", stationData);
    }
});