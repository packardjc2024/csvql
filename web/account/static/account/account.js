// // Set events on the document
// $(document).ready(function(){
//     $("#login_form_form").on('submit', submitForm);
// });


// // Set the cookie to use ajax post with django
// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         const cookies = document.cookie.split(';');
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();
//             // Does this cookie string begin with the name we want?
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }


// // Adds a new comment to the end of the list with the form is submitted
// function submitForm(event){
//     event.preventDefault();
//     const csrftoken = getCookie('csrftoken');
//     $.ajax({
//         method: "POST",
//         url: "/account/login_page/",
//         dataType: "json",
//         data: $(this).serialize(),
//         headers: {"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": csrftoken,},
//         success: function(data) {
//             if(data['success']){
//                 $('#main_login_container').empty();
//                 $('#main_login_container').append(data['html']);
//             } else{
//                 alert(data['message']);
//                 document.getElementById('login_form_form').reset();
//             }
//          },
//         error: function(data){
//             alert('something went wrong');
//          }
//     });
// }

// // window.location.href = '/'