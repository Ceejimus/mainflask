var FileUpload = (function() {
    'use strict';

    var Urls = {};
    var UploadStatus = {};

    var getElements = function() {
        return {
            DropZone: $("#drop-zone"),
            FoldersSelect: $("#folder-select")
        };
    };

    var startUpload = function(file, path, folder, onComplete) {
		createList(file.name);
        var formData = new FormData();
        formData.append("file", file, path);
        var promise = $.ajax({
            xhr : function() {
            var xhr = new window.XMLHttpRequest();

            xhr.upload.addEventListener('progress', function(e) {

                 if (e.lengthComputable) {

                    console.log('Bytes Loaded: ' + e.loaded + ' of ' + e.total + '(' + (e.loaded / e.total) + ')')

                    var percent = Math.floor((e.loaded / e.total) * 100);
					document.getElementById(file.name).childNodes[0].style.width = percent*94.565/100 + '%';
                    document.getElementById(file.name).childNodes[1].innerHTML = percent + '%';
                    
                }

             });

             return xhr;
            },
            url: Urls.UploadFile.replace('__FOLDER__', folder),
            method: "post",
            processData: false,
            contentType: false,
            data: formData,
            success: function(data) {
				document.getElementById(file.name).childNodes[0].setAttribute('class', 'progress-bar progressBarC');
                document.getElementById(file.name).childNodes[1].setAttribute('class', 'progress-bar statusBarC');
                document.getElementById(file.name).childNodes[1].innerHTML = "Success!";
                onComplete();
            },
            error: function(data) {
				document.getElementById(file.name).childNodes[1].innerHTML = "Failure";
                onComplete();
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
        var statBar = document.createElement('div');
        statBar.setAttribute('class', 'progress-bar progress-bar-striped active statusBarC');
        statBar.setAttribute('role', 'progressbar');
        statBar.innerHTML = 'Queued';
        progDiv.appendChild(progBar);
        progDiv.appendChild(statBar);
        $("#list").append(progDiv);
    }

    var uploadFiles = function(folder, fileList) {
        console.log('uploading files', fileList, folder);

        if (fileList.length === 0) {
            console.log('done');
            return;
        }

        var fileToUpload = fileList.pop();
        fileToUpload.file(function(file) {
            startUpload(file, fileToUpload.fullPath, folder, function() { uploadFiles(folder, fileList) });
        });
    };

    var scanFiles = function(item, id, upload) {
        var fileList = []
        if (item.isFile) {
            item.file(function(file) {
                UploadStatus[id]['files'].push(item);
            });
        } else {
            var dirReader = item.createReader();
            dirReader.readEntries(function(entries) {
                for (var i = 0; i < entries.length; i++) {
                    scanFiles(entries[i], id, upload);
                }
            });
        }
        return fileList;
    };

    var getFilePaths = function(files) {
        var paths = []
        var i;
        for (i = 0; i < files.length; i++) {
            paths.push(files[i].fullPath);
        }
        return paths;
    };

    var startScan = function(dir, folder) {
        var path = dir.fullPath;
        UploadStatus[path] = {
            'files': [],
            'intervalId': null
        };

        scanFiles(dir, path, null);

        var lastList = getFilePaths(UploadStatus[path]['files'].slice());

        UploadStatus[path]['intervalId'] = setInterval(function() {
            var diff = false;
            var currentList = getFilePaths(UploadStatus[path]['files'].slice());
            for (var i = 0; i < currentList.length; i++) {
                if (lastList.indexOf(currentList[i]) > 0) {
                    diff = true;
                    break;
                }
            }

            if (diff !== true) {
                clearInterval(UploadStatus[path]['intervalId']);
                var filesToUpload = UploadStatus[path]['files'].slice();
                console.log(fileToUpload);
                uploadFiles(folder, fileToUpload);
            };

            lastList = currentList;
        }, 1300);
    };

    var bindEvents = function(elements) {
        elements.DropZone.on('drop', function(e) {

            console.log(elements);
            var folder = elements.FoldersSelect.val();

            $(this).addClass('upload-drop-zone');

            var fileList = []

            var items = e.originalEvent.dataTransfer.items;
            for (var i = 0; i < items.length; i++) {
                // webkitGetAsEntry is where the magic happens
                var item = items[i].webkitGetAsEntry();
                if (item === undefined || item === null)
                    continue;

                if (item.isFile)
                    console.log('files not supported yet')

                console.log(item)
                startScan(item, folder);
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