const registerBtn = document.getElementById('register-btn');
const registerModal = document.getElementById('register-modal');
const h2 = document.getElementById('register-modal-title');

document.addEventListener('click', () => {
    if (event.target == registerBtn) {
        registerModal.classList.remove('hidden');

    }
    else if (event.target !== registerModal) {
        registerModal.classList.add('hidden');
        }

});
