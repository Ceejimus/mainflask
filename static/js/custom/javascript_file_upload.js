var FileUpload = (function() {
    'use strict';

    var Urls = {}

    var getElements = function() {
        return {
            DropZone: $("#drop-zone"),
            FoldersSelect: $("#folder-select")
        };
    };

    var startUpload = function(file, path, folder) {
        var formData = new FormData();
        formData.append("file", file, path+file.name);
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
            url: Urls.UploadFile.replace('__REPLACE__', folder),
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

    var traverseFileTree = function(item, callback, path=null) {
      path = path || "";
      if (item.isFile) {
        // Get file
        item.file(function(file) {
          console.log("File:", path + file.name);
          callback(file, path);
        });
      } else if (item.isDirectory) {
        // Get folder contents
        var dirReader = item.createReader();
        dirReader.readEntries(function(entries) {
          for (var i=0; i<entries.length; i++) {
            traverseFileTree(entries[i], callback, path + item.name + "/");
          }
        });
      }
    };

    var bindEvents = function(elements) {
        elements.DropZone.on('drop', function(e) {

            console.log(elements);
            var folder = elements.FoldersSelect.val();

            var uploadFunc = function(item, path) {
                return startUpload(item, path, folder);
            };

            $(this).addClass('upload-drop-zone');

            var items = e.originalEvent.dataTransfer.items;
            for (var i=0; i<items.length; i++) {
                // webkitGetAsEntry is where the magic happens
                var item = items[i].webkitGetAsEntry();
                if (item) {
                    traverseFileTree(item, uploadFunc);
                }
            }

            e.stopPropagation();
            e.preventDefault();
            
        }).on('dragover', function(e) {
            $(this).addClass('drop');
            return false;
        }).on('dragleave', function(e) {
            $(this).removeClass('drop');
            return false;
        });
    };

    var init = function(urls) {
        Urls = urls;
        var elements = getElements();

        elements.FoldersSelect.selectize({
            create: false
        });

        bindEvents(elements);
    };

    return {
        Init: init
    };
})();