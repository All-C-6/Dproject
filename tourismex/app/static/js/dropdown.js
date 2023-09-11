const button = document.getElementById('menu-button');
const menu = document.querySelector('[role="menu"]');

button.addEventListener('click', () => {
  const expanded = button.getAttribute('aria-expanded') === 'true' || false;
  button.setAttribute('aria-expanded', !expanded);
  menu.classList.toggle('hidden');
});

document.addEventListener('click', (event) => {
  if (!button.contains(event.target)) {
    button.setAttribute('aria-expanded', false);
    menu.classList.add('hidden');
  }
});

