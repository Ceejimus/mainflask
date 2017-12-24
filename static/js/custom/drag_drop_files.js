var DragDropFiles = (function() {
    'use strict';

    var getElements = function() {
        return {
            DropArea: $(".droparea")
        };
    };

    var dragHandler = function(evt){
        evt.preventDefault();
    };

    var dropHandler = function(evt){
    evt.preventDefault();
    var files = evt.originalEvent.dataTransfer.files;

    var formData = new FormData();
    formData.append("file", files[0]);


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
                alert('success');
            },
        error: function(data) {
                alert('fail');
                console.log(data);
        }
    });
};

    var bindEvents = function(elements) {

        var dropHandlerSet = {
            dragover: dragHandler,
            drop: dropHandler
        };

        elements.DropArea.on(dropHandlerSet)
    }

    var init = function() {
        var elements = getElements();
        bindEvents(elements);
    };

    return {
        Init: init
    };

})();
