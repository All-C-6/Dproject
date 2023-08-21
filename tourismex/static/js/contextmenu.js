let chatblock_CM = document.getElementById('chatblock');
var contextMenu = document.getElementById('ChatContextMenu');
var deleteBtn = document.getElementById('delete_message');


chatblock_CM.addEventListener('contextmenu', function(m1) {
    if (event.target != chatblock_CM) {
        m1.preventDefault();
        contextMenu.style.display = 'block';
        contextMenu.style.top = m1.pageY + 20 + 'px';
        contextMenu.style.left = m1.pageX +20 + 'px';
        contextMenu.addEventListener('click', function() {
         if (event.target == deleteBtn) {
            m1.target.parentElement.classList.add('hidden');
         }
        });
       }

});

document.addEventListener('click', function(event) {
  contextMenu.style.display = 'none';
});