const feed = document.getElementById("feed")
const feed_btn = document.getElementById('feed_button');

feed_btn.addEventListener('click', () => {
    if (!feed.classList.contains('hidden')) {
        feed.classList.add("hidden");

    }
    else {
        feed.classList.remove("hidden");
        }

});
