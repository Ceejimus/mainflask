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
        createList(file.name);
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

                    var percent = Math.floor((e.loaded / e.total) * 100);
                    document.getElementById(file.name).childNodes[0].style.width = percent*94.565/100 + '%';
                    document.getElementById(file.name).childNodes[1].innerHTML = percent + '%';

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
                    document.getElementById(file.name).childNodes[0].setAttribute('class', 'progress-bar progressBarC');
                    document.getElementById(file.name).childNodes[1].setAttribute('class', 'progress-bar statusBarC');
                    document.getElementById(file.name).childNodes[1].innerHTML = "Success!";
                    console.log(data);
                },
            error: function(data) {
                    document.getElementById(file.name).childNodes[1].innerHTML = "Failure";
                    console.log(data);
            }
        });
        
    };

    var createList = function(filename) {
        var progDiv = document.createElement('div');
        progDiv.setAttribute('id', filename);
        progDiv.setAttribute('class', 'progress progressDivC');
        var progBar = document.createElement('div');
        progBar.setAttribute('class', 'progress-bar progress-bar-striped active progressBarC');
        progBar.setAttribute('aria-valuenow', '0');
        progBar.setAttribute('aria-valuemax', '100');
        progBar.setAttribute('role', 'progressbar');
        var progBarPara = document.createElement('p');
        progBarPara.innerHTML = filename;
        progBarPara.style.paddingLeft = '25px';
        progBar.appendChild(progBarPara);
        //progBar.innerHTML = filename;
        var statBar = document.createElement('div');
        statBar.setAttribute('class', 'progress-bar progress-bar-striped active statusBarC');
        statBar.setAttribute('role', 'progressbar');
        statBar.innerHTML = 'Queued';
        progDiv.appendChild(progBar);
        progDiv.appendChild(statBar);
        $("#list").append(progDiv);
        /*var newAnchor = document.createElement('anchor');
        newAnchor.setAttribute('class', 'list-group-item list-group-item-success');
        newAnchor.innerHTML = filename;
        var newSpan = document.createElement('span');
        newSpan.setAttribute('class', 'badge alert-success pull-left');
        newSpan.setAttribute('id', filename);
        newSpan.innerHTML = 'Queued';
        newAnchor.appendChild(newSpan);
        $("#list").append(newAnchor);
        console.log(document.getElementById(filename));*/
    }

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