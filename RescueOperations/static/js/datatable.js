// JavaScript code
document.getElementById('downloadButton').addEventListener('click', function (event) {
    event.preventDefault();
});
document.addEventListener("DOMContentLoaded", function () {
    var searchInput = document.getElementById("searchInput");

    // Event listener for input change
    searchInput.addEventListener("input", function () {
        var searchText = searchInput.value.toLowerCase();
        var headings = document.querySelectorAll("h2");

        // Iterate through headings
        headings.forEach(function (heading) {
            var headingText = heading.textContent.toLowerCase();
            // Check if heading contains search text
            if (headingText.includes(searchText)) {
                // Scroll to heading
                heading.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    });
});




function download(deviceID, deviceName, id) {
    var checkedCheckboxes = document.querySelectorAll('input[name="fileType"]:checked');
    var selectedFiles = [];

    checkedCheckboxes.forEach(function(checkbox) {
        selectedFiles.push(checkbox.value);
    });

    // Get CSRF token from a hidden input field in the HTML
    var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    if (selectedFiles.includes('PDF')) {
        var xhrPdf = new XMLHttpRequest();
        xhrPdf.open("GET", "/generate_pdf/?deviceID=" + deviceID + "&deviceName=" + deviceName + "&id=" + id, true);
        xhrPdf.setRequestHeader('X-CSRFToken', csrfToken); // Set CSRF token in request header
        xhrPdf.responseType = "blob";

        xhrPdf.onreadystatechange = function() {
            if (xhrPdf.readyState === 4) {
                if (xhrPdf.status === 200) {
                    var link = document.createElement('a');
                    link.href = "/generate_pdf/?deviceID=" + deviceID + "&deviceName=" + deviceName + "&id=" + id;
                    link.download = "ChildRescue.pdf";
                    link.click();
                    displaySuccessMessage("PDF");
                } else {
                    displayErrorMessage();
                }
            }
        };

        xhrPdf.send();
    }

    if (selectedFiles.includes('CSV')) {
        var xhrCsv = new XMLHttpRequest();
        xhrCsv.open("GET", "/generate_csv/?deviceID=" + id + "&deviceName=" + deviceName, true);
        xhrCsv.setRequestHeader('X-CSRFToken', csrfToken); // Set CSRF token in request header
        xhrCsv.responseType = "blob";

        xhrCsv.onreadystatechange = function() {
            if (xhrCsv.readyState === 4) {
                if (xhrCsv.status === 200) {
                    var link = document.createElement('a');
                    link.href = "/generate_csv/?deviceID=" + deviceID + "&deviceName=" + deviceName + "&id=" + id;
                    link.download = "ChildRescue.csv";
                    link.click();
                    displaySuccessMessage("CSV");
                } else {
                    displayErrorMessage();
                }
            }
        };

        xhrCsv.send();
    }
}



function displaySuccessMessage(fileType) {
    var alertDiv = document.createElement("div");
    alertDiv.className = "alert alert-info alert-dismissible";
    alertDiv.role = "alert";
    alertDiv.style = "text-align:center";
    alertDiv.innerHTML = `
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true"><i class="notika-icon notika-close"></i></span>
            </button> 
            ${fileType} has been successfully downloaded.`;
    var alert_msg = document.getElementById('alert_msg');
    alert_msg.appendChild(alertDiv);
}

function displayErrorMessage() {
    var alertDiv = document.createElement("div");
    alertDiv.className = "alert alert-danger alert-dismissible";
    alertDiv.role = "alert";
    alertDiv.style = "text-align:center";
    alertDiv.innerHTML = `
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true"><i class="notika-icon notika-close"></i></span>
            </button> 
            Something Went Wrong!!`;
    var alert_msg = document.getElementById('alert_msg');
    alert_msg.appendChild(alertDiv);
}









