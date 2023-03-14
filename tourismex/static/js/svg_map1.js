document.addEventListener('DOMContentLoaded', function() {
  var tooltip = document.querySelector('#tooltip');
  var districts = document.querySelectorAll('.district');
  var popupBg = document.querySelector('#info_bg');
  var cities = document.querySelector('#info_cities');
  var climate = document.querySelector('#info_climate');
  var geo = document.querySelector('#info_geo');

  districts.forEach(district => {

    district.addEventListener('mousemove', function(m1) {
      tooltip.innerText = "Район: " + this.dataset.title;
      cities.innerText = "Крупнейшие города: " + this.dataset.cities;
      climate.innerText = "Климат: " + this.dataset.climate;
      geo.innerText = "Географическая характеристика: " + this.dataset.geo;
      tooltip.style.top = (m1.offsetY + 10) + 'px';
      tooltip.style.left = (m1.offsetX + 40) + 'px';

    });

    tooltip.addEventListener('mouseover', function(m2) {
      tooltip.style.top = (m2.offsetY + 10) + 'px';
      tooltip.style.left = (m2.offsetX + 40) + 'px';
    });

    district.addEventListener('mouseenter', () => {
      tooltip.style.display = 'block';
    });

    district.addEventListener('mouseleave', () => {
      tooltip.style.display = 'none';
    });
  });
});
