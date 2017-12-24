var Admin = (function() {
	'use strict';

    var Urls = {};

    var getElements = function() {
        return {
            AcceptButton: $(".accept-btn"),
            RejectButton: $(".reject-btn"),
        };
    };

    var processUser = function($userRow, action) {
        var userId = $userRow.data('id');
        var groupId = $userRow.find(".group-select").val();

        if (action !== 'reject' && groupId == "") {
            alert("Select a group!");
            return
        }

        $.ajax({
            url: Urls.ProcessUser,
            method: 'POST',
            data: JSON.stringify({
                userId: userId,
                groupId: groupId,
                action: action
            }),
            contentType: 'application/json;charset=UTF-8',
            success: function(data) {
                $uerRow.remove()
                console.log(data);
            },
            error: function(data) {
                alert(JSON.stringify(data));
            }
        });
    };

    var bindEvents = function(elements) {
        elements.AcceptButton.on("click", function() {
            var $userRow = $(this).closest('.pending-user');
            processUser($userRow, 'accept');
        });

        elements.RejectButton.on("click", function() {
            var $userRow = $(this).closest('.pending-user');
            processUser($userRow, 'reject');
        });
    };

    var init = function(urls) {
        Urls = urls;
        var elements = getElements();
        bindEvents(elements)
    };

	return {
		Init: init
	};
})();