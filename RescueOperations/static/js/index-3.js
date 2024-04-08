document.addEventListener("DOMContentLoaded", function() {
    var searchInput = document.getElementById("searchInput");
    var deviceContainers = document.querySelectorAll(".device-container");

    searchInput.addEventListener("input", function() {
        var searchTerm = searchInput.value.toLowerCase();
        deviceContainers.forEach(function(container) {
            var deviceName = container.querySelector("span").innerText.toLowerCase();
            var deviceId = container.querySelector("h2").innerText.toLowerCase();
            if (deviceName.includes(searchTerm) || deviceId.includes(searchTerm)) {
                container.style.display = "block";
            } else {
                container.style.display = "none";
            }
        });
    });
});
