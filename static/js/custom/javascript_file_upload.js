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



    var buf2hex = function(buffer) { // buffer is an ArrayBuffer
        return Array.prototype.map.call(new Uint8Array(buffer), x => ('00' + x.toString(16)).slice(-2)).join('');
    };

    function bin2String(array) {
        var result = "";
        console.log(array.length)
        for (var i = 0; i < array.length; i++) {
            result += String.fromCharCode(parseInt(array[i], 2));
        }
        return result;
    };

    var uploadFile = function(file, dir_id, file_id, start, chunkSize, onComplete) {
        console.log('[UploadFile]', file, dir_id, file_id, start, chunkSize);
        var fileReader = new FileReader();
        fileReader.onload = function(progressEvent) {
            // var payload = bin2String(this.result);
            // console.log(this.result);
            $.ajax({
                url: Urls.UploadChunk,
                method: "post",
                contentType: 'application/json;charset=UTF-8',
                data: JSON.stringify({
                    dir_id: dir_id,
                    file_id: file_id,
                    start: start,
                    payload: this.result
                }),
                success: function(data) {
                    console.log('[success]');
                    if (start > file.size) {
                        onComplete();
                    } else {
                        uploadFile(file, dir_id, file_id, start + chunkSize, chunkSize, onComplete);
                    }
                    console.log(data);
                },
                error: function(data) {
                    console.log(data);
                }
            });
        };
        var chunk = file.slice(start, start + chunkSize);
        console.log('chunk size', chunk.byteLength)
        fileReader.readAsText(chunk);
    };

    var uploadFiles = function(folder, fileList) {
        console.log('uploading files', fileList, folder);

        if (fileList.length === 0) {
            console.log('done');
            return;
        }

        var fileToUpload = fileList.pop();
        fileToUpload.file(function(file) {
            startUpload(file, fileToUpload.fullPath, folder, function() { uploadFiles(folder, fileList) });
            // console.log('[heyhey]', file)
            // $.ajax({
            //     url: Urls.InitFileUpload,
            //     method: "post",
            //     contentType: 'application/json;charset=UTF-8',
            //     data: JSON.stringify({
            //         dir_id: dir_id,
            //         path: fileToUpload.fullPath,
            //         size: file.size
            //     }),
            //     success: function(data) {
            //         data = JSON.parse(data);
            //         var file_id = data['file_id'];
            //         uploadFile(file, dir_id, file_id, 0, (1 * 1024 * 1024), function() { uploadFiles(dir_id, fileList) });
            //     },
            //     error: function(data) {
            //         console.log(data);
            //         uploadFiles(dir_id, fileList);
            //     }
            // });
        });
    };

    var scanFiles = function(item, id, upload) {
        var fileList = []
        if (item.isFile) {
            item.file(function(file) {
                UploadStatus[id]['files'].push(item);
                // upload(file, path);
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
                uploadFiles(folder, UploadStatus[path]['files']);
            };

            lastList = currentList;
        }, 1300);
    };

    var uploadDir = function(dir, folder) {
        $.ajax({
            url: Urls.InitDirUpload,
            method: "post",
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify({
                folder: folder,
                name: dir.fullPath
            }),
            success: function(data) {
                data = JSON.parse(data);
                var dir_id = data['dir_id'];
                console.log(dir_id)
                startScan(dir_id, dir);
            },
            error: function(data) {
                console.log(data);
            }
        });
    };


    var startUpload = function(file, path, folder, onComplete) {
        var formData = new FormData();
        formData.append("file", file, path + file.name);
        // uploadFile(file, 'fakeid', 0, 1000, folder);
        var promise = $.ajax({
            xhr : function() {
            var xhr = new window.XMLHttpRequest();

            xhr.upload.addEventListener('progress', function(e) {

                 if (e.lengthComputable) {

                    console.log('Bytes Loaded: ' + e.loaded + ' of ' + e.total + '(' + (e.loaded / e.total) + ')')

                    var percent = Math.floor((e.loaded / e.total) * 100);

                    $('#progressBar').attr('aria-valuenow', percent).css('width', percent + '%').text(percent + '%');
                }

             });

             return xhr;
            },
            url: Urls.OldUpload.replace('__FOLDER__', folder),
            method: "post",
            processData: false,
            contentType: false,
            data: formData,
            success: function(data) {
                console.log(data);
                onComplete();
            },
            error: function(data) {
                console.log(data);
                onComplete();
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
                // uploadDir(item, folder);
                // traverseFileTree(item, uploadFunc);
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