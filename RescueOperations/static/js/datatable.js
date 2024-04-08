// JavaScript code
document.getElementById('downloadButton').addEventListener('click', function(event) {
    event.preventDefault(); 
});
document.addEventListener("DOMContentLoaded", function() {
    var searchInput = document.getElementById("searchInput");

    // Event listener for input change
    searchInput.addEventListener("input", function() {
        var searchText = searchInput.value.toLowerCase();
        var headings = document.querySelectorAll("h2");

        // Iterate through headings
        headings.forEach(function(heading) {
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
    
    console.log(selectedFiles);
    if (selectedFiles.includes('PDF')) {
        var xhrPdf = new XMLHttpRequest();
        xhrPdf.open("GET", "/generate_pdf/?deviceID=" + deviceID + "&deviceName=" + deviceName + "&id=" + id, true);
        xhrPdf.responseType = "blob"; 
        
        xhrPdf.onreadystatechange = function() {
            if (xhrPdf.readyState === 4 && xhrPdf.status === 200) {
                var aPdf = document.createElement("a");
                var urlPdf = window.URL.createObjectURL(xhrPdf.response);
                aPdf.href = urlPdf;
                aPdf.download = "ChildRescue.pdf"; 
                document.body.appendChild(aPdf);
                aPdf.click(); 
                window.URL.revokeObjectURL(urlPdf); 
                var alertDiv = document.createElement("div");
                alertDiv.className = "alert alert-info alert-dismissible";
                alertDiv.role = "alert";
                alertDiv.style="text-align:center";
                alertDiv.innerHTML = `
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true"><i class="notika-icon notika-close"></i></span>
                </button> 
                PDF has been successfully downloaded.`;
                var alert_msg=document.getElementById('alert_msg')
                alert_msg.appendChild(alertDiv);
            }
            else{
                var alertDiv = document.createElement("div");
                alertDiv.className = "alert alert-danger alert-dismissible";
                alertDiv.role = "alert";
                alertDiv.style="text-align:center";
                alertDiv.innerHTML = `
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true"><i class="notika-icon notika-close"></i></span>
                </button> 
                Something Went Wrong!!.`;
                var alert_msg=document.getElementById('alert_msg')
                alert_msg.appendChild(alertDiv);
            }
        };
        
        xhrPdf.send();
    }


    if(selectedFiles.includes('CSV')) {
        var xhrCsv = new XMLHttpRequest();
        xhrCsv.open("GET", "/generate_csv/?deviceID=" + id + "&deviceName=" + deviceName, true);
        xhrCsv.responseType = "blob";
        
        xhrCsv.onreadystatechange = function() {
            if (xhrCsv.readyState === 4 && xhrCsv.status === 200) {
                var aCsv = document.createElement("a");
                var urlCsv = window.URL.createObjectURL(xhrCsv.response);
                aCsv.href = urlCsv;
                aCsv.download = "ChildRescue.csv";
                document.body.appendChild(aCsv);
                aCsv.click();
                window.URL.revokeObjectURL(urlCsv);
                var alertDiv = document.createElement("div");
                alertDiv.className = "alert alert-info alert-dismissible";
                alertDiv.role = "alert";
                alertDiv.style="text-align:center";
                alertDiv.innerHTML = `
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true"><i class="notika-icon notika-close"></i></span>
                </button> 
                CSV has been successfully downloaded.`;
                var alert_msg=document.getElementById('alert_msg')
                alert_msg.appendChild(alertDiv);
            }
            else{
                var alertDiv = document.createElement("div");
                alertDiv.className = "alert alert-danger alert-dismissible";
                alertDiv.role = "alert";
                alertDiv.style="text-align:center";
                alertDiv.innerHTML = `
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true"><i class="notika-icon notika-close"></i></span>
                </button> 
                Something Went Wrong!!.`;
                var alert_msg=document.getElementById('alert_msg')
                alert_msg.appendChild(alertDiv);
            }
        };
        
        xhrCsv.send();
    }
}



    
    