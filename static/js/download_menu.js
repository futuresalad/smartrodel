 // Get a reference to the select element and the download button
 var fileSelect = document.getElementById('file-select');
 var downloadButton = document.getElementById('download-button');
 
 // Get a reference to the hidden download link
 var downloadLink = document.getElementById('download-link');
 
 // Function to update the dropdown menu
 function updateDropdown() {
   // Clear the dropdown menu
   fileSelect.innerHTML = '';
   
   // Use an XMLHttpRequest to get the list of files from the server
   var xhr = new XMLHttpRequest();
   xhr.open('GET', '/get-files');
   xhr.responseType = 'json';
   xhr.onload = function() {
     if (xhr.status === 200) {
       var fileList = xhr.response;
       
       // Loop through the list of files and add an option element for each file
       for (var i = 0; i < fileList.length; i++) {
         var file = fileList[i];
         var option = document.createElement('option');
         option.value = file.path;
         option.text = file.name;
         fileSelect.add(option);
       }
     }
   };
   xhr.send();
 }
 
 // Update the dropdown menu when the page loads
 updateDropdown();
 
 // When the user clicks the download button
 downloadButton.addEventListener('click', function() {
    // Get the selected file
    var file = fileSelect.value;
    
    // Set the href of the download link to the selected file
    downloadLink.href = file;
    
    // Set the download attribute of the download link to the file name
    downloadLink.download = file.substring(file.lastIndexOf('/') + 1);
    
    // Simulate a click on the download link
    downloadLink.click();
  });