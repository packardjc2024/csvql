// Add event listeners
$(document).ready(function(){
    $('.field').on('change', updateRowField);
    $('#import-csv').on('change', uploadFile);
});


// Set the cookie to use ajax post with django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}



function updateRowField(){
    let field = $(this);
    const csrftoken = getCookie('csrftoken');
    $.ajax({
        method: "POST",
        url: "/update_row_field/",
        dataType: "json",
        data: {
            'row': field.closest('.table-row').attr('id'),
            'column': $(`#${field.attr('name')}`).val(),
            'value': field.val()
        },
        headers: {"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": csrftoken,},
        success: function(data) {
            console.log('Field updated successfully');
        },
        error: function(){
            console.log('Unable to update field');
        }
    });
}


function uploadFile(event){
    console.log('file upload triggered');
    event.preventDefault();
    $('#import-form').submit();
}
