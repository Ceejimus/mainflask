var FileUpload = (function() {
    'use strict';

    var getElements = function() {
        return {
            DropZone: $("#drop-zone"),
            UploadForm: $("#js-upload-form")
        };
    };

    var startUpload = function(files, path) {
        var formData = new FormData();
        formData.append("file", files, path+files.name);
        var promise = $.ajax({
            xhr : function() {
            var xhr = new window.XMLHttpRequest();

            xhr.upload.addEventListener('progress', function(e) {

                 if (e.lengthComputable) {

                    console.log('Bytes Loaded: ' + e.loaded);
                    console.log('Total Size: ' + e.total);
                    console.log('Percentage Uploaded: ' + (e.loaded / e.total))

                    var percent = Math.round((e.loaded / e.total) * 100);

                    $('#progressBar').attr('aria-valuenow', percent).css('width', percent + '%').text(percent + '%');

                }

             });

             return xhr;
            },
            url: "/uploader",
            method: "post",
            processData: false,
            contentType: false,
            data: formData,
            success: function(data) {
                    console.log(data);
                },
            error: function(data) {
                    console.log(data);
            }
        });
        
    };

    var traverseFileTree = function(item, path) {
      path = path || "";
      if (item.isFile) {
        // Get file
        item.file(function(file) {
          console.log("File:", path + file.name);
          startUpload(file, path);
        });
      } else if (item.isDirectory) {
        // Get folder contents
        var dirReader = item.createReader();
        dirReader.readEntries(function(entries) {
          for (var i=0; i<entries.length; i++) {
            traverseFileTree(entries[i], path + item.name + "/");
          }
        });
      }
    };

    var bindEvents = function(elements) {
        elements.UploadForm.on('submit', function(e) {
            console.log("debug2")
            e.preventDefault();
            var files = e.originalEvent.dataTransfer.files;
            startUpload(files)
        })

        elements.DropZone.on('drop', function(e) {
            e.stopPropagation();
            e.preventDefault();
            console.log(e)
            $(this).addClass('upload-drop-zone');
            console.log("debug3")
            // startUpload(e.originalEvent.dataTransfer.files);
            var items = e.originalEvent.dataTransfer.items;
              for (var i=0; i<items.length; i++) {
                // webkitGetAsEntry is where the magic happens
                var item = items[i].webkitGetAsEntry();
                if (item) {
                  traverseFileTree(item);
                }
              }
        }).on('dragover', function(e) {
            $(this).addClass('drop');
            return false;
        }).on('dragleave', function(e) {
            $(this).removeClass('drop');
            return false;
        });
    };

    var init = function() {
        console.log("debug1")
        var elements = getElements();
        bindEvents(elements);
    };

    return {
        Init: init
    };
})();